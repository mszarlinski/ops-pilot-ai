from pydantic import BaseModel, Field
from typing import Literal

class IncidentRequest(BaseModel):
    description: str = Field(min_length=10, max_length=2000)


class IncidentAnalysis(BaseModel):
    category: Literal["STORAGE", "BACKEND", "NETWORK", "UI", "OTHER"]
    severity: Literal["LOW","MEDIUM", "HIGH"]
    summary: str
    suggested_action: str
