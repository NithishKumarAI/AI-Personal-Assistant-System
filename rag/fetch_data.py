import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_todays_entries():
    today = datetime.now().strftime("%Y-%m-%d")
    print("TODAY FROM PYTHON:", today)
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

    response = requests.post(url, headers = headers, data = payload)

    data = response.json()

    logs =[]

    for item in data.get("results",[]):
        try:
            content = item["properties"]["Content"]["title"][0]["text"]["content"]
            logs.append(content)
        except:
            continue
    return logs