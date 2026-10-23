"""OpsPilot AI — FastAPI application entrypoint.

Lab 01 (Direct LLM Integration), Step 3: the endpoint maps LLM-boundary
exceptions from app.llm to HTTP status codes — 503 for transient upstream
unavailability, 502 for requests the Claude API rejected outright.
"""

from fastapi import FastAPI, HTTPException

from app.llm import LLMRequestError, LLMUnavailableError, classify_incident
from app.models import IncidentAnalysis, IncidentRequest

app = FastAPI(title="OpsPilot AI", version="0.1.0")


@app.post("/incidents/analyze", response_model=IncidentAnalysis)
def analyze_incident(request: IncidentRequest) -> IncidentAnalysis:
    try:
        return classify_incident(request.description)
    except LLMUnavailableError as err:
        raise HTTPException(status_code=503, detail="LLM service unavailable") from err
    except LLMRequestError as err:
        raise HTTPException(status_code=502, detail="LLM request rejected") from err
