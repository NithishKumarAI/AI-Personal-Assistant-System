import os
from datetime import datetime

import requests
from core.config import get_secret

NOTION_API_KEY = get_secret("NOTION_API_KEY")
LOG_DATABASE_ID = get_secret("DATABASE_ID")
DAILY_DIARY_DATABASE_ID = get_secret("DAILY_DIARY_DATABASE_ID")
NOTION_VERSION = "2022-06-28"
REQUEST_TIMEOUT_SECONDS = 20


def _require_setting(name, value):
    if not value:
        raise RuntimeError(f"Missing {name}. Add it to your .env file.")

    return value


def _headers():
    api_key = _require_setting("NOTION_API_KEY", NOTION_API_KEY)

    return {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _query_database(database_id, payload):
    database_id = _require_setting("database ID", database_id)
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    response = requests.post(
        url,
        headers=_headers(),
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def _extract_title(properties, property_name):
    title_items = properties.get(property_name, {}).get("title", [])
    if not title_items:
        return ""

    first_title = title_items[0]
    return first_title.get("plain_text") or first_title.get("text", {}).get("content", "")


def fetch_todays_entries():
    today = datetime.now().strftime("%Y-%m-%d")

    payload = {
        "filter": {
            "and": [
                {
                    "property": "Date",
                    "date": {
                        "on_or_after": today
                    }
                },
                {
                    "property": "Date",
                    "date": {
                        "on_or_before": today
                    }
                }
            ]
        }
    }

    data = _query_database(LOG_DATABASE_ID, payload)

    logs = []

    for item in data.get("results", []):
        content = _extract_title(item.get("properties", {}), "Content")
        if content:
            logs.append(content)

    return logs


def fetch_diary_by_date(selected_date):
    payload = {
        "filter": {
            "property": "Date",
            "date": {
                "equals": str(selected_date)
            }
        }
    }

    data = _query_database(DAILY_DIARY_DATABASE_ID, payload)
    results = data.get("results", [])

    if not results:
        return None

    return _extract_title(results[0].get("properties", {}), "Diary")


def get_diary_page_by_date(selected_date):
    payload = {
        "filter": {
            "property": "Date",
            "date": {
                "equals": str(selected_date)
            }
        }
    }

    data = _query_database(DAILY_DIARY_DATABASE_ID, payload)
    results = data.get("results", [])

    if not results:
        return None

    return results[0]["id"]
