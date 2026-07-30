from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.database import get_db
from app.models.page import AuditPage
from app.models.violation import Violation
from app.schemas.page import PageOut
from app.schemas.violation import ViolationOut

router = APIRouter()

@router.get("/job/{job_id}", response_model=list[PageOut])
async def list_pages_for_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditPage).where(AuditPage.job_id == job_id))
    return list(result.scalars().all())

@router.get("/{page_id}/violations", response_model=list[ViolationOut])
async def get_violations(page_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Violation).where(Violation.page_id == page_id))
    return list(result.scalars().all())
