import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
os.environ["COCHEM_DATA_DIR"] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))

from intake_processor import get_flinn_shelf, process_intake, generate_sds_content

REAL_IMAGE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../test.jpg'))

@pytest.mark.parametrize("hazard_class, expected_shelf", [
    ("Organic Flammable", "Flinn Organic #2"),
    ("Organic Acid", "Flinn Organic #1"),
    ("Organic Misc", "Flinn Organic #3"),
    ("Inorganic Acid", "Flinn Inorganic #9"),
    ("Inorganic Base", "Flinn Inorganic #4"),
    ("Inorganic Misc", "Flinn Inorganic #2"),
    ("Oxidizer", "Flinn Inorganic #6"),
    ("Toxic", "Flinn Inorganic #7"),
    ("Nonexistent Hazard", "UNKNOWN (Needs Lab Manager Review)"),
    ("UNKNOWN", "UNKNOWN (Needs Lab Manager Review)"),
])
def test_flinn_logic_matrix_resolution(hazard_class, expected_shelf, monkeypatch):
    """Test deterministic Flinn shelf resolution using real CSV."""
    # Ensure COCHEM_DATA_DIR points to the test data dir
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
    monkeypatch.setenv("COCHEM_DATA_DIR", data_dir)
    shelf = get_flinn_shelf(hazard_class)
    assert shelf == expected_shelf

@pytest.mark.parametrize("email", ["test@cumberland.edu", "lab@cumberland.edu"])
def test_process_intake_missing_api_key(email, monkeypatch):
    """Test process_intake with real image but no API key available."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable missing"):
        process_intake(REAL_IMAGE, email)

def test_generate_sds_content():
    """Test generating SDS content by hitting PubChem for a known chemical."""
    content = generate_sds_content("Aspirin")
    assert content is not None
    assert "Chemical: Aspirin" in content
    assert "CID:" in content
    assert "Synonyms:" in content
    
    # Test unknown chemical
    content_unknown = generate_sds_content("SomeFakeChemicalThatDoesNotExist12345")
    assert content_unknown is None

