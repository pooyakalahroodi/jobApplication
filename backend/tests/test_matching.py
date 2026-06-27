from app.models.email import Email
from app.models.enums import EmailStatus
from app.models.job_ad import JobAd
from app.services.email_extraction_service import extract_email_facts, infer_email_status
from app.services.matching_service import score_job_email_match


def test_infer_email_status_pending() -> None:
    status = infer_email_status("Thanks for applying", "Your application was received.")

    assert status == EmailStatus.PENDING


def test_score_job_email_match() -> None:
    job_ad = JobAd(title="Backend Engineer", company="Acme", location="Berlin")
    email = Email(
        subject="Thanks for applying to Backend Engineer at Acme",
        sender="careers@acme.test",
        body="We received your application for Backend Engineer in Berlin.",
    )

    assert score_job_email_match(job_ad, email) >= 70


def test_extract_email_facts() -> None:
    extraction = extract_email_facts(
        "Thanks for applying to Backend Engineer at Acme",
        "We received your application for Backend Engineer at Acme.",
    )

    assert extraction.email_status == EmailStatus.PENDING
    assert extraction.company == "Acme"
    assert extraction.role_title == "Backend Engineer"
    assert extraction.confidence == 1.0


def test_extract_german_pending_email_facts() -> None:
    extraction = extract_email_facts(
        "Ihre Bewerbung als Softwareentwickler Java (m/w/d) - Remote",
        (
            "Vielen Dank für Ihre Bewerbung als Softwareentwickler Java (m/w/d) - Remote "
            "bei Academic Work Germany GmbH Hamburg. Wir haben Ihre Unterlagen erhalten "
            "und prüfen diese nun."
        ),
    )

    assert extraction.email_status == EmailStatus.PENDING
    assert extraction.company == "Academic Work Germany GmbH Hamburg"
    assert extraction.role_title == "Softwareentwickler Java (m/w/d) - Remote"
    assert extraction.confidence == 1.0


def test_infer_german_rejection_status() -> None:
    status = infer_email_status(
        "Ihre Bewerbung bei Academic Work",
        "Leider können wir Sie für diese Position nicht weiter berücksichtigen.",
    )

    assert status == EmailStatus.REJECTED
