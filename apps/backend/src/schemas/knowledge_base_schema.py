"""
知識庫相關的 Pydantic Schema 定義
用於知識庫 CRUD 操作的請求/回應數據驗證
"""

import os
import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class KnowledgeBaseStatusEnum(str, Enum):
    """知識庫狀態枚舉"""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class CreateKnowledgeBaseRequest(BaseModel):
    """創建知識庫請求 Schema"""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        strip_whitespace=True,
        description="知識庫名稱",
        examples=["我的專案文件"]
    )
    path: str = Field(
        ...,
        min_length=1,
        strip_whitespace=True,
        description="文件資料夾路徑",
        examples=["/home/user/documents", "C:\\Users\\Documents"]
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, name: str) -> str:
        """驗證知識庫名稱"""
        if not name.strip():
            raise ValueError('知識庫名稱不能為空')
        
        # 檢查是否包含不當字元
        if re.search(r'[<>"\'\\\x00-\x1f\x7f-\x9f]', name):
            raise ValueError('知識庫名稱包含無效字元')
        
        return name.strip()
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, path: str) -> str:
        """驗證文件路徑格式和安全性"""
        path = path.strip()
        
        if not path:
            raise ValueError('文件路徑不能為空')
        
        # 檢查路徑長度
        if len(path) > 1000:
            raise ValueError('文件路徑過長')
        
        # 檢查是否包含不安全的字元
        if re.search(r'[<>"\x00-\x1f\x7f-\x9f]', path):
            raise ValueError('文件路徑包含無效字元')
        
        # 防止路徑遍歷攻擊
        if '..' in path:
            raise ValueError('文件路徑不能包含 ".." 序列')
        
        # 檢查路徑格式（支援 Windows 和 Unix 風格）
        unix_pattern = r'^(/[^/\x00]*)+/?$'
        windows_pattern = r'^[A-Za-z]:(\\[^\\/:*?"<>|\x00]*)*\\?$'
        
        if not (re.match(unix_pattern, path) or re.match(windows_pattern, path)):
            raise ValueError('文件路徑格式無效')
        
        return path


class UpdateKnowledgeBaseRequest(BaseModel):
    """更新知識庫請求 Schema"""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        strip_whitespace=True,
        description="知識庫名稱"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, name: Optional[str]) -> Optional[str]:
        """驗證知識庫名稱"""
        if name is None:
            return name
        
        if not name.strip():
            raise ValueError('知識庫名稱不能為空')
        
        # 檢查是否包含不當字元
        if re.search(r'[<>"\'\\\x00-\x1f\x7f-\x9f]', name):
            raise ValueError('知識庫名稱包含無效字元')
        
        return name.strip()


