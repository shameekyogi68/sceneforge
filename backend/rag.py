"""
rag.py — PDF extraction, chunking, embedding, vector search, and answer generation.

Performance optimisations:
- Batch embedding: all chunks per page sent in one Gemini API call (up to 100 at a time)
- Batch insert:    all chunks per PDF sent in one Supabase INSERT
- Cached model:    GenerativeModel instance reused across requests
- Thinking budget: set to 0 to skip reasoning tokens on RAG answers (saves quota)
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, cast

import fitz  # PyMuPDF
from supabase import create_client

import backend.config as config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy Google GenAI Client Initialization
# ---------------------------------------------------------------------------

_client = None

def _get_genai_client():
    """Retrieve or build the Google GenAI client lazily."""
    global _client
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client

def _get_client(token: Optional[str] = None):
    """Return a JWT-authenticated Supabase client, or the module-level anon client."""
    from backend.auth import get_authenticated_client, get_anon_client
    if token:
        return get_authenticated_client(token)
    return get_anon_client()


# ---------------------------------------------------------------------------
# PDF extraction  (FR: F2)
# ---------------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Open a PDF and return non-blank pages as a list.

    Returns:
        [{"text": str, "page": int}, ...]  — 1-indexed, blank pages skipped.
    """
    pages: List[Dict] = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(cast(Any, doc), start=1):
            text = page.get_text().strip()
            if text:
                pages.append({"text": text, "page": i})
    return pages


# ---------------------------------------------------------------------------
# Chunking  (FR: F3)
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = config.CHUNK_SIZE,
    overlap: int = config.CHUNK_OVERLAP,
) -> List[str]:
    """
    Word-based sliding-window chunker.

    - Returns [text] as-is if fewer than 50 words (short page).
    - Sliding window: start=0, end=start+chunk_size, next start=end-overlap.
    """
    words = text.split()
    if len(words) < 50:
        return [text] if text.strip() else []

    chunks: List[str] = []
    start = 0
    while start < len(words):
        chunk = " ".join(words[start : start + chunk_size])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


# ---------------------------------------------------------------------------
# Embeddings  (FR: F4)
# ---------------------------------------------------------------------------

def _embed_batch(texts: List[str], task_type: str) -> List[List[float]]:
    """
    Embed a list of texts in one API call (up to EMBED_BATCH_SIZE at a time).

    Gemini batch embed returns one embedding per input text in the same order.
    """
    from google.genai import types
    client = _get_genai_client()

    results: List[List[float]] = []
    for i in range(0, len(texts), config.EMBED_BATCH_SIZE):
        batch = texts[i : i + config.EMBED_BATCH_SIZE]
        response = client.models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=config.EMBEDDING_DIMENSION,
            )
        )
        embeddings = response.embeddings
        if not embeddings:
            raise RuntimeError("Gemini returned no embeddings.")
        results.extend([e.values for e in embeddings if e.values is not None])
    if len(results) != len(texts):
        raise RuntimeError(
            f"Gemini returned {len(results)} embeddings for {len(texts)} texts."
        )
    return results


def get_embedding(text: str, task_type: str = "retrieval_document") -> List[float]:
    """Embed a single text. Convenience wrapper around _embed_batch."""
    return _embed_batch([text], task_type)[0]


# ---------------------------------------------------------------------------
# PDF processing pipeline  (FR: F4, F5)
# ---------------------------------------------------------------------------

