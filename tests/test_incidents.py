from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_incident_classifies_storage_timeout():
    response = client.post(
        "/incidents/analyze",
        json={"description": "Database connection timeout on prod-db-01 since 10 minutes"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "STORAGE"
    assert body["severity"] == "HIGH"
    assert body["summary"]
    assert body["suggested_action"]


def test_analyze_incident_classifies_other_as_low_severity():
    response = client.post(
        "/incidents/analyze",
        json={"description": "User reports the dashboard logo is slightly misaligned"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "OTHER"
    assert body["severity"] == "LOW"
    assert body["summary"]
    assert body["suggested_action"]


def test_analyze_incident_rejects_description_too_short():
    response = client.post("/incidents/analyze", json={"description": "too short"})

    assert response.status_code == 422
