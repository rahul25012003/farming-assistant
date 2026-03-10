"""
Weather Agent - Hyperlocal weather for farming decisions.
Uses OpenWeatherMap API with Kolar as default location.
"""
import requests
from datetime import datetime
import config


class WeatherAgent:
    def __init__(self):
        self.api_key = config.OWM_API_KEY
        self.base_url = config.OWM_BASE_URL

    def get_forecast(self, location=None):
        """Fetch weather and return farming-relevant advice in Kannada."""
        if not location:
            location = config.DEFAULT_LOCATION

        try:
            # Current weather
            resp = requests.get(f"{self.base_url}/weather", params={
                "lat": location["lat"],
                "lon": location["lon"],
                "appid": self.api_key,
                "units": "metric",
            }, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]

            # 5-day forecast for rain prediction
            forecast_resp = requests.get(f"{self.base_url}/forecast", params={
                "lat": location["lat"],
                "lon": location["lon"],
                "appid": self.api_key,
                "units": "metric",
                "cnt": 8,  # next 24 hours (3-hour intervals)
            }, timeout=10)
            rain_expected = self._check_rain(forecast_resp.json())

            return self._format_kannada(temp, humidity, wind_speed, rain_expected, location["name"])

        except requests.RequestException as e:
            print(f"[WEATHER] API call failed: {e}")
            return "ಹವಾಮಾನ ಮಾಹಿತಿ ಸದ್ಯ ಲಭ್ಯವಿಲ್ಲ. ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕ ಪರಿಶೀಲಿಸಿ."

    def _check_rain(self, forecast_data):
        """Check if rain is expected in next 24 hours."""
        if "list" not in forecast_data:
            return False
        for entry in forecast_data["list"]:
            if "rain" in entry or any("rain" in w["main"].lower() for w in entry.get("weather", [])):
                return True
        return False

    def _format_kannada(self, temp, humidity, wind, rain_expected, location_name):
        """Format weather data into actionable Kannada advice."""
        response = f"{location_name} ಹವಾಮಾನ: ಉಷ್ಣಾಂಶ {temp}°C, ತೇವಾಂಶ {humidity}%."

        # Spray window advice
        if wind > 15:
            response += " ಗಾಳಿ ಜೋರಾಗಿದೆ, ಇಂದು ಸ್ಪ್ರೇ ಮಾಡಬೇಡಿ."
        elif humidity > 85:
            response += " ತೇವಾಂಶ ಹೆಚ್ಚಿದೆ, ಬೆಳಿಗ್ಗೆ ಸ್ಪ್ರೇ ಮಾಡಿ."
        else:
            response += " ಸ್ಪ್ರೇ ಮಾಡಲು ಒಳ್ಳೆಯ ಸಮಯ."

        # Rain advice
        if rain_expected:
            response += " ಮುಂದಿನ 24 ಗಂಟೆಯಲ್ಲಿ ಮಳೆ ನಿರೀಕ್ಷೆ ಇದೆ. ನೀರು ಹಾಯಿಸುವುದು ಬೇಡ."
        else:
            response += " ಮಳೆ ನಿರೀಕ್ಷೆ ಇಲ್ಲ."

        # Temperature-based crop advice
        if temp > 38:
            response += " ಬಿಸಿಲು ತುಂಬಾ ಇದೆ, ಸಂಜೆ ನೀರು ಹಾಯಿಸಿ."
        elif temp < 15:
            response += " ಚಳಿ ಇದೆ, ಬೆಳೆಗಳನ್ನು ಮುಚ್ಚಿ ಕಾಪಾಡಿ."

        return response
