from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List

@dataclass
class AccessibilityViolation:
    wcag_criterion: str
    wcag_level: str
    severity: str
    description: str
    element: str | None
    fix_suggestion: str
    help_url: str | None = None

WCAG_RULES = {
    "1.1.1": {
        "description": "Non-text Content: Images must have alternative text",
        "level": "A",
        "severity": "critical",
    },
    "1.3.1": {
        "description": "Info and Relationships: Form inputs must have labels",
        "level": "A",
        "severity": "serious",
    },
    "2.4.2": {
        "description": "Page Titled: Page must have a title element",
        "level": "A",
        "severity": "serious",
    },
    "3.1.1": {
        "description": "Language of Page: HTML must have a lang attribute",
        "level": "A",
        "severity": "serious",
    },
    "1.4.3": {
        "description": "Contrast: Low contrast text may be present",
        "level": "AA",
        "severity": "serious",
    },
    "2.4.4": {
        "description": "Link Purpose: Links must have descriptive text",
        "level": "A",
        "severity": "serious",
    },
    "4.1.2": {
        "description": "Name, Role, Value: Interactive elements must have accessible names",
        "level": "A",
        "severity": "critical",
    },
    "1.3.5": {
        "description": "Identify Input Purpose: Form fields should have autocomplete attributes",
        "level": "AA",
        "severity": "moderate",
    },
}

def audit_html(html_content: str, url: str = "") -> List[AccessibilityViolation]:
    violations = []

    try:
        soup = BeautifulSoup(html_content, "lxml")
    except Exception:
        soup = BeautifulSoup(html_content, "html.parser")

    # 2.4.2: Page title
    if not soup.find("title") or not soup.find("title").get_text(strip=True):
        violations.append(AccessibilityViolation(
            wcag_criterion="2.4.2", wcag_level="A", severity="serious",
            description="Page is missing a title element",
            element="<title>",
            fix_suggestion="Add a descriptive <title> tag to the <head> element",
            help_url="https://www.w3.org/WAI/WCAG21/Understanding/page-titled.html",
        ))

    # 3.1.1: HTML lang attribute
    html_tag = soup.find("html")
    if html_tag and not html_tag.get("lang"):
        violations.append(AccessibilityViolation(
            wcag_criterion="3.1.1", wcag_level="A", severity="serious",
            description="HTML element is missing a lang attribute",
            element='<html>',
            fix_suggestion='Add lang="en" (or appropriate language code) to the <html> element',
            help_url="https://www.w3.org/WAI/WCAG21/Understanding/language-of-page.html",
        ))

    # 1.1.1: Images without alt text
    for img in soup.find_all("img"):
        if img.get("alt") is None:
            violations.append(AccessibilityViolation(
                wcag_criterion="1.1.1", wcag_level="A", severity="critical",
                description="Image is missing an alt attribute",
                element=str(img)[:200],
                fix_suggestion='Add alt="" for decorative images or alt="descriptive text" for meaningful images',
                help_url="https://www.w3.org/WAI/WCAG21/Understanding/non-text-content.html",
            ))

    # 1.3.1: Form inputs without labels
    for inp in soup.find_all(["input", "select", "textarea"]):
        input_type = inp.get("type", "text")
        if input_type in ("hidden", "submit", "button", "image", "reset"):
            continue
        input_id = inp.get("id")
        aria_label = inp.get("aria-label") or inp.get("aria-labelledby")
        has_label = False
        if input_id:
            has_label = bool(soup.find("label", attrs={"for": input_id}))
        if not has_label and not aria_label:
            violations.append(AccessibilityViolation(
                wcag_criterion="1.3.1", wcag_level="A", severity="serious",
                description=f"Form control ({inp.name}) is missing an associated label",
                element=str(inp)[:200],
                fix_suggestion="Add a <label for='id'> element or aria-label attribute",
                help_url="https://www.w3.org/WAI/WCAG21/Understanding/info-and-relationships.html",
            ))

    # 2.4.4: Links with vague text
    vague_link_texts = {"click here", "here", "read more", "more", "link", "this", "learn more", "click", "download"}
    for a in soup.find_all("a", href=True):
        link_text = a.get_text(strip=True).lower()
        aria_label = a.get("aria-label", "").strip()
        if link_text in vague_link_texts and not aria_label:
            violations.append(AccessibilityViolation(
                wcag_criterion="2.4.4", wcag_level="A", severity="serious",
                description=f'Link text "{a.get_text(strip=True)}" is not descriptive',
                element=str(a)[:200],
                fix_suggestion="Use descriptive link text that makes sense out of context",
                help_url="https://www.w3.org/WAI/WCAG21/Understanding/link-purpose-in-context.html",
            ))

    # 4.1.2: Buttons without accessible names
    for btn in soup.find_all("button"):
        btn_text = btn.get_text(strip=True)
        aria_label = btn.get("aria-label") or btn.get("aria-labelledby")
        if not btn_text and not aria_label:
            violations.append(AccessibilityViolation(
                wcag_criterion="4.1.2", wcag_level="A", severity="critical",
                description="Button has no accessible name",
                element=str(btn)[:200],
                fix_suggestion="Add text content or aria-label attribute to the button",
                help_url="https://www.w3.org/WAI/WCAG21/Understanding/name-role-value.html",
            ))

    # 1.3.5: Input autocomplete
    personal_input_types = {"email", "tel", "name", "username"}
    for inp in soup.find_all("input"):
        inp_type = inp.get("type", "text")
        inp_name = (inp.get("name") or "").lower()
        if inp_type in personal_input_types or any(k in inp_name for k in ["email", "phone", "name", "user"]):
            if not inp.get("autocomplete"):
                violations.append(AccessibilityViolation(
                    wcag_criterion="1.3.5", wcag_level="AA", severity="moderate",
                    description=f"Input field ({inp_name or inp_type}) is missing autocomplete attribute",
                    element=str(inp)[:200],
                    fix_suggestion='Add appropriate autocomplete attribute (e.g., autocomplete="email")',
                    help_url="https://www.w3.org/WAI/WCAG21/Understanding/identify-input-purpose.html",
                ))

    return violations

def calculate_compliance_score(violations: List[AccessibilityViolation]) -> float:
    if not violations:
        return 100.0
    severity_weights = {"critical": 10, "serious": 5, "moderate": 2, "minor": 1}
    penalty = sum(severity_weights.get(v.severity, 1) for v in violations)
    score = max(0.0, 100.0 - penalty)
    return round(score, 1)
