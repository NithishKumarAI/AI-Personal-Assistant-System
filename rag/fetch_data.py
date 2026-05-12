import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_todays_entries():
    today = datetime.now().strftime("%Y-%m-%d")
    #print("TODAY FROM PYTHON:", today)
    url = f"https://api.notion.com/v1/databases/{os.getenv('DATABASE_ID')}/query"

    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
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

    response = requests.post(url, headers = headers, json = payload)

    data = response.json()

    logs =[]

    for item in data.get("results",[]):
        try:
            content = item["properties"]["Content"]["title"][0]["text"]["content"]
            logs.append(content)
        except:
            continue
    return logs

def fetch_diary_by_date(selected_date):

    url = f"https://api.notion.com/v1/databases/{os.getenv('DAILY_DIARY_DATABASE_ID')}/query"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = {
        "filter": {
            "property": "Date",
            "date": {
                "equals": str(selected_date)
            }
        }
    }
    response = requests.post(
        url,
        headers=headers,
        json=payload
    )
    data = response.json()
    results = data.get("results", [])
    #data["results"]
    if not results:
        return None
    item = results[0]
    diary_text = item["properties"]["Diary"]["title"][0]["text"]["content"]
    return diary_text
def get_diary_page_by_date(selected_date):
    url = f"https://api.notion.com/v1/databases/{os.getenv('DAILY_DIARY_DATABASE_ID')}/query"

    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    payload = {
        "filter": {
            "property": "Date",
            "date": {
                "equals": str(selected_date)
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    data = response.json()

    results = data.get("results", [])

    if not results:
        return None

    return results[0]["id"]