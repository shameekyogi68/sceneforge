-- =========================================================================
-- SceneForge Supabase Database Schema Setup
-- Run this in the Supabase SQL Editor (https://supabase.com/dashboard)
--
-- Production-hardened version:
-- - NOT NULL foreign keys and CHECK constraints on enums/status/role.
-- - Trigger to auto-create profiles row for every new auth user.
-- - match_chunks RPC enforces project ownership via auth.uid().
-- - updated_at columns and file metadata on documents.
-- =========================================================================

-- 1. Enable pgvector extension for vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Helper function: updated_at trigger
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Create Projects table
CREATE TABLE IF NOT EXISTS projects (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name        TEXT NOT NULL,
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- 4. Create Documents table (tracks upload metadata and processing status)
CREATE TABLE IF NOT EXISTS documents (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_id  UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    filename    TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'processing',
    page_count  INTEGER DEFAULT 0,
    processed_pages INTEGER DEFAULT 0,
    file_size_bytes BIGINT,
    content_hash TEXT,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    CONSTRAINT documents_status_check CHECK (status IN ('processing', 'ready', 'error')),
    CONSTRAINT documents_processed_pages_check CHECK (processed_pages <= page_count),
    CONSTRAINT documents_filename_not_empty CHECK (LENGTH(filename) > 0)
);

-- 5. Create Document Chunks table (stores PDF text segments and vector embeddings)
CREATE TABLE IF NOT EXISTS document_chunks (
    id          BIGSERIAL PRIMARY KEY,
    project_id  UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    filename    TEXT NOT NULL,
    page_num    INTEGER NOT NULL,
    chunk_text  TEXT NOT NULL,
    embedding   VECTOR(768),
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    CONSTRAINT document_chunks_page_num_positive CHECK (page_num > 0)
);

-- 6. Create Profiles table (used for tracking daily user rate limits)
CREATE TABLE IF NOT EXISTS profiles (
    id                  UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email               TEXT,
    questions_today     INT DEFAULT 0,
    last_question_date  DATE DEFAULT CURRENT_DATE,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    CONSTRAINT profiles_questions_non_negative CHECK (questions_today >= 0)
);

-- 7. Create Conversations table (groups chat messages)
CREATE TABLE IF NOT EXISTS conversations (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_id  UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title       TEXT,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- 8. Create Messages table (stores chat history)
CREATE TABLE IF NOT EXISTS messages (
    id                  BIGSERIAL PRIMARY KEY,
    conversation_id     UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role                TEXT NOT NULL,
    content             TEXT NOT NULL,
    sources             JSONB,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    CONSTRAINT messages_role_check CHECK (role IN ('user', 'assistant', 'system'))
);

-- 9. Create Project Memories table (fast, shared cross-session memory)
CREATE TABLE IF NOT EXISTS project_memories (
    id          BIGSERIAL PRIMARY KEY,
    project_id  UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    fact_text   TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- =========================================================================
-- Indexes
-- =========================================================================

-- Approximate Nearest Neighbor (ANN) index for fast cosine similarity vector search
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx ON document_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Foreign key & filtering indexes for performance and isolation
CREATE INDEX IF NOT EXISTS document_chunks_project_id_idx ON document_chunks (project_id);
CREATE INDEX IF NOT EXISTS document_chunks_document_id_idx ON document_chunks (document_id);
CREATE INDEX IF NOT EXISTS documents_project_id_idx ON documents (project_id);
CREATE INDEX IF NOT EXISTS documents_status_idx ON documents (status);
CREATE INDEX IF NOT EXISTS documents_filename_idx ON documents (filename);
CREATE INDEX IF NOT EXISTS conversations_project_id_idx ON conversations (project_id);
CREATE INDEX IF NOT EXISTS messages_conversation_id_idx ON messages (conversation_id);
CREATE INDEX IF NOT EXISTS messages_role_idx ON messages (role);
CREATE INDEX IF NOT EXISTS projects_user_id_idx ON projects (user_id);
CREATE INDEX IF NOT EXISTS project_memories_project_id_idx ON project_memories (project_id);

-- Full-Text Search GIN index for fast keyword matching and hybrid retrieval
CREATE INDEX IF NOT EXISTS document_chunks_fts_idx ON document_chunks
    USING gin (to_tsvector('english', chunk_text));

-- Missing performance indexes
CREATE INDEX IF NOT EXISTS profiles_last_question_date_idx ON profiles (last_question_date);
CREATE INDEX IF NOT EXISTS messages_conversation_created_idx ON messages (conversation_id, created_at);
CREATE INDEX IF NOT EXISTS conversations_project_created_idx ON conversations (project_id, created_at DESC);

-- =========================================================================
-- Updated-at triggers
-- =========================================================================
CREATE TRIGGER projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER document_chunks_updated_at BEFORE UPDATE ON document_chunks
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER messages_updated_at BEFORE UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER project_memories_updated_at BEFORE UPDATE ON project_memories
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =========================================================================
-- Profile auto-creation trigger
-- =========================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, questions_today, last_question_date)
    VALUES (NEW.id, NEW.email, 0, CURRENT_DATE)
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing trigger if it exists so the SQL file can be re-run safely.
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- =========================================================================
-- Database Functions (RPC)
-- =========================================================================

-- match_chunks: Performs cosine similarity search against document_chunks.
-- SECURITY DEFINER is used so the function can verify ownership regardless of
-- the caller's role. The auth.uid() check prevents cross-user data leakage
-- when the backend calls this with a service-role key.
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding VECTOR(768),
    project_id      UUID,
    match_count     INTEGER DEFAULT 5
)
RETURNS TABLE(
    chunk_text  TEXT,
    filename    TEXT,
    page_num    INTEGER,
    document_id UUID,
    similarity  FLOAT
)
LANGUAGE SQL STABLE SECURITY DEFINER AS $$
    SELECT
        document_chunks.chunk_text,
        document_chunks.filename,
        document_chunks.page_num,
        document_chunks.document_id,
        1 - (document_chunks.embedding <=> query_embedding) AS similarity
    FROM document_chunks
    WHERE document_chunks.project_id = match_chunks.project_id
      AND EXISTS (
          SELECT 1 FROM projects
          WHERE projects.id = document_chunks.project_id
            AND projects.user_id = auth.uid()
      )
    ORDER BY document_chunks.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- =========================================================================
-- Row Level Security (RLS) Policies
-- =========================================================================

-- Enable RLS on all tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_memories ENABLE ROW LEVEL SECURITY;

-- Projects Policy (Users only access their own projects)
DROP POLICY IF EXISTS "Users own their projects" ON projects;
CREATE POLICY "Users own their projects" ON projects
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Documents Policy (Users only access documents belonging to their projects)
DROP POLICY IF EXISTS "Users own their documents" ON documents;
CREATE POLICY "Users own their documents" ON documents
    USING (EXISTS (
        SELECT 1 FROM projects
        WHERE projects.id = documents.project_id
        AND projects.user_id = auth.uid()
    ))
    WITH CHECK (EXISTS (
        SELECT 1 FROM projects
        WHERE projects.id = documents.project_id
        AND projects.user_id = auth.uid()
    ));

-- Document Chunks Policy (Users only access chunks belonging to their projects)
DROP POLICY IF EXISTS "Users own their chunks" ON document_chunks;
CREATE POLICY "Users own their chunks" ON document_chunks
    USING (EXISTS (
        SELECT 1 FROM projects
        WHERE projects.id = document_chunks.project_id
        AND projects.user_id = auth.uid()
    ))
    WITH CHECK (EXISTS (
        SELECT 1 FROM projects
        WHERE projects.id = document_chunks.project_id
        AND projects.user_id = auth.uid()
    ));

-- Conversations Policy (Users only access conversations belonging to their projects)
DROP POLICY IF EXISTS "Users own their conversations" ON conversations;
CREATE POLICY "Users own their conversations" ON conversations
    USING (EXISTS (
        SELECT 1 FROM projects
        WHERE projects.id = conversations.project_id
        AND projects.user_id = auth.uid()
    ))
    WITH CHECK (EXISTS (
        SELECT 1 FROM projects
        WHERE projects.id = conversations.project_id
        AND projects.user_id = auth.uid()
    ));

-- Messages Policy (Users only access messages in their conversations)
DROP POLICY IF EXISTS "Users own their messages" ON messages;
CREATE POLICY "Users own their messages" ON messages
    USING (EXISTS (
        SELECT 1 FROM conversations
        JOIN projects ON projects.id = conversations.project_id
        WHERE conversations.id = messages.conversation_id
        AND projects.user_id = auth.uid()
    ))
    WITH CHECK (EXISTS (
        SELECT 1 FROM conversations
        JOIN projects ON projects.id = conversations.project_id
        WHERE conversations.id = messages.conversation_id
        AND projects.user_id = auth.uid()
    ));

-- Profiles Policy (Users only access their own profile row)
DROP POLICY IF EXISTS "Users own their profiles" ON profiles;
CREATE POLICY "Users own their profiles" ON profiles
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Project Memories Policy (Users only access memories belonging to their projects)
DROP POLICY IF EXISTS "Users own their project memories" ON project_memories;
CREATE POLICY "Users own their project memories" ON project_memories
    USING (EXISTS (
        SELECT 1 FROM projects
        WHERE projects.id = project_memories.project_id
        AND projects.user_id = auth.uid()
    ))
    WITH CHECK (EXISTS (
        SELECT 1 FROM projects
        WHERE projects.id = project_memories.project_id
        AND projects.user_id = auth.uid()
    ));

-- Allow the service role to bypass RLS for trusted backend operations.
-- Supabase service role key bypasses RLS by default, but explicit policies
-- are kept here for documentation and direct client access.
