"""
認證相關的 Pydantic Schema 定義
用於註冊和登入請求/回應的數據驗證
"""

import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing_extensions import Self


class UserRegistrationRequest(BaseModel):
    """使用者註冊請求 Schema"""
    
    email: EmailStr = Field(
        ...,
        description="使用者電子郵件地址",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="使用者密碼，至少8個字元",
        examples=["SecurePass123!"]
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        strip_whitespace=True,
        description="使用者姓名",
        examples=["張三"]
    )
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        """
        驗證密碼強度
        - 至少包含一個大寫字母
        - 至少包含一個小寫字母  
        - 至少包含一個數字
        - 至少包含一個特殊字元
        """
        if not re.search(r'[A-Z]', password):
            raise ValueError('密碼必須包含至少一個大寫字母')
        
        if not re.search(r'[a-z]', password):
            raise ValueError('密碼必須包含至少一個小寫字母')
        
        if not re.search(r'\d', password):
            raise ValueError('密碼必須包含至少一個數字')
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>?]', password):
            raise ValueError('密碼必須包含至少一個特殊字元')
        
        return password
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, name: str) -> str:
        """驗證姓名格式"""
        if not name.strip():
            raise ValueError('姓名不能為空')
        
        # 檢查是否包含不當字元
        if re.search(r'[<>"\'\\\x00-\x1f\x7f-\x9f]', name):
            raise ValueError('姓名包含無效字元')
        
        return name.strip()


class UserLoginRequest(BaseModel):
    """使用者登入請求 Schema"""
    
    email: EmailStr = Field(
        ...,
        description="使用者電子郵件地址",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="使用者密碼",
        examples=["SecurePass123!"]
    )


class UserResponse(BaseModel):
    """使用者資料回應 Schema"""
    
    id: int = Field(
        ...,
        description="使用者唯一識別碼",
        examples=[1]
    )
    email: EmailStr = Field(
        ...,
        description="使用者電子郵件地址",
        examples=["user@example.com"]
    )
    name: str = Field(
        ...,
        description="使用者姓名",
        examples=["張三"],
        alias="full_name"
    )
    
    class Config:
        """Pydantic 配置"""
        from_attributes = True  # 允許從 ORM 對象創建
        json_encoders = {
            # 可以在這裡添加自定義 JSON 編碼器
        }


class AuthResponse(BaseModel):
    """認證成功回應 Schema"""
    
    access_token: str = Field(
        ...,
        description="JWT 存取令牌",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="令牌類型",
        examples=["bearer"]
    )
    user: UserResponse = Field(
        ...,
        description="使用者資料"
    )
    expires_in: Optional[int] = Field(
        default=None,
        description="令牌過期時間（秒）",
        examples=[3600]
    )
    
    @field_validator('token_type')
    @classmethod
    def validate_token_type(cls, token_type: str) -> str:
        """驗證令牌類型格式"""
        return token_type.lower()


class TokenRefreshRequest(BaseModel):
    """令牌刷新請求 Schema"""
    
    refresh_token: str = Field(
        ...,
        description="刷新令牌",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )


class PasswordResetRequest(BaseModel):
    """密碼重置請求 Schema"""
    
    email: EmailStr = Field(
        ...,
        description="使用者電子郵件地址",
        examples=["user@example.com"]
    )


class PasswordChangeRequest(BaseModel):
    """密碼變更請求 Schema"""
    
    current_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="目前密碼",
        examples=["OldPass123!"]
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="新密碼",
        examples=["NewPass123!"]
    )
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password_strength(cls, password: str) -> str:
        """
        驗證新密碼強度
        使用與註冊時相同的驗證規則
        """
        if not re.search(r'[A-Z]', password):
            raise ValueError('新密碼必須包含至少一個大寫字母')
        
        if not re.search(r'[a-z]', password):
            raise ValueError('新密碼必須包含至少一個小寫字母')
        
        if not re.search(r'\d', password):
            raise ValueError('新密碼必須包含至少一個數字')
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>?]', password):
            raise ValueError('新密碼必須包含至少一個特殊字元')
        
        return password


class GoogleAuthRequest(BaseModel):
    """Google 認證請求 Schema"""
    
    id_token: str = Field(
        ...,
        description="Google ID 令牌",
        examples=["eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )


class ErrorResponse(BaseModel):
    """錯誤回應 Schema"""
    
    error: dict = Field(
        ...,
        description="錯誤詳細資訊",
        examples=[{
            "code": "INVALID_CREDENTIALS",
            "message": "電子郵件或密碼錯誤",
            "details": {},
            "timestamp": "2024-01-01T12:00:00Z",
            "requestId": "uuid-request-id"
        }]
    )
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "輸入資料驗證失敗",
                    "details": {
                        "field": "password",
                        "issue": "密碼強度不足"
                    },
                    "timestamp": "2024-01-01T12:00:00Z",
                    "requestId": "550e8400-e29b-41d4-a716-446655440000"
                }
            }
        }