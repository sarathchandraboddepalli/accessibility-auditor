# GIGW Accessibility Auditor

A WCAG 2.1 AA / GIGW 3.0 compliance scanner built for Indian government websites. Submit any URL and get a scored accessibility audit with per-violation fix guidance and an exportable PDF report — all processed asynchronously via a background job queue.

## Why This Exists

Government of India guidelines (GIGW 3.0) mandate WCAG 2.1 AA compliance for all central and state government websites. Manual audits are slow, inconsistent, and expensive. This tool automates the crawl-and-audit pipeline, generates actionable reports, and produces a compliance score that can be tracked over time.

## Architecture

```
Browser / CLI
     |
     v
 Next.js Frontend (port 3001)
     |
     v
 FastAPI (port 8001)
     |          \
     v           v
 PostgreSQL    Redis
               |
               v
          Celery Worker
               |
               v
       Audit Engine (BeautifulSoup)
               |
               v
       WeasyPrint PDF Generator
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI 0.115, Python 3.12 |
| Task Queue | Celery 5.4 + Redis 7 |
| Database | PostgreSQL 16 + SQLAlchemy (async) + Alembic |
| Crawler | httpx (async), BeautifulSoup4, lxml |
| Report Generation | WeasyPrint 62, Jinja2 |
| Frontend | Next.js 14, Tailwind CSS |
| Containerisation | Docker + Docker Compose |

## WCAG Rules Checked

| Criterion | Level | Description |
|-----------|-------|-------------|
| 1.1.1 | A | Images must have alt text |
| 1.3.1 | A | Form inputs must have associated labels |
| 1.3.5 | AA | Personal input fields must declare autocomplete |
| 1.4.3 | AA | Text contrast (flagged for manual review) |
| 2.4.2 | A | Pages must have a descriptive title element |
| 2.4.4 | A | Link text must be descriptive (no "click here") |
| 3.1.1 | A | HTML element must declare a lang attribute |
| 4.1.2 | A | Buttons must have an accessible name |

Violations are weighted by severity (critical: 10pts, serious: 5pts, moderate: 2pts) to produce a 0–100 compliance score.

## Features

- **Async crawl pipeline** — submit a URL and the audit runs in the background; poll for results
- **SSRF protection** — crawler refuses to fetch private RFC-1918 address ranges
- **Per-violation fix guidance** — each finding includes a concrete fix suggestion and a WCAG understanding link
- **HTML + PDF reports** — download audits as a formatted GIGW-branded PDF
- **Compliance score** — single weighted score per page and per audit job
- **GIGW user-agent** — crawls self-identify as a compliance scanner (`GIGW-Accessibility-Auditor/1.0`)

## Quick Start

```bash
git clone https://github.com/sarathchandraboddepalli/accessibility-auditor
cd accessibility-auditor
cp .env.example .env          # edit SECRET_KEY and DATABASE_URL
docker-compose up --build
```

Run migrations on first boot:

```bash
docker-compose exec api alembic upgrade head
```

- **Frontend:** http://localhost:3001
- **API:** http://localhost:8001
- **Swagger docs:** http://localhost:8001/docs

## API Reference

```
POST /api/v1/jobs/              # Submit a new audit job
GET  /api/v1/jobs/              # List all jobs
GET  /api/v1/jobs/{id}          # Get job status and results
GET  /api/v1/reports/{id}       # Download HTML report
GET  /api/v1/reports/{id}/pdf   # Download PDF report
GET  /api/v1/pages/{job_id}     # Per-page violation breakdown
```

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio anyio httpx aiosqlite fastapi pydantic pydantic-settings "sqlalchemy[asyncio]" beautifulsoup4 lxml
python -m pytest tests/ -v
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string (default: `redis://redis:6379/0`) |
| `SECRET_KEY` | App secret for signing |
| `MAX_PAGES_PER_JOB` | Max pages crawled per audit job (default: 50) |
