"""Notion API write operations."""

from __future__ import annotations

import logging

import requests

from core.config import CONFIG_SOURCE, get_secret

LOGGER = logging.getLogger(__name__)
NOTION_VERSION = "2022-06-28"
REQUEST_TIMEOUT_SECONDS = 20
NOTION_TITLE_MAX_CHARS = 2000


def _config_hint() -> str:
    if CONFIG_SOURCE == "streamlit_secrets":
        return "Streamlit Secrets"
    return "your .env file"


def _require_setting(name: str, value: str | None) -> str:
    if not value:
        raise RuntimeError(f"Missing {name}. Add it to {_config_hint()}.")
    return value


def _headers() -> dict[str, str]:
    api_key = _require_setting("NOTION_API_KEY", get_secret("NOTION_API_KEY"))
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def _truncate_title(text: str) -> str:
    if len(text) <= NOTION_TITLE_MAX_CHARS:
        return text
    LOGGER.warning("Notion title truncated to %s characters.", NOTION_TITLE_MAX_CHARS)
    return text[: NOTION_TITLE_MAX_CHARS - 3] + "..."


def _send_to_notion(method: str, url: str, payload: dict) -> dict:
    try:
        response = requests.request(
            method,
            url,
            headers=_headers(),
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        detail = ""
        if exc.response is not None:
            try:
                detail = exc.response.json().get("message", "")
            except ValueError:
                detail = exc.response.text[:200]
        raise RuntimeError(
            f"Notion API error ({exc.response.status_code if exc.response else 'unknown'}): "
            f"{detail or str(exc)}"
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach Notion API: {exc}") from exc


def add_entry_to_notion(content: str, date: str, time: str) -> dict:
    database_id = _require_setting("DATABASE_ID", get_secret("DATABASE_ID"))
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Content": {
                "title": [{"text": {"content": _truncate_title(content)}}],
            },
            "Date": {"date": {"start": date}},
            "Time": {"rich_text": [{"text": {"content": time}}]},
        },
    }
    return _send_to_notion("POST", "https://api.notion.com/v1/pages", data)


def add_daily_diary(content: str, date: str) -> dict:
    database_id = _require_setting(
        "DAILY_DIARY_DATABASE_ID",
        get_secret("DAILY_DIARY_DATABASE_ID"),
    )
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Diary": {
                "title": [{"text": {"content": _truncate_title(content)}}],
            },
            "Date": {"date": {"start": date}},
        },
    }
    return _send_to_notion("POST", "https://api.notion.com/v1/pages", data)


def update_daily_diary(page_id: str, content: str) -> dict:
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "properties": {
            "Diary": {
                "title": [{"text": {"content": _truncate_title(content)}}],
            },
        },
    }
    return _send_to_notion("PATCH", url, data)
