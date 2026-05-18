"""Local Ollama diary generation."""

from __future__ import annotations

import logging

import requests

from core.config import get_ollama_base_url, get_ollama_model

LOGGER = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 120

DIARY_PROMPT = """
You are writing a personal diary.

Rules:
- Write naturally like a human
- Keep it simple and readable
- Do NOT add new information
- Do NOT remove important details
- Combine everything smoothly
- Do NOT add headings
- Do NOT say "Here is"

Logs:
{text}

Diary:
"""


def generate_diary(text: str) -> str:
    base_url = get_ollama_base_url().rstrip("/")
    model_name = get_ollama_model()
    prompt = DIARY_PROMPT.format(text=text)

    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.6},
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except requests.RequestException as exc:
        LOGGER.error("Ollama diary generation failed", exc_info=True)
        raise RuntimeError(
            f"Diary generation failed. Check Ollama at {base_url} and model '{model_name}'."
        ) from exc
