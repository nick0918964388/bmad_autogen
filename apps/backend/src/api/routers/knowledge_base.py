"""
知識庫 API 路由
處理知識庫 CRUD 操作的 HTTP 請求
"""

import asyncio
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ...core.database import get_db
from ...models.user import User
from ...models.knowledge_base import KnowledgeBase, KnowledgeBaseStatus
from ...schemas.knowledge_base_schema import (
    CreateKnowledgeBaseRequest,
    UpdateKnowledgeBaseRequest,
    KnowledgeBaseResponse,
    KnowledgeBaseListResponse,
    KnowledgeBaseStatusResponse,
    KnowledgeBaseDeleteResponse
)
from ...services.document_processing_service import document_processing_service
from ...services.embedding_integration_service import EmbeddingIntegrationService
from ...core.config import settings
from ...core.exceptions import (
    BaseAppException,
    ValidationError,
    SecurityError,
    NotFoundError,
    AuthenticationError,
    DatabaseError
)
from .auth import get_current_user_dependency

# 設置日誌
logger = logging.getLogger(__name__)

# 建立路由器
router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])

# JWT Bearer 安全方案
security = HTTPBearer()

# 創建 embedding 整合服務實例
embedding_service = EmbeddingIntegrationService(
    vector_db_path=settings.vector_db_path
)


