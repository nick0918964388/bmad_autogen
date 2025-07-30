"""
知識庫 API 路由測試
測試知識庫 CRUD 操作的 HTTP 請求處理
"""

import pytest
import uuid
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from ...main import app


client = TestClient(app)


@pytest.fixture
def mock_user():
    """模擬測試使用者"""
    user_mock = Mock()
    user_mock.id = 1
    user_mock.email = "test@example.com"
    user_mock.name = "Test User"
    return user_mock


@pytest.fixture
def auth_headers():
    """模擬 JWT 認證標頭"""
    return {"Authorization": "Bearer test_token"}


class TestKnowledgeBaseAPI:
    """知識庫 API 測試類別"""

    def setup_method(self):
        """每個測試方法前的設置"""
        cleanup_database()

    def teardown_method(self):
        """每個測試方法後的清理"""
        cleanup_database()

    @patch('src.services.document_processing_service.document_processing_service.validate_path_security')
    def test_create_knowledge_base_success(self, mock_validate_path, mock_current_user, auth_headers):
        """測試成功創建知識庫"""
        mock_validate_path.return_value = "/validated/path"
        
        knowledge_base_data = {
            "name": "測試知識庫",
            "path": "/test/path"
        }
        
        response = client.post(
            "/api/knowledge-base/",
            json=knowledge_base_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "測試知識庫"
        assert data["path"] == "/test/path"
        assert data["status"] == "pending"
        assert data["userId"] == str(mock_current_user.id)
        assert "id" in data

    def test_create_knowledge_base_invalid_data(self, mock_current_user, auth_headers):
        """測試使用無效資料創建知識庫"""
        invalid_data = {
            "name": "",  # 空名稱
            "path": ""   # 空路徑
        }
        
        response = client.post(
            "/api/knowledge-base/",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error

    @patch('src.services.document_processing_service.document_processing_service.validate_path_security')
    def test_create_knowledge_base_duplicate_name(self, mock_validate_path, mock_current_user, auth_headers):
        """測試創建重複名稱的知識庫"""
        mock_validate_path.return_value = "/validated/path"
        
        # 先創建一個知識庫
        db = TestingSessionLocal()
        existing_kb = KnowledgeBase(
            user_id=mock_current_user.id,
            name="測試知識庫",
            path="/existing/path",
            status=KnowledgeBaseStatus.PENDING
        )
        db.add(existing_kb)
        db.commit()
        db.close()
        
        # 嘗試創建同名知識庫
        knowledge_base_data = {
            "name": "測試知識庫",
            "path": "/different/path"
        }
        
        response = client.post(
            "/api/knowledge-base/",
            json=knowledge_base_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "已存在同名知識庫" in response.json()["detail"]

    @patch('src.services.document_processing_service.document_processing_service.validate_path_security')
    def test_create_knowledge_base_duplicate_path(self, mock_validate_path, mock_current_user, auth_headers):
        """測試創建重複路徑的知識庫"""
        mock_validate_path.return_value = "/test/path"
        
        # 先創建一個知識庫
        db = TestingSessionLocal()
        existing_kb = KnowledgeBase(
            user_id=mock_current_user.id,
            name="現有知識庫",
            path="/test/path",
            status=KnowledgeBaseStatus.PENDING
        )
        db.add(existing_kb)
        db.commit()
        db.close()
        
        # 嘗試創建同路徑知識庫
        knowledge_base_data = {
            "name": "新知識庫",
            "path": "/test/path"
        }
        
        response = client.post(
            "/api/knowledge-base/",
            json=knowledge_base_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "該路徑已被其他知識庫使用" in response.json()["detail"]

    def test_get_knowledge_bases_empty(self, mock_current_user, auth_headers):
        """測試獲取空的知識庫列表"""
        response = client.get("/api/knowledge-base/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["knowledgeBases"] == []
        assert data["total"] == 0

    def test_get_knowledge_bases_with_data(self, mock_current_user, auth_headers):
        """測試獲取知識庫列表"""
        # 創建測試知識庫
        db = TestingSessionLocal()
        kb1 = KnowledgeBase(
            user_id=mock_current_user.id,
            name="知識庫1",
            path="/path1",
            status=KnowledgeBaseStatus.READY,
            document_count=10
        )
        kb2 = KnowledgeBase(
            user_id=mock_current_user.id,
            name="知識庫2",
            path="/path2",
            status=KnowledgeBaseStatus.PROCESSING,
            document_count=0
        )
        db.add_all([kb1, kb2])
        db.commit()
        db.close()
        
        response = client.get("/api/knowledge-base/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["knowledgeBases"]) == 2
        
        # 檢查資料正確性
        kb_names = [kb["name"] for kb in data["knowledgeBases"]]
        assert "知識庫1" in kb_names
        assert "知識庫2" in kb_names

    def test_get_knowledge_base_by_id(self, mock_current_user, auth_headers):
        """測試根據 ID 獲取特定知識庫"""
        # 創建測試知識庫
        db = TestingSessionLocal()
        kb = KnowledgeBase(
            user_id=mock_current_user.id,
            name="測試知識庫",
            path="/test/path",
            status=KnowledgeBaseStatus.READY,
            document_count=5
        )
        db.add(kb)
        db.commit()
        db.refresh(kb)
        kb_id = str(kb.id)
        db.close()
        
        response = client.get(f"/api/knowledge-base/{kb_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == kb_id
        assert data["name"] == "測試知識庫"
        assert data["path"] == "/test/path"
        assert data["status"] == "ready"
        assert data["documentCount"] == 5

    def test_get_knowledge_base_not_found(self, mock_current_user, auth_headers):
        """測試獲取不存在的知識庫"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/knowledge-base/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
        assert "找不到知識庫" in response.json()["detail"]

    def test_get_knowledge_base_status(self, mock_current_user, auth_headers):
        """測試獲取知識庫狀態"""
        # 創建測試知識庫
        db = TestingSessionLocal()
        kb = KnowledgeBase(
            user_id=mock_current_user.id,
            name="測試知識庫",
            path="/test/path",
            status=KnowledgeBaseStatus.PROCESSING,
            document_count=0,
            total_chunks=0
        )
        db.add(kb)
        db.commit()
        db.refresh(kb)
        kb_id = str(kb.id)
        db.close()
        
        response = client.get(f"/api/knowledge-base/{kb_id}/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == kb_id
        assert data["status"] == "processing"
        assert data["documentCount"] == 0
        assert data["totalChunks"] == 0

    def test_update_knowledge_base_name(self, mock_current_user, auth_headers):
        """測試更新知識庫名稱"""
        # 創建測試知識庫
        db = TestingSessionLocal()
        kb = KnowledgeBase(
            user_id=mock_current_user.id,
            name="原始名稱",
            path="/test/path",
            status=KnowledgeBaseStatus.READY
        )
        db.add(kb)
        db.commit()
        db.refresh(kb)
        kb_id = str(kb.id)
        db.close()
        
        update_data = {"name": "新名稱"}
        response = client.put(
            f"/api/knowledge-base/{kb_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新名稱"
        assert data["path"] == "/test/path"  # 路徑應該保持不變

    def test_update_knowledge_base_processing(self, mock_current_user, auth_headers):
        """測試更新正在處理中的知識庫（應該失敗）"""
        # 創建正在處理的知識庫
        db = TestingSessionLocal()
        kb = KnowledgeBase(
            user_id=mock_current_user.id,
            name="處理中的知識庫",
            path="/test/path",
            status=KnowledgeBaseStatus.PROCESSING
        )
        db.add(kb)
        db.commit()
        db.refresh(kb)
        kb_id = str(kb.id)
        db.close()
        
        update_data = {"name": "新名稱"}
        response = client.put(
            f"/api/knowledge-base/{kb_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "正在處理中，無法修改" in response.json()["detail"]

    @patch('src.services.document_processing_service.document_processing_service.delete_knowledge_base_files')
    def test_delete_knowledge_base(self, mock_delete_files, mock_current_user, auth_headers):
        """測試刪除知識庫"""
        mock_delete_files.return_value = 10  # 模擬刪除了 10 個分塊
        
        # 創建測試知識庫
        db = TestingSessionLocal()
        kb = KnowledgeBase(
            user_id=mock_current_user.id,
            name="要刪除的知識庫",
            path="/test/path",
            status=KnowledgeBaseStatus.READY
        )
        db.add(kb)
        db.commit()
        db.refresh(kb)
        kb_id = str(kb.id)
        db.close()
        
        response = client.delete(f"/api/knowledge-base/{kb_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "知識庫已成功刪除"
        assert data["deletedKnowledgeBaseId"] == kb_id
        assert data["deletedChunksCount"] == 10
        
        # 驗證知識庫已被刪除
        db = TestingSessionLocal()
        deleted_kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
        assert deleted_kb is None
        db.close()

    @patch('src.services.document_processing_service.document_processing_service.delete_knowledge_base_files')
    def test_reprocess_knowledge_base(self, mock_delete_files, mock_current_user, auth_headers):
        """測試重新處理知識庫"""
        mock_delete_files.return_value = 5
        
        # 創建測試知識庫
        db = TestingSessionLocal()
        kb = KnowledgeBase(
            user_id=mock_current_user.id,
            name="重新處理的知識庫",
            path="/test/path",
            status=KnowledgeBaseStatus.ERROR,
            document_count=5,
            total_chunks=15,
            error_details="處理失敗"
        )
        db.add(kb)
        db.commit()
        db.refresh(kb)
        kb_id = str(kb.id)
        db.close()
        
        response = client.post(f"/api/knowledge-base/{kb_id}/reprocess", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "知識庫重新處理已開始"
        assert data["knowledgeBaseId"] == kb_id
        
        # 驗證狀態已重置
        db = TestingSessionLocal()
        updated_kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
        assert updated_kb.status == KnowledgeBaseStatus.PENDING
        assert updated_kb.document_count == 0
        assert updated_kb.total_chunks == 0
        assert updated_kb.error_details is None
        db.close()

    def test_reprocess_knowledge_base_processing(self, mock_current_user, auth_headers):
        """測試重新處理正在處理中的知識庫（應該失敗）"""
        # 創建正在處理的知識庫
        db = TestingSessionLocal()
        kb = KnowledgeBase(
            user_id=mock_current_user.id,
            name="處理中的知識庫",
            path="/test/path",
            status=KnowledgeBaseStatus.PROCESSING
        )
        db.add(kb)
        db.commit()
        db.refresh(kb)
        kb_id = str(kb.id)
        db.close()
        
        response = client.post(f"/api/knowledge-base/{kb_id}/reprocess", headers=auth_headers)
        
        assert response.status_code == 400
        assert "正在處理中，請稍後再試" in response.json()["detail"]

    def test_unauthorized_access(self):
        """測試未認證存取"""
        response = client.get("/api/knowledge-base/")
        assert response.status_code == 401

    def test_user_isolation(self, auth_headers):
        """測試使用者資料隔離"""
        # 創建兩個不同的使用者
        db = TestingSessionLocal()
        user1 = User(id=1, email="user1@test.com", name="User 1", password_hash="hash1")
        user2 = User(id=2, email="user2@test.com", name="User 2", password_hash="hash2")
        db.add_all([user1, user2])
        db.commit()
        
        # 為 user2 創建知識庫
        kb_user2 = KnowledgeBase(
            user_id=user2.id,
            name="User2的知識庫",
            path="/user2/path",
            status=KnowledgeBaseStatus.READY
        )
        db.add(kb_user2)
        db.commit()
        kb_id = str(kb_user2.id)
        db.close()
        
        # 使用 user1 的身份嘗試存取 user2 的知識庫
        with patch('src.api.routers.knowledge_base.get_current_user_dependency') as mock:
            mock.return_value = user1
            response = client.get(f"/api/knowledge-base/{kb_id}", headers=auth_headers)
            
            assert response.status_code == 404  # 應該找不到，因為屬於不同使用者