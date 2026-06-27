from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.application_event import ApplicationEvent
from app.models.email import Email
from app.models.enums import ApplicationStatus, EmailStatus, JobAdStatus, MatchStatus
from app.models.job_ad import JobAd


def score_job_email_match(job_ad: JobAd, email: Email) -> int:
    score = 0
    email_text = f"{email.subject}\n{email.body}".lower()

    if job_ad.company and job_ad.company.lower() in email_text:
        score += 40
    if job_ad.title and job_ad.title.lower() in email_text:
        score += 30
    if job_ad.url and job_ad.url.lower() in email_text:
        score += 20
    if job_ad.location and job_ad.location.lower() in email_text:
        score += 10

    return score


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


def run_matching(db: Session) -> int:
    emails = db.scalars(
        select(Email).where(
            Email.match_status == MatchStatus.NOT_SET,
            Email.email_status.in_([EmailStatus.PENDING, EmailStatus.REJECTED, EmailStatus.ACCEPTED]),
        )
    ).all()
    job_ads = db.scalars(
        select(JobAd).where(JobAd.status.in_([JobAdStatus.NOT_APPLIED, JobAdStatus.APPLIED]))
    ).all()

    matched_count = 0
    for email in emails:
        best_job = None
        best_score = 0
        for job_ad in job_ads:
            score = score_job_email_match(job_ad, email)
            if score > best_score:
                best_score = score
                best_job = job_ad

        if best_job is None:
            continue

        if best_score >= 70:
            status = application_status_from_email(email.email_status)
            application = Application(
                job_ad_id=best_job.id,
                status=status,
                company=best_job.company,
                role_title=best_job.title,
            )
            db.add(application)
            db.flush()

            db.add(
                ApplicationEvent(
                    application_id=application.id,
                    email_id=email.id,
                    event_type=email.email_status.value,
                    event_date=email.received_at,
                    notes=f"Auto-matched with score {best_score}.",
                )
            )
            best_job.status = job_status_from_email(email.email_status)
            email.match_status = MatchStatus.SET
            matched_count += 1
        elif best_score >= 40:
            email.match_status = MatchStatus.NEEDS_REVIEW

    db.commit()
    return matched_count

