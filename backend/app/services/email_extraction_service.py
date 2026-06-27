from app.models.enums import EmailStatus


def infer_email_status(subject: str, body: str) -> EmailStatus:
    text = f"{subject}\n{body}".lower()

    rejected_terms = ["unfortunately", "not moving forward", "decided not to proceed", "rejection"]
    accepted_terms = ["offer", "congratulations", "pleased to offer"]
    pending_terms = [
        "thanks for applying",
        "thank you for applying",
        "application received",
        "interview",
        "next step",
        "assessment",
    ]

    if any(term in text for term in rejected_terms):
        return EmailStatus.REJECTED
    if any(term in text for term in accepted_terms):
        return EmailStatus.ACCEPTED
    if any(term in text for term in pending_terms):
        return EmailStatus.PENDING
    return EmailStatus.UNKNOWN

