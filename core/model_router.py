"""Gemini multi-model fallback routing."""

from __future__ import annotations

import logging

import google.generativeai as genai

from core.config import get_secret

LOGGER = logging.getLogger(__name__)
GEMINI_TIMEOUT_SECONDS = 60

_genai_configured = False


def _ensure_genai_configured() -> None:
    global _genai_configured
    if _genai_configured:
        return

    api_key = get_secret("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    genai.configure(api_key=api_key)
    _genai_configured = True


def _configured_models() -> list[str]:
    models = [
        get_secret("PRIMARY_MODEL"),
        get_secret("SECONDARY_MODEL"),
        get_secret("TERTIARY_MODEL"),
    ]
    return [model for model in models if model]


def generate_with_fallback(prompt: str) -> dict[str, str]:
    _ensure_genai_configured()
    models = _configured_models()

    if not models:
        raise RuntimeError(
            "No Gemini models are configured. Set PRIMARY_MODEL, "
            "SECONDARY_MODEL, and/or TERTIARY_MODEL."
        )

    last_error: Exception | None = None

    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                request_options={"timeout": GEMINI_TIMEOUT_SECONDS},
            )
            return {
                "text": response.text.strip(),
                "model_used": model_name,
            }
        except Exception as exc:
            LOGGER.warning("Gemini model failed: %s", model_name, exc_info=True)
            last_error = exc

    raise RuntimeError(
        "All configured Gemini models are temporarily unavailable. Try again shortly."
    ) from last_error
