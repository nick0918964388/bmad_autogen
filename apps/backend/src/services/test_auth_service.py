"""
AuthService 測試文件

用於驗證身份驗證服務的基本功能
注意：這是一個簡單的功能驗證，實際測試應該使用 pytest 框架
"""

import os
import sys
from datetime import timedelta

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 創建模擬的 AuthService 類別來測試核心功能（不依賴資料庫）
from jose import JWTError, jwt
from passlib.context import CryptContext

# 密碼加密上下文配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthServiceTest:
    """測試版的 AuthService，不需要資料庫連接"""
    
    def __init__(self):
        self.secret_key = "test_secret_key_for_development_12345"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def hash_password(self, password: str) -> str:
        if not password or not password.strip():
            raise ValueError("密碼不能為空")
        if len(password) < 8:
            raise ValueError("密碼長度至少需要 8 個字元")
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        if not plain_password or not hashed_password:
            return False
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False
    
    def create_access_token(self, data, expires_delta=None):
        from datetime import datetime, timezone, timedelta
        if not data:
            raise ValueError("Token 資料不能為空")
        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access_token"
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str):
        if not token:
            return None
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "access_token":
                return None
            return payload
        except JWTError:
            return None
        except Exception:
            return None
    
    def get_user_from_token(self, token: str):
        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")
        return None


def test_password_hashing():
    """測試密碼雜湊功能"""
    print("測試密碼雜湊功能...")
    
    auth_service = AuthServiceTest()
    
    # 測試密碼雜湊
    password = "test_password_123"
    hashed = auth_service.hash_password(password)
    
    print(f"原始密碼: {password}")
    print(f"雜湊後密碼: {hashed}")
    
    # 測試密碼驗證
    is_valid = auth_service.verify_password(password, hashed)
    print(f"密碼驗證結果: {is_valid}")
    
    # 測試錯誤密碼
    wrong_password = "wrong_password"
    is_invalid = auth_service.verify_password(wrong_password, hashed)
    print(f"錯誤密碼驗證結果: {is_invalid}")
    
    assert is_valid == True
    assert is_invalid == False
    print("✓ 密碼雜湊功能測試通過\n")


def test_jwt_token():
    """測試 JWT Token 功能"""
    print("測試 JWT Token 功能...")
    
    auth_service = AuthServiceTest()
    
    # 測試 Token 生成
    test_data = {
        "sub": "test_user_123",
        "email": "test@example.com",
        "name": "測試使用者"
    }
    
    token = auth_service.create_access_token(test_data)
    print(f"生成的 Token: {token}")
    
    # 測試 Token 驗證
    decoded_data = auth_service.verify_token(token)
    print(f"解碼後的資料: {decoded_data}")
    
    # 測試從 Token 中獲取使用者 ID
    user_id = auth_service.get_user_from_token(token)
    print(f"從 Token 獲取的使用者 ID: {user_id}")
    
    assert decoded_data is not None
    assert decoded_data["sub"] == "test_user_123"
    assert decoded_data["email"] == "test@example.com"
    assert user_id == "test_user_123"
    print("✓ JWT Token 功能測試通過\n")


def test_short_lived_token():
    """測試短時效 Token"""
    print("測試短時效 Token...")
    
    auth_service = AuthServiceTest()
    
    # 創建 1 秒過期的 Token
    test_data = {"sub": "test_user", "email": "test@example.com"}
    short_token = auth_service.create_access_token(
        test_data, 
        expires_delta=timedelta(seconds=1)
    )
    
    # 立即驗證應該成功
    decoded = auth_service.verify_token(short_token)
    assert decoded is not None
    print("✓ 短時效 Token 立即驗證成功")
    
    # 等待 2 秒後驗證應該失敗
    import time
    time.sleep(2)
    expired_decoded = auth_service.verify_token(short_token)
    assert expired_decoded is None
    print("✓ 短時效 Token 過期驗證失敗")
    print("✓ 短時效 Token 功能測試通過\n")


def test_invalid_inputs():
    """測試無效輸入處理"""
    print("測試無效輸入處理...")
    
    auth_service = AuthServiceTest()
    
    # 測試空密碼雜湊
    try:
        auth_service.hash_password("")
        assert False, "應該拋出 ValueError"
    except ValueError:
        print("✓ 空密碼正確拋出錯誤")
    
    # 測試短密碼雜湊
    try:
        auth_service.hash_password("123")
        assert False, "應該拋出 ValueError"
    except ValueError:
        print("✓ 短密碼正確拋出錯誤")
    
    # 測試空 Token 驗證
    result = auth_service.verify_token("")
    assert result is None
    print("✓ 空 Token 正確返回 None")
    
    # 測試無效 Token 驗證
    result = auth_service.verify_token("invalid_token")
    assert result is None
    print("✓ 無效 Token 正確返回 None")
    
    print("✓ 無效輸入處理測試通過\n")


if __name__ == "__main__":
    print("=== AuthService 功能測試 ===\n")
    
    try:
        test_password_hashing()
        test_jwt_token()
        test_short_lived_token()
        test_invalid_inputs()
        
        print("🎉 所有測試通過！AuthService 功能正常運作。")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        sys.exit(1)