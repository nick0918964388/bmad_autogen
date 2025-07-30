"""
Backend schemas 模組
包含所有 Pydantic 資料驗證模型
"""

from .auth import (
    UserRegistrationRequest,
    UserLoginRequest,
    AuthResponse,
    UserResponse,
    TokenRefreshRequest,
    PasswordResetRequest,
    PasswordChangeRequest,
    GoogleAuthRequest,
    ErrorResponse,
)

from .knowledge_base_schema import (
    KnowledgeBaseStatusEnum,
    CreateKnowledgeBaseRequest,
    UpdateKnowledgeBaseRequest,
    KnowledgeBaseResponse,
    KnowledgeBaseListResponse,
    KnowledgeBaseStatusResponse,
    DocumentChunkResponse,
    ProcessingProgressResponse,
    KnowledgeBaseDeleteResponse
)

__all__ = [
    # Auth schemas
    "UserRegistrationRequest",
    "UserLoginRequest", 
    "AuthResponse",
    "UserResponse",
    "TokenRefreshRequest",
    "PasswordResetRequest",
    "PasswordChangeRequest",
    "GoogleAuthRequest",
    "ErrorResponse",
    
    # Knowledge base schemas
    "KnowledgeBaseStatusEnum",
    "CreateKnowledgeBaseRequest",
    "UpdateKnowledgeBaseRequest",
    "KnowledgeBaseResponse",
    "KnowledgeBaseListResponse",
    "KnowledgeBaseStatusResponse",
    "DocumentChunkResponse",
    "ProcessingProgressResponse",
    "KnowledgeBaseDeleteResponse"
]