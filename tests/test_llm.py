from unittest.mock import MagicMock, patch

from app.llm import classify_incident
from app.models import IncidentAnalysis


def test_classify_incident_uses_structured_output():
    fake_analysis = IncidentAnalysis(
        category="STORAGE",
        severity="HIGH",
        summary="Database connection pool exhausted on prod-db-01",
        suggested_action="Restart the database connection pool",
    )
    fake_response = MagicMock(parsed_output=fake_analysis)

    with patch("app.llm.get_client") as mock_get_client:
        mock_get_client.return_value.messages.parse.return_value = fake_response

        result = classify_incident("Database connection timeout on prod-db-01")

    assert result == fake_analysis

    parse_call = mock_get_client.return_value.messages.parse
    parse_call.assert_called_once()
    assert parse_call.call_args.kwargs["output_format"] is IncidentAnalysis
