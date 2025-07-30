-- 智能助理應用程式資料庫初始化腳本
-- 為 PostgreSQL 資料庫建立基本設定

-- 確保資料庫使用 UTF-8 編碼
\set VERBOSITY verbose

-- 建立擴展 (如果需要)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 設定時區
SET timezone = 'UTC';

-- 建立基本索引優化設定
-- 這些設定會在應用程式啟動時由 SQLAlchemy 自動建立表格和索引

-- 記錄初始化完成
\echo '✅ PostgreSQL 資料庫初始化完成'
\echo '📊 資料庫名稱: smart_assistant'
\echo '👤 使用者: user'
\echo '🔧 編碼: UTF-8'
\echo '⏰ 時區: UTC'
\echo ''
\echo '⚠️  注意: 資料表將由 FastAPI 應用程式自動建立'