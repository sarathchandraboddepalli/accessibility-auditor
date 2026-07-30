from pydantic import BaseModel
from uuid import UUID

class ViolationOut(BaseModel):
    id: UUID
    page_id: UUID
    wcag_criterion: str
    wcag_level: str
    severity: str
    description: str
    element: str | None
    fix_suggestion: str | None
    model_config = {"from_attributes": True}
