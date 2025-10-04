"""
Unit tests for LEAD_UPDATE intent
Tests the updateLeadStatus function and mock CRM /crm/leads/{lead_id}/status endpoint
"""

import pytest
import requests
from uuid import UUID


# Base URL for mock CRM
BASE_URL = "http://localhost:8001"


@pytest.fixture
def created_lead():
    """Fixture to create a lead for testing status updates"""
    payload = {
        "name": "Test Lead for Update",
        "phone": "8888888888",
        "city": "Delhi"
    }

    response = requests.post(f"{BASE_URL}/crm/leads", json=payload)
    assert response.status_code == 200

    return response.json()["lead_id"]


def test_update_lead_status_to_in_progress(created_lead):
    """Test updating lead status to IN_PROGRESS"""
    payload = {
        "status": "IN_PROGRESS",
        "notes": "Initial contact made"
    }

    response = requests.post(
        f"{BASE_URL}/crm/leads/{created_lead}/status",
        json=payload
    )

    assert response.status_code == 200
    data = response.json()

    assert data["lead_id"] == created_lead
    assert data["status"] == "IN_PROGRESS"


def test_update_lead_status_to_won(created_lead):
    """Test updating lead status to WON"""
    payload = {
        "status": "WON",
        "notes": "Booked unit A2"
    }

    response = requests.post(
        f"{BASE_URL}/crm/leads/{created_lead}/status",
        json=payload
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "WON"


def test_update_lead_status_to_lost(created_lead):
    """Test updating lead status to LOST"""
    payload = {
        "status": "LOST",
        "notes": "Not interested"
    }

    response = requests.post(
        f"{BASE_URL}/crm/leads/{created_lead}/status",
        json=payload
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "LOST"


def test_update_lead_status_to_follow_up(created_lead):
    """Test updating lead status to FOLLOW_UP"""
    payload = {
        "status": "FOLLOW_UP"
    }

    response = requests.post(
        f"{BASE_URL}/crm/leads/{created_lead}/status",
        json=payload
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "FOLLOW_UP"


def test_update_lead_status_without_notes(created_lead):
    """Test updating lead status without optional notes"""
    payload = {
        "status": "IN_PROGRESS"
    }

    response = requests.post(
        f"{BASE_URL}/crm/leads/{created_lead}/status",
        json=payload
    )

    assert response.status_code == 200


def test_update_lead_status_invalid_status(created_lead):
    """Test updating lead with invalid status value"""
    payload = {
        "status": "INVALID_STATUS"
    }

    response = requests.post(
        f"{BASE_URL}/crm/leads/{created_lead}/status",
        json=payload
    )

    # Should return 422 due to pydantic validation (regex pattern)
    assert response.status_code == 422


def test_update_lead_status_lowercase(created_lead):
    """Test updating lead with lowercase status (should fail)"""
    payload = {
        "status": "won"
    }

    response = requests.post(
        f"{BASE_URL}/crm/leads/{created_lead}/status",
        json=payload
    )

    # Should fail validation (requires uppercase)
    assert response.status_code == 422


def test_update_lead_status_invalid_lead_id():
    """Test updating status for non-existent lead"""
    fake_lead_id = "00000000-0000-0000-0000-000000000000"

    payload = {
        "status": "WON"
    }

    response = requests.post(
        f"{BASE_URL}/crm/leads/{fake_lead_id}/status",
        json=payload
    )

    # Should return 404 Not Found
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_lead_status_missing_status(created_lead):
    """Test updating lead without status field"""
    payload = {
        "notes": "Some notes"
    }

    response = requests.post(
        f"{BASE_URL}/crm/leads/{created_lead}/status",
        json=payload
    )

    # Should return 422
    assert response.status_code == 422


def test_update_lead_status_multiple_times(created_lead):
    """Test updating lead status multiple times (status transitions)"""
    status_flow = ["IN_PROGRESS", "FOLLOW_UP", "WON"]

    for status in status_flow:
        payload = {
            "status": status,
            "notes": f"Updating to {status}"
        }

        response = requests.post(
            f"{BASE_URL}/crm/leads/{created_lead}/status",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == status


def test_update_lead_back_to_new(created_lead):
    """Test updating lead back to NEW status"""
    # First update to IN_PROGRESS
    payload1 = {"status": "IN_PROGRESS"}
    response1 = requests.post(
        f"{BASE_URL}/crm/leads/{created_lead}/status",
        json=payload1
    )
    assert response1.status_code == 200

    # Then back to NEW
    payload2 = {"status": "NEW"}
    response2 = requests.post(
        f"{BASE_URL}/crm/leads/{created_lead}/status",
        json=payload2
    )
    assert response2.status_code == 200
    assert response2.json()["status"] == "NEW"


def test_update_lead_with_long_notes(created_lead):
    """Test updating lead with very long notes"""
    long_notes = "A" * 1000  # 1000 characters

    payload = {
        "status": "FOLLOW_UP",
        "notes": long_notes
    }

    response = requests.post(
        f"{BASE_URL}/crm/leads/{created_lead}/status",
        json=payload
    )

    # Should succeed (no length limit)
    assert response.status_code == 200


if __name__ == "__main__":
    print("Running Lead Update Tests...")
    print("Make sure mock CRM server is running on port 8001!")
    pytest.main([__file__, "-v"])
