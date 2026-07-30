from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.models.audit_job import AuditJob
from app.schemas.audit_job import JobCreate, JobOut
from app.services.crawler_service import fetch_html
from app.services.audit_engine import audit_html, calculate_compliance_score
from app.models.page import AuditPage
from app.models.violation import Violation
from datetime import datetime, timezone

router = APIRouter()

async def run_quick_audit(job_id: UUID, db: AsyncSession):
    from sqlalchemy import select as sel
    result = await db.execute(sel(AuditJob).where(AuditJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        return

    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    await db.commit()

    try:
        html = await fetch_html(job.url)
        if not html:
            job.status = "failed"
            job.error_message = "Could not fetch URL"
            await db.commit()
            return

        from app.services.crawler_service import get_page_title
        violations = audit_html(html, job.url)
        score = calculate_compliance_score(violations)
        title = get_page_title(html)
        critical_v = [v for v in violations if v.severity == "critical"]
        warning_v = [v for v in violations if v.severity in ("moderate", "minor")]

        page = AuditPage(
            job_id=job.id, url=job.url, title=title,
            violation_count=len(violations),
            critical_count=len(critical_v),
            warning_count=len(warning_v),
            compliance_score=score,
        )
        db.add(page)
        await db.flush()

        for v in violations:
            db.add(Violation(
                page_id=page.id,
                wcag_criterion=v.wcag_criterion, wcag_level=v.wcag_level,
                severity=v.severity, description=v.description,
                element=v.element, fix_suggestion=v.fix_suggestion, help_url=v.help_url,
            ))

        job.pages_crawled = 1
        job.total_violations = len(violations)
        job.critical_violations = len(critical_v)
        job.compliance_score = score
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)[:500]
        await db.commit()

@router.post("/", response_model=JobOut)
async def create_job(data: JobCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    job = AuditJob(url=data.url, site_name=data.site_name, max_pages=data.max_pages)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    background_tasks.add_task(run_quick_audit, job.id, db)
    return job

@router.get("/", response_model=list[JobOut])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditJob).order_by(AuditJob.created_at.desc()).limit(50))
    return list(result.scalars().all())

@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditJob).where(AuditJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
