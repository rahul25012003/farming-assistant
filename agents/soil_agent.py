"""
Soil Agent - Regional soil profiles and crop recommendations.
Uses hardcoded Karnataka district data + IoT sensor stub.
"""
import json
import os


class SoilAgent:
    def __init__(self):
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "karnataka_soil_profiles.json")
        with open(data_path, "r", encoding="utf-8") as f:
            self.profiles = json.load(f)

    def get_soil_info(self, district="kolar"):
        """Return soil profile and recommendations for a district."""
        district_lower = district.lower()

        # Map Kannada district names to English keys
        kannada_map = {
            "ಕೋಲಾರ": "kolar", "ಬೆಂಗಳೂರು": "bengaluru_rural",
            "ತುಮಕೂರು": "tumkur", "ಮಂಡ್ಯ": "mandya",
            "ಹಾಸನ": "hassan", "ಮೈಸೂರು": "mysuru",
        }
        if district_lower in kannada_map:
            district_lower = kannada_map[district_lower]

        profile = self.profiles.get(district_lower)
        if not profile:
            return f"ಕ್ಷಮಿಸಿ, {district} ಜಿಲ್ಲೆಯ ಮಣ್ಣಿನ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ."

        return self._format_kannada(profile, district)

    def get_soil_from_sensor(self, sensor_id):
        """
        Stub for IoT soil sensor integration.
        TODO: Integrate with Arduino/ESP32 soil moisture + pH sensors
        deployed in Kolar test farms.
        """
        # Placeholder - would read from MQTT broker or Firebase
        return {
            "moisture": 45.2,
            "ph": 6.5,
            "nitrogen": "medium",
            "phosphorus": "low",
            "potassium": "medium",
            "timestamp": "2024-01-15T10:30:00",
        }

    def _format_kannada(self, profile, district):
        """Format soil profile into Kannada advice."""
        response = f"{district} ಜಿಲ್ಲೆಯ ಮಣ್ಣು: {profile['soil_type_kn']}. "
        response += f"pH ಮಟ್ಟ: {profile['ph_range']}. "
        response += f"ಶಿಫಾರಸು ಬೆಳೆಗಳು: {', '.join(profile['recommended_crops_kn'])}. "

        if profile.get("fertilizer_advice_kn"):
            response += f"ಗೊಬ್ಬರ ಸಲಹೆ: {profile['fertilizer_advice_kn']}"

        return response
