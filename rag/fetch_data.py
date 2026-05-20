"""Notion API read operations."""

from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from core.config import get_secret

LOGGER = logging.getLogger(__name__)
NOTION_VERSION = "2022-06-28"
REQUEST_TIMEOUT_SECONDS = 20


def _config_hint() -> str:
    return "your .env file"


def _require_setting(name: str, value: str | None) -> str:
    if not value:
        raise RuntimeError(f"Missing {name}. Add it to {_config_hint()}.")
    return value


def _headers() -> dict[str, str]:
    api_key = _require_setting("NOTION_API_KEY", get_secret("NOTION_API_KEY"))
    return {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _query_database(database_id: str | None, payload: dict) -> dict:
    database_id = _require_setting("DATABASE_ID", database_id)
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    try:
        response = requests.post(
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
            f"Notion query failed ({exc.response.status_code if exc.response else 'unknown'}): "
            f"{detail or str(exc)}"
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach Notion API: {exc}") from exc


def _extract_title(properties: dict, property_name: str) -> str:
    title_items = properties.get(property_name, {}).get("title", [])
    if not title_items:
        return ""

    first_title = title_items[0]
    return first_title.get("plain_text") or first_title.get("text", {}).get("content", "")


def fetch_todays_entries() -> list[str]:
    today = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
    log_database_id = get_secret("DATABASE_ID")

    payload = {
        "filter": {
            "and": [
                {"property": "Date", "date": {"on_or_after": today}},
                {"property": "Date", "date": {"on_or_before": today}},
            ]
        }
    }

    data = _query_database(log_database_id, payload)
    logs: list[str] = []

    for item in data.get("results", []):
        content = _extract_title(item.get("properties", {}), "Content")
        if content:
            logs.append(content)

    return logs


def _query_diary_database(payload: dict) -> dict:
    diary_database_id = _require_setting(
        "DAILY_DIARY_DATABASE_ID",
        get_secret("DAILY_DIARY_DATABASE_ID"),
    )
    url = f"https://api.notion.com/v1/databases/{diary_database_id}/query"

    try:
        response = requests.post(
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
        raise RuntimeError(f"Notion diary query failed: {detail or str(exc)}") from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach Notion API: {exc}") from exc


def fetch_diary_by_date(selected_date) -> str | None:
    payload = {
        "filter": {
            "property": "Date",
            "date": {"equals": str(selected_date)},
        }
    }

    data = _query_diary_database(payload)
    results = data.get("results", [])

    if not results:
        return None

    return _extract_title(results[0].get("properties", {}), "Diary")


def get_diary_page_by_date(selected_date) -> str | None:
    payload = {
        "filter": {
            "property": "Date",
            "date": {"equals": str(selected_date)},
        }
    }

    data = _query_diary_database(payload)
    results = data.get("results", [])

    if not results:
        return None

    return results[0]["id"]
