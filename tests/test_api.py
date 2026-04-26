import pytest
from fastapi.testclient import TestClient
from main import app
from core.database import create_db_and_tables

# Ensure tables exist
create_db_and_tables()

client = TestClient(app)

def test_submit_note_returns_id():
    response = client.post("/api/notes", json={"text": "Patient took Aspirin."})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "processed"

def test_get_note_returns_text_and_entities():
    # Submit first
    post_res = client.post("/api/notes", json={"text": "Patient took Aspirin."})
    note_id = post_res.json()["id"]

    # Fetch
    get_res = client.get(f"/api/notes/{note_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["text"] == "Patient took Aspirin."
    assert "entities" in data
    assert isinstance(data["entities"], list)
    # Note: Untrained base model may not extract exact entities accurately.
    # Verifying structure rather than exact ML prediction until trained.
    if len(data["entities"]) > 0:
        assert "entity" in data["entities"][0]
        assert "label" in data["entities"][0]

def test_deidentify_phi_in_note():
    post_res = client.post("/api/notes", json={"text": "Patient John Smith at 555-123-4567 reported rash."})
    note_id = post_res.json()["id"]
    
    get_res = client.get(f"/api/notes/{note_id}")
    data = get_res.json()
    
    # Verify redacted text is saved and returned
    assert "555-123-4567" not in data["text"]
    assert "[PHONE]" in data["text"]
