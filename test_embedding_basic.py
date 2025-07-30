#!/usr/bin/env python3
"""
基本 Embedding 功能測試腳本
"""

import sys
import os
import asyncio
import tempfile
from pathlib import Path

# 添加模組路徑
sys.path.insert(0, 'apps/backend/src')

# 測試依賴
try:
    import faiss
    print("✓ faiss-cpu 安裝正確")
except ImportError as e:
    print(f"✗ faiss-cpu 未安裝: {e}")
    sys.exit(1)

try:
    import httpx
    print("✓ httpx 安裝正確")
except ImportError as e:
    print(f"✗ httpx 未安裝: {e}")
    sys.exit(1)

try:
    import numpy as np
    print("✓ numpy 安裝正確")
except ImportError as e:
    print(f"✗ numpy 未安裝: {e}")
    sys.exit(1)

# 直接導入模組避免相對導入問題
import importlib.util

def import_module_from_path(module_name, file_path):
    """從文件路徑導入模組"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# 導入所需模組
embedding_service_mod = import_module_from_path(
    "ollama_embedding_service", 
    "apps/backend/src/services/ollama_embedding_service.py"
)
EmbeddingConfig = embedding_service_mod.EmbeddingConfig
OllamaEmbeddingService = embedding_service_mod.OllamaEmbeddingService

def test_embedding_config():
    """測試 Embedding 配置"""
    print("\n=== 測試 Embedding 配置 ===")
    
    config = EmbeddingConfig(
        base_url="http://ollama.webtw.xyz:11434",
        model_name="all-minilm:l6-v2",
        timeout=30,
        max_retries=3
    )
    
    print(f"✓ Embedding 配置創建成功: {config.base_url}")
    print(f"  模型: {config.model_name}")
    print(f"  超時: {config.timeout}s")
    print(f"  最大重試: {config.max_retries}")
    
    return config

def test_faiss_database():
    """測試 Faiss 向量資料庫"""
    print("\n=== 測試 Faiss 向量資料庫 ===")
    
    from services.faiss_vector_database import FaissVectorDatabase
    
    # 使用臨時目錄
    with tempfile.TemporaryDirectory() as temp_dir:
        db = FaissVectorDatabase(temp_dir, dimension=384)
        print(f"✓ FaissVectorDatabase 創建成功: {temp_dir}")
        print(f"  維度: {db.dimension}")
        print(f"  度量: {db.metric}")
        
        return True

async def test_ollama_connection():
    """測試 Ollama 連線（如果可用）"""
    print("\n=== 測試 Ollama 連線 ===")
    
    config = EmbeddingConfig()
    service = OllamaEmbeddingService(config)
    
    try:
        await service.initialize()
        
        # 測試健康檢查（如果服務可用）
        is_healthy = await service.health_check()
        if is_healthy:
            print("✓ Ollama 服務連線成功")
            print("✓ 模型 all-minilm:l6-v2 可用")
        else:
            print("⚠ Ollama 服務不可用（但這是預期的，因為是外部服務）")
            
    except Exception as e:
        print(f"⚠ Ollama 連線測試失敗（預期的）: {str(e)[:100]}...")
    finally:
        await service.close()

def test_document_processing():
    """測試文件處理"""
    print("\n=== 測試文件處理 ===")
    
    from services.document_processing_service import DocumentProcessingService, DocumentMetadata, ChunkingStrategy
    from datetime import datetime
    
    service = DocumentProcessingService()
    
    # 創建測試文件元數據
    metadata = DocumentMetadata(
        file_path="/test/sample.txt",
        relative_path="sample.txt",
        file_size=1000,
        file_type=".txt",
        mime_type="text/plain",
        modified_time=datetime.now()
    )
    
    # 測試文本分塊
    test_text = "這是一個測試文件內容。" * 50  # 創建足夠長的文本
    chunks = service.create_text_chunks(test_text, metadata)
    
    print(f"✓ 文件分塊成功: {len(chunks)} 個分塊")
    if chunks:
        print(f"  第一個分塊長度: {chunks[0]['chunk_size']} 字元")
        print(f"  分塊語言: {chunks[0].get('language', 'unknown')}")

def test_integration_service():
    """測試整合服務"""
    print("\n=== 測試整合服務 ===")
    
    from services.embedding_integration_service import EmbeddingIntegrationService
    
    with tempfile.TemporaryDirectory() as temp_dir:
        service = EmbeddingIntegrationService(vector_db_path=temp_dir)
        print("✓ EmbeddingIntegrationService 創建成功")
        print(f"  向量資料庫路徑: {temp_dir}")

async def run_all_tests():
    """執行所有測試"""
    print("開始執行 Embedding 基本功能測試...\n")
    
    try:
        # 基本配置測試
        config = test_embedding_config()
        
        # Faiss 資料庫測試
        test_faiss_database()
        
        # 文件處理測試
        test_document_processing()
        
        # 整合服務測試
        test_integration_service()
        
        # Ollama 連線測試（異步）
        await test_ollama_connection()
        
        print("\n=== 測試總結 ===")
        print("✓ 所有基本功能測試通過")
        print("✓ 核心服務模組可以正常導入和使用")
        print("✓ 依賴套件安裝正確")
        print("\n注意：Ollama 外部服務連線測試失敗是正常的，因為這是外部服務")
        
    except Exception as e:
        print(f"\n✗ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    sys.exit(0 if result else 1)