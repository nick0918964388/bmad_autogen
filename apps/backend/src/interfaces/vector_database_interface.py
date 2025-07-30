"""
向量資料庫抽象介面
定義向量資料庫的標準操作介面
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VectorSearchResult:
    """向量搜索結果"""
    vector_id: str
    document_id: str
    similarity_score: float
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class VectorRecord:
    """向量記錄"""
    vector_id: str
    document_id: str
    embedding: List[float]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None


class VectorDatabaseInterface(ABC):
    """向量資料庫抽象介面"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        初始化向量資料庫
        
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """關閉向量資料庫連接"""
        pass
    
    @abstractmethod
    async def store_vector(
        self,
        embedding: List[float],
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        儲存向量到資料庫
        
        Args:
            embedding: 向量數據（384維）
            document_id: 關聯的文件ID
            metadata: 額外的元數據
            
        Returns:
            str: 向量ID
        """
        pass
    
    @abstractmethod
    async def store_vectors_batch(
        self,
        embeddings: List[List[float]],
        document_ids: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        批次儲存向量
        
        Args:
            embeddings: 向量數據列表
            document_ids: 文件ID列表
            metadata_list: 元數據列表
            
        Returns:
            List[str]: 向量ID列表
        """
        pass
    
    @abstractmethod
    async def get_vector(self, vector_id: str) -> Optional[VectorRecord]:
        """
        根據向量ID獲取向量記錄
        
        Args:
            vector_id: 向量ID
            
        Returns:
            Optional[VectorRecord]: 向量記錄，如果不存在則返回None
        """
        pass
    
    @abstractmethod
    async def delete_vector(self, vector_id: str) -> bool:
        """
        刪除向量
        
        Args:
            vector_id: 向量ID
            
        Returns:
            bool: 刪除是否成功
        """
        pass
    
    @abstractmethod
    async def delete_vectors_by_document(self, document_id: str) -> int:
        """
        根據文件ID刪除所有相關向量
        
        Args:
            document_id: 文件ID
            
        Returns:
            int: 刪除的向量數量
        """
        pass
    
    @abstractmethod
    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        document_ids: Optional[List[str]] = None
    ) -> List[VectorSearchResult]:
        """
        相似性搜索
        
        Args:
            query_embedding: 查詢向量
            top_k: 返回結果數量
            similarity_threshold: 相似度閾值
            document_ids: 限制搜索的文件ID列表
            
        Returns:
            List[VectorSearchResult]: 搜索結果列表，按相似度降序排列
        """
        pass
    
    @abstractmethod
    async def get_vector_count(self) -> int:
        """
        獲取向量總數
        
        Returns:
            int: 向量總數
        """
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """
        獲取資料庫統計資訊
        
        Returns:
            Dict[str, Any]: 統計資訊
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        健康檢查
        
        Returns:
            bool: 資料庫是否健康
        """
        pass
    
    @abstractmethod
    async def create_index(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine"
    ) -> bool:
        """
        創建索引
        
        Args:
            index_name: 索引名稱
            dimension: 向量維度
            metric: 距離度量方法 ("cosine", "euclidean", "dot_product")
            
        Returns:
            bool: 創建是否成功
        """
        pass
    
    @abstractmethod
    async def drop_index(self, index_name: str) -> bool:
        """
        刪除索引
        
        Args:
            index_name: 索引名稱
            
        Returns:
            bool: 刪除是否成功
        """
        pass
    
    @abstractmethod
    async def list_indexes(self) -> List[str]:
        """
        列出所有索引
        
        Returns:
            List[str]: 索引名稱列表
        """
        pass
    
    @abstractmethod
    async def backup_index(
        self,
        index_name: str,
        backup_path: str
    ) -> bool:
        """
        備份索引
        
        Args:
            index_name: 索引名稱
            backup_path: 備份路徑
            
        Returns:
            bool: 備份是否成功
        """
        pass
    
    @abstractmethod
    async def restore_index(
        self,
        index_name: str,
        backup_path: str
    ) -> bool:
        """
        恢復索引
        
        Args:
            index_name: 索引名稱
            backup_path: 備份路徑
            
        Returns:
            bool: 恢復是否成功
        """
        pass