class KnowledgeBaseResponse(BaseModel):
    """知識庫回應 Schema"""
    
    id: str = Field(
        ...,
        description="知識庫唯一識別碼",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    userId: str = Field(
        ...,
        description="所屬用戶ID",
        examples=["1"]
    )
    name: str = Field(
        ...,
        description="知識庫名稱",
        examples=["我的專案文件"]
    )
    path: str = Field(
        ...,
        description="文件資料夾路徑",
        examples=["/home/user/documents"]
    )
    status: KnowledgeBaseStatusEnum = Field(
        ...,
        description="知識庫處理狀態"
    )
    documentCount: int = Field(
        ...,
        description="文件數量",
        examples=[42]
    )
    errorDetails: Optional[str] = Field(
        None,
        description="錯誤詳細訊息"
    )
    createdAt: datetime = Field(
        ...,
        description="建立時間"
    )
    updatedAt: datetime = Field(
        ...,
        description="更新時間"
    )
    importedAt: Optional[datetime] = Field(
        None,
        description="導入完成時間"
    )
    totalChunks: int = Field(
        default=0,
        description="總分塊數量",
        examples=[128]
    )
    processingStartedAt: Optional[datetime] = Field(
        None,
        description="開始處理時間"
    )
    processingCompletedAt: Optional[datetime] = Field(
        None,
        description="處理完成時間"
    )
    
    # Embedding 相關欄位
    embeddingModel: Optional[str] = Field(
        None,
        description="使用的 Embedding 模型",
        examples=["all-minilm:l6-v2"]
    )
    embeddingDimensions: Optional[int] = Field(
        None,
        description="Embedding 向量維度",
        examples=[384]
    )
    vectorDatabaseType: Optional[str] = Field(
        None,
        description="向量資料庫類型",
        examples=["faiss", "chroma"]
    )
    vectorDatabasePath: Optional[str] = Field(
        None,
        description="向量資料庫路徑"
    )
    embeddingStatus: Optional[str] = Field(
        None,
        description="Embedding 處理狀態",
        examples=["pending", "processing", "completed", "failed"]
    )
    embeddedChunksCount: int = Field(
        default=0,
        description="已生成 Embedding 的分塊數量",
        examples=[85]
    )
    embeddingStartedAt: Optional[datetime] = Field(
        None,
        description="Embedding 處理開始時間"
    )
    embeddingCompletedAt: Optional[datetime] = Field(
        None,
        description="Embedding 處理完成時間"
    )
    
    class Config:
        """Pydantic 配置"""
        from_attributes = True
        use_enum_values = True


class KnowledgeBaseListResponse(BaseModel):
    """知識庫列表回應 Schema"""
    
    knowledgeBases: List[KnowledgeBaseResponse] = Field(
        ...,
        description="知識庫列表"
    )
    total: int = Field(
        ...,
        description="總數量",
        examples=[5]
    )


class KnowledgeBaseStatusResponse(BaseModel):
    """知識庫狀態回應 Schema"""
    
    id: str = Field(
        ...,
        description="知識庫唯一識別碼"
    )
    status: KnowledgeBaseStatusEnum = Field(
        ...,
        description="知識庫處理狀態"
    )
    documentCount: int = Field(
        ...,
        description="文件數量"
    )
    totalChunks: int = Field(
        ...,
        description="總分塊數量"
    )
    errorDetails: Optional[str] = Field(
        None,
        description="錯誤詳細訊息"
    )
    updatedAt: datetime = Field(
        ...,
        description="更新時間"
    )
    importedAt: Optional[datetime] = Field(
        None,
        description="導入完成時間"
    )
    processingStartedAt: Optional[datetime] = Field(
        None,
        description="開始處理時間"
    )
    processingCompletedAt: Optional[datetime] = Field(
        None,
        description="處理完成時間"
    )
    
    class Config:
        """Pydantic 配置"""
        from_attributes = True
        use_enum_values = True


class DocumentChunkResponse(BaseModel):
    """文件分塊回應 Schema"""
    
    id: str = Field(
        ...,
        description="分塊唯一識別碼"
    )
    knowledgeBaseId: str = Field(
        ...,
        description="所屬知識庫ID"
    )
    documentPath: str = Field(
        ...,
        description="文件路徑"
    )
    chunkIndex: int = Field(
        ...,
        description="分塊索引"
    )
    content: str = Field(
        ...,
        description="分塊內容"
    )
    fileSize: Optional[int] = Field(
        None,
        description="原文件大小（字節）"
    )
    fileType: Optional[str] = Field(
        None,
        description="文件類型"
    )
    language: Optional[str] = Field(
        None,
        description="語言代碼"
    )
    
    # Embedding 相關欄位
    vectorId: Optional[str] = Field(
        None,
        description="向量資料庫中的向量ID"
    )
    embeddingModel: Optional[str] = Field(
        None,
        description="使用的 Embedding 模型",
        examples=["all-minilm:l6-v2"]
    )
    embeddingDimensions: Optional[int] = Field(
        None,
        description="向量維度",
        examples=[384]
    )
    encoding: Optional[str] = Field(
        None,
        description="文件編碼",
        examples=["utf-8"]
    )
    chunkSize: Optional[int] = Field(
        None,
        description="分塊大小（字元數）"
    )
    startPosition: Optional[int] = Field(
        None,
        description="在原文件中的開始位置"
    )
    endPosition: Optional[int] = Field(
        None,
        description="在原文件中的結束位置"
    )
    
    createdAt: datetime = Field(
        ...,
        description="建立時間"
    )
    updatedAt: datetime = Field(
        ...,
        description="更新時間"
    )
    
    class Config:
        """Pydantic 配置"""
        from_attributes = True


class ProcessingProgressResponse(BaseModel):
    """處理進度回應 Schema"""
    
    knowledgeBaseId: str = Field(
        ...,
        description="知識庫ID"
    )
    status: KnowledgeBaseStatusEnum = Field(
        ...,
        description="處理狀態"
    )
    processedFiles: int = Field(
        ...,
        description="已處理文件數"
    )
    totalFiles: int = Field(
        ...,
        description="總文件數"
    )
    processedChunks: int = Field(
        ...,
        description="已處理分塊數"
    )
    totalChunks: int = Field(
        ...,
        description="總分塊數"
    )
    currentFile: Optional[str] = Field(
        None,
        description="當前處理的文件"
    )
    estimatedTimeRemaining: Optional[int] = Field(
        None,
        description="預估剩餘時間（秒）"
    )
    
    class Config:
        """Pydantic 配置"""
        use_enum_values = True


class KnowledgeBaseDeleteResponse(BaseModel):
    """知識庫刪除回應 Schema"""
    
    message: str = Field(
        ...,
        description="操作結果訊息",
        examples=["知識庫已成功刪除"]
    )
    deletedKnowledgeBaseId: str = Field(
        ...,
        description="已刪除的知識庫ID"
    )
    deletedChunksCount: int = Field(
        ...,
        description="已刪除的分塊數量"
    )


# Embedding 相關 Schema

class EmbeddingProcessRequest(BaseModel):
    """Embedding 處理請求 Schema"""
    
    batchSize: int = Field(
        default=10,
        ge=1,
        le=50,
        description="批次處理大小",
        examples=[10]
    )
    overrideExisting: bool = Field(
        default=False,
        description="是否覆蓋現有的 Embedding"
    )


class EmbeddingStatusEnum(str, Enum):
    """Embedding 處理狀態枚舉"""
    PENDING = "pending"
    PROCESSING = "processing"
    GENERATING_EMBEDDINGS = "generating_embeddings"
    STORING_VECTORS = "storing_vectors"
    COMPLETED = "completed"
    FAILED = "failed"


class EmbeddingProcessResponse(BaseModel):
    """Embedding 處理回應 Schema"""
    
    knowledgeBaseId: str = Field(
        ...,
        description="知識庫ID"
    )
    status: EmbeddingStatusEnum = Field(
        ...,
        description="處理狀態"
    )
    processedFiles: int = Field(
        ...,
        description="已處理文件數"
    )
    totalChunks: int = Field(
        ...,
        description="總分塊數"
    )
    embeddedChunks: int = Field(
        ...,
        description="已生成 Embedding 的分塊數"
    )
    storedVectors: int = Field(
        ...,
        description="已儲存的向量數"
    )
    processingTimeSeconds: float = Field(
        ...,
        description="處理時間（秒）"
    )
    errorDetails: Optional[str] = Field(
        None,
        description="錯誤詳細訊息"
    )
    
    class Config:
        """Pydantic 配置"""
        use_enum_values = True


class SimilaritySearchRequest(BaseModel):
    """相似性搜索請求 Schema"""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        strip_whitespace=True,
        description="搜索查詢文本",
        examples=["如何實作用戶身份驗證"]
    )
    topK: int = Field(
        default=10,
        ge=1,
        le=50,
        description="返回結果數量",
        examples=[10]
    )
    similarityThreshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="相似度閾值",
        examples=[0.7]
    )
    knowledgeBaseId: Optional[str] = Field(
        None,
        description="限制搜索的知識庫ID"
    )


