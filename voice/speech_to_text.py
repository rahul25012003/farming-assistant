"""
Google Cloud Speech-to-Text integration for Kannada.
Handles audio preprocessing and transcription.
"""
from google.cloud import speech
import io
import config


def transcribe_kannada(audio_path):
    """
    Transcribe Kannada audio file to text using GCP Speech-to-Text.

    Args:
        audio_path: Path to WAV audio file
    Returns:
        Transcribed text string, or empty string if failed
    """
    client = speech.SpeechClient()

    with io.open(audio_path, "rb") as f:
        audio_content = f.read()

    audio = speech.RecognitionAudio(content=audio_content)
    recognition_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=config.AUDIO_SAMPLE_RATE,
        language_code=config.STT_LANGUAGE,
        # Enable automatic punctuation for better sentence structure
        enable_automatic_punctuation=True,
        # Alternative languages in case farmer mixes Kannada with English
        alternative_language_codes=["en-IN"],
        # Model optimized for short queries
        model="command_and_search",
    )

    try:
        response = client.recognize(config=recognition_config, audio=audio)
    except Exception as e:
        print(f"[STT] GCP API error: {e}")
        return ""

    if not response.results:
        print("[STT] No transcription results")
        return ""

    # Take the top result
    transcript = response.results[0].alternatives[0].transcript
    confidence = response.results[0].alternatives[0].confidence
    print(f"[STT] Transcript: '{transcript}' (confidence: {confidence:.2f})")

    # Low confidence warning
    if confidence < 0.6:
        print(f"[STT] Warning: low confidence ({confidence:.2f}), might be noisy audio")

    return transcript


def transcribe_streaming(audio_generator):
    """
    Streaming transcription for real-time push-to-talk.
    TODO: Implement for the Android app version.
    """
    raise NotImplementedError("Streaming STT not implemented yet")
