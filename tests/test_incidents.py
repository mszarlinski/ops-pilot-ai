from unittest.mock import patch

from fastapi.testclient import TestClient

from app.llm import LLMRequestError, LLMUnavailableError
from app.main import app
from app.models import IncidentAnalysis

client = TestClient(app)


def test_analyze_incident_returns_llm_classification():
    fake_analysis = IncidentAnalysis(
        category="STORAGE",
        severity="HIGH",
        summary="Database connection pool exhausted on prod-db-01",
        suggested_action="Restart the database connection pool",
    )
    description = "Database connection timeout on prod-db-01 since 10 minutes"

    with patch("app.main.classify_incident", return_value=fake_analysis) as mock_classify:
        response = client.post("/incidents/analyze", json={"description": description})

    assert response.status_code == 200
    assert response.json() == fake_analysis.model_dump()
    mock_classify.assert_called_once_with(description)


def test_analyze_incident_rejects_description_too_short():
    response = client.post("/incidents/analyze", json={"description": "too short"})

    assert response.status_code == 422


def test_analyze_incident_returns_503_when_llm_unavailable():
    with patch("app.main.classify_incident", side_effect=LLMUnavailableError("down")):
        response = client.post(
            "/incidents/analyze",
            json={"description": "Database connection timeout on prod-db-01"},
        )

    assert response.status_code == 503


def test_analyze_incident_returns_502_when_llm_request_rejected():
    with patch("app.main.classify_incident", side_effect=LLMRequestError("bad request")):
        response = client.post(
            "/incidents/analyze",
            json={"description": "Database connection timeout on prod-db-01"},
        )

    assert response.status_code == 502
