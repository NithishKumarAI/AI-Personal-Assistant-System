import os
import logging

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

LOGGER = logging.getLogger(__name__)
GEMINI_TIMEOUT_SECONDS = 60

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = [
    os.getenv("PRIMARY_MODEL"),
    os.getenv("SECONDARY_MODEL"),
    os.getenv("TERTIARY_MODEL"),
]
MODELS = [model for model in MODELS if model]


def generate_with_fallback(prompt):
    if not MODELS:
        raise RuntimeError("No Gemini models are configured.")

    last_error = None

    for model_name in MODELS:
        try:
            model = genai.GenerativeModel(model_name)

            response = model.generate_content(
                prompt,
                request_options={"timeout": GEMINI_TIMEOUT_SECONDS},
            )

            return {
                "text": response.text.strip(),
                "model_used": model_name,
            }

        except Exception as exc:
            LOGGER.warning("Gemini model failed: %s", model_name, exc_info=True)
            last_error = exc
            continue

    raise RuntimeError(
        "All AI models are temporarily unavailable."
    ) from last_error
