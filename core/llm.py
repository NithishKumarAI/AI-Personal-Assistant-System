from core.model_router import generate_with_fallback


CLEAN_ENTRY_PROMPT = """
You are NOT a chatbot.

You ONLY return cleaned text.

STRICT:
- Output ONLY the cleaned text
- Do NOT add headings
- Do NOT say "Here is"
- Do NOT say "Cleaned text"
- Do NOT add explanations
- Do NOT add extra lines
- Do NOT behave like an assistant

Write in simple, natural language:
- Keep same meaning
- Keep same details
- Remove repetition
- Fix grammar
- Keep it informal and natural

Input:
{text}

Cleaned text (only output this):
"""


def process_input(text):
    cleaned_text = text.strip() if text else ""

    if not cleaned_text:
        return {
            "text": "No input provided.",
            "model_used": "none",
        }

    return generate_with_fallback(CLEAN_ENTRY_PROMPT.format(text=cleaned_text))
