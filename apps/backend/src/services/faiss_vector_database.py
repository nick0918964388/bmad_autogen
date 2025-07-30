"""
Faiss 向量資料庫實作
使用 Faiss 庫提供高效的向量相似性搜索功能
"""

import os
import json
import pickle
import logging
import asyncio
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from dataclasses import asdict
import uuid

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

from ..interfaces.vector_database_interface import (
    VectorDatabaseInterface,
    VectorRecord,
    VectorSearchResult
)
from ..core.exceptions import BaseAppException

logger = logging.getLogger(__name__)


class FaissNotAvailableError(BaseAppException):
    """Faiss 庫不可用錯誤"""
    def __init__(self, message: str = "Faiss 庫未安裝或不可用"):
        super().__init__(
            status_code=500,
            message=message,
            error_code="FAISS_NOT_AVAILABLE"
        )


class VectorStorageError(BaseAppException):
    """向量儲存錯誤"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            message=f"向量儲存失敗: {message}",
            error_code="VECTOR_STORAGE_ERROR",
            details=details
        )


class VectorSearchError(BaseAppException):
    """向量搜索錯誤"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            message=f"向量搜索失敗: {message}",
            error_code="VECTOR_SEARCH_ERROR",
            details=details
        )


class FaissVectorDatabase(VectorDatabaseInterface):
    """Faiss 向量資料庫實作"""
    
    def __init__(
        self,
        index_path: str,
        dimension: int = 384,
        metric: str = "cosine",
        index_factory: str = "Flat"
    ):
        """
        初始化 Faiss 向量資料庫
        
        Args:
            index_path: 索引文件路徑
            dimension: 向量維度
            metric: 距離度量方法
            index_factory: Faiss 索引工廠字符串
        """
        if not FAISS_AVAILABLE:
            raise FaissNotAvailableError()
        
        self.index_path = Path(index_path)
        self.dimension = dimension
        self.metric = metric
        self.index_factory = index_factory
        
        # 索引和元數據
        self.index: Optional[faiss.Index] = None
        self.metadata_map: Dict[int, Dict[str, Any]] = {}
        self.vector_id_map: Dict[str, int] = {}  # vector_id -> faiss_id
        self.reverse_id_map: Dict[int, str] = {}  # faiss_id -> vector_id
        
        # 文件路徑
        self.index_file = self.index_path / "faiss_index.bin"
        self.metadata_file = self.index_path / "metadata.json"
        self.id_map_file = self.index_path / "id_mapping.json"
        
        # 確保目錄存在
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        self.next_id = 0
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> bool:
        """初始化向量資料庫"""
        try:
            async with self._lock:
                # 嘗試加載現有索引
                if await self._load_existing_index():
                    logger.info(f"成功加載現有 Faiss 索引: {self.index_path}")
                    return True
                
                # 創建新索引
                await self._create_new_index()
                logger.info(f"成功創建新 Faiss 索引: {self.index_path}")
                return True
                
        except Exception as e:
            logger.error(f"Faiss 索引初始化失敗: {str(e)}")
            return False
    
    async def _load_existing_index(self) -> bool:
        """加載現有索引"""
        try:
            if not (self.index_file.exists() and 
                   self.metadata_file.exists() and 
                   self.id_map_file.exists()):
                return False
            
            # 加載 Faiss 索引
            self.index = faiss.read_index(str(self.index_file))
            
            # 加載元數據
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata_data = json.load(f)
                self.metadata_map = {int(k): v for k, v in metadata_data.items()}
            
            # 加載ID映射
            with open(self.id_map_file, 'r', encoding='utf-8') as f:
                id_data = json.load(f)
                self.vector_id_map = id_data.get('vector_id_map', {})
                self.reverse_id_map = {int(k): v for k, v in id_data.get('reverse_id_map', {}).items()}
                self.next_id = id_data.get('next_id', 0)
            
            logger.debug(f"加載索引完成: {self.index.ntotal} 個向量")
            return True
            
        except Exception as e:
            logger.error(f"加載現有索引失敗: {str(e)}")
            return False
    
    async def _create_new_index(self) -> None:
        """創建新索引"""
        try:
            # 根據度量方法選擇索引類型
            if self.metric == "cosine":
                # 餘弦相似度使用內積並正規化向量
                index_string = f"Flat"
                self.index = faiss.index_factory(self.dimension, index_string, faiss.METRIC_INNER_PRODUCT)
            elif self.metric == "euclidean":
                index_string = f"Flat"
                self.index = faiss.index_factory(self.dimension, index_string, faiss.METRIC_L2)
            elif self.metric == "dot_product":
                index_string = f"Flat"
                self.index = faiss.index_factory(self.dimension, index_string, faiss.METRIC_INNER_PRODUCT)
            else:
                raise VectorStorageError(f"不支援的度量方法: {self.metric}")
            
            # 初始化數據結構
            self.metadata_map = {}
            self.vector_id_map = {}
            self.reverse_id_map = {}
            self.next_id = 0
            
            # 保存初始索引
            await self._save_index()
            
        except Exception as e:
            raise VectorStorageError(f"創建新索引失敗: {str(e)}")
    
    async def _save_index(self) -> None:
        """保存索引到磁盤"""
        try:
            # 保存 Faiss 索引
            faiss.write_index(self.index, str(self.index_file))
            
            # 保存元數據
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata_map, f, ensure_ascii=False, indent=2, default=str)
            
            # 保存ID映射
            id_data = {
                'vector_id_map': self.vector_id_map,
                'reverse_id_map': self.reverse_id_map,
                'next_id': self.next_id
            }
            with open(self.id_map_file, 'w', encoding='utf-8') as f:
                json.dump(id_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise VectorStorageError(f"保存索引失敗: {str(e)}")
    
    def _normalize_vector(self, embedding: List[float]) -> np.ndarray:
        """正規化向量（用於餘弦相似度）"""
        vector = np.array(embedding, dtype=np.float32).reshape(1, -1)
        
        if self.metric == "cosine":
            # 正規化向量用於餘弦相似度計算
            norm = np.linalg.norm(vector, axis=1, keepdims=True)
            if norm > 0:
                vector = vector / norm
        
        return vector
    
    async def close(self) -> None:
        """關閉向量資料庫連接"""
        try:
            if self.index is not None:
                await self._save_index()
                self.index = None
            
            logger.info("Faiss 索引已關閉")
            
        except Exception as e:
            logger.error(f"關閉 Faiss 索引失敗: {str(e)}")
    
    async def store_vector(
        self,
        embedding: List[float],
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """儲存向量到資料庫"""
        try:
            async with self._lock:
                # 驗證向量維度
                if len(embedding) != self.dimension:
                    raise VectorStorageError(f"向量維度不匹配: {len(embedding)} != {self.dimension}")
                
                # 生成向量ID
                vector_id = str(uuid.uuid4())
                faiss_id = self.next_id
                
                # 正規化向量
                normalized_vector = self._normalize_vector(embedding)
                
                # 添加到索引
                self.index.add(normalized_vector)
                
                # 更新映射
                self.vector_id_map[vector_id] = faiss_id
                self.reverse_id_map[faiss_id] = vector_id
                
                # 儲存元數據
                record_metadata = {
                    'vector_id': vector_id,
                    'document_id': document_id,
                    'created_at': datetime.now().isoformat(),
                    'dimension': len(embedding),
                    **(metadata or {})
                }
                self.metadata_map[faiss_id] = record_metadata
                
                self.next_id += 1
                
                # 定期保存（每100個向量）
                if self.next_id % 100 == 0:
                    await self._save_index()
                
                logger.debug(f"成功儲存向量: {vector_id}")
                return vector_id
                
        except Exception as e:
            logger.error(f"儲存向量失敗: {str(e)}")
            raise VectorStorageError(str(e))
    
    async def store_vectors_batch(
        self,
        embeddings: List[List[float]],
        document_ids: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """批次儲存向量"""
        try:
            if len(embeddings) != len(document_ids):
                raise VectorStorageError("embeddings 和 document_ids 長度不匹配")
            
            if metadata_list and len(metadata_list) != len(embeddings):
                raise VectorStorageError("metadata_list 長度不匹配")
            
            async with self._lock:
                vector_ids = []
                vectors_to_add = []
                
                for i, (embedding, document_id) in enumerate(zip(embeddings, document_ids)):
                    # 驗證向量維度
                    if len(embedding) != self.dimension:
                        raise VectorStorageError(f"向量 {i} 維度不匹配: {len(embedding)} != {self.dimension}")
                    
                    # 生成向量ID
                    vector_id = str(uuid.uuid4())
                    faiss_id = self.next_id + i
                    
                    vector_ids.append(vector_id)
                    
                    # 正規化向量
                    normalized_vector = self._normalize_vector(embedding)
                    vectors_to_add.append(normalized_vector)
                    
                    # 更新映射
                    self.vector_id_map[vector_id] = faiss_id
                    self.reverse_id_map[faiss_id] = vector_id
                    
                    # 儲存元數據
                    metadata = metadata_list[i] if metadata_list else {}
                    record_metadata = {
                        'vector_id': vector_id,
                        'document_id': document_id,
                        'created_at': datetime.now().isoformat(),
                        'dimension': len(embedding),
                        **metadata
                    }
                    self.metadata_map[faiss_id] = record_metadata
                
                # 批次添加向量
                if vectors_to_add:
                    batch_vectors = np.vstack(vectors_to_add)
                    self.index.add(batch_vectors)
                    
                    self.next_id += len(vectors_to_add)
                    
                    # 保存索引
                    await self._save_index()
                
                logger.info(f"成功批次儲存 {len(vector_ids)} 個向量")
                return vector_ids
                
        except Exception as e:
            logger.error(f"批次儲存向量失敗: {str(e)}")
            raise VectorStorageError(str(e))
    
    async def get_vector(self, vector_id: str) -> Optional[VectorRecord]:
        """根據向量ID獲取向量記錄"""
        try:
            async with self._lock:
                faiss_id = self.vector_id_map.get(vector_id)
                if faiss_id is None:
                    return None
                
                metadata = self.metadata_map.get(faiss_id)
                if metadata is None:
                    return None
                
                # 從索引中重建向量（注意：Flat索引不支持直接獲取向量）
                # 這是一個限制，實際應用中可能需要單獨儲存原始向量
                
                record = VectorRecord(
                    vector_id=vector_id,
                    document_id=metadata['document_id'],
                    embedding=[],  # Faiss Flat 索引無法直接獲取原始向量
                    metadata=metadata,
                    created_at=datetime.fromisoformat(metadata['created_at'])
                )
                
                return record
                
        except Exception as e:
            logger.error(f"獲取向量失敗: {vector_id} - {str(e)}")
            return None
    
    async def delete_vector(self, vector_id: str) -> bool:
        """刪除向量"""
        try:
            async with self._lock:
                faiss_id = self.vector_id_map.get(vector_id)
                if faiss_id is None:
                    return False
                
                # Faiss 不支援直接刪除，需要重建索引
                # 這是一個限制，實際應用中可能需要使用支援刪除的索引類型
                logger.warning("Faiss Flat 索引不支援直接刪除，需要重建索引")
                
                # 標記為已刪除（在元數據中）
                if faiss_id in self.metadata_map:
                    self.metadata_map[faiss_id]['deleted'] = True
                    self.metadata_map[faiss_id]['deleted_at'] = datetime.now().isoformat()
                
                await self._save_index()
                return True
                
        except Exception as e:
            logger.error(f"刪除向量失敗: {vector_id} - {str(e)}")
            return False
    
    async def delete_vectors_by_document(self, document_id: str) -> int:
        """根據文件ID刪除所有相關向量"""
        try:
            async with self._lock:
                deleted_count = 0
                
                for faiss_id, metadata in self.metadata_map.items():
                    if metadata.get('document_id') == document_id and not metadata.get('deleted', False):
                        metadata['deleted'] = True
                        metadata['deleted_at'] = datetime.now().isoformat()
                        deleted_count += 1
                
                if deleted_count > 0:
                    await self._save_index()
                
                logger.info(f"標記刪除 {deleted_count} 個向量（文件ID: {document_id}）")
                return deleted_count
                
        except Exception as e:
            logger.error(f"按文件ID刪除向量失敗: {document_id} - {str(e)}")
            return 0
    
    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        document_ids: Optional[List[str]] = None
    ) -> List[VectorSearchResult]:
        """相似性搜索"""
        try:
            async with self._lock:
                if len(query_embedding) != self.dimension:
                    raise VectorSearchError(f"查詢向量維度不匹配: {len(query_embedding)} != {self.dimension}")
                
                # 正規化查詢向量
                query_vector = self._normalize_vector(query_embedding)
                
                # 執行搜索
                search_k = min(top_k * 2, self.index.ntotal)  # 搜索更多候選以過濾
                scores, indices = self.index.search(query_vector, search_k)
                
                results = []
                for i, (score, faiss_id) in enumerate(zip(scores[0], indices[0])):
                    if faiss_id == -1:  # 無效結果
                        continue
                    
                    metadata = self.metadata_map.get(faiss_id)
                    if not metadata or metadata.get('deleted', False):
                        continue
                    
                    # 文件ID過濾
                    if document_ids and metadata['document_id'] not in document_ids:
                        continue
                    
                    # 轉換相似度分數
                    if self.metric == "cosine":
                        similarity_score = float(score)  # 內積結果已經是餘弦相似度
                    elif self.metric == "euclidean":
                        # L2距離轉換為相似度
                        similarity_score = 1.0 / (1.0 + float(score))
                    else:
                        similarity_score = float(score)
                    
                    # 相似度閾值過濾
                    if similarity_score < similarity_threshold:
                        continue
                    
                    vector_id = self.reverse_id_map.get(faiss_id)
                    if not vector_id:
                        continue
                    
                    result = VectorSearchResult(
                        vector_id=vector_id,
                        document_id=metadata['document_id'],
                        similarity_score=similarity_score,
                        metadata=metadata
                    )
                    results.append(result)
                    
                    if len(results) >= top_k:
                        break
                
                # 按相似度降序排序
                results.sort(key=lambda x: x.similarity_score, reverse=True)
                
                logger.debug(f"相似性搜索完成: {len(results)} 個結果")
                return results
                
        except Exception as e:
            logger.error(f"相似性搜索失敗: {str(e)}")
            raise VectorSearchError(str(e))
    
    async def get_vector_count(self) -> int:
        """獲取向量總數"""
        try:
            if self.index is None:
                return 0
            
            # 計算未刪除的向量數量
            active_count = sum(
                1 for metadata in self.metadata_map.values()
                if not metadata.get('deleted', False)
            )
            
            return active_count
            
        except Exception as e:
            logger.error(f"獲取向量總數失敗: {str(e)}")
            return 0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """獲取資料庫統計資訊"""
        try:
            total_vectors = self.index.ntotal if self.index else 0
            active_vectors = await self.get_vector_count()
            deleted_vectors = total_vectors - active_vectors
            
            # 計算文件統計
            document_counts = {}
            for metadata in self.metadata_map.values():
                if not metadata.get('deleted', False):
                    doc_id = metadata['document_id']
                    document_counts[doc_id] = document_counts.get(doc_id, 0) + 1
            
            return {
                'total_vectors': total_vectors,
                'active_vectors': active_vectors,
                'deleted_vectors': deleted_vectors,
                'unique_documents': len(document_counts),
                'dimension': self.dimension,
                'metric': self.metric,
                'index_type': self.index_factory,
                'index_path': str(self.index_path),
                'storage_size_mb': self._get_storage_size_mb()
            }
            
        except Exception as e:
            logger.error(f"獲取統計資訊失敗: {str(e)}")
            return {}
    
    def _get_storage_size_mb(self) -> float:
        """計算儲存大小（MB）"""
        try:
            total_size = 0
            for file_path in [self.index_file, self.metadata_file, self.id_map_file]:
                if file_path.exists():
                    total_size += file_path.stat().st_size
            
            return round(total_size / (1024 * 1024), 2)
            
        except Exception:
            return 0.0
    
    async def health_check(self) -> bool:
        """健康檢查"""
        try:
            if self.index is None:
                return False
            
            # 檢查索引是否可用
            if hasattr(self.index, 'ntotal'):
                vector_count = self.index.ntotal
                return vector_count >= 0
            
            return True
            
        except Exception as e:
            logger.error(f"健康檢查失敗: {str(e)}")
            return False
    
    async def create_index(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine"
    ) -> bool:
        """創建索引（當前實作不支援多索引）"""
        logger.warning("當前 Faiss 實作不支援多索引管理")
        return False
    
    async def drop_index(self, index_name: str) -> bool:
        """刪除索引（當前實作不支援多索引）"""
        logger.warning("當前 Faiss 實作不支援多索引管理")
        return False
    
    async def list_indexes(self) -> List[str]:
        """列出所有索引"""
        return ["default"]  # 當前只有一個預設索引
    
    async def backup_index(
        self,
        index_name: str,
        backup_path: str
    ) -> bool:
        """備份索引"""
        try:
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 複製索引文件
            import shutil
            
            if self.index_file.exists():
                shutil.copy2(self.index_file, backup_dir / self.index_file.name)
            
            if self.metadata_file.exists():
                shutil.copy2(self.metadata_file, backup_dir / self.metadata_file.name)
            
            if self.id_map_file.exists():
                shutil.copy2(self.id_map_file, backup_dir / self.id_map_file.name)
            
            logger.info(f"索引備份完成: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"索引備份失敗: {str(e)}")
            return False
    
    async def restore_index(
        self,
        index_name: str,
        backup_path: str
    ) -> bool:
        """恢復索引"""
        try:
            backup_dir = Path(backup_path)
            
            if not backup_dir.exists():
                raise VectorStorageError(f"備份目錄不存在: {backup_path}")
            
            # 恢復索引文件
            import shutil
            
            backup_index = backup_dir / self.index_file.name
            backup_metadata = backup_dir / self.metadata_file.name
            backup_id_map = backup_dir / self.id_map_file.name
            
            if backup_index.exists():
                shutil.copy2(backup_index, self.index_file)
            
            if backup_metadata.exists():
                shutil.copy2(backup_metadata, self.metadata_file)
            
            if backup_id_map.exists():
                shutil.copy2(backup_id_map, self.id_map_file)
            
            # 重新加載索引
            await self._load_existing_index()
            
            logger.info(f"索引恢復完成: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"索引恢復失敗: {str(e)}")
            return False