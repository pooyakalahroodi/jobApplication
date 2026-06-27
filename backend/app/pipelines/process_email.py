from app.models.enums import EmailStatus
from app.services.email_extraction_service import infer_email_status


def process_email_text(subject: str, body: str) -> EmailStatus:
    return infer_email_status(subject, body)

