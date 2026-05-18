"""Local Ollama text cleanup."""

from __future__ import annotations

import logging

import requests

from core.config import get_ollama_base_url, get_ollama_model

LOGGER = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 90

CLEAN_ENTRY_PROMPT = """
You are NOT a chatbot.

You ONLY return cleaned text.

STRICT:
- Output ONLY the cleaned text
- Do NOT add headings
- Do NOT say "Here is"
- Do NOT say "Cleaned text"
- Do NOT add explanations
- Do NOT add extra lines
- Do NOT behave like an assistant

Write in simple, natural language:
- Keep same meaning
- Keep same details
- Remove repetition
- Fix grammar
- Keep it informal and natural

Input:
{text}

Cleaned text (only output this):
"""


def process_input(text: str) -> dict[str, str]:
    cleaned_text = text.strip() if text else ""
    model_name = get_ollama_model()

    if not cleaned_text:
        return {"text": "No input provided.", "model_used": "none"}

    base_url = get_ollama_base_url().rstrip("/")
    prompt = CLEAN_ENTRY_PROMPT.format(text=cleaned_text)

    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "text": data.get("response", "").strip() or cleaned_text,
            "model_used": f"{model_name} (Ollama)",
        }
    except requests.RequestException as exc:
        LOGGER.error("Ollama request failed", exc_info=True)
        raise RuntimeError(
            f"Could not reach Ollama at {base_url}. Is Ollama running with model '{model_name}'?"
        ) from exc
