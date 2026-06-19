-- =========================================================================
-- SceneForge Supabase Database Schema Setup
-- Run this in the Supabase SQL Editor (https://supabase.com/dashboard)
-- =========================================================================

-- 1. Enable pgvector extension for vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create Projects table
CREATE TABLE IF NOT EXISTS projects (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name        TEXT NOT NULL,
    user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- 3. Create Documents table (tracks upload metadata and processing status)
CREATE TABLE IF NOT EXISTS documents (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
    filename    TEXT NOT NULL,
    status      TEXT DEFAULT 'processing',
    created_at  TIMESTAMP DEFAULT NOW()
);

-- 4. Create Document Chunks table (stores PDF text segments and vector embeddings)
CREATE TABLE IF NOT EXISTS document_chunks (
    id          BIGSERIAL PRIMARY KEY,
    project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    filename    TEXT NOT NULL,
    page_num    INTEGER,
    chunk_text  TEXT NOT NULL,
    embedding   VECTOR(768),
    created_at  TIMESTAMP DEFAULT NOW()
);


-- 5. Create Profiles table (used for tracking daily user rate limits)
CREATE TABLE IF NOT EXISTS profiles (
    id                  UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email               TEXT,
    questions_today     INT DEFAULT 0,
    last_question_date  DATE DEFAULT CURRENT_DATE,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- 6. Create Conversations table (groups chat messages)
CREATE TABLE IF NOT EXISTS conversations (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
    title       TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- 7. Create Messages table (stores chat history)
CREATE TABLE IF NOT EXISTS messages (
    id                  BIGSERIAL PRIMARY KEY,
    conversation_id     UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role                TEXT,
    content             TEXT,
    sources             JSONB,
    created_at          TIMESTAMP DEFAULT NOW()
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
CREATE INDEX IF NOT EXISTS conversations_project_id_idx ON conversations (project_id);

-- Full-Text Search GIN index for fast keyword matching and hybrid retrieval
CREATE INDEX IF NOT EXISTS document_chunks_fts_idx ON document_chunks 
    USING gin (to_tsvector('english', chunk_text));

-- =========================================================================
-- Database Functions (RPC)
-- =========================================================================

-- match_chunks: Performs cosine similarity search against document_chunks
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
LANGUAGE SQL STABLE AS $$
    SELECT
        document_chunks.chunk_text,
        document_chunks.filename,
        document_chunks.page_num,
        document_chunks.document_id,
        1 - (document_chunks.embedding <=> query_embedding) AS similarity
    FROM document_chunks
    WHERE document_chunks.project_id = match_chunks.project_id
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
