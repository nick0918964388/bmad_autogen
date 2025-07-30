"""
統一的錯誤處理機制和自定義異常類別
基於架構文件的錯誤處理策略
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException
from datetime import datetime
import uuid


class BaseAppException(Exception):
    """應用程式基礎異常類別"""
    
    def __init__(
        self,
        message: str,
        code: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        self.timestamp = datetime.now().isoformat()
        self.request_id = str(uuid.uuid4())
        super().__init__(self.message)


class AuthenticationError(BaseAppException):
    """認證失敗異常"""
    
    def __init__(self, message: str = "認證失敗", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="AUTH_FAILED",
            details=details,
            status_code=401
        )


class AuthorizationError(BaseAppException):
    """授權失敗異常"""
    
    def __init__(self, message: str = "權限不足", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="AUTH_INSUFFICIENT",
            details=details,
            status_code=403
        )


class ValidationError(BaseAppException):
    """輸入驗證錯誤"""
    
    def __init__(self, message: str = "輸入驗證失敗", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details,
            status_code=422
        )


class NotFoundError(BaseAppException):
    """資源不存在異常"""
    
    def __init__(self, message: str = "資源不存在", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            details=details,
            status_code=404
        )


class ConflictError(BaseAppException):
    """資源衝突異常"""
    
    def __init__(self, message: str = "資源衝突", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RESOURCE_CONFLICT",
            details=details,
            status_code=409
        )


class ServiceError(BaseAppException):
    """內部服務錯誤"""
    
    def __init__(self, message: str = "內部服務錯誤", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="INTERNAL_SERVICE_ERROR",
            details=details,
            status_code=500
        )


class DatabaseError(BaseAppException):
    """資料庫操作錯誤"""
    
    def __init__(self, message: str = "資料庫操作失敗", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            details=details,
            status_code=500
        )


class SecurityError(BaseAppException):
    """安全性錯誤"""
    
    def __init__(self, message: str = "安全性檢查失敗", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SECURITY_ERROR",
            details=details,
            status_code=403
        )


# 用戶相關的特定異常
class UserAlreadyExistsError(ConflictError):
    """用戶已存在異常"""
    
    def __init__(self, email: str):
        super().__init__(
            message=f"用戶 {email} 已存在",
            details={"email": email}
        )
        self.code = "USER_ALREADY_EXISTS"


class InvalidCredentialsError(AuthenticationError):
    """無效的登入憑證"""
    
    def __init__(self):
        super().__init__(
            message="電子郵件或密碼錯誤",
            details={}
        )
        self.code = "INVALID_CREDENTIALS"


class UserNotFoundError(NotFoundError):
    """用戶不存在異常"""
    
    def __init__(self, email: str):
        super().__init__(
            message=f"用戶 {email} 不存在",
            details={"email": email}
        )
        self.code = "USER_NOT_FOUND"


class WeakPasswordError(ValidationError):
    """密碼強度不足異常"""
    
    def __init__(self, requirements: list):
        super().__init__(
            message="密碼強度不足",
            details={"requirements": requirements}
        )
        self.code = "WEAK_PASSWORD"