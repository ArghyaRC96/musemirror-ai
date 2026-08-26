from google import genai
from google.genai import types


MUSEMIRROR_MODEL = "gemini-3.6-flash"

GEMINI_TIMEOUT_MS = 30_000


def build_gemini_client(api_key):
    """
    Build the Gemini client used by MuseMirror.
    """

    if not api_key:
        raise ValueError(
            "A Gemini API key is required."
        )

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=GEMINI_TIMEOUT_MS
        )
    )
