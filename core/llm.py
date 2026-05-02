import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def process_input(text):
    if not text or not text.strip():
        return "No input provided."
    prompt = f"""
    You are NOT a chatbot.

    You ONLY return cleaned text.

    STRICT:
    - Output ONLY the cleaned text
    - Do NOT add any heading
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
    response = requests.post(
        OLLAMA_URL,
    json={
        "model" : "llama3",
        "prompt" : prompt,
        "stream" : False,
        "options" : {
            "temperature": 0
        }
    })
    data = response.json()
    return data["response"]
