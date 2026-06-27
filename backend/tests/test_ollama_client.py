from typing import Any

from app.llm.ollama_client import ask_ollama


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return {"message": {"content": "{\"status\":\"unknown\"}"}}


def test_ollama_client_requests_json_mode(monkeypatch) -> None:
    captured_payload: dict[str, Any] = {}

    def fake_post(*_: Any, json: dict[str, Any], **__: Any) -> FakeResponse:
        captured_payload.update(json)
        return FakeResponse(json)

    monkeypatch.setattr("app.llm.ollama_client.httpx.post", fake_post)

    result = ask_ollama("Extract something.")

    assert result == "{\"status\":\"unknown\"}"
    assert captured_payload["format"] == "json"
    assert captured_payload["options"]["temperature"] == 0
    assert "Do not include markdown or prose" in captured_payload["messages"][0]["content"]
