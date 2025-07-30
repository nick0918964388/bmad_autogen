"""
Ollama Embedding 服務
提供與 http://ollama.webtw.xyz:11434 的整合
使用 all-minilm:l6-v2 模型進行文件內容向量化
"""

import httpx
import json
import logging
import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from ..core.exceptions import BaseAppException

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Embedding 配置"""
    base_url: str = "http://ollama.webtw.xyz:11434"
    model_name: str = "all-minilm:l6-v2"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


class OllamaConnectionError(BaseAppException):
    """Ollama 連線錯誤"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=503,
            message=f"Ollama 服務連線失敗: {message}",
            error_code="OLLAMA_CONNECTION_FAILED",
            details=details
        )


class EmbeddingGenerationError(BaseAppException):
    """Embedding 生成錯誤"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            message=f"Embedding 生成失敗: {message}",
            error_code="EMBEDDING_GENERATION_FAILED",
            details=details
        )


class OllamaEmbeddingService:
    """Ollama Embedding 服務"""
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        self.config = config or EmbeddingConfig()
        self.client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        """非同步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同步上下文管理器出口"""
        await self.close()
    
    async def initialize(self):
        """初始化 HTTP 客戶端"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
            logger.info(f"初始化 Ollama 客戶端，目標: {self.config.base_url}")
    
    async def close(self):
        """關閉 HTTP 客戶端"""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Ollama 客戶端已關閉")
    
    async def health_check(self) -> bool:
        """
        檢查 Ollama 服務健康狀態
        
        Returns:
            bool: 服務是否健康
        """
        try:
            if not self.client:
                await self.initialize()
            
            response = await self.client.get(f"{self.config.base_url}/api/tags")
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                
                # 檢查所需模型是否可用
                model_available = any(
                    self.config.model_name in name for name in model_names
                )
                
                if not model_available:
                    logger.warning(f"模型 {self.config.model_name} 在服務中不可用")
                    logger.info(f"可用模型: {model_names}")
                
                return model_available
            
            return False
            
        except Exception as e:
            logger.error(f"健康檢查失敗: {str(e)}")
            return False
    
    async def generate_embedding(
        self, 
        text: str, 
        retry_count: int = 0
    ) -> List[float]:
        """
        為給定文本生成 Embedding 向量
        
        Args:
            text: 要生成 Embedding 的文本
            retry_count: 當前重試次數
            
        Returns:
            List[float]: 384 維向量陣列
            
        Raises:
            OllamaConnectionError: 連線失敗
            EmbeddingGenerationError: 生成失敗
        """
        if not text or not text.strip():
            raise EmbeddingGenerationError("空文本無法生成 Embedding")
        
        try:
            if not self.client:
                await self.initialize()
            
            # 準備請求資料
            request_data = {
                "model": self.config.model_name,
                "prompt": text.strip()
            }
            
            logger.debug(f"生成 Embedding，文本長度: {len(text)}")
            
            # 發送請求
            response = await self.client.post(
                f"{self.config.base_url}/api/embeddings",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            # 檢查回應狀態
            if response.status_code == 200:
                result = response.json()
                embedding = result.get("embedding")
                
                if embedding and isinstance(embedding, list):
                    # 驗證向量維度
                    if len(embedding) == 384:
                        logger.debug(f"成功生成 384 維 Embedding")
                        return embedding
                    else:
                        raise EmbeddingGenerationError(
                            f"向量維度不正確: {len(embedding)}，預期: 384"
                        )
                else:
                    raise EmbeddingGenerationError("回應中缺少 embedding 資料")
            
            else:
                error_detail = f"HTTP {response.status_code}: {response.text}"
                raise OllamaConnectionError(
                    f"API 請求失敗",
                    details={"status_code": response.status_code, "response": response.text}
                )
        
        except httpx.TimeoutException:
            if retry_count < self.config.max_retries:
                logger.warning(f"請求超時，重試 {retry_count + 1}/{self.config.max_retries}")
                await asyncio.sleep(self.config.retry_delay * (retry_count + 1))
                return await self.generate_embedding(text, retry_count + 1)
            else:
                raise OllamaConnectionError("請求超時，重試次數已用盡")
        
        except httpx.ConnectError:
            if retry_count < self.config.max_retries:
                logger.warning(f"連線失敗，重試 {retry_count + 1}/{self.config.max_retries}")
                await asyncio.sleep(self.config.retry_delay * (retry_count + 1))
                return await self.generate_embedding(text, retry_count + 1)
            else:
                raise OllamaConnectionError("無法連接到 Ollama 服務")
        
        except Exception as e:
            if isinstance(e, (OllamaConnectionError, EmbeddingGenerationError)):
                raise
            else:
                raise EmbeddingGenerationError(f"未預期的錯誤: {str(e)}")
    
    async def generate_embeddings_batch(
        self, 
        texts: List[str], 
        batch_size: int = 10
    ) -> List[List[float]]:
        """
        批次生成多個文本的 Embedding
        
        Args:
            texts: 文本列表
            batch_size: 批次大小
            
        Returns:
            List[List[float]]: 向量陣列列表
        """
        if not texts:
            return []
        
        results = []
        
        # 分批處理以避免過度負載
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_results = []
            
            logger.info(f"處理批次 {i//batch_size + 1}，包含 {len(batch_texts)} 個文本")
            
            # 並行處理批次中的文本
            tasks = [self.generate_embedding(text) for text in batch_texts]
            
            try:
                batch_embeddings = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_embeddings):
                    if isinstance(result, Exception):
                        logger.error(f"批次中第 {j+1} 個文本處理失敗: {str(result)}")
                        raise result
                    else:
                        batch_results.append(result)
                
                results.extend(batch_results)
                
                # 批次間稍作停頓以避免過載
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"批次處理失敗: {str(e)}")
                raise
        
        logger.info(f"完成批次處理，總共生成 {len(results)} 個 Embedding")
        return results
    
    async def get_model_info(self) -> Dict[str, Any]:
        """
        獲取模型資訊
        
        Returns:
            Dict[str, Any]: 模型資訊
        """
        try:
            if not self.client:
                await self.initialize()
            
            response = await self.client.post(
                f"{self.config.base_url}/api/show",
                json={"name": self.config.model_name}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise OllamaConnectionError(f"無法獲取模型資訊: {response.text}")
                
        except Exception as e:
            logger.error(f"獲取模型資訊失敗: {str(e)}")
            raise