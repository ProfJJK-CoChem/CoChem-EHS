import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from waste_processor import process_waste_dictation, check_explosive_incompatibility
from utils.gemini_client import WasteDictation, Constituent

def test_explosive_incompatibility():
    """Test explosive logic using data structures directly."""
    # Explosive
    data_exp = WasteDictation(
        constituents=[Constituent(name="Nitric acid", volume="1L"), Constituent(name="ethanol", volume="500mL")],
        epa_waste_codes=[]
    )
    assert check_explosive_incompatibility(data_exp) is True
    
    # Safe
    data_safe = WasteDictation(
        constituents=[Constituent(name="Hydrochloric acid", volume="1L"), Constituent(name="water", volume="500mL")],
        epa_waste_codes=[]
    )
    assert check_explosive_incompatibility(data_safe) is False

@pytest.mark.parametrize("dictation", [
    "I have nitric acid and ethanol.",
    "500mL of acetone and 200mL of water.",
    "Dispose of 1L of sulfuric acid.",
    "Nitric acid, organic waste.",
    "A small amount of unknown organic."
])
def test_waste_processing_missing_api_key(dictation, monkeypatch):
    """
    Test that process_waste_dictation handles dictation input, 
    expecting an exception since no API key is available and mocking is strictly forbidden.
    """
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable missing"):
        process_waste_dictation(dictation)

from waste_processor import check_explosive_incompatibility
from utils.gemini_client import WasteDictation, Constituent

def test_explosive_incompatibility():
    """Test the business logic for explosive incompatibilities directly."""
    # Explosive mixture
    data = WasteDictation(
        constituents=[Constituent(name="nitric acid", volume="100mL"), Constituent(name="ethanol", volume="50mL")],
        epa_waste_codes=[]
    )
    assert check_explosive_incompatibility(data) is True

    # Safe mixture
    data_safe = WasteDictation(
        constituents=[Constituent(name="hydrochloric acid", volume="100mL"), Constituent(name="water", volume="500mL")],
        epa_waste_codes=[]
    )
    assert check_explosive_incompatibility(data_safe) is False
