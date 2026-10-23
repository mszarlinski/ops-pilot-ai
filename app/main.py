"""OpsPilot AI — FastAPI application entrypoint.

Lab 01 (Direct LLM Integration), Step 1: this module currently contains a
deterministic, non-LLM incident classifier skeleton. The real classification
logic is left unimplemented on purpose — see the exercise described in
docs/learning-roadmap.md.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="OpsPilot AI", version="0.1.0")


class IncidentRequest(BaseModel):
    description: str = Field(min_length=10, max_length=2000)


class IncidentAnalysis(BaseModel):
    category: str
    severity: str
    summary: str
    suggested_action: str


@app.post("/incidents/analyze", response_model=IncidentAnalysis)
def analyze_incident(request: IncidentRequest) -> IncidentAnalysis:
    desc = request.description

    if "timeout" in desc.lower():
        category, severity = "STORAGE", "HIGH"
    else:
        category, severity = "OTHER", "LOW"

    return IncidentAnalysis(
        category=category,
        severity=severity,
        summary="summary",
        suggested_action="action",
    )