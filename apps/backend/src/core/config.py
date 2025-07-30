"""
應用程式核心配置
基於 Pydantic Settings 的環境變數管理
"""

import os
import secrets
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    """應用程式設定"""
    
    # 基本設定
    app_name: str = "智能助理應用程式 API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # 伺服器設定
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 資料庫設定
    database_url: str = "postgresql://user:password@localhost:5432/smart_assistant"
    
    # JWT 認證設定
    secret_key: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 小時
    
    # 密碼設定
    pwd_min_length: int = 8
    pwd_max_length: int = 100
    
    # 帳戶安全設定
    max_login_attempts: int = 5
    account_lockout_duration: int = 30  # 分鐘
    
    # CORS 配置
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://frontend:3000",
        "http://localhost:5173"  # Vite 開發伺服器
    ]
    
    # Google OAuth 設定 (待實作)
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    
    # Ollama 設定
    ollama_api_base_url: str = "http://ollama.webtw.xyz:11434"
    ollama_embedding_model: str = "all-minilm:l6-v2"
    ollama_timeout: int = 30
    ollama_max_retries: int = 3
    
    # 向量資料庫設定
    vector_db_type: str = "faiss"
    vector_db_path: str = "/app/data/vector_db"
    vector_dimension: int = 384
    vector_metric: str = "cosine"
    
    # Embedding 處理設定
    embedding_batch_size: int = 10
    embedding_concurrent_limit: int = 5
    
    # 文件處理設定
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    chunk_size: int = 1000
    chunk_overlap: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 全域設定實例
settings = Settings()