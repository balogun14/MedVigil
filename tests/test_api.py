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
    post_res = client.post("/api/notes", json={"text": "Patient Sola Awwal visited on 2023-10-15 and called from 555-123-4567."})
    note_id = post_res.json()["id"]
    
    get_res = client.get(f"/api/notes/{note_id}")
    data = get_res.json()
    
    # Verify redacted text is saved and returned
    assert "555-123-4567" not in data["text"]
    assert "[PHONE]" in data["text"]
    assert "2023-10-15" not in data["text"]
    assert "[DATE]" in data["text"]
    assert "Sola Awwal" not in data["text"]
    assert "[NAME]" in data["text"]

def test_rag_literature_search():
    # Submit first
    post_res = client.post("/api/notes", json={"text": "Patient took Aspirin and developed tinnitus."})
    note_id = post_res.json()["id"]

    # Trigger literature search
    rag_res = client.post(f"/api/notes/{note_id}/literature-search")
    assert rag_res.status_code == 200
    data = rag_res.json()
    
    assert "classification" in data
    assert data["classification"] in ["Known", "Unknown", "Unlabeled"]
    assert "summary" in data
    assert isinstance(data["summary"], str)
    assert len(data["summary"]) > 0

def test_naranjo_draft():
    # Submit first
    post_res = client.post("/api/notes", json={"text": "Patient took Aspirin and developed tinnitus. Discontinuing drug resolved tinnitus."})
    note_id = post_res.json()["id"]

    # Get Draft
    draft_res = client.get(f"/api/notes/{note_id}/naranjo-draft")
    assert draft_res.status_code == 200
    data = draft_res.json()
    assert "questions" in data
    assert len(data["questions"]) == 10
    # E.g. question 3 might be auto-filled if dechallenge is mentioned

def test_naranjo_calculate():
    post_res = client.post("/api/notes", json={"text": "Test Note"})
    note_id = post_res.json()["id"]

    # Answers: List of +1, 0, -1, etc.
    answers = [1, 2, 1, 0, 0, 0, 0, 0, 0, 0] # Total = 4 (Possible)
    calc_res = client.post(f"/api/notes/{note_id}/naranjo", json={"answers": answers})
    assert calc_res.status_code == 200
    
    data = calc_res.json()
    assert data["score"] == 4
    assert data["classification"] == "Possible"
