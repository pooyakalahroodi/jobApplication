from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.application_event import ApplicationEvent
from app.models.email import Email
from app.models.enums import ApplicationStatus, EmailStatus, JobAdStatus, MatchStatus
from app.models.job_ad import JobAd
from app.repositories import application_events as event_repository
from app.repositories import applications as application_repository
from app.repositories import emails as email_repository
from app.repositories import job_ads as job_ad_repository
from app.schemas.matching import MatchingRunResult


def score_job_email_match(job_ad: JobAd, email: Email) -> int:
    score = 0
    email_text = f"{email.subject}\n{email.body}".lower()

    if _matches_text_or_extraction(job_ad.company, email.extracted_company, email_text):
        score += 40
    if _matches_text_or_extraction(job_ad.title, email.extracted_role_title, email_text):
        score += 30
    if job_ad.url and job_ad.url.lower() in email_text:
        score += 20
    if job_ad.location and _normalize(job_ad.location) in email_text:
        score += 10

    return score


def _matches_text_or_extraction(expected: str | None, extracted: str | None, text: str) -> bool:
    if not expected:
        return False
    normalized_expected = _normalize(expected)
    if normalized_expected in text:
        return True
    return bool(extracted and normalized_expected == _normalize(extracted))


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace(",", " ").split())


def application_status_from_email(email_status: EmailStatus) -> ApplicationStatus:
    if email_status == EmailStatus.REJECTED:
        return ApplicationStatus.REJECTED
    if email_status == EmailStatus.ACCEPTED:
        return ApplicationStatus.ACCEPTED
    if email_status == EmailStatus.PENDING:
        return ApplicationStatus.PENDING
    return ApplicationStatus.UNKNOWN


def job_status_from_email(email_status: EmailStatus) -> JobAdStatus:
    if email_status == EmailStatus.REJECTED:
        return JobAdStatus.REJECTED
    if email_status == EmailStatus.ACCEPTED:
        return JobAdStatus.ACCEPTED
    return JobAdStatus.APPLIED


def run_matching(db: Session) -> MatchingRunResult:
    emails = email_repository.list_unmatched_actionable_emails(db)
    job_ads = job_ad_repository.list_matchable_job_ads(db)

    matched_count = 0
    needs_review_count = 0
    unmatched_count = 0
    for email in emails:
        best_job = None
        best_score = 0
        for job_ad in job_ads:
            score = score_job_email_match(job_ad, email)
            if score > best_score:
                best_score = score
                best_job = job_ad

        if best_job is None:
            unmatched_count += 1
            continue

        if best_score >= 70:
            status = application_status_from_email(email.email_status)
            application = application_repository.get_application_by_job_ad_id(db, best_job.id)
            if application is None:
                application = Application(
                    job_ad_id=best_job.id,
                    status=status,
                    company=best_job.company or email.extracted_company,
                    role_title=best_job.title or email.extracted_role_title,
                )
                application_repository.create_application(db, application)
            else:
                application.status = status

            event_repository.create_application_event(
                db,
                ApplicationEvent(
                    application_id=application.id,
                    email_id=email.id,
                    event_type=email.email_status.value,
                    event_date=email.received_at,
                    notes=f"Auto-matched with score {best_score}.",
                ),
            )
            best_job.status = job_status_from_email(email.email_status)
            email.match_status = MatchStatus.SET
            matched_count += 1
        elif best_score >= 40:
            email.match_status = MatchStatus.NEEDS_REVIEW
            needs_review_count += 1
        else:
            unmatched_count += 1

    db.commit()
    return MatchingRunResult(
        processed_count=len(emails),
        matched_count=matched_count,
        needs_review_count=needs_review_count,
        unmatched_count=unmatched_count,
    )
