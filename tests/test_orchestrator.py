"""
Tests for the multi-agent orchestrator.
Run: pytest tests/test_orchestrator.py -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from agents.orchestrator import Orchestrator


@pytest.fixture
def orch():
    return Orchestrator()


class TestIntentDetection:
    def test_weather_intent_kannada(self, orch):
        intents = orch.detect_intent("ಇಂದು ಮಳೆ ಬರುತ್ತಾ?")
        assert "weather" in intents

    def test_weather_intent_english(self, orch):
        intents = orch.detect_intent("Will it rain today?")
        assert "weather" in intents

    def test_disease_intent(self, orch):
        intents = orch.detect_intent("ಎಲೆ ಮೇಲೆ ಕಪ್ಪು ಚುಕ್ಕೆ ಬಂದಿದೆ")
        assert "disease" in intents

    def test_market_intent(self, orch):
        intents = orch.detect_intent("ಟೊಮೇಟೊ ಬೆಲೆ ಎಷ್ಟು?")
        assert "market" in intents

    def test_scheme_intent(self, orch):
        intents = orch.detect_intent("ಸರ್ಕಾರ ಯೋಜನೆ ಬಗ್ಗೆ ಹೇಳಿ")
        assert "scheme" in intents

    def test_soil_intent(self, orch):
        intents = orch.detect_intent("ಮಣ್ಣು ಯಾವ ರೀತಿ ಇದೆ?")
        assert "soil" in intents

    def test_default_intent(self, orch):
        """Unknown queries should default to weather."""
        intents = orch.detect_intent("ಹಲೋ ಹೇಗಿದ್ದೀರಿ")
        assert "weather" in intents


class TestCropExtraction:
    def test_extract_tomato_kannada(self, orch):
        crop = orch._extract_crop("ಟೊಮೇಟೊ ಬೆಲೆ ಎಷ್ಟು")
        assert crop == "tomato"

    def test_extract_ragi(self, orch):
        crop = orch._extract_crop("ragi rate enna")
        assert crop == "ragi"

    def test_default_crop(self, orch):
        crop = orch._extract_crop("ಬೆಲೆ ಹೇಳಿ")
        assert crop == "tomato"  # Kolar default


class TestDistrictExtraction:
    def test_extract_kolar(self, orch):
        district = orch._extract_district("Kolar district soil")
        assert district.lower() == "kolar"

    def test_extract_kannada_district(self, orch):
        district = orch._extract_district("ಮಂಡ್ಯ ಜಿಲ್ಲೆ ಮಣ್ಣು")
        assert district == "ಮಂಡ್ಯ"

    def test_default_district(self, orch):
        district = orch._extract_district("ಮಣ್ಣು ಹೇಗಿದೆ")
        assert district == "kolar"


class TestProcessing:
    def test_process_returns_string(self, orch):
        """Orchestrator should always return a non-empty string."""
        result = orch.process("ಹವಾಮಾನ ಹೇಗಿದೆ")
        assert isinstance(result, str)
        assert len(result) > 0
