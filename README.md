# GIGW Accessibility Auditor

A production-ready government website accessibility compliance scanner built for the **GIGW 3.0** and **WCAG 2.1 AA** standards. Crawls websites, detects accessibility violations, scores compliance, and generates downloadable HTML/PDF audit reports.

---

## Features

- **Automated WCAG 2.1 Checks**: Detects 7 common violation types (missing alt text, unlabeled forms, vague link text, missing page titles, missing language declarations, buttons without names, missing autocomplete)
- **Compliance Scoring**: Weighted scoring system — critical violations penalize more heavily than minor ones
- **Multi-Page Crawling**: Follows internal links up to a configurable page limit
- **Report Generation**: Download audit results as HTML or PDF for government compliance records
- **Real-Time Status**: Track jobs from `pending` → `running` → `completed`/`failed`
- **REST API**: Fully documented FastAPI backend with OpenAPI/Swagger UI at `/docs`
- **React Dashboard**: Next.js 14 frontend with Tailwind CSS

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Next.js Frontend (port 3001)                        │
│  Dashboard / Jobs / Job Detail / Reports             │
└──────────────────┬───────────────────────────────────┘
                   │ REST API calls
┌──────────────────▼───────────────────────────────────┐
│  FastAPI Backend (port 8001)                         │
│  /api/v1/jobs  /api/v1/pages  /api/v1/reports        │
│  BackgroundTasks (single-page) / Celery (multi-page) │
└──────────┬──────────────────────┬────────────────────┘
           │                      │
┌──────────▼──────┐    ┌──────────▼──────┐
│  PostgreSQL     │    │  Redis          │
│  (audit data)   │    │  (Celery broker)│
└─────────────────┘    └─────────────────┘
```

**Tech Stack:**
- Backend: FastAPI 0.115, SQLAlchemy 2.0 async, Alembic, Celery 5, httpx, BeautifulSoup4, Jinja2, WeasyPrint
- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS
- Infrastructure: PostgreSQL 16, Redis 7, Docker Compose

---

## Quick Start (Docker)

```bash
# Clone / navigate to project
cd D:\extra\projects\accessibility-auditor

# Copy environment config
cp .env.example .env

# Build and start all services
docker-compose up --build

# In another terminal, run database migrations
docker-compose exec api alembic upgrade head
```

**Access:**
| Service | URL |
|---------|-----|
| Frontend | http://localhost:3001 |
| API | http://localhost:8001 |
| API Docs (Swagger) | http://localhost:8001/docs |
| PostgreSQL | localhost:5433 |
| Redis | localhost:6380 |

---

## Local Development (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set environment (point to local Postgres/Redis or use SQLite for dev)
export DATABASE_URL=postgresql+asyncpg://auditor:changeme@localhost:5433/accessibility_auditor
export REDIS_URL=redis://localhost:6380/0

# Run migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload --port 8000

# Start Celery worker (optional - for multi-page crawls)
celery -A app.worker celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set API URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

Frontend runs on http://localhost:3000.

---

## Running Tests

```bash
cd backend

# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio anyio httpx aiosqlite \
  "beautifulsoup4==4.12.3" "lxml==5.3.0" "jinja2==3.1.4" \
  "fastapi==0.115.0" "pydantic==2.9.2" "pydantic-settings==2.6.1" \
  "sqlalchemy[asyncio]==2.0.36" "aiosqlite==0.20.0" "httpx==0.27.2"

# Run all tests
python -m pytest tests/ -v
```

**Expected output:** 10 tests passing in < 1 second.

Tests use an in-memory SQLite database — no PostgreSQL required for testing.

---

## API Reference

### Start an Audit Job

```bash
curl -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://ap.gov.in",
    "site_name": "Andhra Pradesh Government Portal",
    "max_pages": 10
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://ap.gov.in",
  "site_name": "Andhra Pradesh Government Portal",
  "status": "pending",
  "max_pages": 10,
  "pages_crawled": 0,
  "total_violations": 0,
  "critical_violations": 0,
  "compliance_score": null,
  "error_message": null,
  "created_at": "2026-07-31T10:00:00Z"
}
```

### Check Job Status

```bash
curl http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000
```

### List Pages and Violations

```bash
# Get all pages for a job
curl http://localhost:8000/api/v1/pages/job/{job_id}

