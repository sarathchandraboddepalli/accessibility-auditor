# Accessibility Auditor — CHANGES

## What Was Built

**Government Website Accessibility Compliance Auditor (GIGW 3.0 / WCAG 2.1 AA)**

A production-ready MVP that crawls government websites, detects WCAG 2.1 accessibility violations, scores compliance, and generates downloadable HTML/PDF audit reports. Designed for auditing Indian government websites against GIGW 3.0 guidelines.

---

## Architecture

```
accessibility-auditor/
├── backend/          FastAPI + SQLAlchemy async + Celery
│   ├── app/
│   │   ├── models/   AuditJob, AuditPage, Violation (PostgreSQL)
│   │   ├── schemas/  Pydantic v2 response models
│   │   ├── services/ audit_engine, crawler_service, report_service
│   │   ├── tasks/    Celery crawl task (multi-page)
│   │   └── api/v1/   jobs, pages, reports routers
│   ├── alembic/      DB migrations
│   └── tests/        pytest suite (10 tests, all passing)
└── frontend/         Next.js 14 + Tailwind CSS
    └── src/app/
        ├── dashboard/  Summary metrics + recent audits
        ├── jobs/       Start audits + job list
        ├── jobs/[id]/  Per-job detail + per-page violations
        └── reports/    HTML/PDF report downloads
```

---

## API Endpoints

### Jobs
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/jobs/` | Create and start a new audit job |
| GET | `/api/v1/jobs/` | List all audit jobs (latest 50) |
| GET | `/api/v1/jobs/{job_id}` | Get job status and summary |

### Pages
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/pages/job/{job_id}` | List all pages crawled for a job |
| GET | `/api/v1/pages/{page_id}/violations` | Get all violations for a page |

### Reports
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/reports/{job_id}/html` | Download HTML audit report |
| GET | `/api/v1/reports/{job_id}/pdf` | Download PDF audit report |

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |

---

## WCAG Rules Implemented

| WCAG Criterion | Level | Severity | Check |
|----------------|-------|----------|-------|
| 1.1.1 | A | Critical | Images without alt attribute |
| 1.3.1 | A | Serious | Form inputs without labels or aria-label |
| 1.3.5 | AA | Moderate | Personal inputs missing autocomplete |
| 2.4.2 | A | Serious | Missing page title |
| 2.4.4 | A | Serious | Vague link text (click here, read more, etc.) |
| 3.1.1 | A | Serious | HTML element missing lang attribute |
| 4.1.2 | A | Critical | Buttons without accessible names |

---

## Key Files

| File | Purpose |
|------|---------|
| `backend/app/services/audit_engine.py` | Core WCAG rule checker — parses HTML with BeautifulSoup |
| `backend/app/services/crawler_service.py` | HTTP fetcher + link extractor for multi-page crawls |
| `backend/app/services/report_service.py` | Jinja2 HTML template + WeasyPrint PDF generation |
| `backend/app/api/v1/jobs.py` | Job CRUD + FastAPI BackgroundTasks for quick single-page audit |
| `backend/app/tasks/crawl_tasks.py` | Celery task for full multi-page crawl (uses asyncio.run) |
| `backend/alembic/versions/001_initial.py` | DB schema migration for all 3 tables |
| `frontend/src/app/jobs/[id]/page.tsx` | Per-job detail page with per-page violation drilldown |
| `frontend/src/lib/api.ts` | Type-safe API client wrapping fetch |

---

## How to Run with Docker

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start all services (API, Worker, Frontend, PostgreSQL, Redis)
docker-compose up --build

# 3. Run database migrations
docker-compose exec api alembic upgrade head

# Services:
# API:      http://localhost:8001
# Docs:     http://localhost:8001/docs
# Frontend: http://localhost:3001
```

---

## How to Run Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio anyio httpx aiosqlite \
  "beautifulsoup4==4.12.3" "lxml==5.3.0" "jinja2==3.1.4" \
  "fastapi==0.115.0" "pydantic==2.9.2" "pydantic-settings==2.6.1" \
  "sqlalchemy[asyncio]==2.0.36" "aiosqlite==0.20.0" "httpx==0.27.2"

# Run tests
python -m pytest tests/ -v
```

**Test Results: 10/10 pass**
- 7 unit tests for audit_engine (WCAG rule detection)
- 3 integration tests for the Jobs API (uses in-memory SQLite)

---

## Next Steps for an AI Agent

1. **Expand WCAG coverage**: Add checks for 1.4.3 (color contrast ratio via CSS analysis), 2.1.1 (keyboard navigation), 2.4.1 (skip links), and 3.3.1/3.3.2 (error identification in forms).

2. **Enable Playwright scanning**: Replace httpx with Playwright for JS-rendered pages (SPAs, React/Angular government portals). The Dockerfile already installs Chromium.

3. **Add scheduled audits**: Implement cron-based recurring audits per site with violation trend tracking over time. Add a `scheduled_jobs` table.

4. **Improve PDF reports**: Integrate WeasyPrint fully with fonts and logo. Add WCAG 2.2 criterion mapping table as an appendix.

5. **Authentication**: Add JWT-based auth so only authorized users (government auditors) can access the system. Add an `organizations` table.

6. **Bulk import**: Accept a CSV of URLs (NIC/GIGW website list) to batch-queue audit jobs.

7. **Fix Pydantic deprecation**: Migrate `class Config` to `model_config = ConfigDict(...)` in `Settings`.

8. **Add pytest-asyncio config**: Add `asyncio_mode = "auto"` to `pytest.ini` or `pyproject.toml` to clear the deprecation warning.

9. **Frontend polling**: Add auto-refresh on the jobs list page so status updates from `running` to `completed` appear without manual reload.

10. **Celery integration test**: Write a test that exercises the full `run_audit_job` Celery task using `celery_app.conf.task_always_eager = True`.
