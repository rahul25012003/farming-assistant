"""
Disease Agent - Crop disease identification and treatment.
Uses TF model for image classification, returns treatment in Kannada.
"""
import json
import os
from vision.disease_classifier import DiseaseClassifier
import config


class DiseaseAgent:
    def __init__(self):
        self.classifier = DiseaseClassifier()
        treatments_path = os.path.join(os.path.dirname(__file__), "..", "data", "treatments.json")
        with open(treatments_path, "r", encoding="utf-8") as f:
            self.treatments = json.load(f)

    def diagnose_image(self, image_path):
        """Full pipeline: classify image → get treatment → format response."""
        result = self.classifier.classify(image_path)

        if result["confidence"] < config.CONFIDENCE_THRESHOLD:
            return {
                "disease": "uncertain",
                "confidence": result["confidence"],
                "response_kn": "ಚಿತ್ರ ಸ್ಪಷ್ಟವಾಗಿಲ್ಲ ಅಥವಾ ರೋಗ ಗುರುತಿಸಲು ಆಗಲಿಲ್ಲ. "
                               "ದಯವಿಟ್ಟು ಎಲೆಯ ಹತ್ತಿರದ ಫೋಟೋ ತೆಗೆಯಿರಿ.",
                "heatmap_path": result.get("heatmap_path"),
            }

        treatment = self.get_treatment(result["disease"])
        response_kn = self.format_kannada_response(result["disease"], treatment)

        return {
            "disease": result["disease"],
            "confidence": result["confidence"],
            "treatment": treatment,
            "response_kn": response_kn,
            "heatmap_path": result.get("heatmap_path"),
        }

    def get_treatment(self, disease_name):
        """Look up treatment info for a disease."""
        treatment = self.treatments.get(disease_name)
        if not treatment:
            print(f"[DISEASE] No treatment found for: {disease_name}")
            return {
                "name_kn": disease_name,
                "treatment_kn": "ಈ ರೋಗಕ್ಕೆ ಚಿಕಿತ್ಸೆ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ. ಹತ್ತಿರದ ಕೃಷಿ ಕೇಂದ್ರಕ್ಕೆ ಭೇಟಿ ನೀಡಿ.",
                "chemicals": [],
                "organic_option": "",
            }
        return treatment

    def handle_text_query(self, query):
        """Handle text-only disease queries (no image)."""
        # Try to match disease symptoms from the query
        # This is a rough keyword match - works okay for common queries
        symptom_map = {
            "ಕಪ್ಪು ಚುಕ್ಕೆ": "Tomato_Bacterial_Spot",
            "ಹಳದಿ ಎಲೆ": "Tomato_Early_Blight",
            "ಬಿಳಿ ಪುಡಿ": "Grape_Esca",
            "ತುಕ್ಕು": "Maize_Common_Rust",
            "ಸೊರಗು": "Tomato_Late_Blight",
            "black spot": "Tomato_Bacterial_Spot",
            "yellow leaf": "Tomato_Early_Blight",
            "rust": "Maize_Common_Rust",
        }

        for symptom, disease in symptom_map.items():
            if symptom in query.lower():
                treatment = self.get_treatment(disease)
                return self.format_kannada_response(disease, treatment)

        return ("ರೋಗ ಗುರುತಿಸಲು ಎಲೆಯ ಫೋಟೋ ತೆಗೆಯಿರಿ. "
                "ಫೋಟೋ ಇಲ್ಲದೆ ನಿಖರವಾಗಿ ಹೇಳಲು ಕಷ್ಟ.")

    def format_kannada_response(self, disease_name, treatment):
        """Format a complete Kannada response about the disease and treatment."""
        name_kn = treatment.get("name_kn", disease_name)
        response = f"ಇದು {name_kn} ರೋಗ ಇರಬಹುದು. "

        if treatment.get("treatment_kn"):
            response += treatment["treatment_kn"] + " "

        if treatment.get("chemicals"):
            chemicals = ", ".join(treatment["chemicals"][:2])  # Max 2 chemicals to keep it simple
            response += f"ಔಷಧಿ: {chemicals}. "

        if treatment.get("organic_option"):
            response += f"ಸಾವಯವ ಪರ್ಯಾಯ: {treatment['organic_option']}"

        return response
