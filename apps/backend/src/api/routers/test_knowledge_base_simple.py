"""
知識庫 API 路由基本測試
測試知識庫 CRUD 操作的 HTTP 請求處理
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from ...main import app

client = TestClient(app)


@pytest.fixture
def mock_user():
    """模擬測試使用者"""
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    user.name = "Test User"
    return user


@pytest.fixture
def auth_headers():
    """模擬 JWT 認證標頭"""
    return {"Authorization": "Bearer test_token"}


class TestKnowledgeBaseAPIBasic:
    """知識庫 API 基本測試"""

    @patch('src.api.routers.knowledge_base.get_current_user_dependency')
    @patch('src.core.database.get_db')
    def test_create_knowledge_base_unauthorized(self, mock_get_db, mock_get_user):
        """測試未認證的創建知識庫請求"""
        response = client.post(
            "/api/knowledge-base/",
            json={"name": "測試知識庫", "path": "/test/path"}
        )
        # 應該返回401未認證錯誤
        assert response.status_code == 401

    @patch('src.api.routers.knowledge_base.get_current_user_dependency')
    @patch('src.core.database.get_db')
    def test_get_knowledge_bases_unauthorized(self, mock_get_db, mock_get_user):
        """測試未認證的獲取知識庫列表請求"""
        response = client.get("/api/knowledge-base/")
        # 應該返回401未認證錯誤
        assert response.status_code == 401

    @patch('src.api.routers.knowledge_base.get_current_user_dependency')
    @patch('src.core.database.get_db')
    def test_create_knowledge_base_invalid_data(self, mock_get_db, mock_get_user, mock_user, auth_headers):
        """測試使用無效資料創建知識庫"""
        mock_get_user.return_value = mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # 測試空名稱和路徑
        response = client.post(
            "/api/knowledge-base/",
            json={"name": "", "path": ""},
            headers=auth_headers
        )
        # 應該返回422驗證錯誤
        assert response.status_code == 422

    @patch('src.api.routers.knowledge_base.get_current_user_dependency')
    @patch('src.core.database.get_db')
    def test_create_knowledge_base_missing_fields(self, mock_get_db, mock_get_user, mock_user, auth_headers):
        """測試缺少必要欄位的創建知識庫請求"""
        mock_get_user.return_value = mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # 測試缺少path欄位
        response = client.post(
            "/api/knowledge-base/",
            json={"name": "測試知識庫"},
            headers=auth_headers
        )
        # 應該返回422驗證錯誤
        assert response.status_code == 422

    @patch('src.api.routers.knowledge_base.get_current_user_dependency') 
    @patch('src.core.database.get_db')
    @patch('src.services.document_processing_service.document_processing_service.validate_path_security')
    def test_create_knowledge_base_path_validation_error(self, mock_validate, mock_get_db, mock_get_user, mock_user, auth_headers):
        """測試路徑驗證失敗的情況"""
        mock_get_user.return_value = mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_validate.side_effect = Exception("路徑無效")
        
        response = client.post(
            "/api/knowledge-base/",
            json={"name": "測試知識庫", "path": "/invalid/path"},
            headers=auth_headers
        )
        # 應該返回500內部伺服器錯誤
        assert response.status_code == 500

    def test_api_endpoint_exists(self):
        """測試 API 端點存在"""
        # 測試根路由存在
        response = client.get("/")
        assert response.status_code == 200
        
        # 測試健康檢查端點存在
        response = client.get("/health")
        assert response.status_code == 200

    def test_knowledge_base_endpoints_require_auth(self):
        """測試知識庫端點需要認證"""
        endpoints = [
            ("GET", "/api/knowledge-base/"),
            ("POST", "/api/knowledge-base/"),
            ("GET", "/api/knowledge-base/test-id"),
            ("GET", "/api/knowledge-base/test-id/status"),
            ("PUT", "/api/knowledge-base/test-id"),
            ("DELETE", "/api/knowledge-base/test-id"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            # 所有端點都應該要求認證
            assert response.status_code == 401

    @patch('src.api.routers.knowledge_base.get_current_user_dependency')
    @patch('src.core.database.get_db')
    def test_knowledge_base_not_found(self, mock_get_db, mock_get_user, mock_user, auth_headers):
        """測試獲取不存在的知識庫"""
        mock_get_user.return_value = mock_user
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        mock_get_db.return_value = mock_db
        
        fake_id = "nonexistent-id"
        response = client.get(f"/api/knowledge-base/{fake_id}", headers=auth_headers)
        
        # 應該返回404找不到錯誤
        assert response.status_code == 404


def test_document_processing_service_import():
    """測試文件處理服務可以正常導入"""
    from ...services.document_processing_service import document_processing_service
    assert document_processing_service is not None


def test_knowledge_base_models_import():
    """測試知識庫模型可以正常導入"""
    from ...models.knowledge_base import KnowledgeBase, KnowledgeBaseStatus
    assert KnowledgeBase is not None
    assert KnowledgeBaseStatus is not None


def test_knowledge_base_schemas_import():
    """測試知識庫 Schema 可以正常導入"""
    from ...schemas.knowledge_base_schema import (
        CreateKnowledgeBaseRequest,
        KnowledgeBaseResponse,
        KnowledgeBaseStatusResponse
    )
    assert CreateKnowledgeBaseRequest is not None
    assert KnowledgeBaseResponse is not None
    assert KnowledgeBaseStatusResponse is not None