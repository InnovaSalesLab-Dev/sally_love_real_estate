"""
Tests for Vapi function handlers
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test basic health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Sally Love" in data["service"]


def test_check_property_endpoint():
    """Test check_property function endpoint"""
    payload = {
        "city": "Ocala",
        "state": "FL",
        "min_price": 200000,
        "max_price": 400000,
        "bedrooms": 3
    }
    
    response = client.post("/functions/check_property", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


def test_get_agent_info_endpoint():
    """Test get_agent_info function endpoint"""
    payload = {
        "city": "Ocala"
    }
    
    response = client.post("/functions/get_agent_info", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


def test_create_buyer_lead_endpoint():
    """Test create_buyer_lead function endpoint"""
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "email": "john@example.com",
        "max_price": 300000,
        "bedrooms": 3,
        "location_preference": "Ocala"
    }
    
    response = client.post("/functions/create_buyer_lead", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


def test_create_seller_lead_endpoint():
    """Test create_seller_lead function endpoint"""
    payload = {
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "+1234567890",
        "email": "jane@example.com",
        "property_address": "123 Main St",
        "city": "Ocala",
        "state": "FL",
        "zip_code": "34470",
        "bedrooms": 3,
        "bathrooms": 2
    }
    
    response = client.post("/functions/create_seller_lead", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


def test_route_to_agent_endpoint():
    """Test route_to_agent function endpoint"""
    payload = {
        "agent_id": "test_agent_123",
        "agent_name": "Sally Love",
        "agent_phone": "+13523992010",
        "caller_name": "Test Caller",
        "reason": "property inquiry"
    }
    
    response = client.post("/functions/route_to_agent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


def test_send_notification_endpoint():
    """Test send_notification function endpoint"""
    payload = {
        "recipient_phone": "+1234567890",
        "message": "Test notification message",
        "notification_type": "sms"
    }
    
    response = client.post("/functions/send_notification", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


# Test webhook endpoints
def test_vapi_webhook_health():
    """Test Vapi webhook health check"""
    response = client.get("/webhooks/vapi/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_crm_webhook_health():
    """Test CRM webhook health check"""
    response = client.get("/webhooks/crm/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

