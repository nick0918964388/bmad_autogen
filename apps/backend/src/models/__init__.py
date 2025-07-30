"""
資料庫模型模組
定義 SQLAlchemy 資料庫模型
"""

from .database import Base, get_db, create_tables, drop_tables
from .user import User
from .knowledge_base import KnowledgeBase, DocumentChunk, KnowledgeBaseStatus, add_user_relationships

# 設置用戶關聯關係
add_user_relationships()

__all__ = [
    'Base',
    'get_db', 
    'create_tables',
    'drop_tables',
    'User',
    'KnowledgeBase',
    'DocumentChunk',
    'KnowledgeBaseStatus'
]