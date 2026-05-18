"""Startup configuration checks for the offline branch."""

from __future__ import annotations

import logging

import requests

from core.config import CONFIG_SOURCE, get_ollama_base_url, get_secret

LOGGER = logging.getLogger(__name__)

REQUIRED_KEYS = (
    "NOTION_API_KEY",
    "DATABASE_ID",
    "DAILY_DIARY_DATABASE_ID",
)


def _config_hint() -> str:
    if CONFIG_SOURCE == "streamlit_secrets":
        return "Streamlit Secrets"
    return "your .env file"


def validate_config() -> list[str]:
    issues: list[str] = []

    for key in REQUIRED_KEYS:
        if not get_secret(key):
            issues.append(key)

    return issues


def check_ollama_available() -> str | None:
    """Return a warning message if Ollama is not reachable."""
    base_url = get_ollama_base_url().rstrip("/")
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=3)
        if response.ok:
            return None
        return f"Ollama responded with status {response.status_code} at {base_url}"
    except requests.RequestException as exc:
        LOGGER.debug("Ollama health check failed: %s", exc)
        return (
            f"Cannot reach Ollama at {base_url}. Start Ollama and run "
            f"`ollama pull {get_secret('OLLAMA_MODEL', 'llama3')}`."
        )


def format_config_issues(issues: list[str]) -> str:
    if not issues:
        return ""
    joined = ", ".join(issues)
    return f"Missing configuration: {joined}. Add them to {_config_hint()}."
