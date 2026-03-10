"""
Market Agent - Mandi prices and selling advice.
Fetches from Agmarknet / data.gov.in API.
"""
import requests
from datetime import datetime
import config


class MarketAgent:
    def __init__(self):
        self.api_key = config.DATA_GOV_API_KEY
        self.base_url = config.AGMARKNET_BASE_URL
        self.default_mandi = config.DEFAULT_MANDI

        # Fallback hardcoded prices (updated weekly by us when API is down)
        # These are approximate Kolar mandi rates in INR per quintal
        self.fallback_prices = {
            "tomato": {"min": 800, "max": 2200, "modal": 1500, "unit": "quintal"},
            "ragi": {"min": 3200, "max": 3800, "modal": 3500, "unit": "quintal"},
            "grape": {"min": 3000, "max": 6000, "modal": 4500, "unit": "quintal"},
            "maize": {"min": 1800, "max": 2400, "modal": 2100, "unit": "quintal"},
            "groundnut": {"min": 5000, "max": 7000, "modal": 6000, "unit": "quintal"},
            "paddy": {"min": 1800, "max": 2200, "modal": 2000, "unit": "quintal"},
        }

    def get_prices(self, crop="tomato", mandi=None):
        """Fetch current mandi prices for a crop."""
        mandi = mandi or self.default_mandi

        try:
            prices = self._fetch_from_api(crop, mandi)
        except Exception as e:
            print(f"[MARKET] API failed, using fallback: {e}")
            prices = self.fallback_prices.get(crop)

        if not prices:
            return f"ಕ್ಷಮಿಸಿ, {crop} ಬೆಲೆ ಮಾಹಿತಿ ಸಿಗಲಿಲ್ಲ."

        return self._format_kannada(crop, prices, mandi)

    def _fetch_from_api(self, crop, mandi):
        """Fetch prices from data.gov.in Agmarknet API."""
        if not self.api_key:
            raise ValueError("No API key configured")

        resp = requests.get(self.base_url, params={
            "api-key": self.api_key,
            "format": "json",
            "filters[commodity]": crop.capitalize(),
            "filters[market]": mandi,
            "limit": 5,
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("records"):
            record = data["records"][0]
            return {
                "min": int(record.get("min_price", 0)),
                "max": int(record.get("max_price", 0)),
                "modal": int(record.get("modal_price", 0)),
                "unit": "quintal",
            }
        return None

    def _format_kannada(self, crop, prices, mandi):
        """Format price info as Kannada advice."""
        crop_names_kn = {
            "tomato": "ಟೊಮೇಟೊ", "ragi": "ರಾಗಿ", "grape": "ದ್ರಾಕ್ಷಿ",
            "maize": "ಮೆಕ್ಕೆಜೋಳ", "groundnut": "ಶೇಂಗಾ", "paddy": "ಭತ್ತ",
        }
        crop_kn = crop_names_kn.get(crop, crop)

        response = (f"{mandi} ಮಂಡಿಯಲ್ಲಿ {crop_kn} ದರ: "
                    f"ಕನಿಷ್ಠ ₹{prices['min']}, ಗರಿಷ್ಠ ₹{prices['max']}, "
                    f"ಸರಾಸರಿ ₹{prices['modal']} ಪ್ರತಿ {prices['unit']}.")

        # Simple selling advice based on modal price
        if crop == "tomato" and prices["modal"] > 2000:
            response += " ಬೆಲೆ ಒಳ್ಳೆಯದಿದೆ, ಮಾರಾಟ ಮಾಡಬಹುದು."
        elif crop == "tomato" and prices["modal"] < 1000:
            response += " ಬೆಲೆ ಕಡಿಮೆ ಇದೆ, ಸಾಧ್ಯವಾದರೆ ಒಂದೆರಡು ದಿನ ಕಾಯಿರಿ."

        return response
