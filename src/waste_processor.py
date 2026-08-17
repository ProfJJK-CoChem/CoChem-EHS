import os
import logging
from utils.gemini_client import parse_waste_dictation, WasteDictation, check_compatibility_with_gemini
from utils.pdf_generator import generate_waste_tag
from utils.gcp_auth import send_email
from utils.paths import get_artifacts_dir

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_explosive_incompatibility(data: WasteDictation) -> bool:
    """Check for incompatible waste mixtures that could be explosive."""
    return check_compatibility_with_gemini(data)

def process_waste_dictation(dictation: str) -> None:
    """Process dictated text and generate a Waste Tag."""
    logger.info("Parsing waste dictation...")
    data = parse_waste_dictation(dictation)
    
    # Check for incompatibilities
    if check_explosive_incompatibility(data):
        constituents_str = " ".join([c.name.lower() for c in data.constituents])
        logger.error("EXPLOSIVE INCOMPATIBILITY DETECTED. Halting tag generation.")
        lab_manager_email = os.environ.get("LAB_MANAGER_EMAIL", "manager@cumberland.edu")
        send_email(lab_manager_email, "URGENT: Explosive Waste Mixture Prevented", 
                   f"A user attempted to mix incompatible waste: {constituents_str}")
        return
        
    output_pdf = get_artifacts_dir() / "waste_tag.pdf"
    logger.info("Generating PDF tag...")
    generate_waste_tag(data, str(output_pdf))
    
    printer_email = os.environ.get("PRINTER_EMAIL")
    if not printer_email:
        logger.error("[MISSING DATA] PRINTER_EMAIL missing.")
        raise ValueError("PRINTER_EMAIL missing")
        
    logger.info(f"Emailing tag to {printer_email}")
    send_email(printer_email, "Waste Tag Output", "Please print the attached waste tag.", attachment_path=str(output_pdf))
    
    logger.info("Waste processing complete.")
    if os.path.exists(output_pdf):
        os.remove(output_pdf)

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process dictated text and generate a Waste Tag.")
    parser.add_argument("--dictation", required=True, help="The dictated text")
    args = parser.parse_args()
    process_waste_dictation(args.dictation)
