import os
import csv
import logging
from typing import Optional
import pubchempy as pcp
from utils.gcp_auth import get_sheets_service, send_email, get_drive_service
from utils.gemini_client import extract_label_info
from utils.paths import get_data_dir, get_artifacts_dir
import googleapiclient.http

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_flinn_shelf(hazard_class: str) -> str:
    """Map hazard class to physical shelf deterministically."""
    matrix_path = get_data_dir() / 'flinn_logic_matrix.csv'
    try:
        with open(matrix_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['hazard_class'].lower() == hazard_class.lower():
                    return row['flinn_shelf']
    except FileNotFoundError:
        logger.error(f"[MISSING DATA] flinn_logic_matrix.csv not found at {matrix_path}")
        raise
    return "UNKNOWN (Needs Lab Manager Review)"

def generate_sds_content(chemical_name: str) -> Optional[str]:
    """Fetch chemical data from PubChem and generate SDS content."""
    try:
        compounds = pcp.get_compounds(chemical_name, 'name')
        if compounds:
            c = compounds[0]
            sds_content = f"Chemical: {chemical_name}\nCID: {c.cid}\nSynonyms: {', '.join(c.synonyms[:5])}\n"
            return sds_content
        else:
            logger.warning(f"No PubChem data found for {chemical_name}")
            return None
    except Exception as e:
        logger.error(f"Failed to fetch from PubChem: {e}")
        return None

def process_intake(image_path: str, submitter_email: str) -> None:
    """Process a chemical intake from a label image."""
    logger.info("Extracting label info...")
    label_info = extract_label_info(image_path)
    
    # We now extract hazard class via Gemini directly from the label
    hazard_class = label_info.hazard_class 
    shelf = get_flinn_shelf(hazard_class)
    
    logger.info(f"Appending to Inventory. Shelf: {shelf}")
    
    sheet_id = os.environ.get("INVENTORY_SHEET_ID")
    if not sheet_id:
        logger.error("[MISSING DATA] INVENTORY_SHEET_ID environment variable not set")
        raise ValueError("INVENTORY_SHEET_ID missing")
        
    sheets_service = get_sheets_service()
    
    chemical_name = label_info.chemical_name
    
    values = [[
        chemical_name,
        label_info.cas_number,
        label_info.vendor,
        label_info.volume,
        shelf
    ]]
    
    body = {'values': values}
    
    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="Sheet1!A1",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        logger.info("Inventory updated successfully.")
    except Exception as e:
        logger.error(f"Failed to update sheet: {e}")
        raise

    # SDS Fetching via PubChem
    logger.info("Fetching chemical data from PubChem...")
    sds_content = generate_sds_content(chemical_name)
    if sds_content:
        try:
            # Save locally then upload to Google Drive Pending folder
            sds_filename = get_artifacts_dir() / f"{chemical_name}_SDS_Info.txt"
            with open(sds_filename, "w") as f:
                f.write(sds_content)
                
            drive_service = get_drive_service()
            file_metadata = {
                'name': f"{chemical_name}_SDS_Info.txt",
                'parents': ['root'] # In reality, we'd look up the /SDS_Archive/Pending folder ID
            }
            media = MediaFileUpload(str(sds_filename), mimetype='text/plain')
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            logger.info(f"SDS data uploaded to Drive with ID: {file.get('id')}")
            os.remove(sds_filename)
        except Exception as e:
            logger.error(f"Failed to upload to Drive: {e}")

    # Email submitter
    logger.info("Emailing submitter...")
    body_text = f"Chemical logged: {chemical_name}.\nPlace on physical shelf: [{shelf}]."
    try:
        send_email(submitter_email, "Chemical Intake Processed", body_text)
    except Exception as e:
        logger.error(f"Failed to email submitter: {e}")

import sys
import argparse
from googleapiclient.http import MediaFileUpload

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a chemical intake from a label image.")
    parser.add_argument("--image_path", required=True, help="Path to the label image")
    parser.add_argument("--submitter_email", required=True, help="Email of the submitter")
    args = parser.parse_args()
    process_intake(args.image_path, args.submitter_email)
