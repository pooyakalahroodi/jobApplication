def test_capture_job_ad_from_extension_payload(client) -> None:
    payload = {
        "url": "https://example.test/jobs/backend-engineer",
        "title": "Backend Engineer",
        "source": "browser_extension",
        "page_title": "Backend Engineer - Example",
        "selected_text": "Backend Engineer role in Berlin.",
        "raw_text": "Backend Engineer role in Berlin. Python, APIs, and databases.",
        "json_ld": [{"@type": "JobPosting", "title": "Backend Engineer"}],
    }

    response = client.post("/job-ads/capture", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Backend Engineer"
    assert data["status"] == "not_applied"
    assert data["source"] == "browser_extension"
    assert data["description"] == "Backend Engineer role in Berlin."
    assert data["json_ld"][0]["@type"] == "JobPosting"
