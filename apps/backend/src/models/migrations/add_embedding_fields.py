"""
資料庫遷移腳本：添加 Embedding 相關欄位
新增向量化相關的欄位到 knowledge_bases 和 document_chunks 表
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import Base, engine
import logging

logger = logging.getLogger(__name__)


def upgrade_knowledge_bases_table(db: Session):
    """升級 knowledge_bases 表"""
    try:
        # 添加 Embedding 相關欄位到 knowledge_bases 表
        migrations = [
            """
            ALTER TABLE knowledge_bases 
            ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(100) DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS embedding_dimensions INTEGER DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS vector_database_type VARCHAR(50) DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS vector_database_path TEXT DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS embedding_status VARCHAR(50) DEFAULT 'pending',
            ADD COLUMN IF NOT EXISTS embedded_chunks_count INTEGER DEFAULT 0 NOT NULL,
            ADD COLUMN IF NOT EXISTS embedding_started_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS embedding_completed_at TIMESTAMP WITH TIME ZONE DEFAULT NULL;
            """,
            """
            COMMENT ON COLUMN knowledge_bases.embedding_model IS '使用的 Embedding 模型';
            """,
            """
            COMMENT ON COLUMN knowledge_bases.embedding_dimensions IS 'Embedding 向量維度';
            """,
            """
            COMMENT ON COLUMN knowledge_bases.vector_database_type IS '向量資料庫類型';
            """,
            """
            COMMENT ON COLUMN knowledge_bases.vector_database_path IS '向量資料庫路徑';
            """,
            """
            COMMENT ON COLUMN knowledge_bases.embedding_status IS 'Embedding 處理狀態';
            """,
            """
            COMMENT ON COLUMN knowledge_bases.embedded_chunks_count IS '已生成 Embedding 的分塊數量';
            """,
            """
            COMMENT ON COLUMN knowledge_bases.embedding_started_at IS 'Embedding 處理開始時間';
            """,
            """
            COMMENT ON COLUMN knowledge_bases.embedding_completed_at IS 'Embedding 處理完成時間';
            """
        ]
        
        for migration in migrations:
            db.execute(text(migration))
            
        logger.info("knowledge_bases 表 Embedding 欄位添加完成")
        
    except Exception as e:
        logger.error(f"升級 knowledge_bases 表失敗: {str(e)}")
        raise


def upgrade_document_chunks_table(db: Session):
    """升級 document_chunks 表"""
    try:
        # 添加 Embedding 相關欄位到 document_chunks 表
        migrations = [
            """
            ALTER TABLE document_chunks 
            ADD COLUMN IF NOT EXISTS vector_id VARCHAR(255) DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(100) DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS embedding_dimensions INTEGER DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS encoding VARCHAR(50) DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS chunk_size INTEGER DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS start_position INTEGER DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS end_position INTEGER DEFAULT NULL;
            """,
            """
            COMMENT ON COLUMN document_chunks.vector_id IS '向量資料庫中的向量ID';
            """,
            """
            COMMENT ON COLUMN document_chunks.embedding_model IS '使用的 Embedding 模型';
            """,
            """
            COMMENT ON COLUMN document_chunks.embedding_dimensions IS '向量維度';
            """,
            """
            COMMENT ON COLUMN document_chunks.encoding IS '文件編碼';
            """,
            """
            COMMENT ON COLUMN document_chunks.chunk_size IS '分塊大小（字元數）';
            """,
            """
            COMMENT ON COLUMN document_chunks.start_position IS '在原文件中的開始位置';
            """,
            """
            COMMENT ON COLUMN document_chunks.end_position IS '在原文件中的結束位置';
            """
        ]
        
        for migration in migrations:
            db.execute(text(migration))
            
        logger.info("document_chunks 表 Embedding 欄位添加完成")
        
    except Exception as e:
        logger.error(f"升級 document_chunks 表失敗: {str(e)}")
        raise


def create_indexes(db: Session):
    """創建相關索引"""
    try:
        indexes = [
            # 為 knowledge_bases 表創建索引
            """
            CREATE INDEX IF NOT EXISTS idx_knowledge_bases_embedding_status 
            ON knowledge_bases(embedding_status);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_knowledge_bases_embedding_model 
            ON knowledge_bases(embedding_model);
            """,
            
            # 為 document_chunks 表創建索引
            """
            CREATE INDEX IF NOT EXISTS idx_document_chunks_vector_id 
            ON document_chunks(vector_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_model 
            ON document_chunks(embedding_model);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_document_chunks_language 
            ON document_chunks(language);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_document_chunks_file_type 
            ON document_chunks(file_type);
            """,
            
            # 複合索引
            """
            CREATE INDEX IF NOT EXISTS idx_document_chunks_kb_vector 
            ON document_chunks(knowledge_base_id, vector_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_document_chunks_kb_path_chunk 
            ON document_chunks(knowledge_base_id, document_path, chunk_index);
            """
        ]
        
        for index_sql in indexes:
            db.execute(text(index_sql))
            
        logger.info("相關索引創建完成")
        
    except Exception as e:
        logger.error(f"創建索引失敗: {str(e)}")
        raise


def run_migration():
    """執行完整遷移"""
    try:
        with Session(engine) as db:
            logger.info("開始執行 Embedding 欄位遷移...")
            
            # 升級表結構
            upgrade_knowledge_bases_table(db)
            upgrade_document_chunks_table(db)
            
            # 創建索引
            create_indexes(db)
            
            # 提交更改
            db.commit()
            
            logger.info("Embedding 欄位遷移完成")
            
    except Exception as e:
        logger.error(f"遷移失敗: {str(e)}")
        raise


def downgrade_knowledge_bases_table(db: Session):
    """降級 knowledge_bases 表（移除新增欄位）"""
    try:
        migration = """
        ALTER TABLE knowledge_bases 
        DROP COLUMN IF EXISTS embedding_model,
        DROP COLUMN IF EXISTS embedding_dimensions,
        DROP COLUMN IF EXISTS vector_database_type,
        DROP COLUMN IF EXISTS vector_database_path,
        DROP COLUMN IF EXISTS embedding_status,
        DROP COLUMN IF EXISTS embedded_chunks_count,
        DROP COLUMN IF EXISTS embedding_started_at,
        DROP COLUMN IF EXISTS embedding_completed_at;
        """
        
        db.execute(text(migration))
        logger.info("knowledge_bases 表 Embedding 欄位移除完成")
        
    except Exception as e:
        logger.error(f"降級 knowledge_bases 表失敗: {str(e)}")
        raise


def downgrade_document_chunks_table(db: Session):
    """降級 document_chunks 表（移除新增欄位）"""
    try:
        migration = """
        ALTER TABLE document_chunks 
        DROP COLUMN IF EXISTS vector_id,
        DROP COLUMN IF EXISTS embedding_model,
        DROP COLUMN IF EXISTS embedding_dimensions,
        DROP COLUMN IF EXISTS encoding,
        DROP COLUMN IF EXISTS chunk_size,
        DROP COLUMN IF EXISTS start_position,
        DROP COLUMN IF EXISTS end_position;
        """
        
        db.execute(text(migration))
        logger.info("document_chunks 表 Embedding 欄位移除完成")
        
    except Exception as e:
        logger.error(f"降級 document_chunks 表失敗: {str(e)}")
        raise


def drop_indexes(db: Session):
    """刪除相關索引"""
    try:
        indexes = [
            "DROP INDEX IF EXISTS idx_knowledge_bases_embedding_status;",
            "DROP INDEX IF EXISTS idx_knowledge_bases_embedding_model;",
            "DROP INDEX IF EXISTS idx_document_chunks_vector_id;",
            "DROP INDEX IF EXISTS idx_document_chunks_embedding_model;",
            "DROP INDEX IF EXISTS idx_document_chunks_language;",
            "DROP INDEX IF EXISTS idx_document_chunks_file_type;",
            "DROP INDEX IF EXISTS idx_document_chunks_kb_vector;",
            "DROP INDEX IF EXISTS idx_document_chunks_kb_path_chunk;"
        ]
        
        for index_sql in indexes:
            db.execute(text(index_sql))
            
        logger.info("相關索引刪除完成")
        
    except Exception as e:
        logger.error(f"刪除索引失敗: {str(e)}")
        raise


def run_downgrade():
    """執行降級遷移（回滾）"""
    try:
        with Session(engine) as db:
            logger.info("開始執行 Embedding 欄位降級...")
            
            # 刪除索引
            drop_indexes(db)
            
            # 降級表結構
            downgrade_knowledge_bases_table(db)
            downgrade_document_chunks_table(db)
            
            # 提交更改
            db.commit()
            
            logger.info("Embedding 欄位降級完成")
            
    except Exception as e:
        logger.error(f"降級失敗: {str(e)}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        run_downgrade()
    else:
        run_migration()