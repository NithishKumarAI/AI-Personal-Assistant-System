import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = [
    os.getenv("PRIMARY_MODEL"),
    os.getenv("SECONDARY_MODEL"),
    os.getenv("TERTIARY_MODEL")
]


def generate_with_fallback(prompt):

    last_error = None

    for model_name in MODELS:

        try:

            model = genai.GenerativeModel(model_name)

            response = model.generate_content(prompt)

            return {
                "text": response.text.strip(),
                "model_used": model_name
            }

        except Exception as e:

            print(f"Model failed: {model_name}")
            print(e)

            last_error = e

            continue

    raise Exception(f"All Gemini models failed. Last error: {last_error}")