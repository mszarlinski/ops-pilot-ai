"""LLM integration boundary.

This module is the one place in the app that talks to the Claude API. Keeping
it isolated behind a plain function lets the rest of the app (and its tests)
depend on a stable interface instead of the Anthropic SDK directly.
"""

import logging
import os

from anthropic import (
    Anthropic,
    APIConnectionError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    RateLimitError,
)
from dotenv import load_dotenv

from app.models import IncidentAnalysis

load_dotenv()

logger = logging.getLogger(__name__)

LLM_MODEL = os.environ["LLM_MODEL"]


class LLMUnavailableError(Exception):
    """The Claude API is transiently unavailable; retrying later may succeed.

    Raise this for failures where the SDK's own retries (429, 5xx, connection
    errors) were already exhausted but the failure is still not the caller's
    fault — e.g. anthropic.RateLimitError, anthropic.APIConnectionError,
    anthropic.InternalServerError.
    """


class LLMRequestError(Exception):
    """The request to the Claude API was rejected and will not succeed on retry.

    Raise this for failures caused by how *we* built the request, not by
    transient upstream conditions — e.g. anthropic.BadRequestError,
    anthropic.AuthenticationError.
    """


_client: Anthropic | None = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


SYSTEM_PROMPT = (
    "You are an IT incident triage assistant. Classify the incident "
    "description you are given.\n\n"
    "category must be exactly one of:\n"
    "- STORAGE: databases, disks, object storage (e.g. S3), backups, or "
    "storage arrays.\n"
    "- BACKEND: application or service logic, internal APIs, job queues, or "
    "server-side errors not caused by storage or network infrastructure.\n"
    "- NETWORK: connectivity, VPNs, DNS, load balancers, or packet loss "
    "between systems.\n"
    "- UI: frontend, layout, rendering, or visual/display issues.\n"
    "- OTHER: anything that does not clearly fit the categories above.\n\n"
    "severity must be exactly one of:\n"
    "- HIGH: a core capability is broken or widely unavailable, data "
    "integrity is at risk, or there is no workaround.\n"
    "- MEDIUM: degraded performance or a partial, non-blocking impact; a "
    "workaround usually exists.\n"
    "- LOW: cosmetic or isolated issues with no functional impact."
)


def classify_incident(description: str) -> IncidentAnalysis:
    """Classify an incident description using the Claude API.

    Must use structured outputs (`output_format=IncidentAnalysis`) so the
    response is validated into an IncidentAnalysis instance by the SDK,
    rather than parsed from free text.
    """
    try:
        response = get_client().messages.parse(
            model=LLM_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": description}],
            output_format=IncidentAnalysis,
        )
    except (RateLimitError, APIConnectionError, InternalServerError) as err:
        logger.exception("Claude API transiently unavailable")
        raise LLMUnavailableError() from err
    except (BadRequestError, AuthenticationError) as err:
        logger.exception("Claude API rejected the request")
        raise LLMRequestError() from err

    return response.parsed_output
