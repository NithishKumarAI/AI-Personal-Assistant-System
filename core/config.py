"""Configuration for local Gemini execution (.env only)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


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