# Get violations for a specific page
curl http://localhost:8000/api/v1/pages/{page_id}/violations
```

### Download Reports

```bash
# HTML report (view in browser)
open http://localhost:8000/api/v1/reports/{job_id}/html

# PDF report (download)
curl -o report.pdf http://localhost:8000/api/v1/reports/{job_id}/pdf
```

---

## WCAG Rules Checked

| WCAG | Level | Severity | What is Checked |
|------|-------|----------|-----------------|
| 1.1.1 | A | Critical | `<img>` tags missing `alt` attribute |
| 1.3.1 | A | Serious | `<input>`, `<select>`, `<textarea>` without labels |
| 1.3.5 | AA | Moderate | Personal data inputs missing `autocomplete` |
| 2.4.2 | A | Serious | `<title>` element missing or empty |
| 2.4.4 | A | Serious | Links with vague text ("click here", "read more", etc.) |
| 3.1.1 | A | Serious | `<html>` element missing `lang` attribute |
| 4.1.2 | A | Critical | `<button>` elements without text or `aria-label` |

---

## Compliance Scoring

Scores are calculated from 100, with penalties per violation:

| Severity | Penalty |
|----------|---------|
| Critical | -10 points |
| Serious | -5 points |
| Moderate | -2 points |
| Minor | -1 point |

Score range: 0–100. Minimum clamped at 0.

---

## Data Model

```
AuditJob
  ├── id (UUID)
  ├── url, site_name, status, max_pages
  ├── pages_crawled, total_violations, critical_violations
  ├── compliance_score, error_message
  └── AuditPage[]
        ├── id, job_id, url, title
        ├── violation_count, critical_count, warning_count
        ├── compliance_score
        └── Violation[]
              ├── id, page_id
              ├── wcag_criterion, wcag_level, severity
              ├── description, element, fix_suggestion, help_url
```

---

## Project Structure

```
accessibility-auditor/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py              # Pydantic settings
│   │   ├── database.py            # Async SQLAlchemy engine + session
│   │   ├── main.py                # FastAPI app + CORS
│   │   ├── worker.py              # Celery app
│   │   ├── models/
│   │   │   ├── audit_job.py
│   │   │   ├── page.py
│   │   │   └── violation.py
│   │   ├── schemas/
│   │   │   ├── audit_job.py
│   │   │   ├── page.py
│   │   │   └── violation.py
│   │   ├── services/
│   │   │   ├── audit_engine.py    # WCAG rule checker
│   │   │   ├── crawler_service.py # httpx fetcher + link extractor
│   │   │   └── report_service.py  # HTML/PDF report generator
│   │   ├── tasks/
│   │   │   └── crawl_tasks.py     # Celery multi-page crawl task
│   │   └── api/v1/
│   │       ├── router.py
│   │       ├── jobs.py
│   │       ├── pages.py
│   │       └── reports.py
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/001_initial.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_audit_engine.py
│   │   └── test_jobs_api.py
│   ├── alembic.ini
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx           # Redirects to /dashboard
│   │   │   ├── globals.css
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── jobs/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/page.tsx
│   │   │   └── reports/page.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   └── types/index.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   ├── postcss.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── CHANGES.md
└── README.md
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://auditor:changeme@db:5432/accessibility_auditor` | Async PostgreSQL URL |
| `REDIS_URL` | `redis://redis:6379/0` | Redis URL for Celery |
| `SECRET_KEY` | `dev-secret-key` | App secret (change in production) |
| `MAX_PAGES_PER_JOB` | `50` | Maximum pages to crawl per job |
| `DB_PASSWORD` | `changeme` | PostgreSQL password (used in docker-compose) |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Frontend → backend API URL |

---

## License

MIT — for government and public sector use without restriction.
