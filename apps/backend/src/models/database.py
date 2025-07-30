"""
資料庫連接和會話管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from ..core.config import settings

# SQLAlchemy 引擎配置
if settings.database_url:
    # 生產環境使用 PostgreSQL
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug
    )
else:
    # 開發環境使用 SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.debug
    )

# 會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基礎模型類別
Base = declarative_base()


def get_db():
    """
    取得資料庫會話
    用於 FastAPI 依賴注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """建立所有資料表"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """刪除所有資料表（僅供開發使用）"""
    Base.metadata.drop_all(bind=engine)