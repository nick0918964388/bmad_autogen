"""
認證服務
處理用戶註冊、登入、密碼管理等認證相關業務邏輯
"""

from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from jose import JWTError, jwt

from ..models.user import User
from ..schemas.auth import UserRegistrationRequest, UserLoginRequest, UserResponse, AuthResponse
from ..core.config import settings
from ..core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
    AuthenticationError,
    ServiceError,
    DatabaseError
)


class AuthService:
    """認證服務類別"""
    
    def __init__(self):
        # 密碼加密上下文
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # JWT 設定
        self.secret_key = settings.secret_key or "dev-secret-key-change-in-production"
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """驗證密碼"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            raise ServiceError(f"密碼驗證失敗: {str(e)}")
    
    def get_password_hash(self, password: str) -> str:
        """生成密碼雜湊"""
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            raise ServiceError(f"密碼加密失敗: {str(e)}")
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """建立 JWT 存取令牌"""
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.now(timezone.utc) + expires_delta
            else:
                expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
            
        except Exception as e:
            raise ServiceError(f"JWT 令牌建立失敗: {str(e)}")
    
    def verify_token(self, token: str) -> dict:
        """驗證 JWT 令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            raise AuthenticationError(f"無效的令牌: {str(e)}")
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """根據電子郵件取得用戶"""
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            raise DatabaseError(f"查詢用戶失敗: {str(e)}")
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """根據 ID 取得用戶"""
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            raise DatabaseError(f"查詢用戶失敗: {str(e)}")
    
    def register_user(self, db: Session, user_data: UserRegistrationRequest) -> User:
        """用戶註冊"""
        try:
            # 檢查用戶是否已存在
            existing_user = self.get_user_by_email(db, user_data.email)
            if existing_user:
                raise UserAlreadyExistsError(user_data.email)
            
            # 建立新用戶
            hashed_password = self.get_password_hash(user_data.password)
            
            db_user = User(
                email=user_data.email,
                full_name=user_data.name,
                hashed_password=hashed_password,
                is_active=True,
                is_verified=False  # 需要電子郵件驗證
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return db_user
            
        except UserAlreadyExistsError:
            raise
        except IntegrityError as e:
            db.rollback()
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                raise UserAlreadyExistsError(user_data.email)
            raise DatabaseError(f"資料庫完整性錯誤: {str(e)}")
        except Exception as e:
            db.rollback()
            raise ServiceError(f"用戶註冊失敗: {str(e)}")
    
    def authenticate_user(self, db: Session, login_data: UserLoginRequest) -> User:
        """用戶身份驗證"""
        try:
            # 取得用戶
            user = self.get_user_by_email(db, login_data.email)
            if not user:
                raise UserNotFoundError(login_data.email)
            
            # 檢查帳戶狀態
            if not user.is_active:
                raise AuthenticationError("帳戶已被停用")
            
            if user.is_locked:
                raise AuthenticationError("帳戶已被鎖定，請稍後再試")
            
            # 驗證密碼
            if not self.verify_password(login_data.password, user.hashed_password):
                # 記錄失敗嘗試
                user.failed_login_attempts += 1
                
                # 如果失敗次數過多，鎖定帳戶
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
                
                db.commit()
                raise InvalidCredentialsError()
            
            # 成功登入，重置失敗計數
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login_at = datetime.now(timezone.utc)
            db.commit()
            
            return user
            
        except (UserNotFoundError, InvalidCredentialsError, AuthenticationError):
            raise
        except Exception as e:
            raise ServiceError(f"用戶驗證失敗: {str(e)}")
    
    def login_user(self, db: Session, login_data: UserLoginRequest) -> AuthResponse:
        """用戶登入"""
        try:
            # 驗證用戶
            user = self.authenticate_user(db, login_data)
            
            # 建立存取令牌
            access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
            access_token = self.create_access_token(
                data={"sub": str(user.id), "email": user.email},
                expires_delta=access_token_expires
            )
            
            # 建立用戶響應
            user_response = UserResponse.from_orm(user)
            
            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=self.access_token_expire_minutes * 60,  # 轉換為秒
                user=user_response
            )
            
        except Exception as e:
            if isinstance(e, (UserNotFoundError, InvalidCredentialsError, AuthenticationError)):
                raise
            raise ServiceError(f"用戶登入失敗: {str(e)}")
    
    def get_current_user(self, db: Session, token: str) -> User:
        """根據令牌取得當前用戶"""
        try:
            # 驗證令牌
            payload = self.verify_token(token)
            user_id = payload.get("sub")
            
            if user_id is None:
                raise AuthenticationError("無效的令牌內容")
            
            # 取得用戶
            user = self.get_user_by_id(db, int(user_id))
            if user is None:
                raise UserNotFoundError(f"用戶 ID {user_id}")
            
            if not user.is_active:
                raise AuthenticationError("帳戶已被停用")
            
            return user
            
        except (AuthenticationError, UserNotFoundError):
            raise
        except Exception as e:
            raise ServiceError(f"取得當前用戶失敗: {str(e)}")
    
    def change_password(
        self, 
        db: Session, 
        user: User, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """變更用戶密碼"""
        try:
            # 驗證當前密碼
            if not self.verify_password(current_password, user.hashed_password):
                raise InvalidCredentialsError()
            
            # 更新密碼
            user.hashed_password = self.get_password_hash(new_password)
            user.password_changed_at = datetime.now(timezone.utc)
            
            db.commit()
            return True
            
        except InvalidCredentialsError:
            raise
        except Exception as e:
            db.rollback()
            raise ServiceError(f"密碼變更失敗: {str(e)}")


# 建立全局服務實例
auth_service = AuthService()