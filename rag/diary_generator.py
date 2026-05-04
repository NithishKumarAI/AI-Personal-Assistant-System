import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_diary(text):

    prompt = f"""
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

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.6}
        },
        timeout=60

    
    )

    data = response.json()
    return data["response"]
