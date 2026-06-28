from difflib import SequenceMatcher

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
    email_text = _normalize(f"{email.subject}\n{email.body}")

    company_score = _best_similarity(job_ad.company, [email.extracted_company, email_text])
    title_score = _best_similarity(job_ad.title, [email.extracted_role_title, email_text])

    if company_score >= 0.9:
        score += 40
    elif company_score >= 0.65:
        score += 28

    if title_score >= 0.9:
        score += 30
    elif title_score >= 0.55:
        score += 22

    if job_ad.url and _normalize(job_ad.url) in email_text:
        score += 20
    if job_ad.location and _normalize(job_ad.location) in email_text:
        score += 10

    return score


def _best_similarity(expected: str | None, candidates: list[str | None]) -> float:
    if not expected:
        return 0.0
    normalized_expected = _normalize(expected)
    if not normalized_expected:
        return 0.0

    scores = [_similarity(normalized_expected, _normalize(candidate)) for candidate in candidates]
    return max(scores, default=0.0)


def _similarity(expected: str, candidate: str) -> float:
    if not candidate:
        return 0.0
    if expected in candidate or candidate in expected:
        return 1.0

    expected_tokens = set(expected.split())
    candidate_tokens = set(candidate.split())
    if not expected_tokens or not candidate_tokens:
        return 0.0

    token_coverage = len(expected_tokens.intersection(candidate_tokens)) / len(expected_tokens)
    sequence_score = SequenceMatcher(None, expected, candidate).ratio()
    return max(token_coverage, sequence_score)


def _normalize(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.lower()
    for character in ",.;:()[]{}|/\\-_":
        normalized = normalized.replace(character, " ")
    ignored_tokens = {"gmbh", "inc", "llc", "ltd", "ag", "se", "the", "and", "und", "m", "w", "d"}
    return " ".join(token for token in normalized.split() if token not in ignored_tokens)


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


def confirm_match(db: Session, job_ad_id: int, email_id: int) -> Application:
    job_ad = job_ad_repository.get_job_ad(db, job_ad_id)
    email = email_repository.get_email(db, email_id)
    status = application_status_from_email(email.email_status)

    application = application_repository.get_application_by_job_ad_id(db, job_ad.id)
    if application is None:
        application = Application(
            job_ad_id=job_ad.id,
            status=status,
            company=job_ad.company or email.extracted_company,
            role_title=job_ad.title or email.extracted_role_title,
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
            notes="Manually confirmed match.",
        ),
    )
    job_ad.status = job_status_from_email(email.email_status)
    email.match_status = MatchStatus.SET
    db.commit()
    db.refresh(application)
    return application
