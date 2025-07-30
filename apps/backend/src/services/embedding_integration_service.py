"""
Embedding 整合服務
整合文件處理、Embedding 生成和向量資料庫儲存的完整工作流程
"""

import logging
import asyncio
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .document_processing_service import DocumentProcessingService, DocumentMetadata, ChunkingStrategy
from .ollama_embedding_service import OllamaEmbeddingService, EmbeddingConfig
from .faiss_vector_database import FaissVectorDatabase
from ..interfaces.vector_database_interface import VectorDatabaseInterface
from ..models.knowledge_base import KnowledgeBase, DocumentChunk, KnowledgeBaseStatus
from ..core.exceptions import BaseAppException, ServiceError

logger = logging.getLogger(__name__)


class EmbeddingProcessingStatus(Enum):
    """Embedding 處理狀態"""
    PENDING = "pending"
    PROCESSING = "processing"
    GENERATING_EMBEDDINGS = "generating_embeddings"
    STORING_VECTORS = "storing_vectors"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class EmbeddingProcessingResult:
    """Embedding 處理結果"""
    knowledge_base_id: str
    status: EmbeddingProcessingStatus
    processed_files: int
    total_chunks: int
    embedded_chunks: int
    stored_vectors: int
    processing_time_seconds: float
    error_details: Optional[str] = None


