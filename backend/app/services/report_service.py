from jinja2 import Template
from datetime import datetime

REPORT_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Accessibility Audit Report - {{ job.site_name or job.url }}</title>
<style>
  body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
  h1 { color: #1a56db; border-bottom: 2px solid #1a56db; padding-bottom: 10px; }
  .score { font-size: 48px; font-weight: bold; color: {{ '#16a34a' if job.compliance_score and job.compliance_score > 70 else '#dc2626' }}; }
  table { width: 100%; border-collapse: collapse; margin-top: 20px; }
  th { background: #1a56db; color: white; padding: 10px; text-align: left; }
  td { padding: 8px 10px; border-bottom: 1px solid #e5e7eb; }
  .critical { background: #fee2e2; }
  .serious { background: #fef3c7; }
</style>
</head>
<body>
<h1>GIGW 3.0 / WCAG 2.1 AA Accessibility Audit Report</h1>
<p><strong>Site:</strong> {{ job.site_name or job.url }}</p>
<p><strong>URL:</strong> {{ job.url }}</p>
<p><strong>Date:</strong> {{ report_date }}</p>
<p><strong>Pages Crawled:</strong> {{ job.pages_crawled }}</p>

<h2>Compliance Score</h2>
<div class="score">{{ job.compliance_score or 'N/A' }}%</div>

<h2>Summary</h2>
<table>
<tr><th>Metric</th><th>Count</th></tr>
<tr><td>Total Violations</td><td>{{ job.total_violations }}</td></tr>
<tr><td>Critical Violations</td><td>{{ job.critical_violations }}</td></tr>
<tr><td>Pages Audited</td><td>{{ job.pages_crawled }}</td></tr>
</table>

{% for page in pages %}
<h2 style="margin-top:30px;">{{ page.url }}</h2>
<p>Score: {{ page.compliance_score }}% | Violations: {{ page.violation_count }}</p>
{% if page.violations %}
<table>
<tr><th>WCAG</th><th>Level</th><th>Severity</th><th>Description</th><th>Fix</th></tr>
{% for v in page.violations %}
<tr class="{{ v.severity }}">
  <td>{{ v.wcag_criterion }}</td>
  <td>{{ v.wcag_level }}</td>
  <td>{{ v.severity }}</td>
  <td>{{ v.description }}</td>
  <td>{{ v.fix_suggestion }}</td>
</tr>
{% endfor %}
</table>
{% endif %}
{% endfor %}
</body>
</html>
"""

def generate_html_report(job, pages: list) -> str:
    template = Template(REPORT_HTML_TEMPLATE)
    return template.render(job=job, pages=pages, report_date=datetime.now().strftime("%d %B %Y"))

def generate_pdf_report(job, pages: list) -> bytes:
    try:
        from weasyprint import HTML
        html_content = generate_html_report(job, pages)
        return HTML(string=html_content).write_pdf()
    except Exception:
        html_content = generate_html_report(job, pages)
        return html_content.encode("utf-8")
