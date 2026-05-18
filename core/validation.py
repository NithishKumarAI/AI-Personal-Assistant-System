"""Startup configuration checks."""

from __future__ import annotations

from core.config import CONFIG_SOURCE, get_secret

REQUIRED_KEYS = (
    "NOTION_API_KEY",
    "DATABASE_ID",
    "DAILY_DIARY_DATABASE_ID",
    "GROQ_API_KEY",
    "GEMINI_API_KEY",
)

MODEL_KEYS = ("PRIMARY_MODEL", "SECONDARY_MODEL", "TERTIARY_MODEL")


def _config_hint() -> str:
    if CONFIG_SOURCE == "streamlit_secrets":
        return "Add the value in Streamlit Cloud → Secrets (or .streamlit/secrets.toml locally)."
    return "Add the value to your .env file and restart the app."


def validate_config() -> list[str]:
    """Return a list of missing or invalid configuration items."""
    issues: list[str] = []

    for key in REQUIRED_KEYS:
        if not get_secret(key):
            issues.append(key)

    models = [get_secret(key) for key in MODEL_KEYS]
    if not any(models):
        issues.append("At least one of PRIMARY_MODEL, SECONDARY_MODEL, TERTIARY_MODEL")

    return issues


def format_config_issues(issues: list[str]) -> str:
    if not issues:
        return ""
    joined = ", ".join(issues)
    return f"Missing configuration: {joined}. {_config_hint()}"
