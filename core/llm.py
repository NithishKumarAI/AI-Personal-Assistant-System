from core.model_router import generate_with_fallback


def process_input(text):

    if not text or not text.strip():
        return {
            "text": "No input provided.",
            "model_used": "none"
        }

    prompt = f"""
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

    result = generate_with_fallback(prompt)

    return result