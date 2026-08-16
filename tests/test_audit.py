import sys
import os
import pytest
from datetime import datetime, timedelta
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from audit_validator import process_audit_photo

REAL_IMAGE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../test.jpg'))

@pytest.fixture
def missing_exif_photo(tmp_path):
    img_path = tmp_path / "missing_exif.jpg"
    img = Image.open(REAL_IMAGE)
    # Strip EXIF by saving data without EXIF payload
    data = list(img.getdata())
    image_without_exif = Image.new(img.mode, img.size)
    image_without_exif.putdata(data)
    image_without_exif.save(img_path)
    return str(img_path)

@pytest.fixture
def outdated_exif_photo():
    # test.jpg natively has EXIF 2023:01:01, which is outdated
    return REAL_IMAGE

@pytest.fixture
def valid_exif_photo(tmp_path):
    img_path = tmp_path / "valid.jpg"
    img = Image.open(REAL_IMAGE)
    exif = img.getexif()
    dt = datetime.now() - timedelta(hours=1)
    exif[36867] = dt.strftime('%Y:%m:%d %H:%M:%S')
    img.save(img_path, exif=exif)
    return str(img_path)

@pytest.mark.parametrize("item_type", ["eyewash", "carboy"])
def test_missing_exif(missing_exif_photo, item_type):
    """Ensure missing EXIF data is rejected using real images."""
    result = process_audit_photo(missing_exif_photo, item_type)
    assert result is False

@pytest.mark.parametrize("item_type", ["eyewash", "carboy"])
def test_outdated_exif(outdated_exif_photo, item_type):
    """Ensure outdated photos are rejected using real EXIF logic."""
    result = process_audit_photo(outdated_exif_photo, item_type)
    assert result is False

@pytest.mark.parametrize("item_type", ["eyewash", "carboy"])
def test_valid_audit_missing_api_key(valid_exif_photo, item_type, monkeypatch):
    """Test valid EXIF but no API key available."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable missing"):
        process_audit_photo(valid_exif_photo, item_type)
