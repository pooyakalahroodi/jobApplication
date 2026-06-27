def test_manual_email_import_and_matching_flow(client) -> None:
    job_response = client.post(
        "/job-ads/capture",
        json={
            "url": "https://acme.test/jobs/backend-engineer",
            "title": "Backend Engineer",
            "company": "Acme",
            "location": "Berlin",
            "source": "browser_extension",
            "raw_text": "Backend Engineer at Acme in Berlin.",
        },
    )
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "not_applied"

    email_response = client.post(
        "/emails/import",
        json={
            "subject": "Thanks for applying to Backend Engineer at Acme",
            "sender": "careers@acme.test",
            "body": "We received your application for Backend Engineer at Acme.",
        },
    )
    assert email_response.status_code == 200
    email_data = email_response.json()
    assert email_data["email_status"] == "pending"
    assert email_data["match_status"] == "not_set"
    assert email_data["extracted_company"] == "Acme"
    assert email_data["extracted_role_title"] == "Backend Engineer"

    matching_response = client.post("/matching/run")
    assert matching_response.status_code == 200
    assert matching_response.json() == {
        "processed_count": 1,
        "matched_count": 1,
        "needs_review_count": 0,
        "unmatched_count": 0,
    }

    applications_response = client.get("/applications")
    assert applications_response.status_code == 200
    applications = applications_response.json()
    assert len(applications) == 1
    assert applications[0]["company"] == "Acme"
    assert applications[0]["role_title"] == "Backend Engineer"
    assert applications[0]["status"] == "pending"

    emails_response = client.get("/emails")
    assert emails_response.status_code == 200
    assert emails_response.json()[0]["match_status"] == "set"

    jobs_response = client.get("/job-ads")
    assert jobs_response.status_code == 200
    assert jobs_response.json()[0]["status"] == "applied"


def test_german_email_import_and_matching_flow(client) -> None:
    job_response = client.post(
        "/job-ads/capture",
        json={
            "url": "https://www.stepstone.de/stellenangebote--Softwareentwickler-Java.html",
            "title": "Softwareentwickler Java (m/w/d) - Remote",
            "company": "Academic Work Germany GmbH Hamburg",
            "location": "bundesweit, Home-Office",
            "source": "browser_extension",
            "raw_text": "Softwareentwickler Java (m/w/d) - Remote bei Academic Work Germany GmbH Hamburg.",
        },
    )
    assert job_response.status_code == 200

    email_response = client.post(
        "/emails/import",
        json={
            "subject": "Ihre Bewerbung als Softwareentwickler Java (m/w/d) - Remote",
            "sender": "info@academicwork.de",
            "body": (
                "Vielen Dank für Ihre Bewerbung als Softwareentwickler Java (m/w/d) - Remote "
                "bei Academic Work Germany GmbH Hamburg. Wir haben Ihre Unterlagen erhalten "
                "und prüfen diese nun."
            ),
        },
    )
    assert email_response.status_code == 200
    assert email_response.json()["email_status"] == "pending"
    assert email_response.json()["extracted_company"] == "Academic Work Germany GmbH Hamburg"
    assert email_response.json()["extracted_role_title"] == "Softwareentwickler Java (m/w/d) - Remote"

    matching_response = client.post("/matching/run")

    assert matching_response.status_code == 200
    assert matching_response.json()["matched_count"] == 1
