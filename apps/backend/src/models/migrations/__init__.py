"""
資料庫遷移模組
包含各種資料庫結構更新腳本
"""

from .add_embedding_fields import run_migration, run_downgrade

__all__ = ['run_migration', 'run_downgrade']