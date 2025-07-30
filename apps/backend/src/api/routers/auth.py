"""
認證 API 路由
處理用戶註冊、登入相關的 HTTP 請求
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any

from ...core.database import get_db
from ...schemas.auth import (
    UserRegistrationRequest,
    UserLoginRequest,
    UserResponse,
    AuthResponse,
    PasswordChangeRequest
)
from ...services.auth_service import auth_service
from ...core.exceptions import (
    BaseAppException,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
    AuthenticationError,
    WeakPasswordError
)

# 建立路由器
router = APIRouter()

# JWT Bearer 安全方案
security = HTTPBearer()


def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    FastAPI 依賴：取得當前認證用戶
    用於需要認證的端點
    """
    try:
        token = credentials.credentials
        return auth_service.get_current_user(db, token)
    except BaseAppException:
        raise
    except Exception as e:
        raise AuthenticationError(f"認證失敗: {str(e)}")


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用戶註冊",
    description="建立新的用戶帳戶",
    responses={
        201: {
            "description": "註冊成功",
            "content": {
                "application/json": {
                    "example": {
                        "message": "註冊成功",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "full_name": "張三",
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00Z"
                        }
                    }
                }
            }
        },
        409: {
            "description": "用戶已存在",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "USER_ALREADY_EXISTS",
                            "message": "用戶 user@example.com 已存在",
                            "details": {"email": "user@example.com"},
                            "timestamp": "2024-01-01T00:00:00Z",
                            "requestId": "uuid-string"
                        }
                    }
                }
            }
        },
        422: {
            "description": "密碼強度不足或驗證錯誤",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "WEAK_PASSWORD",
                            "message": "密碼強度不足",
                            "details": {
                                "requirements": [
                                    "包含至少一個大寫字母",
                                    "包含至少一個數字"
                                ]
                            },
                            "timestamp": "2024-01-01T00:00:00Z",
                            "requestId": "uuid-string"
                        }
                    }
                }
            }
        }
    }
)
async def register(
    user_data: UserRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    用戶註冊端點
    
    建立新的用戶帳戶，包含完整的輸入驗證和錯誤處理。
    
    - **email**: 有效的電子郵件地址
    - **password**: 至少 8 個字符，包含大小寫字母、數字和特殊字符
    - **confirm_password**: 必須與密碼一致
    - **full_name**: 用戶全名，2-100 個字符
    """
    try:
        # 註冊用戶
        user = auth_service.register_user(db, user_data)
        
        # 生成 JWT token (自動登入)
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # 建立響應
        user_response = UserResponse.from_orm(user)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response,
            expires_in=auth_service.access_token_expire_minutes * 60
        )
        
    except BaseAppException:
        # 重新拋出自定義異常，由全域錯誤處理器處理
        raise
    except Exception as e:
        # 處理未預期的錯誤
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"註冊失敗: {str(e)}"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="用戶登入",
    description="用戶身份驗證並取得存取令牌",
    responses={
        200: {
            "description": "登入成功",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "full_name": "張三",
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00Z"
                        }
                    }
                }
            }
        },
        401: {
            "description": "認證失敗",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "INVALID_CREDENTIALS",
                            "message": "電子郵件或密碼錯誤",
                            "details": {},
                            "timestamp": "2024-01-01T00:00:00Z",
                            "requestId": "uuid-string"
                        }
                    }
                }
            }
        }
    }
)
async def login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    用戶登入端點
    
    驗證用戶憑證並返回 JWT 存取令牌。
    
    - **email**: 用戶電子郵件地址
    - **password**: 用戶密碼
    
    成功登入後會返回：
    - JWT 存取令牌（用於後續 API 請求的認證）
    - 令牌過期時間
    - 用戶基本資訊
    """
    try:
        # 用戶登入
        auth_response = auth_service.login_user(db, login_data)
        
        return auth_response
        
    except BaseAppException:
        # 重新拋出自定義異常，由全域錯誤處理器處理
        raise
    except Exception as e:
        # 處理未預期的錯誤
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登入失敗: {str(e)}"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="取得當前用戶資訊",
    description="根據認證令牌取得當前用戶的詳細資訊",
    responses={
        200: {
            "description": "成功取得用戶資訊",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "張三",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "未認證或令牌無效",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "AUTH_FAILED",
                            "message": "認證失敗",
                            "details": {},
                            "timestamp": "2024-01-01T00:00:00Z",
                            "requestId": "uuid-string"
                        }
                    }
                }
            }
        }
    }
)
async def get_current_user(
    current_user = Depends(get_current_user_dependency)
):
    """
    取得當前用戶資訊端點
    
    需要提供有效的 JWT 令牌在 Authorization header 中：
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    """
    try:
        return UserResponse.from_orm(current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得用戶資訊失敗: {str(e)}"
        )


@router.post(
    "/change-password",
    response_model=Dict[str, str],
    summary="變更密碼",
    description="變更當前用戶的密碼",
    responses={
        200: {
            "description": "密碼變更成功",
            "content": {
                "application/json": {
                    "example": {
                        "message": "密碼變更成功"
                    }
                }
            }
        },
        401: {
            "description": "當前密碼錯誤或未認證",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "INVALID_CREDENTIALS",
                            "message": "電子郵件或密碼錯誤",
                            "details": {},
                            "timestamp": "2024-01-01T00:00:00Z",
                            "requestId": "uuid-string"
                        }
                    }
                }
            }
        }
    }
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    變更密碼端點
    
    需要認證，用戶可以變更自己的密碼。
    
    - **current_password**: 當前密碼
    - **new_password**: 新密碼（需符合強度要求）
    - **confirm_new_password**: 確認新密碼
    """
    try:
        # 變更密碼
        auth_service.change_password(
            db=db,
            user=current_user,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        return {"message": "密碼變更成功"}
        
    except BaseAppException:
        # 重新拋出自定義異常，由全域錯誤處理器處理
        raise
    except Exception as e:
        # 處理未預期的錯誤
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"密碼變更失敗: {str(e)}"
        )


@router.post(
    "/logout",
    response_model=Dict[str, str],
    summary="用戶登出",
    description="登出當前用戶（僅客戶端需要清除令牌）",
    responses={
        200: {
            "description": "登出成功",
            "content": {
                "application/json": {
                    "example": {
                        "message": "登出成功"
                    }
                }
            }
        }
    }
)
async def logout():
    """
    用戶登出端點
    
    由於使用 JWT 無狀態認證，伺服器端不需要特別處理登出邏輯。
    客戶端應該刪除本地儲存的令牌。
    
    注意：實際的令牌失效需要在客戶端實現，或者可以考慮實作令牌黑名單機制。
    """
    return {"message": "登出成功"}


# 路由器標籤和元數據
router.tags = ["認證"]