"""
FastAPI 全域錯誤處理器
統一處理應用程式異常並返回標準化的錯誤響應
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from typing import Dict, Any

from .exceptions import BaseAppException


logger = logging.getLogger(__name__)


def create_error_response(
    error_code: str,
    message: str,
    details: Dict[str, Any] = None,
    timestamp: str = None,
    request_id: str = None
) -> Dict[str, Any]:
    """建立標準化的錯誤響應格式"""
    return {
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
            "timestamp": timestamp,
            "requestId": request_id
        }
    }


async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """處理自定義應用程式異常"""
    logger.error(
        f"Application error occurred: {exc.code} - {exc.message}",
        extra={
            "request_id": exc.request_id,
            "error_code": exc.code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    error_response = create_error_response(
        error_code=exc.code,
        message=exc.message,
        details=exc.details,
        timestamp=exc.timestamp,
        request_id=exc.request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """處理 FastAPI HTTP 異常"""
    error_response = create_error_response(
        error_code="HTTP_ERROR",
        message=exc.detail if isinstance(exc.detail, str) else "HTTP 錯誤",
        details={"status_code": exc.status_code} if not isinstance(exc.detail, str) else {}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """處理 Pydantic 驗證錯誤"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    # 將 Pydantic 錯誤轉換為更友善的格式
    validation_errors = {}
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"])
        validation_errors[field] = error["msg"]
    
    error_response = create_error_response(
        error_code="VALIDATION_ERROR",
        message="輸入驗證失敗",
        details={"field_errors": validation_errors}
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """處理資料庫完整性約束錯誤"""
    logger.error(f"Database integrity error: {str(exc)}")
    
    # 根據錯誤類型提供更具體的訊息
    error_message = "資料庫約束錯誤"
    error_code = "DATABASE_CONSTRAINT_ERROR"
    
    if "duplicate key" in str(exc).lower() or "unique constraint" in str(exc).lower():
        error_message = "資料已存在"
        error_code = "DUPLICATE_ENTRY"
    elif "foreign key" in str(exc).lower():
        error_message = "關聯資料不存在"
        error_code = "FOREIGN_KEY_ERROR"
    
    error_response = create_error_response(
        error_code=error_code,
        message=error_message,
        details={"database_error": "約束違反"}
    )
    
    return JSONResponse(
        status_code=409,
        content=error_response
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """處理 SQLAlchemy 資料庫錯誤"""
    logger.error(f"Database error: {str(exc)}")
    
    error_response = create_error_response(
        error_code="DATABASE_ERROR",
        message="資料庫操作失敗",
        details={"database_error": "操作異常"}
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """處理未捕獲的一般異常"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    error_response = create_error_response(
        error_code="INTERNAL_ERROR",
        message="內部服務錯誤",
        details={"error_type": type(exc).__name__}
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )