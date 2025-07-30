"""
知識庫資料庫模型
定義知識庫相關的 SQLAlchemy 模型
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, FLOAT
from enum import Enum as PyEnum
import uuid
from ..core.database import Base


class KnowledgeBaseStatus(PyEnum):
    """知識庫狀態枚舉"""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class KnowledgeBase(Base):
    """知識庫模型"""
    
    __tablename__ = "knowledge_bases"
    
    # 基本欄位
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
        index=True,
        comment="知識庫唯一識別符"
    )
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True,
        comment="所屬用戶ID"
    )
    name = Column(String(255), nullable=False, comment="知識庫名稱")
    path = Column(Text, nullable=False, comment="文件資料夾路徑")
    
    # 狀態欄位
    status = Column(
        SQLEnum(KnowledgeBaseStatus),
        default=KnowledgeBaseStatus.PENDING,
        nullable=False,
        comment="知識庫處理狀態"
    )
    document_count = Column(Integer, default=0, nullable=False, comment="文件數量")
    error_details = Column(Text, nullable=True, comment="錯誤詳細訊息")
    
    # 時間戳記
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="建立時間"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新時間"
    )
    imported_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="導入完成時間"
    )
    
    # 處理統計
    total_chunks = Column(Integer, default=0, nullable=False, comment="總分塊數量")
    processing_started_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="開始處理時間"
    )
    processing_completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="處理完成時間"
    )
    
    # Embedding 相關欄位
    embedding_model = Column(String(100), nullable=True, comment="使用的 Embedding 模型")
    embedding_dimensions = Column(Integer, nullable=True, comment="Embedding 向量維度")
    vector_database_type = Column(String(50), nullable=True, comment="向量資料庫類型")
    vector_database_path = Column(Text, nullable=True, comment="向量資料庫路徑")
    embedding_status = Column(String(50), default="pending", comment="Embedding 處理狀態")
    embedded_chunks_count = Column(Integer, default=0, nullable=False, comment="已生成 Embedding 的分塊數量")
    embedding_started_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Embedding 處理開始時間"
    )
    embedding_completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Embedding 處理完成時間"
    )
    
    # 關聯關係
    user = relationship("User", back_populates="knowledge_bases")
    document_chunks = relationship(
        "DocumentChunk", 
        back_populates="knowledge_base",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name='{self.name}', status='{self.status.value}')>"
    
    def __str__(self):
        return f"{self.name} ({self.status.value})"
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "userId": str(self.user_id),
            "name": self.name,
            "path": self.path,
            "status": self.status.value,
            "documentCount": self.document_count,
            "errorDetails": self.error_details,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "importedAt": self.imported_at,
            "totalChunks": self.total_chunks,
            "processingStartedAt": self.processing_started_at,
            "processingCompletedAt": self.processing_completed_at,
            "embeddingModel": self.embedding_model,
            "embeddingDimensions": self.embedding_dimensions,
            "vectorDatabaseType": self.vector_database_type,
            "vectorDatabasePath": self.vector_database_path,
            "embeddingStatus": self.embedding_status,
            "embeddedChunksCount": self.embedded_chunks_count,
            "embeddingStartedAt": self.embedding_started_at,
            "embeddingCompletedAt": self.embedding_completed_at
        }
    
    def update_status(self, status: KnowledgeBaseStatus, error_details: str = None):
        """更新知識庫狀態"""
        self.status = status
        if error_details:
            self.error_details = error_details
        
        # 更新相關時間戳記
        if status == KnowledgeBaseStatus.PROCESSING and not self.processing_started_at:
            self.processing_started_at = func.now()
        elif status in [KnowledgeBaseStatus.READY, KnowledgeBaseStatus.ERROR]:
            self.processing_completed_at = func.now()
            if status == KnowledgeBaseStatus.READY:
                self.imported_at = func.now()


class DocumentChunk(Base):
    """文件分塊模型"""
    
    __tablename__ = "document_chunks"
    
    # 基本欄位
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
        index=True,
        comment="分塊唯一識別符"
    )
    knowledge_base_id = Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所屬知識庫ID"
    )
    document_path = Column(Text, nullable=False, comment="文件路徑")
    chunk_index = Column(Integer, nullable=False, comment="分塊索引")
    content = Column(Text, nullable=False, comment="分塊內容")
    
    # 向量嵌入
    embedding = Column(ARRAY(FLOAT), nullable=True, comment="向量嵌入")
    vector_id = Column(String(255), nullable=True, comment="向量資料庫中的向量ID")
    embedding_model = Column(String(100), nullable=True, comment="使用的 Embedding 模型")
    embedding_dimensions = Column(Integer, nullable=True, comment="向量維度")
    
    # 元數據
    file_size = Column(Integer, nullable=True, comment="原文件大小（字節）")
    file_type = Column(String(50), nullable=True, comment="文件類型")
    language = Column(String(10), nullable=True, comment="語言代碼")
    encoding = Column(String(50), nullable=True, comment="文件編碼")
    chunk_size = Column(Integer, nullable=True, comment="分塊大小（字元數）")
    start_position = Column(Integer, nullable=True, comment="在原文件中的開始位置")
    end_position = Column(Integer, nullable=True, comment="在原文件中的結束位置")
    
    # 時間戳記
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="建立時間"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新時間"
    )
    
    # 關聯關係
    knowledge_base = relationship("KnowledgeBase", back_populates="document_chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_path='{self.document_path}', chunk_index={self.chunk_index})>"
    
    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.document_path}"
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "knowledgeBaseId": str(self.knowledge_base_id),
            "documentPath": self.document_path,
            "chunkIndex": self.chunk_index,
            "content": self.content,
            "embedding": self.embedding,
            "vectorId": self.vector_id,
            "embeddingModel": self.embedding_model,
            "embeddingDimensions": self.embedding_dimensions,
            "fileSize": self.file_size,
            "fileType": self.file_type,
            "language": self.language,
            "encoding": self.encoding,
            "chunkSize": self.chunk_size,
            "startPosition": self.start_position,
            "endPosition": self.end_position,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }


# 添加用戶關聯關係到 User 模型
def add_user_relationships():
    """為 User 模型添加知識庫關聯"""
    from .user import User
    User.knowledge_bases = relationship(
        "KnowledgeBase", 
        back_populates="user",
        cascade="all, delete-orphan"
    )