def process_and_store_pdf(
    pdf_path: str,
    filename: str,
    project_id: str,
    document_id: Optional[str] = None,
    token: Optional[str] = None,
) -> int:
    """
    Extract → chunk → batch-embed → batch-insert all chunks for a PDF.

    Optimisations vs. naïve approach:
    - All chunks accumulated first, then embedded in batches of up to 100
    - All rows inserted in a single Supabase INSERT (one round-trip)

    Returns total chunks stored.
    """
    pages = extract_text_from_pdf(pdf_path)
    client = _get_client(token)

    # 1. Collect all valid (chunk, page_num) pairs
    pending: List[Tuple[str, int]] = []
    for page_data in pages:
        for chunk in chunk_text(page_data["text"]):
            if len(chunk) >= config.MIN_CHUNK_CHARS:
                pending.append((chunk, page_data["page"]))

    if not pending:
        return 0

    # 2. Batch-embed all chunks
    texts = [c for c, _ in pending]
    embeddings = _embed_batch(texts, task_type="retrieval_document")

    # 3. Build rows and batch-insert
    rows = [
        {
            "project_id": project_id,
            **({"document_id": document_id} if document_id else {}),
            "filename":   filename,
            "page_num":   page_num,
            "chunk_text": chunk,
            "embedding":  embedding,
        }
        for (chunk, page_num), embedding in zip(pending, embeddings)
    ]

    # Supabase has a default row limit per insert; split into safe batches of 500
    BATCH = 500
    total_stored = 0
    for i in range(0, len(rows), BATCH):
        try:
            client.table("document_chunks").insert(rows[i : i + BATCH]).execute()
            total_stored += len(rows[i : i + BATCH])
        except Exception as exc:
            logger.exception("Batch insert failed for %s rows %d-%d", filename, i, i + BATCH)
            raise RuntimeError(f"Failed to store chunks for {filename}") from exc

    return total_stored


# ---------------------------------------------------------------------------
# Vector search  (FR: F7)
# ---------------------------------------------------------------------------

def generate_hyde_response(question: str) -> str:
    """
    Generate a hypothetical document answer (HyDE) for query expansion.
    Fails open (returns empty string) on any configuration or network error.
    """
    if config.GEMINI_API_KEY == "dummy_key":
        return ""
    try:
        client = _get_genai_client()
        prompt = (
            f"Write a short, hypothetical sentence or paragraph answering this film-research question: '{question}'\n"
            f"Write a plausible factual answer matching standard research style."
        )
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
        )
        return response.text or ""
    except Exception as exc:
        logger.warning("Failed to generate HyDE expansion: %s", exc)
        return ""


def search_documents(
    question: str,
    project_id: str,
    top_k: int = config.TOP_K_CHUNKS,
    token: Optional[str] = None,
) -> List[Dict]:
    """
    Retrieve top-k chunks using Hybrid Search (Vector Similarity + Full-Text Search)
    merged via Reciprocal Rank Fusion (RRF).
    """
    if top_k <= 0:
        return []

    client = _get_client(token)
    candidate_limit = top_k

    # 1. Vector Search and Full-Text Search (FTS) concurrently
    import concurrent.futures

    def _do_vector_search():
        try:
            # Removed HyDE to save latency
            query_embedding = get_embedding(question, task_type="retrieval_query")
            result = client.rpc(
                "match_chunks",
                {
                    "query_embedding": query_embedding,
                    "project_id":      project_id,
                    "match_count":     candidate_limit,
                },
            ).execute()
            return cast(List[Dict], result.data or [])
        except Exception as exc:
            logger.exception("Vector search RPC failed: %s", exc)
            return []

    def _do_fts_search():
        try:
            fts_res = (
                client.table("document_chunks")
                .select("chunk_text", "filename", "page_num", "document_id")
                .eq("project_id", project_id)
                .wfts("chunk_text", question)
                .limit(candidate_limit)
                .execute()
            )
            return cast(List[Dict], fts_res.data or [])
        except Exception as exc:
            logger.warning("FTS text_search failed: %s", exc)
            return []

    vector_chunks: List[Dict] = []
    fts_chunks: List[Dict] = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        vector_future = executor.submit(_do_vector_search)
        fts_future = executor.submit(_do_fts_search)
        
        vector_chunks = vector_future.result()
        fts_chunks = fts_future.result()

    # 3. Reciprocal Rank Fusion (RRF)
    k_const = 60
    rrf_scores: Dict[Tuple[str, int, str], float] = {}
    chunk_map: Dict[Tuple[str, int, str], Dict] = {}

    def _normalize_key(fn: str, pg: int, txt: str) -> Tuple[str, int, str]:
        # Normalize whitespace and lowercase to prevent duplicate keys due to formatting differences
        return (fn, pg, " ".join(txt.split()).strip().lower())

    # Rank vector chunks
    for rank, chunk in enumerate(vector_chunks, start=1):
        key = _normalize_key(chunk["filename"], chunk["page_num"], chunk["chunk_text"])
        chunk_map[key] = chunk
        rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (k_const + rank)

    # Rank FTS chunks
    for rank, chunk in enumerate(fts_chunks, start=1):
        key = _normalize_key(chunk["filename"], chunk["page_num"], chunk["chunk_text"])
        if key not in chunk_map:
            chunk_copy = dict(chunk)
            if "similarity" not in chunk_copy:
                chunk_copy["similarity"] = 0.0
            chunk_map[key] = chunk_copy
        rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (k_const + rank)

    # Sort keys by RRF score descending
    sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)

    results = [chunk_map[key] for key in sorted_keys[:top_k]]
    return results



