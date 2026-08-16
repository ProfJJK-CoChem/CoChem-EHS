import os
import json
import logging
import base64
import mimetypes
from email.message import EmailMessage
from typing import Optional, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_credentials() -> Any:
    """Retrieve and build GCP credentials from the environment variable."""
    creds_json = os.environ.get("GCP_CREDENTIALS")
    if not creds_json:
        logger.error("[MISSING DATA] GCP_CREDENTIALS environment variable is not set.")
        raise ValueError("GCP_CREDENTIALS environment variable missing.")
    
    try:
        creds_info = json.loads(creds_json)
        return service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    except Exception as e:
        logger.error(f"Failed to load GCP credentials: {e}")
        raise

def get_sheets_service() -> Any:
    """Build and return the Google Sheets API service."""
    creds = get_credentials()
    return build('sheets', 'v4', credentials=creds)

def get_drive_service() -> Any:
    """Build and return the Google Drive API service."""
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)

def get_gmail_service() -> Any:
    """Build and return the Google Gmail API service."""
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)

def send_email(to_email: str, subject: str, body: str, attachment_path: str | None = None) -> None:
    """Sends an email with an optional attachment using the Gmail API."""
    service = get_gmail_service()
    message = EmailMessage()
    message.set_content(body)
    message['To'] = to_email
    message['Subject'] = subject
    
    if attachment_path and os.path.exists(attachment_path):
        ctype, encoding = mimetypes.guess_type(attachment_path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(attachment_path, 'rb') as fp:
            msg_data = fp.read()
        message.add_attachment(msg_data, maintype=maintype, subtype=subtype, filename=os.path.basename(attachment_path))
        
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    try:
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        logger.info(f"Message sent successfully. Id: {send_message['id']}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise
