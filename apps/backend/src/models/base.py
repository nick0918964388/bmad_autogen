"""
SQLAlchemy 基底類別定義
使用 SQLAlchemy 2.0+ 的 DeclarativeBase
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 ORM 模型的基底類別"""
    pass