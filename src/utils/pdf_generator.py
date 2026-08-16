import os
from reportlab.lib.pagesizes import landscape, letter, inch
from reportlab.pdfgen import canvas
import qrcode
import tempfile
import uuid
from utils.paths import get_artifacts_dir

from typing import Any

def generate_waste_tag(data: Any, output_path: str) -> str:
    """Generate a 4x6 inch PDF Waste Tag with constituents and EPA codes."""
    # 4x6 inches is 288x432 points
    c = canvas.Canvas(output_path, pagesize=(432, 288))
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(10, 260, "HAZARDOUS WASTE TAG")
    
    c.setFont("Helvetica", 12)
    y_pos = 230
    
    c.drawString(10, y_pos, "Constituents:")
    y_pos -= 20
    for constituent in getattr(data, "constituents", []):
        name = getattr(constituent, "name", "Unknown")
        vol = getattr(constituent, "volume", "Unknown")
        c.drawString(20, y_pos, f"- {name}: {vol}")
        y_pos -= 15
        
    y_pos -= 10
    c.drawString(10, y_pos, "EPA Waste Codes:")
    codes = ", ".join(getattr(data, "epa_waste_codes", []))
    c.drawString(20, y_pos - 15, codes)
    
    c.save()
    return output_path

def generate_qr_cover_sheet(pages_info: str, webhook_url: str, output_path: str) -> str:
    """Generate a cover sheet with a QR code for the SDS batch routing."""
    c = canvas.Canvas(output_path, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 24)
    c.drawString(inch, 10 * inch, "SDS Batch Routing Cover Sheet")
    
    c.setFont("Helvetica", 14)
    c.drawString(inch, 9 * inch, pages_info)
    c.drawString(inch, 8.5 * inch, "Scan the QR code below to confirm deployment:")
    
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(webhook_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR to artifacts and draw on canvas
    temp_img_path = get_artifacts_dir() / f"qr_{uuid.uuid4().hex}.png"
    img.save(str(temp_img_path))
    
    c.drawImage(str(temp_img_path), inch, 5 * inch, width=3*inch, height=3*inch)
    
    c.save()
    
    # Cleanup temp image
    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)
        
    return output_path
