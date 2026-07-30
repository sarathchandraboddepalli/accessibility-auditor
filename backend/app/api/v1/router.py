from fastapi import APIRouter
from app.api.v1 import jobs, pages, reports

api_router = APIRouter()
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(pages.router, prefix="/pages", tags=["pages"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
