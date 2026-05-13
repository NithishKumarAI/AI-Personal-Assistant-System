import os

import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
LOG_DATABASE_ID = os.getenv("DATABASE_ID")
DAILY_DIARY_DATABASE_ID = os.getenv("DAILY_DIARY_DATABASE_ID")
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
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def _send_to_notion(method, url, payload):
    response = requests.request(
        method,
        url,
        headers=_headers(),
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def add_entry_to_notion(content, date, time):
    data = {
        "parent": {"database_id": _require_setting("DATABASE_ID", LOG_DATABASE_ID)},
        "properties": {
            "Content": {
                "title": [
                    {
                        "text": {
                            "content": content
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": date
                }
            },
            "Time": {
                "rich_text": [
                    {
                        "text": {
                            "content": time
                        }
                    }
                ]
            }
        }
    }

    return _send_to_notion("POST", "https://api.notion.com/v1/pages", data)


def add_daily_diary(content, date):
    data = {
        "parent": {
            "database_id": _require_setting(
                "DAILY_DIARY_DATABASE_ID",
                DAILY_DIARY_DATABASE_ID,
            )
        },
        "properties": {
            "Diary": {
                "title": [
                    {
                        "text": {
                            "content": content
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": date
                }
            }
        }
    }

    return _send_to_notion("POST", "https://api.notion.com/v1/pages", data)


def update_daily_diary(page_id, content):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    data = {
        "properties": {
            "Diary": {
                "title": [
                    {
                        "text": {
                            "content": content
                        }
                    }
                ]
            }
        }
    }

    return _send_to_notion("PATCH", url, data)
