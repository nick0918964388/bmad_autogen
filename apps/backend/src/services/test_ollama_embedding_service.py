"""
Ollama Embedding 服務測試
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from .ollama_embedding_service import (
    OllamaEmbeddingService, 
    EmbeddingConfig,
    OllamaConnectionError,
    EmbeddingGenerationError
)


class TestOllamaEmbeddingService:
    """Ollama Embedding 服務測試類"""
    
    @pytest.fixture
    def config(self):
        """測試配置"""
        return EmbeddingConfig(
            base_url="http://test-ollama:11434",
            model_name="all-minilm:l6-v2",
            timeout=10,
            max_retries=2,
            retry_delay=0.1
        )
    
    @pytest.fixture
    def service(self, config):
        """服務實例"""
        return OllamaEmbeddingService(config)
    
    @pytest.fixture
    def mock_embedding_response(self):
        """Mock Embedding API 回應"""
        return {
            "embedding": [0.1, 0.2, 0.3] * 128  # 384 維向量
        }
    
    @pytest.mark.asyncio
    async def test_initialize_and_close(self, service):
        """測試初始化和關閉"""
        # 測試初始化
        await service.initialize()
        assert service.client is not None
        assert isinstance(service.client, httpx.AsyncClient)
        
        # 測試關閉
        await service.close()
        assert service.client is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, service):
        """測試上下文管理器"""
        async with service as s:
            assert s.client is not None
        # 確保自動關閉
        assert service.client is None
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, service):
        """測試健康檢查成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "all-minilm:l6-v2"},
                {"name": "other-model:latest"}
            ]
        }
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            result = await service.health_check()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_model_not_available(self, service):
        """測試健康檢查 - 模型不可用"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "other-model:latest"}
            ]
        }
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            result = await service.health_check()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_connection_error(self, service):
        """測試健康檢查連線錯誤"""
        with patch('httpx.AsyncClient.get', side_effect=httpx.ConnectError("Connection failed")):
            result = await service.health_check()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_generate_embedding_success(self, service, mock_embedding_response):
        """測試成功生成 Embedding"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_embedding_response
        
        with patch('httpx.AsyncClient.post', return_value=mock_response) as mock_post:
            result = await service.generate_embedding("test content")
            
            # 驗證結果
            assert len(result) == 384
            assert all(isinstance(x, (int, float)) for x in result)
            
            # 驗證請求參數
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]['json']['model'] == 'all-minilm:l6-v2'
            assert call_args[1]['json']['prompt'] == 'test content'
    
    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self, service):
        """測試空文本生成 Embedding"""
        with pytest.raises(EmbeddingGenerationError) as exc_info:
            await service.generate_embedding("")
        
        assert "空文本無法生成 Embedding" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_embedding_wrong_dimension(self, service):
        """測試錯誤的向量維度"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "embedding": [0.1, 0.2, 0.3]  # 錯誤維度
        }
        
        with patch('httpx.AsyncClient.post', return_value=mock_response):
            with pytest.raises(EmbeddingGenerationError) as exc_info:
                await service.generate_embedding("test content")
            
            assert "向量維度不正確" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_embedding_missing_data(self, service):
        """測試缺少 embedding 資料"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # 缺少 embedding
        
        with patch('httpx.AsyncClient.post', return_value=mock_response):
            with pytest.raises(EmbeddingGenerationError) as exc_info:
                await service.generate_embedding("test content")
            
            assert "回應中缺少 embedding 資料" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_embedding_http_error(self, service):
        """測試 HTTP 錯誤"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        with patch('httpx.AsyncClient.post', return_value=mock_response):
            with pytest.raises(OllamaConnectionError) as exc_info:
                await service.generate_embedding("test content")
            
            assert "API 請求失敗" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_embedding_timeout_retry(self, service, mock_embedding_response):
        """測試超時重試機制"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_embedding_response
        
        # 第一次超時，第二次成功
        with patch('httpx.AsyncClient.post', side_effect=[
            httpx.TimeoutException("Timeout"),
            mock_response
        ]) as mock_post:
            with patch('asyncio.sleep'):  # 模擬睡眠以加速測試
                result = await service.generate_embedding("test content")
                
                assert len(result) == 384
                assert mock_post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_generate_embedding_max_retries_exceeded(self, service):
        """測試超過最大重試次數"""
        with patch('httpx.AsyncClient.post', side_effect=httpx.TimeoutException("Timeout")):
            with patch('asyncio.sleep'):  # 模擬睡眠以加速測試
                with pytest.raises(OllamaConnectionError) as exc_info:
                    await service.generate_embedding("test content")
                
                assert "重試次數已用盡" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_embedding_connection_error_retry(self, service, mock_embedding_response):
        """測試連線錯誤重試機制"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_embedding_response
        
        # 第一次連線錯誤，第二次成功
        with patch('httpx.AsyncClient.post', side_effect=[
            httpx.ConnectError("Connection failed"),
            mock_response
        ]) as mock_post:
            with patch('asyncio.sleep'):  # 模擬睡眠以加速測試
                result = await service.generate_embedding("test content")
                
                assert len(result) == 384
                assert mock_post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_success(self, service, mock_embedding_response):
        """測試批次生成 Embedding 成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_embedding_response
        
        texts = ["text 1", "text 2", "text 3"]
        
        with patch('httpx.AsyncClient.post', return_value=mock_response) as mock_post:
            with patch('asyncio.sleep'):  # 模擬睡眠以加速測試
                results = await service.generate_embeddings_batch(texts, batch_size=2)
                
                assert len(results) == 3
                assert all(len(embedding) == 384 for embedding in results)
                assert mock_post.call_count == 3
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_empty_list(self, service):
        """測試批次生成空列表"""
        results = await service.generate_embeddings_batch([])
        assert results == []
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_partial_failure(self, service):
        """測試批次生成部分失敗"""
        texts = ["text 1", "text 2"]
        
        # 第一個成功，第二個失敗
        with patch('httpx.AsyncClient.post', side_effect=[
            MagicMock(status_code=200, json=lambda: {"embedding": [0.1] * 384}),
            httpx.ConnectError("Connection failed")
        ]):
            with pytest.raises(httpx.ConnectError):
                await service.generate_embeddings_batch(texts)
    
    @pytest.mark.asyncio
    async def test_get_model_info_success(self, service):
        """測試獲取模型資訊成功"""
        mock_model_info = {
            "modelfile": "model info",
            "parameters": "model parameters",
            "template": "model template"
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_model_info
        
        with patch('httpx.AsyncClient.post', return_value=mock_response) as mock_post:
            result = await service.get_model_info()
            
            assert result == mock_model_info
            
            # 驗證請求參數
            call_args = mock_post.call_args
            assert call_args[1]['json']['name'] == 'all-minilm:l6-v2'
    
    @pytest.mark.asyncio
    async def test_get_model_info_error(self, service):
        """測試獲取模型資訊失敗"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Model not found"
        
        with patch('httpx.AsyncClient.post', return_value=mock_response):
            with pytest.raises(OllamaConnectionError) as exc_info:
                await service.get_model_info()
            
            assert "無法獲取模型資訊" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])