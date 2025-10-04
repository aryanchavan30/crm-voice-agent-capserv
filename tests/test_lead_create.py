"""
Unit tests for LEAD_CREATE intent
Tests the createLead function and mock CRM /crm/leads endpoint
"""

import pytest
import requests
from uuid import UUID

# Base URL for mock CRM
BASE_URL = "http://localhost:8001"


def test_create_lead_success():
    """Test successful lead creation with all fields"""
    payload = {
        "name": "Rohan Sharma",
        "phone": "9876543210",
        "city": "Gurgaon",
        "source": "Instagram"
    }

    response = requests.post(f"{BASE_URL}/crm/leads", json=payload)

    assert response.status_code == 200
    data = response.json()

    # Validate response structure
    assert "lead_id" in data
    assert "status" in data

    # Validate UUID format
    try:
        UUID(data["lead_id"])
    except ValueError:
        pytest.fail("lead_id is not a valid UUID")

    # Validate status
    assert data["status"] == "NEW"


def test_create_lead_without_source():
    """Test lead creation without optional source field"""
    payload = {
        "name": "Priya Nair",
        "phone": "9123456789",
        "city": "Mumbai"
    }

    response = requests.post(f"{BASE_URL}/crm/leads", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "lead_id" in data
    assert data["status"] == "NEW"


def test_create_lead_missing_name():
    """Test lead creation with missing required name field"""
    payload = {
        "phone": "9876543210",
        "city": "Gurgaon"
    }

    response = requests.post(f"{BASE_URL}/crm/leads", json=payload)

    # Should return 422 Unprocessable Entity
    assert response.status_code == 422


def test_create_lead_missing_phone():
    """Test lead creation with missing required phone field"""
    payload = {
        "name": "Test User",
        "city": "Delhi"
    }

    response = requests.post(f"{BASE_URL}/crm/leads", json=payload)

    assert response.status_code == 422


def test_create_lead_missing_city():
    """Test lead creation with missing required city field"""
    payload = {
        "name": "Test User",
        "phone": "9876543210"
    }

    response = requests.post(f"{BASE_URL}/crm/leads", json=payload)

    assert response.status_code == 422


def test_create_lead_empty_fields():
    """Test lead creation with empty string values"""
    payload = {
        "name": "",
        "phone": "",
        "city": ""
    }

    response = requests.post(f"{BASE_URL}/crm/leads", json=payload)

    # Should succeed but with empty values (or fail based on validation)
    # This test documents current behavior
    assert response.status_code in [200, 422]


def test_create_multiple_leads():
    """Test creating multiple leads to ensure uniqueness of IDs"""
    leads = []

    for i in range(3):
        payload = {
            "name": f"Lead {i}",
            "phone": f"999999999{i}",
            "city": "Mumbai"
        }

        response = requests.post(f"{BASE_URL}/crm/leads", json=payload)
        assert response.status_code == 200

        data = response.json()
        leads.append(data["lead_id"])

    # Ensure all lead_ids are unique
    assert len(leads) == len(set(leads))


def test_create_lead_special_characters_in_name():
    """Test lead creation with special characters in name"""
    payload = {
        "name": "O'Brien & Sons",
        "phone": "9876543210",
        "city": "Chennai"
    }

    response = requests.post(f"{BASE_URL}/crm/leads", json=payload)

    assert response.status_code == 200


def test_create_lead_long_phone_number():
    """Test lead creation with longer phone number (with country code)"""
    payload = {
        "name": "Test User",
        "phone": "+919876543210",
        "city": "Bangalore"
    }

    response = requests.post(f"{BASE_URL}/crm/leads", json=payload)

    # Should accept any string for phone
    assert response.status_code == 200


if __name__ == "__main__":
    print("Running Lead Create Tests...")
    print("Make sure mock CRM server is running on port 8001!")
    pytest.main([__file__, "-v"])
