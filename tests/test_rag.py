import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add workspace to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the environment variables before main import
os.environ["GEMINI_API_KEY"] = "dummy_key"
os.environ["SUPABASE_URL"] = "https://dummy.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy_anon_key"

with patch("supabase.create_client") as mock_create_client:
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    from backend.rag import chunk_text, build_prompt, extract_text_from_pdf

class TestRag(unittest.TestCase):
    
    def test_chunk_text_basic(self):
        # 100 words input
        words = ["word"] * 100
        text = " ".join(words)
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        # First chunk: 0 to 50
        # Second chunk: 40 to 90
        # Third chunk: 80 to 100
        self.assertEqual(len(chunks), 3)
        self.assertEqual(len(chunks[0].split()), 50)
        self.assertEqual(len(chunks[1].split()), 50)
        self.assertEqual(len(chunks[2].split()), 20)

    def test_chunk_text_short(self):
        text = "This is a short text with less than fifty words."
        chunks = chunk_text(text)
        self.assertEqual(chunks, [text])

    def test_chunk_text_empty(self):
        self.assertEqual(chunk_text(""), [])
        self.assertEqual(chunk_text("   "), [])

    @patch("fitz.open")
    def test_extract_text_returns_pages(self, mock_fitz_open):
        mock_doc = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "   "  # Blank page
        mock_page3 = MagicMock()
        mock_page3.get_text.return_value = "Page 3 content"
        
        mock_doc.__iter__.return_value = [mock_page1, mock_page2, mock_page3]
        mock_fitz_open.return_value.__enter__.return_value = mock_doc
        
        pages = extract_text_from_pdf("dummy.pdf")
        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[0], {"text": "Page 1 content", "page": 1})
        self.assertEqual(pages[1], {"text": "Page 3 content", "page": 3})

    def test_build_prompt_contains_sources(self):
        question = "What is the secret?"
        chunks = [
            {"filename": "doc1.pdf", "page_num": 5, "chunk_text": "The secret is chocolate."},
            {"filename": "doc2.pdf", "page_num": 12, "chunk_text": "Chocolate is good."}
        ]
        prompt = build_prompt(question, chunks)
        
        self.assertIn("Question: What is the secret?", prompt)
        self.assertIn("[SOURCE 1: doc1.pdf, page 5]", prompt)
        self.assertIn("The secret is chocolate.", prompt)
        self.assertIn("[SOURCE 2: doc2.pdf, page 12]", prompt)
        self.assertIn("Chocolate is good.", prompt)

    def test_build_prompt_with_memory(self):
        question = "What is the secret?"
        chunks = [{"filename": "doc1.pdf", "page_num": 5, "chunk_text": "Some text."}]
        memory = "• User likes chocolate.\n• Project name is secret."
        prompt = build_prompt(question, chunks, project_memory=memory)
        
        self.assertIn("=== PREVIOUS SESSION FACTS ===", prompt)
        self.assertIn("• User likes chocolate.", prompt)
        self.assertIn("• Project name is secret.", prompt)

    def test_build_prompt_no_hallucination_instruction(self):
        prompt = build_prompt("any", [])
        self.assertIn("Answer ONLY from the numbered source documents", prompt)
        self.assertIn("Do NOT add outside knowledge", prompt)

if __name__ == "__main__":
    unittest.main()
