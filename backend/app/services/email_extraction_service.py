import re
from dataclasses import dataclass

from app.models.enums import EmailStatus


@dataclass(frozen=True)
class EmailExtraction:
    email_status: EmailStatus
    company: str | None = None
    role_title: str | None = None
    confidence: float = 0.0


def infer_email_status(subject: str, body: str) -> EmailStatus:
    text = f"{subject}\n{body}".lower()

    rejected_terms = [
        "unfortunately",
        "not moving forward",
        "decided not to proceed",
        "rejection",
        "leider",
        "absage",
        "nicht berücksichtigen",
        "nicht weiter berücksichtigen",
        "nicht in die engere auswahl",
    ]
    accepted_terms = [
        "offer",
        "congratulations",
        "pleased to offer",
        "angebot",
        "vertragsangebot",
        "wir freuen uns, ihnen ein angebot",
        "wir möchten ihnen ein angebot",
    ]
    pending_terms = [
        "thanks for applying",
        "thank you for applying",
        "application received",
        "interview",
        "next step",
        "assessment",
        "vielen dank für ihre bewerbung",
        "vielen dank fuer ihre bewerbung",
        "bewerbung erhalten",
        "unterlagen erhalten",
        "eingang ihrer bewerbung",
        "prüfen diese",
        "pruefen diese",
        "vorstellungsgespräch",
        "vorstellungsgespraech",
        "kennenlerngespräch",
        "kennenlerngespraech",
        "nächster schritt",
        "naechster schritt",
    ]

    if any(term in text for term in rejected_terms):
        return EmailStatus.REJECTED
    if any(term in text for term in accepted_terms):
        return EmailStatus.ACCEPTED
    if any(term in text for term in pending_terms):
        return EmailStatus.PENDING
    return EmailStatus.UNKNOWN


def extract_email_facts(subject: str, body: str) -> EmailExtraction:
    text = f"{subject}\n{body}"
    status = infer_email_status(subject, body)
    role_title = _extract_role_title(text)
    company = _extract_company(text)

    confidence = 0.25
    if status != EmailStatus.UNKNOWN:
        confidence += 0.25
    if company:
        confidence += 0.25
    if role_title:
        confidence += 0.25

    return EmailExtraction(
        email_status=status,
        company=company,
        role_title=role_title,
        confidence=round(confidence, 2),
    )


def _extract_role_title(text: str) -> str | None:
    patterns = [
        r"applying (?:to|for)\s+(?P<role>.+?)\s+at\s+",
        r"application (?:to|for)\s+(?P<role>.+?)\s+at\s+",
        r"received your application (?:to|for)\s+(?P<role>.+?)\s+(?:at|with)\s+",
        r"your application for\s+(?P<role>.+?)(?:\.|,|\n|$)",
        r"bewerbung\s+(?:als|auf die stelle|für|fuer)\s+(?P<role>.+?)\s+(?:bei|an)\s+",
        r"ihre bewerbung\s+(?:als|auf die stelle|für|fuer)\s+(?P<role>.+?)\s+(?:bei|an)\s+",
        r"bewerbung\s+(?:als|auf die stelle|für|fuer)\s+(?P<role>.+?)(?:\.|,|\n|$)",
    ]
    return _first_group_match(patterns, text, "role")


def _extract_company(text: str) -> str | None:
    patterns = [
        r"\s+at\s+(?P<company>[A-Z][A-Za-z0-9&.,\- ]{1,80}?)(?=\.|,|\n|$)",
        r"\s+with\s+(?P<company>[A-Z][A-Za-z0-9&.,\- ]{1,80}?)(?=\.|,|\n|$)",
        r"from\s+(?P<company>[A-Z][A-Za-z0-9&.,\- ]{1,80}?)(?=\.|,|\n|$)",
        r"\s+bei\s+(?P<company>[A-ZÄÖÜ][A-Za-zÄÖÜäöüß0-9&.,\- ]{1,100}?)(?=\.|,|\n|$)",
        r"\s+von\s+(?P<company>[A-ZÄÖÜ][A-Za-zÄÖÜäöüß0-9&.,\- ]{1,100}?)(?=\.|,|\n|$)",
    ]
    return _first_group_match(patterns, text, "company")


def _first_group_match(patterns: list[str], text: str, group_name: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = match.group(group_name).strip(" .,-\n\t")
            return value if value else None
    return None
