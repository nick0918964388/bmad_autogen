import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root_endpoint():
    """測試根路由"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "智能助理應用程式 API"
    assert data["version"] == "1.0.0"

def test_health_check():
    """測試健康檢查端點"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "智能助理後端服務"
    assert "timestamp" in data

def test_api_health_check():
    """測試 API 健康檢查端點"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert "timestamp" in data
    assert data["environment"] == "development"