"""
用戶資料庫模型
定義用戶相關的 SQLAlchemy 模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from ..core.database import Base


class User(Base):
    """用戶模型"""
    
    __tablename__ = "users"
    
    # 基本欄位
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False, comment="用戶電子郵件")
    full_name = Column(String(100), nullable=False, comment="用戶全名")
    hashed_password = Column(String(255), nullable=False, comment="加密後的密碼")
    
    # 狀態欄位
    is_active = Column(Boolean, default=True, nullable=False, comment="用戶是否啟用")
    is_verified = Column(Boolean, default=False, nullable=False, comment="電子郵件是否已驗證")
    is_superuser = Column(Boolean, default=False, nullable=False, comment="是否為超級用戶")
    
    # 時間戳記
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="建立時間"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新時間"
    )
    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="最後登入時間"
    )
    
    # 額外資訊
    profile_picture_url = Column(String(500), nullable=True, comment="個人頭像 URL")
    bio = Column(Text, nullable=True, comment="個人簡介")
    
    # 安全相關
    failed_login_attempts = Column(Integer, default=0, nullable=False, comment="失敗登入次數")
    locked_until = Column(DateTime(timezone=True), nullable=True, comment="帳戶鎖定直到此時間")
    password_changed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="密碼最後變更時間"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    @property
    def is_locked(self) -> bool:
        """檢查帳戶是否被鎖定"""
        if self.locked_until is None:
            return False
        
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) < self.locked_until
    
    def to_dict(self) -> dict:
        """轉換為字典格式（不包含敏感資訊）"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login_at": self.last_login_at,
            "profile_picture_url": self.profile_picture_url,
            "bio": self.bio
        }