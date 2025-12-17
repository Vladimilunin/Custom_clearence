"""Unit tests for Parts API endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_create_part(client: TestClient):
    """Test creating a new part."""
    part_data = {
        "designation": "TEST-001",
        "name": "Test Part",
        "material": "Steel",
        "weight": 1.5,
        "dimensions": "100x50x25",
        "description": "Test description"
    }
    
    response = client.post("/api/v1/parts/", json=part_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["designation"] == part_data["designation"]
    assert data["name"] == part_data["name"]
    assert "id" in data


def test_read_parts(client: TestClient):
    """Test reading list of parts."""
    # Create a test part first
    part_data = {
        "designation": "TEST-002",
        "name": "Test Part 2"
    }
    client.post("/api/v1/parts/", json=part_data)
    
    # Get parts list
    response = client.get("/api/v1/parts/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_search_parts(client: TestClient):
    """Test searching parts."""
    # Create test parts
    client.post("/api/v1/parts/", json={"designation": "SEARCH-001", "name": "Searchable Part"})
    client.post("/api/v1/parts/", json={"designation": "OTHER-001", "name": "Other Part"})
    
    # Search
    response = client.get("/api/v1/parts/?search=SEARCH")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["designation"] == "SEARCH-001"


def test_update_part(client: TestClient):
    """Test updating a part."""
    # Create a part
    create_response = client.post("/api/v1/parts/", json={
        "designation": "UPDATE-001",
        "name": "Original Name"
    })
    part_id = create_response.json()["id"]
    
    # Update it
    update_data = {"name": "Updated Name"}
    response = client.put(f"/api/v1/parts/{part_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["designation"] == "UPDATE-001"


def test_update_nonexistent_part(client: TestClient):
    """Test updating a part that doesn't exist."""
    response = client.put("/api/v1/parts/99999", json={"name": "Test"})
    
    assert response.status_code == 404