class EmbeddingProcessingError(BaseAppException):
    """Embedding 處理錯誤"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            message=f"Embedding 處理失敗: {message}",
            error_code="EMBEDDING_PROCESSING_ERROR",
            details=details
        )


class EmbeddingIntegrationService:
    """Embedding 整合服務"""
    
    def __init__(
        self,
        document_service: Optional[DocumentProcessingService] = None,
        embedding_service: Optional[OllamaEmbeddingService] = None,
        vector_database: Optional[VectorDatabaseInterface] = None,
        chunking_strategy: Optional[ChunkingStrategy] = None,
        embedding_config: Optional[EmbeddingConfig] = None,
        vector_db_path: Optional[str] = None
    ):
        """
        初始化 Embedding 整合服務
        
        Args:
            document_service: 文件處理服務
            embedding_service: Embedding 服務
            vector_database: 向量資料庫
            chunking_strategy: 分塊策略
            embedding_config: Embedding 配置
            vector_db_path: 向量資料庫路徑
        """
        self.document_service = document_service or DocumentProcessingService(chunking_strategy)
        self.embedding_config = embedding_config or EmbeddingConfig()
        self.embedding_service = embedding_service
        self.vector_database = vector_database
        
        # 如果沒有提供向量資料庫，創建預設的 Faiss 資料庫
        if not self.vector_database and vector_db_path:
            self.vector_database = FaissVectorDatabase(vector_db_path)
        
        self._processing_lock = asyncio.Lock()
        self._processing_status: Dict[str, EmbeddingProcessingStatus] = {}
    
    async def initialize(self) -> bool:
        """初始化所有服務組件"""
        try:
            # 初始化 Embedding 服務
            if not self.embedding_service:
                self.embedding_service = OllamaEmbeddingService(self.embedding_config)
            
            await self.embedding_service.initialize()
            
            # 初始化向量資料庫
            if self.vector_database:
                await self.vector_database.initialize()
            
            # 健康檢查
            if not await self.health_check():
                raise ServiceError("服務健康檢查失敗")
            
            logger.info("Embedding 整合服務初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"Embedding 整合服務初始化失敗: {str(e)}")
            return False
    
    async def close(self) -> None:
        """關閉所有服務組件"""
        try:
            if self.embedding_service:
                await self.embedding_service.close()
            
            if self.vector_database:
                await self.vector_database.close()
            
            logger.info("Embedding 整合服務已關閉")
            
        except Exception as e:
            logger.error(f"關閉 Embedding 整合服務失敗: {str(e)}")
    
    async def health_check(self) -> bool:
        """健康檢查"""
        try:
            # 檢查 Embedding 服務
            if not self.embedding_service:
                return False
            
            embedding_health = await self.embedding_service.health_check()
            if not embedding_health:
                logger.warning("Embedding 服務健康檢查失敗")
                return False
            
            # 檢查向量資料庫
            if self.vector_database:
                vector_db_health = await self.vector_database.health_check()
                if not vector_db_health:
                    logger.warning("向量資料庫健康檢查失敗")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"健康檢查失敗: {str(e)}")
            return False
    
    async def process_knowledge_base_with_embeddings(
        self,
        knowledge_base: KnowledgeBase,
        db: Session,
        batch_size: int = 10,
        progress_callback: Optional[callable] = None
    ) -> EmbeddingProcessingResult:
        """
        處理知識庫並生成 Embeddings
        
        Args:
            knowledge_base: 知識庫對象
            db: 資料庫會話
            batch_size: 批次處理大小
            progress_callback: 進度回調函數
            
        Returns:
            EmbeddingProcessingResult: 處理結果
        """
        start_time = datetime.now()
        knowledge_base_id = str(knowledge_base.id)
        
        try:
            async with self._processing_lock:
                self._processing_status[knowledge_base_id] = EmbeddingProcessingStatus.PROCESSING
            
            logger.info(f"開始處理知識庫 Embedding: {knowledge_base.name} (ID: {knowledge_base_id})")
            
            # 更新知識庫狀態
            knowledge_base.update_status(KnowledgeBaseStatus.PROCESSING)
            db.commit()
            
            if progress_callback:
                await progress_callback("開始掃描文件...", 0)
            
            # 1. 掃描目錄獲取文件
            files_metadata = await self.document_service.scan_directory(
                knowledge_base.path, 
                return_metadata=True
            )
            
            if not files_metadata:
                raise EmbeddingProcessingError("指定目錄中沒有找到支援的文件")
            
            logger.info(f"找到 {len(files_metadata)} 個文件")
            
            # 2. 處理文件並生成分塊
            all_chunks = []
            processed_files = 0
            
            for i, file_metadata in enumerate(files_metadata):
                try:
                    if progress_callback:
                        progress = (i / len(files_metadata)) * 0.5  # 文件處理佔50%
                        await progress_callback(f"處理文件: {file_metadata.relative_path}", progress)
                    
                    # 讀取文件內容
                    content, encoding = await self.document_service.extract_text_content(
                        file_metadata.file_path
                    )
                    
                    # 更新元數據中的編碼信息
                    file_metadata.encoding = encoding
                    
                    # 分塊處理
                    chunks = self.document_service.create_text_chunks(content, file_metadata)
                    
                    if chunks:
                        all_chunks.extend(chunks)
                        processed_files += 1
                        
                        logger.debug(f"文件 {file_metadata.relative_path} 生成 {len(chunks)} 個分塊")
                    
                except Exception as e:
                    logger.warning(f"處理文件失敗，跳過: {file_metadata.file_path} - {str(e)}")
                    continue
            
            if not all_chunks:
                raise EmbeddingProcessingError("沒有生成任何有效的文本分塊")
            
            logger.info(f"總共生成 {len(all_chunks)} 個文本分塊")
            
            # 3. 生成 Embeddings
            self._processing_status[knowledge_base_id] = EmbeddingProcessingStatus.GENERATING_EMBEDDINGS
            
            if progress_callback:
                await progress_callback("生成 Embeddings...", 0.5)
            
            embedded_chunks = 0
            stored_vectors = 0
            
            # 批次處理分塊
            for i in range(0, len(all_chunks), batch_size):
                batch_chunks = all_chunks[i:i + batch_size]
                
                try:
                    # 提取文本內容
                    batch_texts = [chunk['content'] for chunk in batch_chunks]
                    
                    # 生成 Embeddings
                    embeddings = await self.embedding_service.generate_embeddings_batch(
                        batch_texts, 
                        batch_size=min(len(batch_texts), 5)  # 控制並發數
                    )
                    
                    embedded_chunks += len(embeddings)
                    
                    if progress_callback:
                        progress = 0.5 + (embedded_chunks / len(all_chunks)) * 0.3  # Embedding 佔30%
                        await progress_callback(f"已生成 {embedded_chunks}/{len(all_chunks)} 個 Embeddings", progress)
                    
                    # 4. 儲存到向量資料庫
                    if self.vector_database:
                        self._processing_status[knowledge_base_id] = EmbeddingProcessingStatus.STORING_VECTORS
                        
                        # 準備向量資料庫儲存的資料
                        document_ids = [f"{knowledge_base_id}_{chunk['document_path']}_{chunk['chunk_index']}" 
                                       for chunk in batch_chunks]
                        
                        metadata_list = [
                            {
                                'knowledge_base_id': knowledge_base_id,
                                'document_path': chunk['document_path'],
                                'chunk_index': chunk['chunk_index'],
                                'chunk_size': chunk['chunk_size'],
                                'language': chunk.get('language', 'unknown'),
                                'file_type': chunk.get('file_type', ''),
                                'encoding': chunk.get('encoding', '')
                            }
                            for chunk in batch_chunks
                        ]
                        
                        # 批次儲存向量
                        vector_ids = await self.vector_database.store_vectors_batch(
                            embeddings, 
                            document_ids, 
                            metadata_list
                        )
                        
                        stored_vectors += len(vector_ids)
                        
                        logger.debug(f"批次儲存 {len(vector_ids)} 個向量")
                    
                    # 5. 儲存到 PostgreSQL
                    for j, (chunk, embedding) in enumerate(zip(batch_chunks, embeddings)):
                        try:
                            # 獲取對應的向量ID（如果有）
                            vector_id = None
                            if self.vector_database and j < len(vector_ids):
                                vector_id = vector_ids[j]
                            
                            # 創建 DocumentChunk 記錄
                            chunk_record = DocumentChunk(
                                knowledge_base_id=knowledge_base.id,
                                document_path=chunk['document_path'],
                                chunk_index=chunk['chunk_index'],
                                content=chunk['content'],
                                file_size=chunk.get('chunk_size', len(chunk['content'])),
                                file_type=chunk.get('file_type', ''),
                                language=chunk.get('language', 'unknown'),
                                encoding=chunk.get('encoding', 'utf-8'),
                                vector_id=vector_id,
                                embedding_model=self.embedding_config.model_name,
                                embedding_dimensions=384  # 由 all-minilm:l6-v2 模型決定
                            )
                            
                            db.add(chunk_record)
                            
                        except Exception as e:
                            logger.error(f"儲存分塊記錄失敗: {str(e)}")
                            continue
                    
                    # 定期提交資料庫
                    if (i // batch_size) % 5 == 0:  # 每5個批次提交一次
                        db.commit()
                        logger.debug(f"已提交 {i + len(batch_chunks)} 個分塊到資料庫")
                
                except Exception as e:
                    logger.error(f"處理批次失敗: {str(e)}")
                    # 回滾當前批次的資料庫變更
                    db.rollback()
                    continue
            
            # 最終提交
            db.commit()
            
            # 更新知識庫統計和狀態
            knowledge_base.document_count = processed_files
            knowledge_base.total_chunks = len(all_chunks)
            knowledge_base.embedding_model = self.embedding_config.model_name
            knowledge_base.embedding_dimensions = 384  # 由 all-minilm:l6-v2 模型決定
            knowledge_base.update_status(KnowledgeBaseStatus.READY)
            
            db.commit()
            db.refresh(knowledge_base)
            
            # 計算處理時間
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 更新處理狀態
            self._processing_status[knowledge_base_id] = EmbeddingProcessingStatus.COMPLETED
            
            result = EmbeddingProcessingResult(
                knowledge_base_id=knowledge_base_id,
                status=EmbeddingProcessingStatus.COMPLETED,
                processed_files=processed_files,
                total_chunks=len(all_chunks),
                embedded_chunks=embedded_chunks,
                stored_vectors=stored_vectors,
                processing_time_seconds=processing_time
            )
            
            if progress_callback:
                await progress_callback("處理完成", 1.0)
            
            logger.info(f"知識庫 Embedding 處理完成: {knowledge_base.name}, "
                       f"文件: {processed_files}, 分塊: {len(all_chunks)}, "
                       f"向量: {stored_vectors}, 耗時: {processing_time:.2f}秒")
            
            return result
            
        except Exception as e:
            logger.error(f"知識庫 Embedding 處理失敗: {str(e)}")
            
            # 更新錯誤狀態
            self._processing_status[knowledge_base_id] = EmbeddingProcessingStatus.FAILED
            
            try:
                knowledge_base.update_status(KnowledgeBaseStatus.ERROR, str(e))
                db.commit()
            except SQLAlchemyError as db_error:
                logger.error(f"更新錯誤狀態失敗: {str(db_error)}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return EmbeddingProcessingResult(
                knowledge_base_id=knowledge_base_id,
                status=EmbeddingProcessingStatus.FAILED,
                processed_files=0,
                total_chunks=0,
                embedded_chunks=0,
                stored_vectors=0,
                processing_time_seconds=processing_time,
                error_details=str(e)
            )
    
    async def search_similar_chunks(
        self,
        query_text: str,
        knowledge_base_id: Optional[str] = None,
        top_k: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        搜索相似的文本分塊
        
        Args:
            query_text: 查詢文本
            knowledge_base_id: 限制搜索的知識庫ID
            top_k: 返回結果數量
            similarity_threshold: 相似度閾值
            
        Returns:
            List[Dict[str, Any]]: 搜索結果
        """
        try:
            if not self.vector_database:
                raise ServiceError("向量資料庫未初始化")
            
            # 生成查詢向量
            query_embedding = await self.embedding_service.generate_embedding(query_text)
            
            # 設置文件ID過濾（如果指定了知識庫）
            document_ids = None
            if knowledge_base_id:
                # 生成該知識庫的文件ID模式
                document_ids = [f"{knowledge_base_id}_*"]  # 這需要向量資料庫支援模式匹配
            
            # 執行相似性搜索
            search_results = await self.vector_database.similarity_search(
                query_embedding,
                top_k=top_k,
                similarity_threshold=similarity_threshold,
                document_ids=document_ids
            )
            
            # 格式化結果
            formatted_results = []
            for result in search_results:
                formatted_result = {
                    'vector_id': result.vector_id,
                    'document_id': result.document_id,
                    'similarity_score': result.similarity_score,
                    'metadata': result.metadata,
                    'content': result.metadata.get('content', ''),  # 如果元數據中有內容
                    'document_path': result.metadata.get('document_path', ''),
                    'chunk_index': result.metadata.get('chunk_index', 0)
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"相似性搜索完成: 查詢='{query_text[:50]}...', 結果數={len(formatted_results)}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"相似性搜索失敗: {str(e)}")
            raise ServiceError(f"相似性搜索失敗: {str(e)}")
    
    def get_processing_status(self, knowledge_base_id: str) -> Optional[EmbeddingProcessingStatus]:
        """獲取處理狀態"""
        return self._processing_status.get(knowledge_base_id)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """獲取服務統計資訊"""
        try:
            stats = {
                'embedding_service': {
                    'model': self.embedding_config.model_name,
                    'base_url': self.embedding_config.base_url,
                    'healthy': await self.embedding_service.health_check() if self.embedding_service else False
                },
                'vector_database': None,
                'processing_status': dict(self._processing_status)
            }
            
            if self.vector_database:
                vector_stats = await self.vector_database.get_statistics()
                stats['vector_database'] = vector_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"獲取統計資訊失敗: {str(e)}")
            return {}