"""
Embedding 整合服務測試
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from .embedding_integration_service import (
    EmbeddingIntegrationService,
    EmbeddingProcessingStatus,
    EmbeddingProcessingResult,
    EmbeddingProcessingError
)
from .document_processing_service import DocumentProcessingService, DocumentMetadata
from .ollama_embedding_service import OllamaEmbeddingService, EmbeddingConfig
from .faiss_vector_database import FaissVectorDatabase
from ..interfaces.vector_database_interface import VectorSearchResult
from ..models.knowledge_base import KnowledgeBase, KnowledgeBaseStatus


class TestEmbeddingIntegrationService:
    """Embedding 整合服務測試類別"""
    
    def setup_method(self):
        """每個測試方法前的設置"""
        # Mock 各種服務
        self.mock_document_service = Mock(spec=DocumentProcessingService)
        self.mock_embedding_service = Mock(spec=OllamaEmbeddingService)
        self.mock_vector_database = Mock(spec=FaissVectorDatabase)
        self.mock_db_session = Mock()
        
        # 創建服務實例
        self.service = EmbeddingIntegrationService(
            document_service=self.mock_document_service,
            embedding_service=self.mock_embedding_service,
            vector_database=self.mock_vector_database
        )
    
    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """測試成功初始化"""
        # Mock 服務初始化
        self.mock_embedding_service.initialize = AsyncMock(return_value=True)
        self.mock_embedding_service.health_check = AsyncMock(return_value=True)
        self.mock_vector_database.initialize = AsyncMock(return_value=True)
        self.mock_vector_database.health_check = AsyncMock(return_value=True)
        
        result = await self.service.initialize()
        
        assert result is True
        self.mock_embedding_service.initialize.assert_called_once()
        self.mock_vector_database.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_embedding_service_failure(self):
        """測試 Embedding 服務初始化失敗"""
        self.mock_embedding_service.initialize = AsyncMock(return_value=True)
        self.mock_embedding_service.health_check = AsyncMock(return_value=False)
        
        result = await self.service.initialize()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_initialize_vector_database_failure(self):
        """測試向量資料庫初始化失敗"""
        self.mock_embedding_service.initialize = AsyncMock(return_value=True)
        self.mock_embedding_service.health_check = AsyncMock(return_value=True)
        self.mock_vector_database.initialize = AsyncMock(return_value=True)
        self.mock_vector_database.health_check = AsyncMock(return_value=False)
        
        result = await self.service.initialize()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_close_services(self):
        """測試關閉服務"""
        self.mock_embedding_service.close = AsyncMock()
        self.mock_vector_database.close = AsyncMock()
        
        await self.service.close()
        
        self.mock_embedding_service.close.assert_called_once()
        self.mock_vector_database.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """測試健康檢查成功"""
        self.mock_embedding_service.health_check = AsyncMock(return_value=True)
        self.mock_vector_database.health_check = AsyncMock(return_value=True)
        
        result = await self.service.health_check()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_embedding_service_failure(self):
        """測試 Embedding 服務健康檢查失敗"""
        self.mock_embedding_service.health_check = AsyncMock(return_value=False)
        
        result = await self.service.health_check()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_vector_database_failure(self):
        """測試向量資料庫健康檢查失敗"""
        self.mock_embedding_service.health_check = AsyncMock(return_value=True)
        self.mock_vector_database.health_check = AsyncMock(return_value=False)
        
        result = await self.service.health_check()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_process_knowledge_base_success(self):
        """測試成功處理知識庫"""
        # 準備測試數據
        mock_kb = Mock(spec=KnowledgeBase)
        mock_kb.id = "test-kb-id"
        mock_kb.name = "測試知識庫"
        mock_kb.path = "/test/path"
        mock_kb.update_status = Mock()
        
        # Mock 文件掃描結果
        mock_files = [
            DocumentMetadata(
                file_path="/test/path/file1.txt",
                relative_path="file1.txt",
                file_size=1000,
                file_type=".txt",
                mime_type="text/plain",
                modified_time=datetime.now()
            )
        ]
        
        # Mock 文件內容和分塊
        mock_chunks = [
            {
                'chunk_index': 0,
                'content': '這是測試內容',
                'document_path': 'file1.txt',
                'chunk_size': 10,
                'language': 'zh',
                'file_type': '.txt',
                'encoding': 'utf-8'
            }
        ]
        
        # Mock Embeddings
        mock_embeddings = [[0.1] * 384]
        mock_vector_ids = ["vector_1"]
        
        # 設置 Mock 行為
        self.mock_document_service.scan_directory = AsyncMock(return_value=mock_files)
        self.mock_document_service.extract_text_content = AsyncMock(return_value=("測試內容", "utf-8"))
        self.mock_document_service.create_text_chunks = Mock(return_value=mock_chunks)
        self.mock_embedding_service.generate_embeddings_batch = AsyncMock(return_value=mock_embeddings)
        self.mock_vector_database.store_vectors_batch = AsyncMock(return_value=mock_vector_ids)
        
        # Mock 資料庫操作
        self.mock_db_session.add = Mock()
        self.mock_db_session.commit = Mock()
        self.mock_db_session.refresh = Mock()
        
        # 執行測試
        result = await self.service.process_knowledge_base_with_embeddings(mock_kb, self.mock_db_session)
        
        # 驗證結果
        assert result.status == EmbeddingProcessingStatus.COMPLETED
        assert result.processed_files == 1
        assert result.total_chunks == 1
        assert result.embedded_chunks == 1
        assert result.stored_vectors == 1
        
        # 驗證方法調用
        self.mock_document_service.scan_directory.assert_called_once()
        self.mock_document_service.extract_text_content.assert_called_once()
        self.mock_embedding_service.generate_embeddings_batch.assert_called_once()
        self.mock_vector_database.store_vectors_batch.assert_called_once()
        
        # 驗證知識庫狀態更新
        mock_kb.update_status.assert_called_with(KnowledgeBaseStatus.READY)
    
    @pytest.mark.asyncio
    async def test_process_knowledge_base_no_files(self):
        """測試處理沒有文件的知識庫"""
        mock_kb = Mock(spec=KnowledgeBase)
        mock_kb.id = "test-kb-id"
        mock_kb.name = "空知識庫"
        mock_kb.path = "/empty/path"
        mock_kb.update_status = Mock()
        
        # Mock 空文件列表
        self.mock_document_service.scan_directory = AsyncMock(return_value=[])
        
        # 執行測試
        result = await self.service.process_knowledge_base_with_embeddings(mock_kb, self.mock_db_session)
        
        # 驗證結果
        assert result.status == EmbeddingProcessingStatus.FAILED
        assert "沒有找到支援的文件" in result.error_details
        
        # 驗證錯誤狀態更新
        mock_kb.update_status.assert_called_with(KnowledgeBaseStatus.ERROR, result.error_details)
    
    @pytest.mark.asyncio
    async def test_process_knowledge_base_embedding_failure(self):
        """測試 Embedding 生成失敗"""
        mock_kb = Mock(spec=KnowledgeBase)
        mock_kb.id = "test-kb-id"
        mock_kb.name = "測試知識庫"
        mock_kb.path = "/test/path"
        mock_kb.update_status = Mock()
        
        # Mock 文件和分塊
        mock_files = [
            DocumentMetadata(
                file_path="/test/path/file1.txt",
                relative_path="file1.txt",
                file_size=1000,
                file_type=".txt",
                mime_type="text/plain",
                modified_time=datetime.now()
            )
        ]
        
        mock_chunks = [
            {
                'chunk_index': 0,
                'content': '測試內容',
                'document_path': 'file1.txt',
                'chunk_size': 10
            }
        ]
        
        # 設置 Mock 行為
        self.mock_document_service.scan_directory = AsyncMock(return_value=mock_files)
        self.mock_document_service.extract_text_content = AsyncMock(return_value=("測試內容", "utf-8"))
        self.mock_document_service.create_text_chunks = Mock(return_value=mock_chunks)
        
        # Mock Embedding 失敗
        self.mock_embedding_service.generate_embeddings_batch = AsyncMock(
            side_effect=Exception("Embedding 生成失敗")
        )
        
        # 執行測試
        result = await self.service.process_knowledge_base_with_embeddings(mock_kb, self.mock_db_session)
        
        # 驗證結果
        assert result.status == EmbeddingProcessingStatus.FAILED
        assert "Embedding 生成失敗" in result.error_details
    
    @pytest.mark.asyncio
    async def test_search_similar_chunks_success(self):
        """測試成功搜索相似分塊"""
        query_text = "測試查詢"
        
        # Mock Embedding 生成
        mock_query_embedding = [0.1] * 384
        self.mock_embedding_service.generate_embedding = AsyncMock(return_value=mock_query_embedding)
        
        # Mock 搜索結果
        mock_search_results = [
            VectorSearchResult(
                vector_id="vector_1",
                document_id="doc_1",
                similarity_score=0.95,
                metadata={
                    'content': '相似的測試內容',
                    'document_path': 'test.txt',
                    'chunk_index': 0
                }
            )
        ]
        
        self.mock_vector_database.similarity_search = AsyncMock(return_value=mock_search_results)
        
        # 執行搜索
        results = await self.service.search_similar_chunks(query_text)
        
        # 驗證結果
        assert len(results) == 1
        assert results[0]['vector_id'] == "vector_1"
        assert results[0]['similarity_score'] == 0.95
        assert results[0]['content'] == '相似的測試內容'
        
        # 驗證方法調用
        self.mock_embedding_service.generate_embedding.assert_called_once_with(query_text)
        self.mock_vector_database.similarity_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_similar_chunks_no_vector_database(self):
        """測試沒有向量資料庫時的搜索"""
        # 創建沒有向量資料庫的服務
        service = EmbeddingIntegrationService(
            document_service=self.mock_document_service,
            embedding_service=self.mock_embedding_service,
            vector_database=None
        )
        
        # 執行搜索應該失敗
        with pytest.raises(Exception) as exc_info:
            await service.search_similar_chunks("測試查詢")
        
        assert "向量資料庫未初始化" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_similar_chunks_embedding_failure(self):
        """測試查詢 Embedding 生成失敗"""
        query_text = "測試查詢"
        
        # Mock Embedding 生成失敗
        self.mock_embedding_service.generate_embedding = AsyncMock(
            side_effect=Exception("Embedding 生成失敗")
        )
        
        # 執行搜索應該失敗
        with pytest.raises(Exception) as exc_info:
            await self.service.search_similar_chunks(query_text)
        
        assert "相似性搜索失敗" in str(exc_info.value)
    
    def test_get_processing_status(self):
        """測試獲取處理狀態"""
        knowledge_base_id = "test-kb-id"
        
        # 設置狀態
        self.service._processing_status[knowledge_base_id] = EmbeddingProcessingStatus.PROCESSING
        
        # 獲取狀態
        status = self.service.get_processing_status(knowledge_base_id)
        
        assert status == EmbeddingProcessingStatus.PROCESSING
    
    def test_get_processing_status_not_found(self):
        """測試獲取不存在的處理狀態"""
        status = self.service.get_processing_status("nonexistent-id")
        
        assert status is None
    
    @pytest.mark.asyncio
    async def test_get_statistics(self):
        """測試獲取統計資訊"""
        # Mock 健康檢查
        self.mock_embedding_service.health_check = AsyncMock(return_value=True)
        
        # Mock 向量資料庫統計
        mock_vector_stats = {
            'total_vectors': 100,
            'active_vectors': 95,
            'deleted_vectors': 5
        }
        self.mock_vector_database.get_statistics = AsyncMock(return_value=mock_vector_stats)
        
        # 獲取統計資訊
        stats = await self.service.get_statistics()
        
        # 驗證結果
        assert 'embedding_service' in stats
        assert 'vector_database' in stats
        assert 'processing_status' in stats
        
        assert stats['embedding_service']['healthy'] is True
        assert stats['vector_database'] == mock_vector_stats
    
    @pytest.mark.asyncio
    async def test_process_knowledge_base_with_progress_callback(self):
        """測試帶進度回調的知識庫處理"""
        mock_kb = Mock(spec=KnowledgeBase)
        mock_kb.id = "test-kb-id"
        mock_kb.name = "測試知識庫"
        mock_kb.path = "/test/path"
        mock_kb.update_status = Mock()
        
        # 創建進度回調
        progress_calls = []
        
        async def progress_callback(message, progress):
            progress_calls.append((message, progress))
        
        # Mock 簡單的處理流程
        self.mock_document_service.scan_directory = AsyncMock(return_value=[])
        
        # 執行測試（會因為沒有文件而失敗，但我們主要測試回調）
        await self.service.process_knowledge_base_with_embeddings(
            mock_kb, 
            self.mock_db_session, 
            progress_callback=progress_callback
        )
        
        # 驗證進度回調被調用
        assert len(progress_calls) > 0
        assert progress_calls[0][0] == "開始掃描文件..."
        assert progress_calls[0][1] == 0
    
    @pytest.mark.asyncio
    async def test_embedding_processing_status_enum(self):
        """測試 Embedding 處理狀態枚舉"""
        # 驗證所有狀態值
        assert EmbeddingProcessingStatus.PENDING.value == "pending"
        assert EmbeddingProcessingStatus.PROCESSING.value == "processing"
        assert EmbeddingProcessingStatus.GENERATING_EMBEDDINGS.value == "generating_embeddings"
        assert EmbeddingProcessingStatus.STORING_VECTORS.value == "storing_vectors"
        assert EmbeddingProcessingStatus.COMPLETED.value == "completed"
        assert EmbeddingProcessingStatus.FAILED.value == "failed"
    
    def test_embedding_processing_result_dataclass(self):
        """測試 Embedding 處理結果數據類"""
        result = EmbeddingProcessingResult(
            knowledge_base_id="test-id",
            status=EmbeddingProcessingStatus.COMPLETED,
            processed_files=5,
            total_chunks=50,
            embedded_chunks=50,
            stored_vectors=50,
            processing_time_seconds=120.5,
            error_details=None
        )
        
        assert result.knowledge_base_id == "test-id"
        assert result.status == EmbeddingProcessingStatus.COMPLETED
        assert result.processed_files == 5
        assert result.total_chunks == 50
        assert result.embedded_chunks == 50
        assert result.stored_vectors == 50
        assert result.processing_time_seconds == 120.5
        assert result.error_details is None


if __name__ == "__main__":
    pytest.main([__file__])