from pydantic import BaseModel, field_validator
from datetime import datetime
from uuid import UUID
from urllib.parse import urlparse

class JobCreate(BaseModel):
    url: str
    site_name: str | None = None
    max_pages: int = 10

    @field_validator('url')
    @classmethod
    def url_must_be_http_or_https(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL scheme must be http or https")
        return v

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
