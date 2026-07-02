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


def test_marking_captured_job_applied_creates_application(client) -> None:
    job = client.post(
        "/job-ads/capture",
        json={
            "title": "Backend Engineer",
            "company": "Acme",
            "location": "Berlin",
            "raw_text": "Backend Engineer at Acme in Berlin.",
        },
    ).json()

    updated_job = client.patch(f"/job-ads/{job['id']}", json={"status": "applied"})

    assert updated_job.status_code == 200
    assert updated_job.json()["status"] == "applied"
    applications = client.get("/applications").json()
    assert len(applications) == 1
    assert applications[0]["job_ad_id"] == job["id"]
    assert applications[0]["status"] == "applied"
    assert applications[0]["company"] == "Acme"
    assert applications[0]["role_title"] == "Backend Engineer"

    detail = client.get(f"/applications/{applications[0]['id']}/detail").json()
    assert detail["events"][0]["email_id"] is None
    assert detail["events"][0]["notes"] == "Created when captured job was marked as applied."


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
        json={
            "status": "accepted",
            "company": "Academic Work",
            "manual_notes": "Filled relocation form before interview.",
        },
    )
    assert updated_application.status_code == 200
    assert updated_application.json()["status"] == "accepted"
    assert updated_application.json()["company"] == "Academic Work"
    assert updated_application.json()["manual_notes"] == "Filled relocation form before interview."


def test_application_detail_includes_job_and_events(client) -> None:
    job = client.post(
        "/job-ads/capture",
        json={"title": "Backend Engineer", "company": "Acme", "raw_text": "Backend at Acme"},
    ).json()
    email = client.post(
        "/emails/import",
        json={
            "subject": "Thanks for applying to Backend Engineer at Acme",
            "body": "We received your application for Backend Engineer at Acme.",
        },
    ).json()
    application = client.post(
        "/matching/confirm",
        json={"job_ad_id": job["id"], "email_id": email["id"]},
    ).json()

    response = client.get(f"/applications/{application['id']}/detail")

    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == application["id"]
    assert detail["manual_notes"] is None
    assert detail["job_ad"]["id"] == job["id"]
    assert detail["events"][0]["email_id"] == email["id"]
    assert detail["events"][0]["notes"] == "Manually confirmed match."


def test_delete_email_unlinks_timeline_event(client) -> None:
    job = client.post(
        "/job-ads/capture",
        json={"title": "Backend Engineer", "company": "Acme", "raw_text": "Backend at Acme"},
    ).json()
    email = client.post(
        "/emails/import",
        json={
            "subject": "Thanks for applying to Backend Engineer at Acme",
            "body": "We received your application for Backend Engineer at Acme.",
        },
    ).json()
    application = client.post(
        "/matching/confirm",
        json={"job_ad_id": job["id"], "email_id": email["id"]},
    ).json()

    response = client.delete(f"/emails/{email['id']}")

    assert response.status_code == 204
    assert client.get("/emails").json() == []
    detail = client.get(f"/applications/{application['id']}/detail").json()
    assert detail["events"][0]["email_id"] is None


def test_delete_job_detaches_application(client) -> None:
    job = client.post(
        "/job-ads/capture",
        json={"title": "Backend Engineer", "company": "Acme", "raw_text": "Backend at Acme"},
    ).json()
    email = client.post(
        "/emails/import",
        json={
            "subject": "Thanks for applying to Backend Engineer at Acme",
            "body": "We received your application for Backend Engineer at Acme.",
        },
    ).json()
    application = client.post(
        "/matching/confirm",
        json={"job_ad_id": job["id"], "email_id": email["id"]},
    ).json()

    response = client.delete(f"/job-ads/{job['id']}")

    assert response.status_code == 204
    assert client.get("/job-ads").json() == []
    detail = client.get(f"/applications/{application['id']}/detail").json()
    assert detail["job_ad_id"] is None
    assert detail["job_ad"] is None


def test_delete_application_removes_record(client) -> None:
    job = client.post(
        "/job-ads/capture",
        json={"title": "Backend Engineer", "company": "Acme", "raw_text": "Backend at Acme"},
    ).json()
    email = client.post(
        "/emails/import",
        json={
            "subject": "Thanks for applying to Backend Engineer at Acme",
            "body": "We received your application for Backend Engineer at Acme.",
        },
    ).json()
    application = client.post(
        "/matching/confirm",
        json={"job_ad_id": job["id"], "email_id": email["id"]},
    ).json()

    response = client.delete(f"/applications/{application['id']}")

    assert response.status_code == 204
    assert client.get("/applications").json() == []

