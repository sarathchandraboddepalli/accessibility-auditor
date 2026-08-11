from app.worker import celery_app

@celery_app.task(name="tasks.run_audit_job")
def run_audit_job(job_id: str):
    import asyncio
    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.audit_job import AuditJob
    from app.models.page import AuditPage
    from app.models.violation import Violation
    from app.services.crawler_service import fetch_html, extract_links, get_page_title
    from app.services.audit_engine import audit_html, calculate_compliance_score
    from urllib.parse import urlparse
    from datetime import datetime, timezone
    import uuid

    async def _run():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(AuditJob).where(AuditJob.id == uuid.UUID(job_id)))
            job = result.scalar_one_or_none()
            if not job:
                return

            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            await db.commit()

            visited = set()
            to_visit = [job.url]
            domain = urlparse(job.url).netloc
            total_violations = 0
            critical_violations = 0
            page_scores = []

            try:
                while to_visit and len(visited) < job.max_pages:
                    url = to_visit.pop(0)
                    if url in visited:
                        continue
                    visited.add(url)

                    html = await fetch_html(url)
                    if not html:
                        continue

                    violations = audit_html(html, url)
                    score = calculate_compliance_score(violations)
                    title = get_page_title(html)

                    critical_v = [v for v in violations if v.severity == "critical"]
                    warning_v = [v for v in violations if v.severity in ("serious", "moderate", "minor")]

                    page = AuditPage(
                        job_id=job.id,
                        url=url,
                        title=title,
                        violation_count=len(violations),
                        critical_count=len(critical_v),
                        warning_count=len(warning_v),
                        compliance_score=score,
                    )
                    db.add(page)
                    await db.flush()

                    for v in violations:
                        violation = Violation(
                            page_id=page.id,
                            wcag_criterion=v.wcag_criterion,
                            wcag_level=v.wcag_level,
                            severity=v.severity,
                            description=v.description,
                            element=v.element,
                            fix_suggestion=v.fix_suggestion,
                            help_url=v.help_url,
                        )
                        db.add(violation)

                    total_violations += len(violations)
                    critical_violations += len(critical_v)
                    page_scores.append(score)

                    if len(visited) < job.max_pages:
                        links = extract_links(html, url, domain)
                        for link in links:
                            if link not in visited and link not in to_visit:
                                to_visit.append(link)

                job.pages_crawled = len(visited)
                job.total_violations = total_violations
                job.critical_violations = critical_violations
                job.compliance_score = (sum(page_scores) / len(page_scores)) if page_scores else None
                job.status = "completed"
                job.completed_at = datetime.now(timezone.utc)

            except Exception as e:
                job.status = "failed"
                job.error_message = str(e)[:500]

            await db.commit()

    asyncio.run(_run())
