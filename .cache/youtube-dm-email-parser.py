#!/usr/bin/env python3
"""
Gmail to DM Queue Parser
Reads YouTube DM notification emails and appends to youtube-dm-inbox.jsonl
Install: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import json
import sys
import base64
import email
import re
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    HAS_GMAIL_API = True
except ImportError:
    HAS_GMAIL_API = False
    print("ERROR: Missing Gmail API libraries. Run:", file=sys.stderr)
    print("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client", file=sys.stderr)
    sys.exit(1)

CACHE_DIR = Path.home() / ".openclaw/workspace/.cache"
DM_INBOX_QUEUE = CACHE_DIR / "youtube-dm-inbox.jsonl"
GMAIL_CREDS = Path.home() / ".openclaw/workspace/.secrets/gmail-credentials.json"
GMAIL_TOKEN = Path.home() / ".openclaw/workspace/.secrets/gmail-token.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def authenticate_gmail():
    """Authenticate with Gmail API."""
    creds = None
    
    # Load existing token
    if GMAIL_TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(GMAIL_TOKEN), SCOPES)
    
    # Or authenticate with OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not GMAIL_CREDS.exists():
                print("ERROR: Gmail credentials not found at:", GMAIL_CREDS, file=sys.stderr)
                print("Download from Google Cloud Console and save to .secrets/gmail-credentials.json", file=sys.stderr)
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(str(GMAIL_CREDS), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save token for next time
        GMAIL_TOKEN.parent.mkdir(parents=True, exist_ok=True)
        with open(GMAIL_TOKEN, "w") as f:
            f.write(creds.to_json())
    
    return creds

def get_gmail_service(creds):
    """Build Gmail API service."""
    return build("gmail", "v1", credentials=creds)

def extract_channel_id(email_text):
    """Try to extract YouTube channel ID from email."""
    # YouTube DM notifications usually include the channel ID
    match = re.search(r'UC[a-zA-Z0-9_-]{21}', email_text)
    if match:
        return match.group()
    return "unknown"

def extract_sender_name(headers):
    """Extract sender name from email headers."""
    from_header = headers.get("From", "Unknown <unknown@example.com>")
    # Parse "Name <email@domain.com>" format
    match = re.search(r'^([^<]+)', from_header)
    if match:
        return match.group(1).strip().strip('"')
    return "Unknown"

def parse_dm_email(message_id, service):
    """Parse a single Gmail message as DM."""
    try:
        # Fetch full message
        msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
        
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        subject = headers.get("Subject", "")
        
        # Only process YouTube DM notifications
        if "youtube" not in subject.lower() and "message" not in subject.lower():
            return None
        
        # Extract body
        body_text = ""
        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode("utf-8")
                    break
        elif "body" in msg["payload"]:
            data = msg["payload"]["body"].get("data", "")
            if data:
                body_text = base64.urlsafe_b64decode(data).decode("utf-8")
        
        # Parse YouTube DM from email body
        # YouTube DM email format typically includes sender name and message
        lines = body_text.split("\n")
        
        # Extract message (usually after sender info)
        message_text = "\n".join(lines).strip()
        
        # Remove common email footers
        message_text = re.sub(r'(--+.*View.*Reply.*)', '', message_text, flags=re.IGNORECASE | re.DOTALL)
        message_text = message_text.strip()
        
        if not message_text or len(message_text) < 3:
            return None
        
        dm = {
            "sender_name": extract_sender_name(headers),
            "sender_id": extract_channel_id(body_text),
            "text": message_text[:500],  # Truncate very long messages
            "received_at": headers.get("Date", datetime.now().isoformat() + "Z")
        }
        
        return dm
    
    except Exception as e:
        print(f"Error parsing message {message_id}: {e}", file=sys.stderr)
        return None

def append_to_queue(dm):
    """Append DM to input queue."""
    try:
        with open(DM_INBOX_QUEUE, "a") as f:
            f.write(json.dumps(dm) + "\n")
        return True
    except Exception as e:
        print(f"Error writing to queue: {e}", file=sys.stderr)
        return False

def mark_as_read(service, message_id):
    """Mark email as read in Gmail."""
    try:
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": [], "removeLabelIds": ["UNREAD"]}
        ).execute()
    except Exception as e:
        print(f"Warning: Could not mark as read: {e}", file=sys.stderr)

def run_parser(label="UNREAD"):
    """Main parser function."""
    if not HAS_GMAIL_API:
        print("ERROR: Gmail API not available", file=sys.stderr)
        return {"status": "error", "message": "Missing dependencies"}
    
    # Authenticate
    creds = authenticate_gmail()
    if not creds:
        return {"status": "error", "message": "Authentication failed"}
    
    service = get_gmail_service(creds)
    
    stats = {
        "status": "success",
        "emails_scanned": 0,
        "dms_extracted": 0,
        "dms_queued": 0,
        "errors": 0
    }
    
    try:
        # Search for YouTube DM notifications
        query = 'from:noreply-notification@youtube.com subject:(message OR dm) is:unread'
        results = service.users().messages().list(userId="me", q=query, maxResults=10).execute()
        
        messages = results.get("messages", [])
        stats["emails_scanned"] = len(messages)
        
        for msg in messages:
            dm = parse_dm_email(msg["id"], service)
            
            if dm:
                if append_to_queue(dm):
                    stats["dms_queued"] += 1
                    stats["dms_extracted"] += 1
                    # Mark as read in Gmail
                    mark_as_read(service, msg["id"])
                    print(f"✓ Queued DM from {dm['sender_name']}")
                else:
                    stats["errors"] += 1
            else:
                stats["errors"] += 1
    
    except Exception as e:
        stats["status"] = "error"
        stats["message"] = str(e)
        print(f"ERROR: {e}", file=sys.stderr)
    
    return stats

def generate_report(stats):
    """Generate report."""
    report = []
    report.append("=" * 60)
    report.append("GMAIL DM PARSER REPORT")
    report.append("=" * 60)
    report.append(f"Status: {stats['status'].upper()}")
    report.append(f"Timestamp: {datetime.now().isoformat()}Z")
    report.append("")
    report.append(f"Emails Scanned: {stats['emails_scanned']}")
    report.append(f"DMs Extracted: {stats['dms_extracted']}")
    report.append(f"DMs Queued: {stats['dms_queued']}")
    report.append(f"Errors: {stats['errors']}")
    report.append("")
    if stats.get("message"):
        report.append(f"Message: {stats['message']}")
    report.append("=" * 60)
    
    return "\n".join(report)

if __name__ == "__main__":
    stats = run_parser()
    report = generate_report(stats)
    print(report)
