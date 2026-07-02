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


def test_matching_prefers_not_applied_captured_job_before_existing_application(client) -> None:
    first_job = client.post(
        "/job-ads/capture",
        json={
            "url": "https://acme.test/jobs/backend-engineer-first",
            "title": "Backend Engineer",
            "company": "Acme",
            "location": "Berlin",
            "source": "browser_extension",
            "raw_text": "Backend Engineer at Acme in Berlin.",
        },
    ).json()
    client.post(
        "/emails/import",
        json={
            "subject": "Thanks for applying to Backend Engineer at Acme",
            "sender": "careers@acme.test",
            "body": "We received your application for Backend Engineer at Acme.",
        },
    )
    assert client.post("/matching/run").json()["matched_count"] == 1

    second_job = client.post(
        "/job-ads/capture",
        json={
            "url": "https://acme.test/jobs/backend-engineer-second",
            "title": "Backend Engineer",
            "company": "Acme",
            "location": "Berlin",
            "source": "browser_extension",
            "raw_text": "Backend Engineer at Acme in Berlin.",
        },
    ).json()
    client.post(
        "/emails/import",
        json={
            "subject": "Thanks for applying to Backend Engineer at Acme",
            "sender": "careers@acme.test",
            "body": "We received your application for Backend Engineer at Acme.",
        },
    )

    matching_response = client.post("/matching/run")

    assert matching_response.status_code == 200
    assert matching_response.json()["matched_count"] == 1
    applications = client.get("/applications").json()
    application_job_ids = {application["job_ad_id"] for application in applications}
    assert first_job["id"] in application_job_ids
    assert second_job["id"] in application_job_ids


def test_matching_updates_existing_non_rejected_application_when_no_captured_job_matches(client) -> None:
    job = client.post(
        "/job-ads/capture",
        json={
            "url": "https://acme.test/jobs/data-engineer",
            "title": "Data Engineer",
            "company": "Acme",
            "location": "Berlin",
            "source": "browser_extension",
            "raw_text": "Data Engineer at Acme in Berlin.",
        },
    ).json()
    client.post(
        "/emails/import",
        json={
            "subject": "Thanks for applying to Data Engineer at Acme",
            "sender": "careers@acme.test",
            "body": "We received your application for Data Engineer at Acme.",
        },
    )
    assert client.post("/matching/run").json()["matched_count"] == 1

    unrelated_job = client.post(
        "/job-ads/capture",
        json={
            "url": "https://globex.test/jobs/frontend-engineer",
            "title": "Frontend Engineer",
            "company": "Globex",
            "location": "Hamburg",
            "source": "browser_extension",
            "raw_text": "Frontend Engineer at Globex in Hamburg.",
        },
    ).json()
    rejection_email = client.post(
        "/emails/import",
        json={
            "subject": "Update on your application for Data Engineer at Acme",
            "sender": "careers@acme.test",
            "body": (
                "Unfortunately, we decided not to proceed with your application "
                "for Data Engineer at Acme."
            ),
        },
    ).json()
    assert rejection_email["email_status"] == "rejected"

    matching_response = client.post("/matching/run")

    assert matching_response.status_code == 200
    assert matching_response.json()["matched_count"] == 1
    applications = client.get("/applications").json()
    assert len(applications) == 1
    assert applications[0]["job_ad_id"] == job["id"]
    assert applications[0]["status"] == "rejected"

    jobs = client.get("/job-ads").json()
    unrelated_job_status = next(item["status"] for item in jobs if item["id"] == unrelated_job["id"])
    assert unrelated_job_status == "not_applied"


def test_matching_reruns_needs_review_emails(client) -> None:
    client.post(
        "/job-ads/capture",
        json={
            "url": "https://acme.test/jobs/platform-engineer",
            "title": "Platform Engineer",
            "company": "Acme",
            "location": "Berlin",
            "source": "browser_extension",
            "raw_text": "Platform Engineer at Acme in Berlin.",
        },
    )
    email = client.post(
        "/emails/import",
        json={
            "subject": "Thanks for applying to Platform Engineer at Acme",
            "sender": "careers@acme.test",
            "body": "We received your application for Platform Engineer at Acme.",
        },
    ).json()
    client.patch(f"/emails/{email['id']}", json={"match_status": "needs_review"})

    matching_response = client.post("/matching/run")

    assert matching_response.status_code == 200
    assert matching_response.json()["matched_count"] == 1
    updated_email = next(item for item in client.get("/emails").json() if item["id"] == email["id"])
    assert updated_email["match_status"] == "set"
