"""Configuration for offline local execution (.env)."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

CONFIG_SOURCE = "dotenv"

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3"


def get_secret(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key, default)
    if value is None or value == "":
        return default
    return str(value).strip()


def get_required_secret(key: str) -> str:
    value = get_secret(key)
    if not value:
        raise RuntimeError(
            f"Missing required setting '{key}'. Add it to your .env file and restart."
        )
    return value


def get_ollama_base_url() -> str:
    return get_secret("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL) or DEFAULT_OLLAMA_BASE_URL


def get_ollama_model() -> str:
    return get_secret("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL) or DEFAULT_OLLAMA_MODEL
