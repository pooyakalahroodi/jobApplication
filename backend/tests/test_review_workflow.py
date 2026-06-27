def test_update_job_email_and_application_statuses(client) -> None:
    job = client.post(
        "/job-ads/capture",
        json={
            "title": "Backend Engineer",
            "company": "Acme",
            "raw_text": "Backend Engineer at Acme",
        },
    ).json()

    updated_job = client.patch(
        f"/job-ads/{job['id']}",
        json={"status": "archived", "location": "Remote"},
    )
    assert updated_job.status_code == 200
    assert updated_job.json()["status"] == "archived"
    assert updated_job.json()["location"] == "Remote"

    email = client.post(
        "/emails/import",
        json={
            "subject": "Thanks for applying to Backend Engineer at Acme",
            "body": "We received your application for Backend Engineer at Acme.",
        },
    ).json()

    updated_email = client.patch(
        f"/emails/{email['id']}",
        json={"match_status": "needs_review", "extracted_company": "Acme GmbH"},
    )
    assert updated_email.status_code == 200
    assert updated_email.json()["match_status"] == "needs_review"
    assert updated_email.json()["extracted_company"] == "Acme GmbH"


def test_confirm_manual_match(client) -> None:
    job = client.post(
        "/job-ads/capture",
        json={
            "title": "Softwareentwickler Java (m/w/d) - Remote",
            "company": "Academic Work Germany GmbH Hamburg",
            "raw_text": "Softwareentwickler Java bei Academic Work.",
        },
    ).json()
    email = client.post(
        "/emails/import",
        json={
            "subject": "Ihre Bewerbung als Softwareentwickler Java (m/w/d) - Remote",
            "body": (
                "Vielen Dank für Ihre Bewerbung als Softwareentwickler Java (m/w/d) - Remote "
                "bei Academic Work Germany GmbH Hamburg."
            ),
        },
    ).json()

    response = client.post(
        "/matching/confirm",
        json={"job_ad_id": job["id"], "email_id": email["id"]},
    )

    assert response.status_code == 200
    application = response.json()
    assert application["job_ad_id"] == job["id"]
    assert application["status"] == "pending"

    assert client.get("/job-ads").json()[0]["status"] == "applied"
    assert client.get("/emails").json()[0]["match_status"] == "set"

    updated_application = client.patch(
        f"/applications/{application['id']}",
        json={"status": "accepted", "company": "Academic Work"},
    )
    assert updated_application.status_code == 200
    assert updated_application.json()["status"] == "accepted"
    assert updated_application.json()["company"] == "Academic Work"

