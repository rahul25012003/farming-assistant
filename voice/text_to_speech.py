"""
Google Cloud Text-to-Speech integration for Kannada.
Converts response text to natural Kannada audio.
"""
from google.cloud import texttospeech
import hashlib
import os
import config


# Simple in-memory + disk cache for common TTS responses
_tts_cache_dir = os.path.join(os.path.dirname(__file__), "..", "cache", "tts_audio")
os.makedirs(_tts_cache_dir, exist_ok=True)


def synthesize_kannada(text):
    """
    Convert Kannada text to speech audio file.

    Args:
        text: Kannada text to synthesize
    Returns:
        Path to MP3 audio file
    """
    # Check cache first - common responses like greetings get cached
    cache_key = hashlib.md5(text.encode("utf-8")).hexdigest()
    cached_path = os.path.join(_tts_cache_dir, f"{cache_key}.mp3")
    if os.path.exists(cached_path):
        print(f"[TTS] Cache hit: {text[:40]}...")
        return cached_path

    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=config.TTS_LANGUAGE,
        name=config.TTS_VOICE_NAME,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.9,  # Slightly slower for clarity - farmers prefer this
        pitch=0.0,
    )

    try:
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )
    except Exception as e:
        print(f"[TTS] GCP API error: {e}")
        raise

    # Save to cache
    with open(cached_path, "wb") as f:
        f.write(response.audio_content)

    print(f"[TTS] Generated audio for: {text[:50]}...")
    return cached_path


def clear_tts_cache():
    """Clear all cached TTS audio files."""
    for f in os.listdir(_tts_cache_dir):
        os.remove(os.path.join(_tts_cache_dir, f))
    print("[TTS] Cache cleared")
