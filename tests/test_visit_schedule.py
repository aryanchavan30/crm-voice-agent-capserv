"""
Unit tests for VISIT_SCHEDULE intent
Tests the scheduleVisit function and mock CRM /crm/visits endpoint
"""

import pytest
import requests
from uuid import UUID
from datetime import datetime, timedelta


# Base URL for mock CRM
BASE_URL = "http://localhost:8001"


@pytest.fixture
def created_lead():
    """Fixture to create a lead for testing visits"""
    payload = {
        "name": "Test Lead for Visit",
        "phone": "9999999999",
        "city": "Mumbai"
    }

    response = requests.post(f"{BASE_URL}/crm/leads", json=payload)
    assert response.status_code == 200

    return response.json()["lead_id"]


def test_schedule_visit_success(created_lead):
    """Test successful visit scheduling with all fields"""
    visit_time = (datetime.now() + timedelta(days=1)).isoformat()

    payload = {
        "lead_id": created_lead,
        "visit_time": visit_time,
        "notes": "Follow up site visit"
    }

    response = requests.post(f"{BASE_URL}/crm/visits", json=payload)

    assert response.status_code == 200
    data = response.json()

    # Validate response structure
    assert "visit_id" in data
    assert "status" in data

    # Validate UUID format
    try:
        UUID(data["visit_id"])
    except ValueError:
        pytest.fail("visit_id is not a valid UUID")

    # Validate status
    assert data["status"] == "SCHEDULED"


def test_schedule_visit_without_notes(created_lead):
    """Test visit scheduling without optional notes field"""
    visit_time = "2025-10-05T15:00:00+05:30"

    payload = {
        "lead_id": created_lead,
        "visit_time": visit_time
    }

    response = requests.post(f"{BASE_URL}/crm/visits", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "visit_id" in data
    assert data["status"] == "SCHEDULED"


def test_schedule_visit_invalid_lead_id():
    """Test visit scheduling with non-existent lead_id"""
    fake_lead_id = "00000000-0000-0000-0000-000000000000"
    visit_time = "2025-10-05T15:00:00+05:30"

    payload = {
        "lead_id": fake_lead_id,
        "visit_time": visit_time
    }

    response = requests.post(f"{BASE_URL}/crm/visits", json=payload)

    # Should return 404 Not Found
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_schedule_visit_missing_lead_id():
    """Test visit scheduling with missing required lead_id"""
    payload = {
        "visit_time": "2025-10-05T15:00:00+05:30"
    }

    response = requests.post(f"{BASE_URL}/crm/visits", json=payload)

    # Should return 422 Unprocessable Entity
    assert response.status_code == 422


def test_schedule_visit_missing_visit_time(created_lead):
    """Test visit scheduling with missing required visit_time"""
    payload = {
        "lead_id": created_lead
    }

    response = requests.post(f"{BASE_URL}/crm/visits", json=payload)

    assert response.status_code == 422


def test_schedule_visit_invalid_datetime_format(created_lead):
    """Test visit scheduling with invalid datetime format"""
    payload = {
        "lead_id": created_lead,
        "visit_time": "not-a-valid-datetime"
    }

    response = requests.post(f"{BASE_URL}/crm/visits", json=payload)

    # Should return 422 due to pydantic validation
    assert response.status_code == 422


def test_schedule_multiple_visits_same_lead(created_lead):
    """Test scheduling multiple visits for the same lead"""
    visits = []

    for i in range(3):
        visit_time = (datetime.now() + timedelta(days=i+1)).isoformat()

        payload = {
            "lead_id": created_lead,
            "visit_time": visit_time,
            "notes": f"Visit {i+1}"
        }

        response = requests.post(f"{BASE_URL}/crm/visits", json=payload)
        assert response.status_code == 200

        data = response.json()
        visits.append(data["visit_id"])

    # Ensure all visit_ids are unique
    assert len(visits) == len(set(visits))


def test_schedule_visit_past_datetime(created_lead):
    """Test scheduling visit in the past (should be allowed by API)"""
    past_time = (datetime.now() - timedelta(days=1)).isoformat()

    payload = {
        "lead_id": created_lead,
        "visit_time": past_time
    }

    response = requests.post(f"{BASE_URL}/crm/visits", json=payload)

    # API doesn't validate past dates - should succeed
    assert response.status_code == 200


def test_schedule_visit_with_timezone(created_lead):
    """Test visit scheduling with timezone in ISO 8601 format"""
    visit_time = "2025-10-05T17:00:00+05:30"  # IST

    payload = {
        "lead_id": created_lead,
        "visit_time": visit_time
    }

    response = requests.post(f"{BASE_URL}/crm/visits", json=payload)

    assert response.status_code == 200


if __name__ == "__main__":
    print("Running Visit Schedule Tests...")
    print("Make sure mock CRM server is running on port 8001!")
    pytest.main([__file__, "-v"])
