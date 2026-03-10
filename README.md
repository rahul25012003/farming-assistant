# Farming Assistant: Voice-First AI & Computer Vision for Rural Karnataka

A voice-and-camera based farming assistant designed for low-literacy Kannada-speaking farmers in rural Karnataka, India. Built as a B.Tech CS final year project at UVCE, Bangalore.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## Problem Statement

Over 60% of farmers in rural Karnataka cannot comfortably read digital interfaces in English or even Kannada script. Existing agri-tech apps assume text literacy, leaving out the farmers who need help the most. They need a **voice-first, camera-assisted** tool that speaks their language and understands their problems.

This project was built after spending time with farmers in **Kolar district** who grow tomatoes, ragi, and grapes — and watching them struggle with text-heavy apps they couldn't use.

## Features

- **Kannada Voice Interaction** - Push-to-talk mic button, full conversation in Kannada using GCP Speech-to-Text / Text-to-Speech
- **Crop Disease Diagnosis** - Take a photo of a diseased leaf, get diagnosis + treatment advice spoken back in Kannada
- **Multi-Agent Backend** - Specialized agents for weather, soil, market prices, government schemes, and disease
- **Offline Caching** - SQLite-based cache so the app works even with spotty rural connectivity
- **Explainable AI** - GradCAM-style heatmaps show which part of the leaf triggered the diagnosis
- **Hyperlocal Weather** - Rain forecasts, spray windows, and irrigation advice for their specific taluk
- **Market Prices** - Current mandi rates so farmers know when to sell
- **Government Schemes** - Matches farmer profile to eligible schemes (PM-KISAN, Raitha Siri, etc.)

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    FARMER'S PHONE                         │
│  ┌─────────┐  ┌──────────┐  ┌─────────────────────────┐ │
│  │ Mic Btn  │  │ Camera   │  │  Audio Playback         │ │
│  └────┬─────┘  └────┬─────┘  └───────────▲─────────────┘ │
│       │              │                    │               │
└───────┼──────────────┼────────────────────┼───────────────┘
        │              │                    │
   ┌────▼─────┐  ┌─────▼──────┐  ┌─────────┴──────────┐
   │ GCP STT  │  │  /diagnose │  │    GCP TTS          │
   │ (kn-IN)  │  │  endpoint  │  │    (Kannada)        │
   └────┬─────┘  └─────┬──────┘  └─────────▲──────────┘
        │              │                    │
   ┌────▼──────────────▼────────────────────┴──────────┐
   │              FLASK APP (app.py)                     │
   │                                                     │
   │  ┌──────────────────────────────────────────────┐  │
   │  │         ORCHESTRATOR (orchestrator.py)        │  │
   │  │                                              │  │
   │  │  Intent Detection → Agent Routing → Response │  │
   │  └──┬───────┬───────┬───────┬───────┬───────────┘  │
   │     │       │       │       │       │               │
   │  ┌──▼──┐ ┌─▼──┐ ┌──▼──┐ ┌─▼──┐ ┌──▼───┐          │
   │  │Weather│ │Soil│ │Mkt │ │Sch.│ │Disease│          │
   │  │Agent │ │Agt │ │Agt │ │Agt │ │Agent  │          │
   │  └──┬──┘ └─┬──┘ └──┬──┘ └─┬──┘ └──┬───┘          │
   │     │       │       │       │       │               │
   │  ┌──▼──┐ ┌─▼────┐ ┌▼────┐ ┌▼────┐ ┌▼──────────┐  │
   │  │OWM  │ │Local │ │Mandi│ │JSON │ │TF Model + │  │
   │  │API  │ │Data  │ │API  │ │DB   │ │OpenCV     │  │
   │  └─────┘ └──────┘ └─────┘ └─────┘ └───────────┘  │
   │                                                     │
   │  ┌──────────────────────────────────────────────┐  │
   │  │     OFFLINE CACHE (SQLite)                    │  │
   │  └──────────────────────────────────────────────┘  │
   └─────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.9+, Flask |
