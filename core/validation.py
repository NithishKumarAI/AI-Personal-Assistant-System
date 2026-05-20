"""Startup configuration checks."""

from __future__ import annotations

from core.config import get_secret

REQUIRED_KEYS = (
    "NOTION_API_KEY",
    "DATABASE_ID",
    "DAILY_DIARY_DATABASE_ID",
    "GROQ_API_KEY",
    "GEMINI_API_KEY",
)

MODEL_KEYS = ("PRIMARY_MODEL", "SECONDARY_MODEL", "TERTIARY_MODEL")


def _config_hint() -> str:
    return "Add the value to your .env file and restart the app."


def validate_config() -> list[str]:
    issues: list[str] = []

    for key in REQUIRED_KEYS:
        if not get_secret(key):
            issues.append(key)

    if not any(get_secret(key) for key in MODEL_KEYS):
        issues.append("At least one of PRIMARY_MODEL, SECONDARY_MODEL, TERTIARY_MODEL")

    return issues


def format_config_issues(issues: list[str]) -> str:
    if not issues:
        return ""
    return f"Missing configuration: {', '.join(issues)}. {_config_hint()}"
