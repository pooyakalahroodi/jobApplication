from fastapi.testclient import TestClient


def test_extract_email_with_ollama_updates_email_and_records_run(
    client: TestClient,
    monkeypatch,
) -> None:
    email_response = client.post(
        "/emails/import",
        json={
            "subject": "Ihre Bewerbung als Softwareentwickler",
            "sender": "jobs@example.com",
            "body": "Vielen Dank fuer Ihre Bewerbung.",
        },
    )
    email_id = email_response.json()["id"]

    def fake_ollama(_: str) -> str:
        return """
        {
          "status": "pending",
          "company": "Academic Work",
          "role_title": "Softwareentwickler Java",
          "confidence": 0.92,
          "evidence": "Vielen Dank fuer Ihre Bewerbung"
        }
        """

    monkeypatch.setattr("app.services.extraction_service.ask_ollama", fake_ollama)

    response = client.post(f"/extraction/emails/{email_id}")

    assert response.status_code == 200
    run = response.json()
    assert run["source_type"] == "email"
    assert run["source_id"] == email_id
    assert run["status"] == "success"
    assert run["parsed_json"]["company"] == "Academic Work"

    email = client.get(f"/emails/{email_id}").json()
    assert email["email_status"] == "pending"
    assert email["extracted_company"] == "Academic Work"
    assert email["extracted_role_title"] == "Softwareentwickler Java"
    assert email["extraction_confidence"] == 0.92


def test_extract_job_ad_with_ollama_fills_missing_fields_and_records_run(
    client: TestClient,
    monkeypatch,
) -> None:
    job_response = client.post(
        "/job-ads/capture",
        json={
            "url": "https://example.com/jobs/1",
            "title": "Untitled job",
            "raw_text": "Academic Work sucht Softwareentwickler Java in Muenchen.",
        },
    )
    job_id = job_response.json()["id"]

    def fake_ollama(_: str) -> str:
        return """
        {
          "title": "Softwareentwickler Java",
          "company": "Academic Work",
          "location": "Muenchen",
          "description": "Java development role.",
          "confidence": 0.87,
          "evidence": "sucht Softwareentwickler Java"
        }
        """

    monkeypatch.setattr("app.services.extraction_service.ask_ollama", fake_ollama)

    response = client.post(f"/extraction/job-ads/{job_id}")

    assert response.status_code == 200
    run = response.json()
    assert run["source_type"] == "job_ad"
    assert run["source_id"] == job_id
    assert run["status"] == "success"
    assert run["confidence"] == 0.87

    job = client.get(f"/job-ads/{job_id}").json()
    assert job["title"] == "Untitled job"
    assert job["company"] == "Academic Work"
    assert job["location"] == "Muenchen"
    assert job["description"] == "Academic Work sucht Softwareentwickler Java in Muenchen."


def test_failed_ollama_extraction_records_failed_run(client: TestClient, monkeypatch) -> None:
    email_response = client.post(
        "/emails/import",
        json={
            "subject": "Application update",
            "sender": "jobs@example.com",
            "body": "We received your application.",
        },
    )
    email_id = email_response.json()["id"]

    def fake_ollama(_: str) -> str:
        return "not json"

    monkeypatch.setattr("app.services.extraction_service.ask_ollama", fake_ollama)

    response = client.post(f"/extraction/emails/{email_id}")

    assert response.status_code == 503

    runs = client.get("/extraction/runs").json()
    assert len(runs) == 1
    assert runs[0]["status"] == "failed"
    assert runs[0]["source_type"] == "email"
