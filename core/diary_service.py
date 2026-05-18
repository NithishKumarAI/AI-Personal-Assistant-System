from datetime import datetime

from core.notion import add_daily_diary, update_daily_diary
from rag.combine_logs import combine_logs
from rag.diary_generator import generate_diary
from rag.fetch_data import fetch_todays_entries, get_diary_page_by_date


def generate_or_update_diary() -> str:
    logs = fetch_todays_entries()

    if not logs:
        return "No logs found for today."

    combined_logs = combine_logs(logs)
    diary = generate_diary(combined_logs)
    today = datetime.now().strftime("%Y-%m-%d")
    existing_page_id = get_diary_page_by_date(today)

    if existing_page_id:
        update_daily_diary(existing_page_id, diary)
        return "Diary updated successfully."

    add_daily_diary(diary, today)
    return "Diary created successfully."
