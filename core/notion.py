import os
from dotenv import load_dotenv
import requests

load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")

def  add_entry_to_notion(content,date,time):
    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": DATABASE_ID},
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
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def add_daily_diary(content, date):
    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {
            "database_id": os.getenv("DAILY_DIARY_DATABASE_ID")
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

    response = requests.post(url, headers=headers, json=data)
    return response.json()