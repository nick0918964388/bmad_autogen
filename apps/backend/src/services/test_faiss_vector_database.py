"""
Faiss 向量資料庫測試
"""

import pytest
import tempfile
import shutil
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Mock faiss if not available
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    # Create a mock faiss module for testing
    faiss = MagicMock()
    faiss.METRIC_INNER_PRODUCT = 0
    faiss.METRIC_L2 = 1
    faiss.index_factory = MagicMock()
    faiss.read_index = MagicMock()
    faiss.write_index = MagicMock()

from .faiss_vector_database import (
    FaissVectorDatabase,
    FaissNotAvailableError,
    VectorStorageError,
    VectorSearchError
)
from ..interfaces.vector_database_interface import VectorRecord, VectorSearchResult


class TestFaissVectorDatabase:
    """Faiss 向量資料庫測試類別"""
    
    def setup_method(self):
        """每個測試方法前的設置"""
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = Path(self.temp_dir) / "test_index"
        
        # Mock 索引
        self.mock_index = Mock()
        self.mock_index.ntotal = 0
        self.mock_index.add = Mock()
        self.mock_index.search = Mock()
        
    def teardown_method(self):
        """每個測試方法後的清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="Faiss not available")
    def test_initialization_with_faiss(self):
        """測試有 Faiss 的初始化"""
        db = FaissVectorDatabase(str(self.index_path))
        
        assert db.index_path == self.index_path
        assert db.dimension == 384
        assert db.metric == "cosine"
        assert db.index_factory == "Flat"
    
    def test_initialization_without_faiss(self):
        """測試無 Faiss 的初始化"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.FAISS_AVAILABLE', False):
            with pytest.raises(FaissNotAvailableError):
                FaissVectorDatabase(str(self.index_path))
    
    @pytest.mark.asyncio
    async def test_initialize_new_index(self):
        """測試初始化新索引"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            result = await db.initialize()
            
            assert result is True
            assert db.index is not None
    
    @pytest.mark.asyncio
    async def test_initialize_load_existing_index(self):
        """測試加載現有索引"""
        # 創建假的索引文件
        self.index_path.mkdir(parents=True, exist_ok=True)
        (self.index_path / "faiss_index.bin").touch()
        (self.index_path / "metadata.json").write_text('{"0": {"vector_id": "test", "document_id": "doc1"}}')
        (self.index_path / "id_mapping.json").write_text('{"vector_id_map": {"test": 0}, "reverse_id_map": {"0": "test"}, "next_id": 1}')
        
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.read_index.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            result = await db.initialize()
            
            assert result is True
            assert len(db.metadata_map) == 1
            assert "test" in db.vector_id_map
    
    @pytest.mark.asyncio
    async def test_store_vector_success(self):
        """測試成功儲存向量"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            embedding = [0.1] * 384
            document_id = "test_doc"
            metadata = {"key": "value"}
            
            vector_id = await db.store_vector(embedding, document_id, metadata)
            
            assert vector_id is not None
            assert len(vector_id) > 0
            assert vector_id in db.vector_id_map
            self.mock_index.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_vector_wrong_dimension(self):
        """測試錯誤維度的向量儲存"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            embedding = [0.1] * 100  # 錯誤維度
            document_id = "test_doc"
            
            with pytest.raises(VectorStorageError) as exc_info:
                await db.store_vector(embedding, document_id)
            
            assert "向量維度不匹配" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_store_vectors_batch_success(self):
        """測試批次儲存向量成功"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            embeddings = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
            document_ids = ["doc1", "doc2", "doc3"]
            metadata_list = [{"key": f"value{i}"} for i in range(3)]
            
            vector_ids = await db.store_vectors_batch(embeddings, document_ids, metadata_list)
            
            assert len(vector_ids) == 3
            assert all(vid in db.vector_id_map for vid in vector_ids)
            self.mock_index.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_vectors_batch_dimension_mismatch(self):
        """測試批次儲存維度不匹配"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            embeddings = [[0.1] * 384, [0.2] * 100]  # 第二個維度錯誤
            document_ids = ["doc1", "doc2"]
            
            with pytest.raises(VectorStorageError) as exc_info:
                await db.store_vectors_batch(embeddings, document_ids)
            
            assert "向量 1 維度不匹配" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_store_vectors_batch_length_mismatch(self):
        """測試批次儲存長度不匹配"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            embeddings = [[0.1] * 384, [0.2] * 384]
            document_ids = ["doc1"]  # 長度不匹配
            
            with pytest.raises(VectorStorageError) as exc_info:
                await db.store_vectors_batch(embeddings, document_ids)
            
            assert "document_ids 長度不匹配" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_vector_success(self):
        """測試成功獲取向量"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            # 模擬已儲存的向量
            vector_id = "test_vector_id"
            faiss_id = 0
            db.vector_id_map[vector_id] = faiss_id
            db.metadata_map[faiss_id] = {
                'vector_id': vector_id,
                'document_id': 'test_doc',
                'created_at': datetime.now().isoformat()
            }
            
            record = await db.get_vector(vector_id)
            
            assert record is not None
            assert record.vector_id == vector_id
            assert record.document_id == 'test_doc'
    
    @pytest.mark.asyncio
    async def test_get_vector_not_found(self):
        """測試獲取不存在的向量"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            record = await db.get_vector("nonexistent_id")
            
            assert record is None
    
    @pytest.mark.asyncio
    async def test_delete_vector_success(self):
        """測試刪除向量成功"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            # 模擬已儲存的向量
            vector_id = "test_vector_id"
            faiss_id = 0
            db.vector_id_map[vector_id] = faiss_id
            db.metadata_map[faiss_id] = {
                'vector_id': vector_id,
                'document_id': 'test_doc',
                'created_at': datetime.now().isoformat()
            }
            
            result = await db.delete_vector(vector_id)
            
            assert result is True
            assert db.metadata_map[faiss_id]['deleted'] is True
    
    @pytest.mark.asyncio
    async def test_delete_vector_not_found(self):
        """測試刪除不存在的向量"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            result = await db.delete_vector("nonexistent_id")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_vectors_by_document(self):
        """測試按文件ID刪除向量"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            # 模擬多個向量
            for i in range(3):
                faiss_id = i
                db.metadata_map[faiss_id] = {
                    'vector_id': f'vector_{i}',
                    'document_id': 'test_doc' if i < 2 else 'other_doc',
                    'created_at': datetime.now().isoformat()
                }
            
            deleted_count = await db.delete_vectors_by_document('test_doc')
            
            assert deleted_count == 2
            assert db.metadata_map[0]['deleted'] is True
            assert db.metadata_map[1]['deleted'] is True
            assert 'deleted' not in db.metadata_map[2]
    
    @pytest.mark.asyncio
    async def test_similarity_search_success(self):
        """測試相似性搜索成功"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            # 模擬搜索結果
            self.mock_index.search.return_value = (
                np.array([[0.9, 0.8, 0.7]]),  # scores
                np.array([[0, 1, 2]])         # indices
            )
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            # 模擬已儲存的向量
            for i in range(3):
                vector_id = f'vector_{i}'
                db.vector_id_map[vector_id] = i
                db.reverse_id_map[i] = vector_id
                db.metadata_map[i] = {
                    'vector_id': vector_id,
                    'document_id': f'doc_{i}',
                    'created_at': datetime.now().isoformat()
                }
            
            query_embedding = [0.1] * 384
            results = await db.similarity_search(query_embedding, top_k=3)
            
            assert len(results) == 3
            assert all(isinstance(r, VectorSearchResult) for r in results)
            assert results[0].similarity_score >= results[1].similarity_score
    
    @pytest.mark.asyncio
    async def test_similarity_search_wrong_dimension(self):
        """測試相似性搜索錯誤維度"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            query_embedding = [0.1] * 100  # 錯誤維度
            
            with pytest.raises(VectorSearchError) as exc_info:
                await db.similarity_search(query_embedding)
            
            assert "查詢向量維度不匹配" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_similarity_search_with_filters(self):
        """測試帶過濾條件的相似性搜索"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            # 模擬搜索結果
            self.mock_index.search.return_value = (
                np.array([[0.9, 0.8, 0.7]]),
                np.array([[0, 1, 2]])
            )
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            # 模擬已儲存的向量
            for i in range(3):
                vector_id = f'vector_{i}'
                db.vector_id_map[vector_id] = i
                db.reverse_id_map[i] = vector_id
                db.metadata_map[i] = {
                    'vector_id': vector_id,
                    'document_id': f'doc_{i}',
                    'created_at': datetime.now().isoformat()
                }
            
            query_embedding = [0.1] * 384
            results = await db.similarity_search(
                query_embedding, 
                top_k=3, 
                document_ids=['doc_0', 'doc_2']
            )
            
            # 應該只返回 doc_0 和 doc_2 的結果
            assert len(results) == 2
            returned_doc_ids = [r.document_id for r in results]
            assert 'doc_0' in returned_doc_ids
            assert 'doc_2' in returned_doc_ids
            assert 'doc_1' not in returned_doc_ids
    
    @pytest.mark.asyncio
    async def test_get_vector_count(self):
        """測試獲取向量總數"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            self.mock_index.ntotal = 5
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            # 模擬一些向量，其中一些被刪除
            for i in range(5):
                db.metadata_map[i] = {
                    'vector_id': f'vector_{i}',
                    'document_id': f'doc_{i}',
                    'deleted': i >= 3  # 後兩個被刪除
                }
            
            count = await db.get_vector_count()
            
            assert count == 3  # 只有前3個是活躍的
    
    @pytest.mark.asyncio
    async def test_get_statistics(self):
        """測試獲取統計資訊"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            self.mock_index.ntotal = 5
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            # 模擬一些向量
            for i in range(5):
                db.metadata_map[i] = {
                    'vector_id': f'vector_{i}',
                    'document_id': f'doc_{i % 2}',  # 2個不同的文件
                    'deleted': i >= 3
                }
            
            stats = await db.get_statistics()
            
            assert stats['total_vectors'] == 5
            assert stats['active_vectors'] == 3
            assert stats['deleted_vectors'] == 2
            assert stats['unique_documents'] == 2
            assert stats['dimension'] == 384
            assert stats['metric'] == 'cosine'
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """測試健康檢查成功"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            self.mock_index.ntotal = 10
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            result = await db.health_check()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_no_index(self):
        """測試健康檢查無索引"""
        db = FaissVectorDatabase(str(self.index_path))
        # 不初始化索引
        
        result = await db.health_check()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_backup_and_restore_index(self):
        """測試索引備份和恢復"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            # 創建一些測試文件
            db.index_file.touch()
            db.metadata_file.write_text('{"test": "data"}')
            db.id_map_file.write_text('{"test": "mapping"}')
            
            backup_path = str(Path(self.temp_dir) / "backup")
            
            # 測試備份
            backup_result = await db.backup_index("default", backup_path)
            assert backup_result is True
            
            # 驗證備份文件存在
            backup_dir = Path(backup_path)
            assert (backup_dir / "faiss_index.bin").exists()
            assert (backup_dir / "metadata.json").exists()
            assert (backup_dir / "id_mapping.json").exists()
            
            # 測試恢復
            restore_result = await db.restore_index("default", backup_path)
            assert restore_result is True
    
    def test_normalize_vector_cosine(self):
        """測試餘弦度量的向量正規化"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path), metric="cosine")
            
            embedding = [3.0, 4.0, 0.0]  # 長度為5的向量
            normalized = db._normalize_vector(embedding)
            
            # 檢查是否正規化（長度為1）
            assert abs(np.linalg.norm(normalized) - 1.0) < 1e-6
    
    def test_normalize_vector_euclidean(self):
        """測試歐幾里得度量的向量處理"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path), metric="euclidean")
            
            embedding = [3.0, 4.0, 0.0]
            normalized = db._normalize_vector(embedding)
            
            # 歐幾里得度量不應該正規化
            assert np.allclose(normalized[0], embedding)
    
    @pytest.mark.asyncio
    async def test_close_database(self):
        """測試關閉資料庫"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            await db.initialize()
            
            await db.close()
            
            assert db.index is None
    
    def test_get_storage_size_mb(self):
        """測試獲取儲存大小"""
        with patch('bmad_autogen.apps.backend.src.services.faiss_vector_database.faiss') as mock_faiss:
            mock_faiss.index_factory.return_value = self.mock_index
            
            db = FaissVectorDatabase(str(self.index_path))
            
            # 創建一些測試文件
            db.index_path.mkdir(parents=True, exist_ok=True)
            db.index_file.write_bytes(b'0' * 1024)  # 1KB
            db.metadata_file.write_text('test')
            db.id_map_file.write_text('test')
            
            size_mb = db._get_storage_size_mb()
            
            assert size_mb > 0
            assert isinstance(size_mb, float)


if __name__ == "__main__":
    pytest.main([__file__])