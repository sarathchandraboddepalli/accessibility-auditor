import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class Violation(Base):
    __tablename__ = "violations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audit_pages.id", ondelete="CASCADE"))
    wcag_criterion: Mapped[str] = mapped_column(String(50))     # e.g. "1.1.1"
    wcag_level: Mapped[str] = mapped_column(String(5))          # A, AA, AAA
    severity: Mapped[str] = mapped_column(String(20))           # critical, serious, moderate, minor
    description: Mapped[str] = mapped_column(Text)
    element: Mapped[str | None] = mapped_column(Text)           # HTML element that failed
    fix_suggestion: Mapped[str | None] = mapped_column(Text)
    help_url: Mapped[str | None] = mapped_column(String(512))
    page: Mapped["AuditPage"] = relationship("AuditPage", back_populates="violations")