@router.post("/", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    request: CreateKnowledgeBaseRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    創建新的知識庫
    
    - **name**: 知識庫名稱
    - **path**: 文件資料夾路徑
    
    創建成功後會在背景開始處理文件
    """
    try:
        # 檢查用戶是否已有同名知識庫
        existing_kb = db.query(KnowledgeBase).filter(
            KnowledgeBase.user_id == current_user.id,
            KnowledgeBase.name == request.name
        ).first()
        
        if existing_kb:
            raise ValidationError(f"已存在同名知識庫: {request.name}")
        
        # 檢查路徑是否已被使用
        existing_path = db.query(KnowledgeBase).filter(
            KnowledgeBase.user_id == current_user.id,
            KnowledgeBase.path == request.path
        ).first()
        
        if existing_path:
            raise ValidationError(f"該路徑已被其他知識庫使用: {request.path}")
        
        # 驗證路徑安全性
        await document_processing_service.validate_path_security(request.path)
        
        # 創建知識庫記錄
        knowledge_base = KnowledgeBase(
            user_id=current_user.id,
            name=request.name,
            path=request.path,
            status=KnowledgeBaseStatus.PENDING
        )
        
        db.add(knowledge_base)
        db.commit()
        db.refresh(knowledge_base)
        
        # 添加背景任務處理文件
        background_tasks.add_task(
            _process_knowledge_base_background,
            str(knowledge_base.id)
        )
        
        logger.info(f"創建知識庫成功: {knowledge_base.name} (ID: {knowledge_base.id})")
        
        return KnowledgeBaseResponse.model_validate(knowledge_base.to_dict())
        
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"創建知識庫失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"創建知識庫失敗: {str(e)}"
        )


@router.get("/", response_model=KnowledgeBaseListResponse)
async def get_knowledge_bases(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    獲取當前用戶的所有知識庫
    """
    try:
        knowledge_bases = db.query(KnowledgeBase).filter(
            KnowledgeBase.user_id == current_user.id
        ).order_by(KnowledgeBase.created_at.desc()).all()
        
        kb_responses = [
            KnowledgeBaseResponse.model_validate(kb.to_dict()) 
            for kb in knowledge_bases
        ]
        
        return KnowledgeBaseListResponse(
            knowledgeBases=kb_responses,
            total=len(kb_responses)
        )
        
    except Exception as e:
        logger.error(f"獲取知識庫列表失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取知識庫列表失敗: {str(e)}"
        )


@router.get("/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    knowledge_base_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    獲取特定知識庫詳細資訊
    """
    try:
        knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not knowledge_base:
            raise NotFoundError(f"找不到知識庫: {knowledge_base_id}")
        
        return KnowledgeBaseResponse.model_validate(knowledge_base.to_dict())
        
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"獲取知識庫失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取知識庫失敗: {str(e)}"
        )


@router.get("/{knowledge_base_id}/status", response_model=KnowledgeBaseStatusResponse)
async def get_knowledge_base_status(
    knowledge_base_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    獲取知識庫處理狀態
    """
    try:
        knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not knowledge_base:
            raise NotFoundError(f"找不到知識庫: {knowledge_base_id}")
        
        return KnowledgeBaseStatusResponse(
            id=str(knowledge_base.id),
            status=knowledge_base.status,
            documentCount=knowledge_base.document_count,
            totalChunks=knowledge_base.total_chunks,
            errorDetails=knowledge_base.error_details,
            updatedAt=knowledge_base.updated_at,
            importedAt=knowledge_base.imported_at,
            processingStartedAt=knowledge_base.processing_started_at,
            processingCompletedAt=knowledge_base.processing_completed_at
        )
        
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"獲取知識庫狀態失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取知識庫狀態失敗: {str(e)}"
        )


@router.put("/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    knowledge_base_id: str,
    request: UpdateKnowledgeBaseRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    更新知識庫資訊（僅限名稱）
    """
    try:
        knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not knowledge_base:
            raise NotFoundError(f"找不到知識庫: {knowledge_base_id}")
        
        # 檢查是否正在處理中
        if knowledge_base.status == KnowledgeBaseStatus.PROCESSING:
            raise ValidationError("知識庫正在處理中，無法修改")
        
        # 更新名稱
        if request.name:
            # 檢查新名稱是否與其他知識庫重複
            existing_kb = db.query(KnowledgeBase).filter(
                KnowledgeBase.user_id == current_user.id,
                KnowledgeBase.name == request.name,
                KnowledgeBase.id != knowledge_base_id
            ).first()
            
            if existing_kb:
                raise ValidationError(f"已存在同名知識庫: {request.name}")
            
            knowledge_base.name = request.name
        
        db.commit()
        db.refresh(knowledge_base)
        
        logger.info(f"更新知識庫成功: {knowledge_base.name} (ID: {knowledge_base.id})")
        
        return KnowledgeBaseResponse.model_validate(knowledge_base.to_dict())
        
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"更新知識庫失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新知識庫失敗: {str(e)}"
        )


@router.delete("/{knowledge_base_id}", response_model=KnowledgeBaseDeleteResponse)
async def delete_knowledge_base(
    knowledge_base_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    刪除知識庫及其所有相關資料
    """
    try:
        knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not knowledge_base:
            raise NotFoundError(f"找不到知識庫: {knowledge_base_id}")
        
        # 刪除相關分塊
        deleted_chunks_count = await document_processing_service.delete_knowledge_base_files(
            knowledge_base, db
        )
        
        # 刪除知識庫記錄
        db.delete(knowledge_base)
        db.commit()
        
        logger.info(f"刪除知識庫成功: {knowledge_base.name} (ID: {knowledge_base.id})")
        
        return KnowledgeBaseDeleteResponse(
            message="知識庫已成功刪除",
            deletedKnowledgeBaseId=str(knowledge_base.id),
            deletedChunksCount=deleted_chunks_count
        )
        
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"刪除知識庫失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除知識庫失敗: {str(e)}"
        )


@router.post("/{knowledge_base_id}/reprocess")
async def reprocess_knowledge_base(
    knowledge_base_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    重新處理知識庫文件
    """
    try:
        knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not knowledge_base:
            raise NotFoundError(f"找不到知識庫: {knowledge_base_id}")
        
        # 檢查當前狀態
        if knowledge_base.status == KnowledgeBaseStatus.PROCESSING:
            raise ValidationError("知識庫正在處理中，請稍後再試")
        
        # 清除現有分塊
        await document_processing_service.delete_knowledge_base_files(knowledge_base, db)
        
        # 重置狀態
        knowledge_base.status = KnowledgeBaseStatus.PENDING
        knowledge_base.document_count = 0
        knowledge_base.total_chunks = 0
        knowledge_base.error_details = None
        knowledge_base.processing_started_at = None
        knowledge_base.processing_completed_at = None
        knowledge_base.imported_at = None
        
        db.commit()
        db.refresh(knowledge_base)
        
        # 添加背景任務重新處理
        background_tasks.add_task(
            _process_knowledge_base_background,
            str(knowledge_base.id)
        )
        
        logger.info(f"開始重新處理知識庫: {knowledge_base.name} (ID: {knowledge_base.id})")
        
        return {"message": "知識庫重新處理已開始", "knowledgeBaseId": str(knowledge_base.id)}
        
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"重新處理知識庫失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新處理知識庫失敗: {str(e)}"
        )


async def _process_knowledge_base_background(knowledge_base_id: str):
    """
    背景任務：處理知識庫文件
    """
    # 建立新的資料庫會話，避免跨線程會話問題
    from ...core.database import get_db
    
    db = next(get_db())
    try:
        # 查詢知識庫
        knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_base_id
        ).first()
        
        if not knowledge_base:
            logger.error(f"背景任務中找不到知識庫: {knowledge_base_id}")
            return
        
        # 開始處理
        await document_processing_service.process_knowledge_base(knowledge_base, db)
        
    except Exception as e:
        logger.error(f"背景處理知識庫失敗: {knowledge_base_id} - {str(e)}")
        
        # 嘗試更新錯誤狀態
        try:
            knowledge_base = db.query(KnowledgeBase).filter(
                KnowledgeBase.id == knowledge_base_id
            ).first()
            
            if knowledge_base:
                knowledge_base.update_status(KnowledgeBaseStatus.ERROR, str(e))
                db.commit()
        except Exception as update_error:
            logger.error(f"更新錯誤狀態失敗: {str(update_error)}")
    finally:
        db.close()


@router.post("/{knowledge_base_id}/process")
async def process_knowledge_base_embeddings(
    knowledge_base_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    觸發知識庫的 Embedding 處理
    
    這會開始為知識庫中的所有文件生成 Embedding 並儲存到向量資料庫
    """
    try:
        knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not knowledge_base:
            raise NotFoundError(f"找不到知識庫: {knowledge_base_id}")
        
        # 檢查當前狀態
        if knowledge_base.status == KnowledgeBaseStatus.PROCESSING:
            raise ValidationError("知識庫正在處理中，請稍後再試")
        
        if knowledge_base.embedding_status == "processing":
            raise ValidationError("Embedding 正在處理中，請稍後再試")
        
        # 更新 embedding 狀態
        knowledge_base.embedding_status = "processing"
        knowledge_base.embedding_started_at = func.now()
        db.commit()
        
        # 添加背景任務處理 Embedding
        background_tasks.add_task(
            _process_embeddings_background,
            str(knowledge_base.id)
        )
        
        logger.info(f"開始 Embedding 處理: {knowledge_base.name} (ID: {knowledge_base.id})")
        
        return {
            "message": "Embedding 處理已開始", 
            "knowledgeBaseId": str(knowledge_base.id),
            "status": "processing"
        }
        
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"觸發 Embedding 處理失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"觸發 Embedding 處理失敗: {str(e)}"
        )


@router.get("/{knowledge_base_id}/embedding-status")
async def get_embedding_status(
    knowledge_base_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    獲取知識庫 Embedding 處理進度
    """
    try:
        knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not knowledge_base:
            raise NotFoundError(f"找不到知識庫: {knowledge_base_id}")
        
        # 獲取處理進度
        processing_status = embedding_service.get_processing_status(knowledge_base_id)
        
        return {
            "knowledgeBaseId": str(knowledge_base.id),
            "embeddingStatus": knowledge_base.embedding_status,
            "embeddedChunksCount": knowledge_base.embedded_chunks_count,
            "totalChunks": knowledge_base.total_chunks,
            "embeddingModel": knowledge_base.embedding_model,
            "embeddingDimensions": knowledge_base.embedding_dimensions,
            "embeddingStartedAt": knowledge_base.embedding_started_at,
            "embeddingCompletedAt": knowledge_base.embedding_completed_at,
            "processingStatus": processing_status.value if processing_status else None
        }
        
    except BaseAppException:
        raise
    except Exception as e:
        logger.error(f"獲取 Embedding 狀態失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取 Embedding 狀態失敗: {str(e)}"
        )


async def _process_embeddings_background(knowledge_base_id: str):
    """
    背景任務：處理知識庫 Embedding
    """
    from ...core.database import get_db
    
    db = next(get_db())
    try:
        # 查詢知識庫
        knowledge_base = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_base_id
        ).first()
        
        if not knowledge_base:
            logger.error(f"背景任務中找不到知識庫: {knowledge_base_id}")
            return
        
        # 初始化 embedding 服務
        await embedding_service.initialize()
        
        # 開始處理 Embedding
        result = await embedding_service.process_knowledge_base_with_embeddings(
            knowledge_base, 
            db,
            batch_size=settings.embedding_batch_size
        )
        
        # 更新結果
        knowledge_base.embedded_chunks_count = result.embedded_chunks
        knowledge_base.embedding_status = "completed" if result.status.value == "completed" else "failed"
        knowledge_base.embedding_completed_at = func.now()
        
        if result.error_details:
            knowledge_base.error_details = result.error_details
        
        db.commit()
        
        logger.info(f"背景 Embedding 處理完成: {knowledge_base_id}")
        
    except Exception as e:
        logger.error(f"背景 Embedding 處理失敗: {knowledge_base_id} - {str(e)}")
        
        # 嘗試更新錯誤狀態
        try:
            knowledge_base = db.query(KnowledgeBase).filter(
                KnowledgeBase.id == knowledge_base_id
            ).first()
            
            if knowledge_base:
                knowledge_base.embedding_status = "failed"
                knowledge_base.embedding_completed_at = func.now()
                knowledge_base.error_details = str(e)
                db.commit()
        except Exception as update_error:
            logger.error(f"更新 Embedding 錯誤狀態失敗: {str(update_error)}")
    finally:
        await embedding_service.close()
        db.close()


# 注意：異常處理器應該在主應用中定義，不是在路由器中