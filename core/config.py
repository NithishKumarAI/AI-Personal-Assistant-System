"""Configuration for local Gemini execution (.env only)."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

CONFIG_SOURCE = "dotenv"


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
