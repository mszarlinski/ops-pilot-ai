"""OpsPilot AI — FastAPI application entrypoint.

Lab 01 (Direct LLM Integration), Step 2: the endpoint now delegates
classification to app.llm.classify_incident, which is responsible for
calling the Claude API with structured outputs. That function is
intentionally unimplemented — see the exercise described in
docs/learning-roadmap.md.
"""

from fastapi import FastAPI

from app.llm import classify_incident
from app.models import IncidentAnalysis, IncidentRequest

app = FastAPI(title="OpsPilot AI", version="0.1.0")


@app.post("/incidents/analyze", response_model=IncidentAnalysis)
def analyze_incident(request: IncidentRequest) -> IncidentAnalysis:
    return classify_incident(request.description)
