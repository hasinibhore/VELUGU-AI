"""
backend/tts.py  —  Telugu Text-to-Speech helper
Uses gTTS (Google TTS) with Telugu language code.
Returns base64-encoded MP3 so Streamlit can play it inline.
"""

import base64
import io
from gtts import gTTS


def text_to_audio_b64(text: str, lang: str = "te") -> str:
    """
    Convert text to speech audio.
    Returns a base64 string of the MP3 bytes,
    ready to embed in an HTML <audio> tag.

    Args:
        text: Telugu (or any) text to speak.
        lang: BCP-47 language code. 'te' = Telugu.

    Returns:
        Base64-encoded MP3 string, or empty string on failure.
    """
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception as e:
        print(f"[TTS Error] {e}")
        return ""


def audio_html(b64_audio: str) -> str:
    """Return an HTML snippet that auto-plays the audio."""
    if not b64_audio:
        return ""
    return (
        f'<audio autoplay style="display:none">'
        f'<source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">'
        f"</audio>"
    )