# ---------------------------------------------------------------------------
# Prompt builder  (FR: F8, F9)
# ---------------------------------------------------------------------------

def build_prompt(
    question: str,
    chunks: List[Dict],
    project_memory: str = "",
) -> str:
    """
    Assemble the Gemini prompt: system instructions + optional memory + source blocks.

    Kept concise to minimise token usage while preserving strict grounding.
    """
    parts: List[str] = [
        "You are ScriptIQ, a film-research assistant.\n"
        "Rules:\n"
        "1. Answer ONLY from the source documents below.\n"
        "2. Cite every fact with [filename, p. page_num] inline (e.g. [c.pdf, p. 4]).\n"
        "3. If the answer is not in the sources, reply: "
        '"I cannot find this information in the uploaded documents."\n'
        "4. Do NOT add outside knowledge.\n",
    ]

    if project_memory:
        parts.append(
            f"=== PREVIOUS SESSION FACTS ===\n{project_memory}\n=== END FACTS ===\n"
        )

    for chunk in chunks:
        parts.append(
            f"[DOCUMENT: {chunk['filename']}, PAGE: {chunk['page_num']}]\n"
            f"{chunk['chunk_text']}\n"
        )

    parts.append(f"Question: {question}")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Answer generation  (FR: F8, F9)
# ---------------------------------------------------------------------------

def answer_with_sources(
    question: str,
    project_id: str,
    project_memory: str = "",
    token: Optional[str] = None,
) -> Tuple[str, List[Dict]]:
    """
    Full RAG pipeline: search → prompt → generate → return (answer, sources).

    Returns ("I cannot find...", []) when no chunks match.
    """
    chunks = search_documents(question, project_id, token=token)

    if not chunks:
        return (
            "I cannot find this information in the uploaded documents.",
            [],
        )

    prompt = build_prompt(question, chunks, project_memory)

    from google.genai import types
    client = _get_genai_client()
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=2048,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    answer_text = response.text or ""

    sources = [
        {
            "filename":     chunk["filename"],
            "page":         chunk["page_num"],
            "document_id":   chunk.get("document_id"),
            "text_preview": chunk["chunk_text"][:200] + "...",
        }
        for chunk in chunks
    ]

    return answer_text, sources


# ---------------------------------------------------------------------------
# Deletion
# ---------------------------------------------------------------------------

def delete_project_documents(project_id: str, token: Optional[str] = None) -> int:
    """Delete all document_chunks for a project. Returns row count deleted."""
    client = _get_client(token)
    result = (
        client.table("document_chunks")
        .delete()
        .eq("project_id", project_id)
        .execute()
    )
    return len(result.data) if result.data else 0
