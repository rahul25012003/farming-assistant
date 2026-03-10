"""
Scheme Agent - Government farming schemes for Karnataka farmers.
Matches farmer profile to eligible central + state schemes.
"""
import json
import os


class SchemeAgent:
    def __init__(self):
        schemes_path = os.path.join(os.path.dirname(__file__), "..", "data", "govt_schemes.json")
        with open(schemes_path, "r", encoding="utf-8") as f:
            self.schemes = json.load(f)

    def find_schemes(self, query="", farmer_profile=None):
        """Find relevant schemes based on query or farmer profile."""
        # If we have a farmer profile, filter by eligibility
        if farmer_profile:
            return self._match_by_profile(farmer_profile)

        # Otherwise do keyword matching against query
        matched = []
        for scheme in self.schemes:
            keywords = scheme.get("keywords", [])
            if any(kw.lower() in query.lower() for kw in keywords):
                matched.append(scheme)

        # If nothing matched, return top 3 most popular schemes
        if not matched:
            matched = self.schemes[:3]

        return self._format_kannada(matched)

    def _match_by_profile(self, profile):
        """Match schemes based on farmer profile (land size, crop, etc.)."""
        matched = []
        land_acres = profile.get("land_acres", 2)

        for scheme in self.schemes:
            max_land = scheme.get("max_land_acres", 999)
            if land_acres <= max_land:
                matched.append(scheme)

        return self._format_kannada(matched[:4])

    def _format_kannada(self, schemes):
        """Format scheme info in Kannada."""
        if not schemes:
            return "ಯಾವುದೇ ಯೋಜನೆ ಹೊಂದಾಣಿಕೆ ಆಗಲಿಲ್ಲ."

        parts = ["ನಿಮಗೆ ಅನ್ವಯವಾಗುವ ಯೋಜನೆಗಳು: "]
        for i, scheme in enumerate(schemes, 1):
            name_kn = scheme.get("name_kn", scheme["name"])
            benefit_kn = scheme.get("benefit_kn", "")
            parts.append(f"{i}. {name_kn}: {benefit_kn}")

        parts.append("ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗೆ ಹತ್ತಿರದ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರಕ್ಕೆ ಭೇಟಿ ನೀಡಿ.")
        return " ".join(parts)
