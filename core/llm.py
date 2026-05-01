import requests
from click import prompt

OLLAMA_URL = "http://localhost:11434/api/generate"

def process_input(text):
    prompt = f"""Convert the following into a short diary entry.
Do not give advice. Do not explain. Only rewrite.
    
    input:
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