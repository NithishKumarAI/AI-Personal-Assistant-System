"""Groq Whisper transcription (browser audio upload)."""

from __future__ import annotations

import logging
from pathlib import Path

from groq import Groq

from core.config import get_secret

LOGGER = logging.getLogger(__name__)
TRANSCRIPTION_MODEL = "whisper-large-v3-turbo"
TRANSCRIPTION_TIMEOUT_SECONDS = 45
TRANSCRIPTION_FAILED_MESSAGE = "Transcription failed."

_groq_client: Groq | None = None


def _get_client() -> Groq:
    global _groq_client
    if _groq_client is not None:
        return _groq_client

    api_key = get_secret("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    _groq_client = Groq(api_key=api_key)
    return _groq_client


def transcribe_audio(filename: str = "temp_audio.wav") -> str:
    try:
        with Path(filename).open("rb") as audio_file:
            transcription = _get_client().audio.transcriptions.create(
                file=audio_file,
                model=TRANSCRIPTION_MODEL,
                response_format="verbose_json",
                timeout=TRANSCRIPTION_TIMEOUT_SECONDS,
            )
        return transcription.text.strip()
    except Exception:
        LOGGER.warning("Groq transcription failed", exc_info=True)
        return TRANSCRIPTION_FAILED_MESSAGE
