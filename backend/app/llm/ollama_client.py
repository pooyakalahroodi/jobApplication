import httpx

from app.core.config import get_settings


def ask_ollama(prompt: str) -> str:
    settings = get_settings()
    response = httpx.post(
        f"{settings.ollama_base_url}/api/chat",
        json={
            "model": settings.ollama_model,
            "messages": [
                {
                    "role": "system",
                    "content": "Return exactly one valid JSON object. Do not include markdown or prose.",
                },
                {"role": "user", "content": prompt},
            ],
            "format": "json",
            "options": {"temperature": 0},
            "stream": False,
        },
        timeout=60,
    )
    response.raise_for_status()
    return str(response.json()["message"]["content"])