| Speech | Google Cloud Speech-to-Text, Text-to-Speech (Kannada kn-IN) |
| Vision | OpenCV, TensorFlow 2.13, GradCAM |
| Agents | Custom multi-agent orchestrator (Google Agent Stack pattern) |
| Data | SQLite (cache), JSON (local data) |
| APIs | OpenWeatherMap, Agmarknet (mandi prices) |
| Deploy | Docker-ready, tested on Raspberry Pi 4 for kiosk mode |

## Getting Started

### Prerequisites

- Python 3.9+
- Google Cloud account with Speech-to-Text and Text-to-Speech APIs enabled
- OpenWeatherMap API key (free tier works)

### Installation

```bash
git clone https://github.com/rahul-kolar/farming-assistant.git
cd farming-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

1. Place your GCP service account JSON at `config/gcp-credentials.json`
2. Set your OpenWeatherMap API key in `.env`
3. Download the crop disease model (see models/README)

```bash
export GOOGLE_APPLICATION_CREDENTIALS="config/gcp-credentials.json"
```

### Running

```bash
python app.py
```

The server starts at `http://localhost:5000`. Open in a browser or use the Android companion app.

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/voice` | POST | Send Kannada audio, get audio response |
| `/diagnose` | POST | Send leaf image, get disease diagnosis |
| `/health` | GET | Health check |

## Demo Screenshots

> Screenshots coming soon - currently testing with farmers in Kolar taluk

| Voice Interaction | Disease Detection | Market Prices |
|---|---|---|
| *screenshot placeholder* | *screenshot placeholder* | *screenshot placeholder* |

## Project Structure

```
farming-assistant/
├── app.py                  # Main Flask application
├── config.py               # Configuration and constants
├── requirements.txt
├── agents/
│   ├── orchestrator.py     # Multi-agent orchestrator
│   ├── weather_agent.py    # Hyperlocal weather
│   ├── soil_agent.py       # Soil profiles & recommendations
│   ├── disease_agent.py    # Crop disease diagnosis
│   ├── market_agent.py     # Mandi/market prices
│   └── scheme_agent.py     # Government scheme matching
├── voice/
│   ├── speech_to_text.py   # GCP STT (Kannada)
│   └── text_to_speech.py   # GCP TTS (Kannada)
├── vision/
│   ├── disease_classifier.py  # TF model + GradCAM
│   └── image_utils.py        # Image preprocessing
├── cache/
│   └── offline_cache.py    # SQLite offline cache
├── data/
│   ├── karnataka_soil_profiles.json
│   ├── govt_schemes.json
│   └── treatments.json
└── tests/
    └── test_orchestrator.py
```

## How It Works

1. Farmer presses the mic button on their phone
2. Speaks in Kannada: *"Nanna tomato eleya mele kappuchikte bandide, enu madli?"* (Black spots appeared on my tomato leaves, what should I do?)
3. GCP Speech-to-Text transcribes the Kannada audio
4. Orchestrator detects intent → routes to Disease Agent
5. If a photo is attached, the TF model classifies the disease
6. Treatment info is fetched and composed in Kannada
7. GCP Text-to-Speech converts the response to audio
8. Farmer hears the advice in their own language

## Future Roadmap

- [ ] Android companion app with offline model (TFLite)
- [ ] WhatsApp Business API integration (farmers already use WhatsApp)
- [ ] Tulu and Telugu language support
- [ ] Drone imagery integration for large farms
- [ ] Community knowledge sharing - farmer-to-farmer tips
- [ ] Integration with FPO (Farmer Producer Organization) networks
- [ ] Soil moisture IoT sensor real-time data
- [ ] Crop price prediction using historical mandi data

## Acknowledgements

- Farmers of Kolar, Malur, and Bangarpet taluks who patiently tested early prototypes
- Dr. [Professor Name], UVCE, for project guidance
- PlantVillage dataset for crop disease training data
- Google Cloud for Education credits

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built with care for the farmers who feed us.*
