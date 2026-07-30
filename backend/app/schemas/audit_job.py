from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class JobCreate(BaseModel):
    url: str
    site_name: str | None = None
    max_pages: int = 10

class JobOut(BaseModel):
    id: UUID
    url: str
    site_name: str | None
    status: str
    max_pages: int
    pages_crawled: int
    total_violations: int
    critical_violations: int
    compliance_score: float | None
    error_message: str | None
    created_at: datetime
    model_config = {"from_attributes": True}
