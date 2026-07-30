from pydantic import BaseModel
from uuid import UUID

class PageOut(BaseModel):
    id: UUID
    job_id: UUID
    url: str
    title: str | None
    violation_count: int
    critical_count: int
    warning_count: int
    compliance_score: float | None
    model_config = {"from_attributes": True}
