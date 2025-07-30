"""
資料庫連接和配置管理
支援 PostgreSQL 資料庫的初始化和會話管理
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 資料庫配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://user:password@localhost:5432/smart_assistant"
)

# 針對測試環境使用 SQLite
if os.getenv("TESTING"):
    DATABASE_URL = "sqlite:///./test.db"

# 建立資料庫引擎
if DATABASE_URL.startswith("sqlite"):
    # SQLite 配置
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
else:
    # PostgreSQL 配置
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )

# 建立會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立基底類別
Base = declarative_base()

def get_db() -> Session:
    """
    取得資料庫會話的依賴函數
    用於 FastAPI 依賴注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    初始化資料庫，建立所有表格
    """
    try:
        # 匯入所有模型以確保它們被註冊
        from ..models import user  # noqa: F401
        
        logger.info("正在建立資料庫表格...")
        Base.metadata.create_all(bind=engine)
        logger.info("資料庫表格建立完成")
        
        return True
    except Exception as e:
        logger.error(f"資料庫初始化失敗: {e}")
        return False

def drop_db():
    """
    刪除所有資料庫表格（僅用於開發/測試）
    """
    try:
        logger.warning("正在刪除所有資料庫表格...")
        Base.metadata.drop_all(bind=engine)
        logger.warning("所有資料庫表格已刪除")
        return True
    except Exception as e:
        logger.error(f"刪除資料庫表格失敗: {e}")
        return False

def check_db_connection() -> bool:
    """
    檢查資料庫連接是否正常
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("資料庫連接正常")
        return True
    except Exception as e:
        logger.error(f"資料庫連接失敗: {e}")
        return False

def get_db_info():
    """
    取得資料庫連接資訊
    """
    return {
        "database_url": DATABASE_URL.replace(DATABASE_URL.split("@")[0].split("//")[1], "***") if "@" in DATABASE_URL else DATABASE_URL,
        "engine_info": str(engine.url),
        "pool_size": getattr(engine.pool, 'size', None),
        "max_overflow": getattr(engine.pool, 'max_overflow', None),
    }