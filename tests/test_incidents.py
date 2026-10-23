from unittest.mock import patch

from fastapi.testclient import TestClient

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
