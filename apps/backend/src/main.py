"""
智能助理應用程式後端 - FastAPI 主要應用程式
基於架構文件規範建立的 RESTful API 服務
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime
import os
import logging
from typing import Dict, Any

# 匯入路由器
from .api.routers.auth import router as auth_router
from .api.routers.knowledge_base import router as knowledge_base_router

# 匯入錯誤處理器
from .core.error_handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    integrity_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from .core.exceptions import BaseAppException

# 匯入資料庫相關
from .core.database import init_db

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用程式實例
app = FastAPI(
    title="智能助理應用程式 API",
    description="基於 AutoGen 的多代理智能體系統後端服務，包含完整的用戶認證系統",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 註冊錯誤處理器
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://frontend:3000",
        "http://10.10.10.168:3000"
    ],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 應用程式啟動事件
@app.on_event("startup")
async def startup_event():
    """應用程式啟動時執行的初始化作業"""
    logger.info("正在啟動智能助理應用程式後端服務...")
    
    try:
        # 建立資料庫表格
        if init_db():
            logger.info("資料庫表格建立完成")
        else:
            logger.error("資料庫表格建立失敗")
    except Exception as e:
        logger.error(f"資料庫初始化失敗: {str(e)}")
        raise
    
    logger.info("智能助理應用程式後端服務啟動完成")

# 應用程式關閉事件
@app.on_event("shutdown")
async def shutdown_event():
    """應用程式關閉時執行的清理作業"""
    logger.info("正在關閉智能助理應用程式後端服務...")
    logger.info("智能助理應用程式後端服務已關閉")

@app.get("/")
async def root():
    """根路由 - 基本資訊"""
    return {
        "message": "智能助理應用程式 API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """
    健康檢查端點
    用於 Docker Compose 和負載均衡器檢查服務狀態
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "智能助理後端服務",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def api_health_check():
    """
    API 健康檢查端點
    提供更詳細的服務狀態資訊
    """
    # 這裡未來可以加入資料庫、向量資料庫、Ollama 服務的連接檢查
    services_status = {
        "database": "not_configured",  # 待實作
        "ollama": "not_configured",    # 待實作
        "vectorDb": "not_configured"   # 待實作
    }
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": services_status,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# 註冊 API 路由器
app.include_router(auth_router, prefix="/api/auth", tags=["認證"])
app.include_router(knowledge_base_router, prefix="/api", tags=["知識庫"])

# 未來的其他 API 路由將在這裡添加
# 例如: app.include_router(chat_router, prefix="/api/chat", tags=["聊天"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )