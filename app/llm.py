"""LLM integration boundary.

This module is the one place in the app that talks to the Claude API. Keeping
it isolated behind a plain function lets the rest of the app (and its tests)
depend on a stable interface instead of the Anthropic SDK directly.
"""

import logging

from anthropic import Anthropic, APIError
from dotenv import load_dotenv

from app.models import IncidentAnalysis

load_dotenv()

logger = logging.getLogger(__name__)

_client: Anthropic | None = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


SYSTEM_PROMPT = (
    "You are an IT incident triage assistant. Classify the incident "
    "description you are given."
)


def classify_incident(description: str) -> IncidentAnalysis:
    """Classify an incident description using the Claude API.

    Must use structured outputs (`output_format=IncidentAnalysis`) so the
    response is validated into an IncidentAnalysis instance by the SDK,
    rather than parsed from free text.
    """
    try:
        response = get_client().messages.parse(
            model="claude-opus-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": description}],
            output_format=IncidentAnalysis,
        )
    except APIError:
        logger.exception("Claude API call failed while classifying incident")
        raise

    return response.parsed_output
