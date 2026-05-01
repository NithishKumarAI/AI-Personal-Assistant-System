import requests
from click import prompt

OLLAMA_URL = "http://localhost:11434/api/generate"

def process_input(text):
    prompt = f"""
Rewrite the following input as a personal diary entry.

Rules:
- Preserve the full meaning of the input
- Remove repeated or unnecessary phrases
- Do NOT add any new information
- Do NOT remove important details
- Keep it concise but complete
- Write in a natural personal diary style
- Do NOT add date or time
- Do NOT give advice

Input:
{text}
    """
    response = requests.post(
        OLLAMA_URL,
    json={
        "model" : "llama3",
        "prompt" : prompt,
        "stream" : False
    })
    data = response.json()
    return data["response"]