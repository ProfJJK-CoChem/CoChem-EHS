import os
import logging
import PyPDF2
from utils.pdf_generator import generate_qr_cover_sheet
from utils.gcp_auth import get_drive_service, send_email
from utils.paths import get_artifacts_dir

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_sds_batch() -> None:
    """Merge OSHA 16-section SDS pages into a packet."""
    logger.info("Starting SDS Friday Batch Job")
    
    drive_service = get_drive_service()
    
    # In a real environment we would query by folder ID for /SDS_Archive/Pending
    # For now, search for all PDF files in the root that have "SDS" in the name
    query = "name contains 'SDS' and mimeType='application/pdf'"
    try:
        results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
    except Exception as e:
        logger.error(f"Failed to query Drive for SDS files: {e}")
        return
        
    if not items:
        logger.info("No pending SDS files found in Drive.")
        return
        
    merger = PyPDF2.PdfMerger()
    downloaded_files = []
    
    for item in items:
        file_id = item['id']
        file_name = item['name']
        logger.info(f"Downloading {file_name}...")
        
        try:
            request = drive_service.files().get_media(fileId=file_id)
            file_path = get_artifacts_dir() / file_name
            with open(file_path, "wb") as f:
                f.write(request.execute())
        except Exception as e:
            logger.error(f"Failed to download {file_name}: {e}")
            continue
            
        # Truncate logic (OSHA first 16 sections are usually pages 1-8 depending on vendor)
        # We append up to the first 8 pages to save toner
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            pages_to_add = min(8, len(reader.pages))
            merger.append(fileobj=f, pages=(0, pages_to_add))
            
        downloaded_files.append(file_path)

    merged_pdf_path = get_artifacts_dir() / "merged_sds_batch.pdf"
    with open(merged_pdf_path, "wb") as f:
        merger.write(f)
        
    # Generate QR cover sheet
    webhook_url = os.environ.get("SDS_WEBHOOK_URL")
    if not webhook_url:
        logger.error("[MISSING DATA] SDS_WEBHOOK_URL missing.")
        raise ValueError("SDS_WEBHOOK_URL missing")
    cover_pdf = get_artifacts_dir() / "cover_sheet.pdf"
    generate_qr_cover_sheet(f"Batch contains {len(items)} SDS files.", webhook_url, str(cover_pdf))
    
    # Final assembly: Cover sheet + Merged SDS
    final_merger = PyPDF2.PdfMerger()
    final_merger.append(cover_pdf)
    final_merger.append(merged_pdf_path)
    final_batch_path = get_artifacts_dir() / "FINAL_SDS_BATCH.pdf"
    
    with open(final_batch_path, "wb") as f:
        final_merger.write(f)
        
    printer_email = os.environ.get("PRINTER_EMAIL")
    if not printer_email:
        logger.error("[MISSING DATA] PRINTER_EMAIL missing.")
        raise ValueError("PRINTER_EMAIL missing")
    
    logger.info(f"Emailing finalized packet to {printer_email}...")
    send_email(printer_email, "Friday SDS Batch", "Please print and binder these SDS pages.", attachment_path=str(final_batch_path))
    
    # Cleanup
    for f in downloaded_files + [merged_pdf_path, cover_pdf, final_batch_path]:
        if os.path.exists(f):
            os.remove(f)
            
if __name__ == "__main__":
    process_sds_batch()
