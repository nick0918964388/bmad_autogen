"""
知識庫功能基本測試
測試知識庫相關的基本功能
"""

import pytest
from unittest.mock import Mock


def test_knowledge_base_models_can_be_imported():
    """測試知識庫模型可以正常導入"""
    try:
        from src.models.knowledge_base import KnowledgeBase, KnowledgeBaseStatus
        assert KnowledgeBase is not None
        assert KnowledgeBaseStatus is not None
        
        # 測試枚舉值
        assert hasattr(KnowledgeBaseStatus, 'PENDING')
        assert hasattr(KnowledgeBaseStatus, 'PROCESSING')
        assert hasattr(KnowledgeBaseStatus, 'READY')
        assert hasattr(KnowledgeBaseStatus, 'ERROR')
    except ImportError as e:
        pytest.fail(f"Failed to import knowledge base models: {e}")


def test_knowledge_base_schemas_can_be_imported():
    """測試知識庫 Schema 可以正常導入"""
    try:
        from src.schemas.knowledge_base_schema import (
            CreateKnowledgeBaseRequest,
            KnowledgeBaseResponse,
            KnowledgeBaseStatusResponse,
            KnowledgeBaseStatusEnum
        )
        assert CreateKnowledgeBaseRequest is not None
        assert KnowledgeBaseResponse is not None
        assert KnowledgeBaseStatusResponse is not None
        assert KnowledgeBaseStatusEnum is not None
    except ImportError as e:
        pytest.fail(f"Failed to import knowledge base schemas: {e}")


def test_document_processing_service_can_be_imported():
    """測試文件處理服務可以正常導入"""
    try:
        from src.services.document_processing_service import DocumentProcessingService
        service = DocumentProcessingService()
        assert service is not None
        
        # 測試服務配置
        assert hasattr(service, 'SUPPORTED_EXTENSIONS')
        assert hasattr(service, 'DOCUMENT_EXTENSIONS')
        assert hasattr(service, 'MAX_FILE_SIZE')
        assert hasattr(service, 'CHUNK_SIZE')
        assert hasattr(service, 'CHUNK_OVERLAP')
        
        # 測試配置值
        assert service.CHUNK_SIZE == 1000
        assert service.CHUNK_OVERLAP == 100
        assert service.MAX_FILE_SIZE == 10 * 1024 * 1024
        
    except ImportError as e:
        pytest.fail(f"Failed to import document processing service: {e}")


def test_knowledge_base_api_router_can_be_imported():
    """測試知識庫 API 路由可以正常導入"""
    try:
        from src.api.routers.knowledge_base import router
        assert router is not None
        assert hasattr(router, 'prefix')
        assert router.prefix == "/knowledge-base"
    except ImportError as e:
        pytest.fail(f"Failed to import knowledge base router: {e}")


def test_create_knowledge_base_request_validation():
    """測試創建知識庫請求的驗證"""
    from src.schemas.knowledge_base_schema import CreateKnowledgeBaseRequest
    from pydantic import ValidationError
    
    # 測試有效請求
    valid_request = CreateKnowledgeBaseRequest(
        name="測試知識庫",
        path="/valid/path"
    )
    assert valid_request.name == "測試知識庫"
    assert valid_request.path == "/valid/path"
    
    # 測試無效請求 - 空名稱
    with pytest.raises(ValidationError):
        CreateKnowledgeBaseRequest(name="", path="/valid/path")
    
    # 測試無效請求 - 空路徑
    with pytest.raises(ValidationError):
        CreateKnowledgeBaseRequest(name="測試知識庫", path="")
    
    # 測試無效請求 - 包含不安全字元的路徑
    with pytest.raises(ValidationError):
        CreateKnowledgeBaseRequest(name="測試知識庫", path="/path/../unsafe")


def test_knowledge_base_status_enum():
    """測試知識庫狀態枚舉"""
    from src.schemas.knowledge_base_schema import KnowledgeBaseStatusEnum
    
    # 測試枚舉值
    assert KnowledgeBaseStatusEnum.PENDING == "pending"
    assert KnowledgeBaseStatusEnum.PROCESSING == "processing"
    assert KnowledgeBaseStatusEnum.READY == "ready"
    assert KnowledgeBaseStatusEnum.ERROR == "error"


def test_document_processing_service_text_chunking():
    """測試文件處理服務的文字分塊功能"""
    from src.services.document_processing_service import DocumentProcessingService
    
    service = DocumentProcessingService()
    
    # 測試短文字
    short_text = "這是一段短文字。"
    chunks = service.create_text_chunks(short_text, "test.txt")
    assert len(chunks) == 1
    assert chunks[0]['content'] == short_text
    assert chunks[0]['chunk_index'] == 0
    assert chunks[0]['document_path'] == "test.txt"
    
    # 測試空文字
    empty_chunks = service.create_text_chunks("", "empty.txt")
    assert len(empty_chunks) == 0
    
    # 測試長文字（會被分塊）
    long_text = "這是測試文字。" * 200  # 創建足夠長的文字
    long_chunks = service.create_text_chunks(long_text, "long.txt")
    assert len(long_chunks) > 1
    
    # 檢查分塊結構
    for i, chunk in enumerate(long_chunks):
        assert chunk['chunk_index'] == i
        assert chunk['document_path'] == "long.txt"
        assert len(chunk['content']) <= service.CHUNK_SIZE


def test_fastapi_app_can_be_imported():
    """測試 FastAPI 應用程式可以正常導入"""
    try:
        from src.main import app
        assert app is not None
        assert hasattr(app, 'title')
        assert "智能助理應用程式 API" in app.title
    except ImportError as e:
        pytest.fail(f"Failed to import FastAPI app: {e}")


def test_knowledge_base_model_to_dict():
    """測試知識庫模型的 to_dict 方法"""
    from src.models.knowledge_base import KnowledgeBase, KnowledgeBaseStatus
    from datetime import datetime
    import uuid
    
    # 創建模擬知識庫實例
    kb = KnowledgeBase()
    kb.id = uuid.uuid4()
    kb.user_id = 1
    kb.name = "測試知識庫"
    kb.path = "/test/path"
    kb.status = KnowledgeBaseStatus.PENDING
    kb.document_count = 0
    kb.created_at = datetime.now()
    kb.updated_at = datetime.now()
    kb.imported_at = None
    kb.total_chunks = 0
    kb.processing_started_at = None
    kb.processing_completed_at = None
    
    # 測試 to_dict 方法
    kb_dict = kb.to_dict()
    
    assert isinstance(kb_dict, dict)
    assert kb_dict['name'] == "測試知識庫"
    assert kb_dict['path'] == "/test/path"
    assert kb_dict['status'] == "pending"
    assert kb_dict['documentCount'] == 0
    assert 'id' in kb_dict
    assert 'userId' in kb_dict
    assert 'createdAt' in kb_dict
    assert 'updatedAt' in kb_dict


def test_supported_file_extensions():
    """測試支援的檔案擴展名配置"""
    from src.services.document_processing_service import DocumentProcessingService
    
    service = DocumentProcessingService()
    
    # 測試支援的文字檔案格式
    text_extensions = {'.txt', '.md', '.markdown', '.rst'}
    for ext in text_extensions:
        assert ext in service.SUPPORTED_EXTENSIONS
    
    # 測試支援的程式碼檔案格式
    code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json'}
    for ext in code_extensions:
        assert ext in service.SUPPORTED_EXTENSIONS
    
    # 測試文件格式
    doc_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}
    for ext in doc_extensions:
        assert ext in service.DOCUMENT_EXTENSIONS