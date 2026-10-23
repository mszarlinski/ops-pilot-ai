from unittest.mock import MagicMock, patch

import pytest
from anthropic import APIConnectionError, BadRequestError, RateLimitError

from app.llm import LLMRequestError, LLMUnavailableError, classify_incident
from app.models import IncidentAnalysis


def _fake_response(status_code: int) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.headers.get.return_value = None
    return response


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


def test_classify_incident_raises_llm_unavailable_on_rate_limit():
    error = RateLimitError("rate limited", response=_fake_response(429), body=None)

    with patch("app.llm.get_client") as mock_get_client:
        mock_get_client.return_value.messages.parse.side_effect = error

        with pytest.raises(LLMUnavailableError):
            classify_incident("Database connection timeout on prod-db-01")


def test_classify_incident_raises_llm_unavailable_on_connection_error():
    error = APIConnectionError(request=MagicMock())

    with patch("app.llm.get_client") as mock_get_client:
        mock_get_client.return_value.messages.parse.side_effect = error

        with pytest.raises(LLMUnavailableError):
            classify_incident("Database connection timeout on prod-db-01")


def test_classify_incident_raises_llm_request_error_on_bad_request():
    error = BadRequestError("bad request", response=_fake_response(400), body=None)

    with patch("app.llm.get_client") as mock_get_client:
        mock_get_client.return_value.messages.parse.side_effect = error

        with pytest.raises(LLMRequestError):
            classify_incident("Database connection timeout on prod-db-01")
