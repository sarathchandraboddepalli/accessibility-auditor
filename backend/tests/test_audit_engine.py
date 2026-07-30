from app.services.audit_engine import audit_html, calculate_compliance_score

def test_detects_missing_title():
    html = "<html><head></head><body><p>Hello</p></body></html>"
    violations = audit_html(html)
    criteria = [v.wcag_criterion for v in violations]
    assert "2.4.2" in criteria

def test_detects_missing_lang():
    html = "<html><head><title>Test</title></head><body></body></html>"
    violations = audit_html(html)
    criteria = [v.wcag_criterion for v in violations]
    assert "3.1.1" in criteria

def test_detects_images_without_alt():
    html = '<html lang="en"><head><title>Test</title></head><body><img src="photo.jpg"></body></html>'
    violations = audit_html(html)
    criteria = [v.wcag_criterion for v in violations]
    assert "1.1.1" in criteria

def test_compliant_page_has_no_basic_violations():
    html = """<html lang="en">
    <head><title>Good Page</title></head>
    <body>
      <img src="photo.jpg" alt="A beautiful landscape">
      <a href="/contact">Contact Us</a>
    </body>
    </html>"""
    violations = audit_html(html)
    criteria = [v.wcag_criterion for v in violations]
    assert "2.4.2" not in criteria
    assert "3.1.1" not in criteria
    assert "1.1.1" not in criteria

def test_detects_vague_link_text():
    html = '<html lang="en"><head><title>Test</title></head><body><a href="/more">click here</a></body></html>'
    violations = audit_html(html)
    criteria = [v.wcag_criterion for v in violations]
    assert "2.4.4" in criteria

def test_compliance_score_perfect():
    score = calculate_compliance_score([])
    assert score == 100.0

def test_compliance_score_with_critical():
    violations = audit_html('<html><head></head><body><img src="x.jpg"></body></html>')
    score = calculate_compliance_score(violations)
    assert score < 100.0
