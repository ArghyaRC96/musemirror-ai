from google import genai
from google.genai import types


MUSEMIRROR_TRANSCRIPTION_MODEL = "gemini-3.5-transcribe"
MUSEMIRROR_VIBE_MODEL = "gemini-3.6-flash"

# Backwards-compatible alias for creator-side generation.
MUSEMIRROR_MODEL = MUSEMIRROR_VIBE_MODEL

GEMINI_TIMEOUT_MS = 45_000


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
