from datetime import datetime, timedelta
import logging
from PIL import Image
from PIL.ExifTags import TAGS
from utils.gemini_client import verify_audit_photo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_exif_datetime(image_path: str) -> datetime | None:
    """Extract DateTimeOriginal from EXIF."""
    try:
        image = Image.open(image_path)
        exifdata = image.getexif()
        if exifdata is not None:
            for tag_id in exifdata:
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'DateTimeOriginal':
                    return datetime.strptime(exifdata.get(tag_id), '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        logger.error(f"Failed to extract EXIF: {e}")
    return None

def process_audit_photo(image_path: str, item_type: str) -> bool:
    """Validate EXIF and verify photo contents visually."""
    dt = get_exif_datetime(image_path)
    if not dt:
        logger.error("Audit Rejected: Photo stripped of EXIF data.")
        return False
        
    if datetime.now() - dt > timedelta(hours=48):
        logger.error("Audit Rejected: Photo is older than 48 hours.")
        return False
        
    if item_type == "eyewash":
        prompt = "Does this image clearly show an eyewash station with water actively flowing out of the nozzles?"
    elif item_type == "carboy":
        prompt = "Does this image clearly show an open waste carboy?"
    else:
        prompt = "Is this a valid safety check?"
        
    is_valid = verify_audit_photo(image_path, prompt)
    if is_valid:
        logger.info("Audit VERIFIED.")
    else:
        logger.warning("Audit Rejected: Visual verification failed.")
        
    return is_valid

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate EXIF and verify photo contents visually.")
    parser.add_argument("--image_path", required=True, help="Path to the audit photo")
    parser.add_argument("--item_type", required=True, help="Type of item audited")
    args = parser.parse_args()
    process_audit_photo(args.image_path, args.item_type)
