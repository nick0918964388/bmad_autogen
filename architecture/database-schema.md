# Database Schema

本節將 `智能助理應用程式` 的概念數據模型轉換為具體的 PostgreSQL 數據庫 Schema。這些定義將包含表結構、關鍵屬性、索引、約束和表之間的關係。

```sql
-- 使用者 (User) Table
-- 儲存應用程式中使用者的基本資訊，包括本地註冊使用者和透過第三方登入的使用者。
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- 加密過的使用者密碼（僅限本地登入）
    google_id VARCHAR(255) UNIQUE, -- Google 帳號的唯一識別符（僅限 Google 登入）
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引，加速查詢
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_google_id ON users (google_id);


-- 聊天會話 (ChatSession) Table
-- 儲存使用者與智能助理之間的單次對話會話記錄。
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- 索引，加速查詢
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions (user_id);


-- 訊息 (Message) Table
-- 儲存單條聊天訊息的內容和發送者。
CREATE TYPE message_sender_enum AS ENUM ('user', 'assistant', 'system');
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    sender message_sender_enum NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tool_calls JSONB, -- AutoGen 代理人呼叫工具的記錄
    tool_outputs JSONB, -- AutoGen 工具執行輸出的記錄
    CONSTRAINT fk_session
        FOREIGN KEY(session_id)
        REFERENCES chat_sessions(id)
        ON DELETE CASCADE
);

-- 索引，加速查詢
CREATE INDEX idx_messages_session_id ON messages (session_id);
CREATE INDEX idx_messages_timestamp ON messages (timestamp);


-- 知識庫 (KnowledgeBase) Table
-- 代表使用者定義的一個文件資料夾，其內容被導入到向量資料庫中。
CREATE TYPE knowledge_base_status_enum AS ENUM ('pending', 'processing', 'ready', 'error');
CREATE TABLE knowledge_bases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    path TEXT UNIQUE NOT NULL, -- 使用者指定的本地文件資料夾路徑，需要唯一
    status knowledge_base_status_enum NOT NULL DEFAULT 'pending',
    imported_at TIMESTAMP WITH TIME ZONE, -- 最後導入時間
    document_count INTEGER DEFAULT 0, -- 已導入的文件數量
    error_details TEXT, -- 導入錯誤的詳細資訊
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_kb
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- 索引，加速查詢
CREATE INDEX idx_knowledge_bases_user_id ON knowledge_bases (user_id);


-- 文件分塊 (DocumentChunk) Table
-- 儲存從原始文件提取並分塊後的內容，以及其對應的 Embedding 向量。
-- 注意: Embedding 向量本身將主要儲存在向量資料庫中，此處僅作為元數據和引用。
-- 如果 Vector Database 是獨立的 (如 ChromaDB server)，此處可能只儲存向量 ID。
-- 如果 Vector Database 是嵌入式的 (如 Faiss)，則向量本身可能在此處或作為輔助文件儲存。
-- 為了簡潔和示範，假設 `embedding_vector_id` 指向外部向量資料庫中的實際向量。
-- 或者，如果選擇了可以內嵌在 PostgreSQL 的向量擴展，則 `embedding_vector` 可以直接儲存在這裡 (例如 pgvector)。
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_base_id UUID NOT NULL,
    document_path TEXT NOT NULL, -- 原始文件在本地的完整路徑
    chunk_index INTEGER NOT NULL, -- 該分塊在原始文件中的順序
    content TEXT NOT NULL, -- 分塊的文本內容
    -- embedding_vector_id UUID, -- 如果向量本身在獨立的向量資料庫，此處存 ID
    -- 或者，如果使用 pgvector 擴展，則為：embedding_vector VECTOR(384),
    -- all-minilm:l6-v2 模型輸出 384 維向量
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_knowledge_base
        FOREIGN KEY(knowledge_base_id)
        REFERENCES knowledge_bases(id)
        ON DELETE CASCADE,
    UNIQUE (knowledge_base_id, document_path, chunk_index) -- 確保每個分塊的唯一性
);

-- 索引，加速查詢
CREATE INDEX idx_document_chunks_knowledge_base_id ON document_chunks (knowledge_base_id);
-- CREATE INDEX idx_document_chunks_embedding_vector_id ON document_chunks (embedding_vector_id);
-- 如果使用 pgvector，則為 CREATE INDEX ON document_chunks USING HNSW (embedding_vector vector_l2_ops);
```
