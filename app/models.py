from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    description: str = Field(min_length=10, max_length=2000)


class IncidentAnalysis(BaseModel):
    category: str
    severity: str
    summary: str
    suggested_action: str
