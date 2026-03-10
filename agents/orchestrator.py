"""
Multi-Agent Orchestrator
Routes farmer queries to the appropriate agent(s) based on intent detection.
"""
import re
from agents.weather_agent import WeatherAgent
from agents.soil_agent import SoilAgent
from agents.disease_agent import DiseaseAgent
from agents.market_agent import MarketAgent
from agents.scheme_agent import SchemeAgent


class Orchestrator:
    def __init__(self):
        self.weather = WeatherAgent()
        self.soil = SoilAgent()
        self.disease = DiseaseAgent()
        self.market = MarketAgent()
        self.scheme = SchemeAgent()

        # Kannada keywords → intent mapping
        # TODO: Replace this with a proper NLU model, keyword matching is fragile
        self.intent_keywords = {
            "weather": [
                "ಮಳೆ", "ಹವಾಮಾನ", "ಬಿಸಿಲು", "ಚಳಿ", "ಗಾಳಿ", "ತೇವಾಂಶ",
                "rain", "weather", "temperature", "humidity"
            ],
            "soil": [
                "ಮಣ್ಣು", "ಗೊಬ್ಬರ", "ರಸಗೊಬ್ಬರ", "ಬೆಳೆ", "ಬಿತ್ತನೆ",
                "soil", "fertilizer", "crop", "sowing"
            ],
            "disease": [
                "ರೋಗ", "ಕೀಟ", "ಕಪ್ಪು", "ಹಳದಿ", "ಎಲೆ", "ಸೊರಗು", "ಹುಳ",
                "disease", "pest", "leaf", "spot", "wilt"
            ],
            "market": [
                "ಬೆಲೆ", "ಮಂಡಿ", "ಮಾರಾಟ", "ದರ", "ರೇಟ್",
                "price", "market", "sell", "rate", "mandi"
            ],
            "scheme": [
                "ಯೋಜನೆ", "ಸರ್ಕಾರ", "ಸಹಾಯಧನ", "ವಿಮೆ", "ಪಿಎಂ",
                "scheme", "government", "subsidy", "insurance", "PM"
            ],
        }

    def detect_intent(self, query):
        """Simple keyword-based intent detection. Returns list of matched intents."""
        query_lower = query.lower()
        intents = []

        for intent, keywords in self.intent_keywords.items():
            for kw in keywords:
                if kw.lower() in query_lower:
                    intents.append(intent)
                    break

        if not intents:
            # Default to weather + general advice if we can't figure out intent
            intents = ["weather"]
            print(f"[ORCH] No intent matched for: {query[:60]}... defaulting to weather")

        return intents

    def process(self, query, location=None):
        """
        Main processing pipeline.
        Detects intent, routes to agents, combines responses.
        """
        intents = self.detect_intent(query)
        print(f"[ORCH] Detected intents: {intents} for query: {query[:80]}")

        responses = []

        for intent in intents:
            try:
                if intent == "weather":
                    resp = self.weather.get_forecast(location)
                    responses.append(resp)
                elif intent == "soil":
                    # Try to extract district name from query
                    district = self._extract_district(query)
                    resp = self.soil.get_soil_info(district)
                    responses.append(resp)
                elif intent == "disease":
                    # Text-only disease query (no image)
                    resp = self.disease.handle_text_query(query)
                    responses.append(resp)
                elif intent == "market":
                    crop = self._extract_crop(query)
                    resp = self.market.get_prices(crop)
                    responses.append(resp)
                elif intent == "scheme":
                    resp = self.scheme.find_schemes(query)
                    responses.append(resp)
            except Exception as e:
                print(f"[ORCH] Agent {intent} failed: {e}")
                responses.append(f"ಕ್ಷಮಿಸಿ, {intent} ಮಾಹಿತಿ ಸಿಗಲಿಲ್ಲ.")  # Sorry, couldn't get info

        combined = " ".join(responses)
        return combined if combined.strip() else "ಕ್ಷಮಿಸಿ, ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಅರ್ಥವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಹೇಳಿ."

    def _extract_district(self, query):
        """Try to find a Karnataka district name in the query."""
        districts = ["kolar", "bengaluru", "tumkur", "mandya", "hassan", "mysuru",
                      "ಕೋಲಾರ", "ಬೆಂಗಳೂರು", "ತುಮಕೂರು", "ಮಂಡ್ಯ", "ಹಾಸನ", "ಮೈಸೂರು"]
        for d in districts:
            if d.lower() in query.lower():
                return d
        return "kolar"  # default to our home district

    def _extract_crop(self, query):
        """Try to find a crop name in the query."""
        crops = {
            "ಟೊಮೇಟೊ": "tomato", "tomato": "tomato",
            "ರಾಗಿ": "ragi", "ragi": "ragi",
            "ದ್ರಾಕ್ಷಿ": "grape", "grape": "grape",
            "ಮೆಕ್ಕೆಜೋಳ": "maize", "maize": "maize",
            "ಭತ್ತ": "paddy", "paddy": "paddy",
            "ಶೇಂಗಾ": "groundnut", "groundnut": "groundnut",
        }
        for kw, crop in crops.items():
            if kw.lower() in query.lower():
                return crop
        return "tomato"  # most common in Kolar