class SimilaritySearchResult(BaseModel):
    """相似性搜索結果項 Schema"""
    
    vectorId: str = Field(
        ...,
        description="向量ID"
    )
    documentId: str = Field(
        ...,
        description="文件ID"
    )
    documentPath: str = Field(
        ...,
        description="文件路徑"
    )
    chunkIndex: int = Field(
        ...,
        description="分塊索引"
    )
    content: str = Field(
        ...,
        description="分塊內容"
    )
    similarityScore: float = Field(
        ...,
        description="相似度分數"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="額外的元數據"
    )


class SimilaritySearchResponse(BaseModel):
    """相似性搜索回應 Schema"""
    
    query: str = Field(
        ...,
        description="搜索查詢"
    )
    results: List[SimilaritySearchResult] = Field(
        ...,
        description="搜索結果列表"
    )
    totalResults: int = Field(
        ...,
        description="總結果數"
    )
    searchTimeMs: float = Field(
        ...,
        description="搜索時間（毫秒）"
    )


class EmbeddingStatusResponse(BaseModel):
    """Embedding 狀態回應 Schema"""
    
    knowledgeBaseId: str = Field(
        ...,
        description="知識庫ID"
    )
    embeddingStatus: EmbeddingStatusEnum = Field(
        ...,
        description="Embedding 處理狀態"
    )
    embeddingModel: Optional[str] = Field(
        None,
        description="使用的 Embedding 模型"
    )
    embeddingDimensions: Optional[int] = Field(
        None,
        description="向量維度"
    )
    totalChunks: int = Field(
        ...,
        description="總分塊數"
    )
    embeddedChunks: int = Field(
        ...,
        description="已生成 Embedding 的分塊數"
    )
    vectorDatabaseType: Optional[str] = Field(
        None,
        description="向量資料庫類型"
    )
    embeddingStartedAt: Optional[datetime] = Field(
        None,
        description="Embedding 處理開始時間"
    )
    embeddingCompletedAt: Optional[datetime] = Field(
        None,
        description="Embedding 處理完成時間"
    )
    
    class Config:
        """Pydantic 配置"""
        use_enum_values = True