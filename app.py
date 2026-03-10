"""
Farming Assistant - Main Flask Application
Voice-first AI assistant for Kannada-speaking farmers in rural Karnataka.

Run: python app.py
"""
from flask import Flask, request, jsonify, send_file
import tempfile
import os
import traceback

from agents.orchestrator import Orchestrator
from voice.speech_to_text import transcribe_kannada
from voice.text_to_speech import synthesize_kannada
from vision.disease_classifier import DiseaseClassifier
from cache.offline_cache import OfflineCache
import config

app = Flask(__name__)
orchestrator = Orchestrator()
classifier = DiseaseClassifier()
cache = OfflineCache(config.CACHE_DB_PATH)


@app.before_request
def check_connectivity():
    """Middleware: if we're offline, try to serve from cache."""
    if request.endpoint == "health":
        return None
    # This flag gets set by the cache module when network calls fail
    app.config["is_offline"] = False


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": classifier.model is not None,
        "cache_size": cache.get_size(),
    })


@app.route("/voice", methods=["POST"])
def voice():
    """
    Main voice endpoint.
    Receives Kannada audio → transcribes → processes → returns audio response.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    if audio_file.content_length and audio_file.content_length > config.MAX_AUDIO_SIZE_MB * 1024 * 1024:
        return jsonify({"error": "Audio file too large"}), 413

    try:
        # Save uploaded audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name

        # Step 1: Transcribe Kannada audio
        transcript = transcribe_kannada(tmp_path)
        print(f"[STT] Transcribed: {transcript}")

        if not transcript:
            return jsonify({"error": "Could not understand audio"}), 422

        # Step 2: Check cache first
        cached = cache.get(transcript)
        if cached:
            print(f"[CACHE] Hit for: {transcript[:50]}")
            response_text = cached
        else:
            # Step 3: Process through orchestrator
            response_text = orchestrator.process(transcript)
            cache.put(transcript, response_text)

        # Step 4: Convert response to Kannada audio
        audio_output_path = synthesize_kannada(response_text)

        return send_file(audio_output_path, mimetype="audio/mp3",
                         as_attachment=True, download_name="response.mp3")

    except Exception as e:
        print(f"[ERROR] /voice failed: {e}")
        traceback.print_exc()
        return jsonify({"error": "Processing failed", "detail": str(e)}), 500
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.route("/diagnose", methods=["POST"])
def diagnose():
    """
    Disease diagnosis endpoint.
    Receives leaf image → classifies → returns diagnosis + treatment.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files["image"]

    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            image_file.save(tmp.name)
            tmp_path = tmp.name

        # Run classification
        result = classifier.classify(tmp_path)
        print(f"[VISION] Detected: {result['disease']} ({result['confidence']:.1%})")

        # Get treatment info from disease agent
        from agents.disease_agent import DiseaseAgent
        disease_agent = DiseaseAgent()
        treatment = disease_agent.get_treatment(result["disease"])

        response = {
            "disease": result["disease"],
            "confidence": round(result["confidence"], 3),
            "treatment": treatment,
            "heatmap_available": result.get("heatmap_path") is not None,
        }

        # If farmer wants audio explanation, generate TTS
        if request.form.get("audio_response", "false") == "true":
            explanation = disease_agent.format_kannada_response(result["disease"], treatment)
            audio_path = synthesize_kannada(explanation)
            response["audio_url"] = f"/static/{os.path.basename(audio_path)}"

        return jsonify(response)

    except Exception as e:
        print(f"[ERROR] /diagnose failed: {e}")
        traceback.print_exc()
        return jsonify({"error": "Diagnosis failed", "detail": str(e)}), 500
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    print(f"Starting Farming Assistant on {config.HOST}:{config.PORT}")
    print(f"Debug mode: {config.DEBUG}")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
