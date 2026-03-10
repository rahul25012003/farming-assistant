"""
Configuration for Farming Assistant.
Keep API keys in .env file, not here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Google Cloud ---
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "farming-assistant-kolar")
GCP_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "config/gcp-credentials.json")

# --- Speech ---
STT_LANGUAGE = "kn-IN"  # Kannada (India)
TTS_LANGUAGE = "kn-IN"
TTS_VOICE_NAME = "kn-IN-Standard-A"  # Female voice, more natural for instructions
AUDIO_SAMPLE_RATE = 16000
AUDIO_ENCODING = "LINEAR16"

# --- OpenWeatherMap ---
OWM_API_KEY = os.getenv("OWM_API_KEY", "")
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"
DEFAULT_LOCATION = {"lat": 13.1362, "lon": 78.1292, "name": "Kolar"}  # Kolar district

# --- Model ---
DISEASE_MODEL_PATH = os.getenv("DISEASE_MODEL_PATH", "models/crop_disease_model.h5")
MODEL_INPUT_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.65  # Below this, say "not sure" instead of wrong diagnosis

# --- Mandi / Market ---
AGMARKNET_BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "")
DEFAULT_MANDI = "Kolar"

# --- Cache ---
CACHE_DB_PATH = "cache/farming_cache.db"
CACHE_EXPIRY_HOURS = 6  # Weather data expires in 6 hours
CACHE_MAX_ENTRIES = 500

# --- Supported crops (Kolar region focus) ---
SUPPORTED_CROPS = [
    "tomato", "ragi", "grape", "mulberry", "mango",
    "groundnut", "maize", "paddy", "jowar", "banana"
]

# --- Disease classes (matches model output) ---
DISEASE_CLASSES = [
    "Tomato_Bacterial_Spot",
    "Tomato_Early_Blight",
    "Tomato_Late_Blight",
    "Tomato_Leaf_Mold",
    "Tomato_Healthy",
    "Grape_Black_Rot",
    "Grape_Esca",
    "Grape_Leaf_Blight",
    "Grape_Healthy",
    "Maize_Common_Rust",
    "Maize_Northern_Leaf_Blight",
    "Maize_Healthy",
]

# --- App ---
DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 5000))
MAX_AUDIO_SIZE_MB = 10
MAX_IMAGE_SIZE_MB = 15
