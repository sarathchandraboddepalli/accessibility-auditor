from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.database import get_db
from app.models.audit_job import AuditJob
from app.models.page import AuditPage
from app.models.violation import Violation
from app.services.report_service import generate_html_report, generate_pdf_report

router = APIRouter()

@router.get("/{job_id}/html")
async def get_html_report(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditJob).where(AuditJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    pages_result = await db.execute(select(AuditPage).where(AuditPage.job_id == job_id))
    pages = list(pages_result.scalars().all())

    pages_with_violations = []
    for page in pages:
        v_result = await db.execute(select(Violation).where(Violation.page_id == page.id))
        violations = list(v_result.scalars().all())
        pages_with_violations.append({"url": page.url, "compliance_score": page.compliance_score,
                                       "violation_count": page.violation_count, "violations": violations})

    html = generate_html_report(job, pages_with_violations)
    return Response(content=html, media_type="text/html")

@router.get("/{job_id}/pdf")
async def get_pdf_report(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditJob).where(AuditJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    pages_result = await db.execute(select(AuditPage).where(AuditPage.job_id == job_id))
    pages = list(pages_result.scalars().all())

    pages_data = []
    for page in pages:
        v_result = await db.execute(select(Violation).where(Violation.page_id == page.id))
        violations = list(v_result.scalars().all())
        pages_data.append({"url": page.url, "compliance_score": page.compliance_score,
                           "violation_count": page.violation_count, "violations": violations})

    pdf = generate_pdf_report(job, pages_data)
    return Response(content=pdf, media_type="application/pdf",
                   headers={"Content-Disposition": f"attachment; filename=audit-{job_id}.pdf"})
