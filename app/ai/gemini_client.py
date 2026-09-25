from google import genai

from app.config import get_settings


def get_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to the .env file before generating an AI plan."
        )
    return genai.Client(api_key=settings.gemini_api_key)
