from core.model_router import generate_with_fallback


DIARY_PROMPT = """
You are writing a personal diary.

Rules:
- Write naturally like a human
- Keep it simple and readable
- Do NOT add new information
- Do NOT remove important details
- Combine everything smoothly
- Do NOT add headings
- Do NOT say "Here is"

Logs:
{text}

Diary:
"""


def generate_diary(text):
    result = generate_with_fallback(DIARY_PROMPT.format(text=text))
    return result["text"]
