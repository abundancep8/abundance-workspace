#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius channel.
Monitors for new comments, categorizes them, auto-responds, and logs to JSONL.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import re
from typing import Optional

# YouTube API
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Google API libraries not installed. Run:")
    print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Config
WORKSPACE = Path("/Users/abundance/.openclaw/workspace")
CACHE_DIR = WORKSPACE / ".cache"
CREDENTIALS_FILE = WORKSPACE / ".secrets" / "youtube-credentials.json"
TOKEN_FILE = WORKSPACE / ".secrets" / "youtube-token.json"
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"
CONFIG_FILE = WORKSPACE / ".config" / "youtube-monitor.json"

# YouTube API scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly", 
          "https://www.googleapis.com/auth/youtube"]

# Response templates
RESPONSE_TEMPLATES = {
    "question": """Thanks for the question! Here's how you can get started:
1. Check our getting started guide (link in bio)
2. Watch our intro video
3. Join our community Discord for live support

Feel free to reply with more questions!""",
    
    "praise": """Thank you so much for the kind words! 🙏 This means a lot to us and motivates us to keep creating.
Feel free to reach out anytime — we love hearing from our community!"""
}

# Category keywords
CATEGORY_KEYWORDS = {
    "question": [
        r"\bhow\s+(do|to|can)\b",
        r"\bwhat\s+(is|are)\b",
        r"\bwhere\b",
        r"\bwhen\b",
        r"\bwhy\b",
        r"\bcost\b",
        r"\bprice\b",
        r"\btimeline\b",
        r"\btools\b",
        r"\bget\s+started\b",
        r"\bstart\b",
        r"\bhow\s+much\b",
        r"\btutorial\b",
        r"\bhelp\b"
    ],
    "praise": [
        r"\bamazing\b",
        r"\binspiring\b",
        r"\bincredible\b",
        r"\blove\s+(this|it)\b",
        r"\bawesome\b",
        r"\bgreat\b",
        r"\bexcellent\b",
        r"\bwonderful\b",
        r"\bthanks?\s+for\b",
        r"\bappreciate\b",
        r"\b❤️\b",
        r"\b👏\b"
    ],
    "spam": [
        r"\bcrypto\b",
        r"\bbitcoin\b",
        r"\bethereum\b",
        r"\bmlm\b",
        r"\bmulti\s*level\s*marketing\b",
        r"\bget\s+rich\b",
        r"\bguaranteed\b",
        r"\bclick\s+here\b",
        r"\bfake\b",
        r"\bscam\b",
        r"\bbuy\s+now\b",
        r"\bvisit\s+my\s+site\b"
    ]
}


def authenticate_youtube():
    """Authenticate with YouTube API using OAuth2."""
    creds = None
    
    # Load existing token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    
    # Refresh or create new token
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        if not CREDENTIALS_FILE.exists():
            print(f"ERROR: {CREDENTIALS_FILE} not found.")
            print("Set up YouTube API credentials:")
            print("  1. Go to https://console.cloud.google.com/")
            print("  2. Create OAuth 2.0 credentials (Desktop app)")
            print("  3. Download JSON and save to: .secrets/youtube-credentials.json")
            sys.exit(1)
        
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save token for future runs
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds


def load_config():
    """Load monitor config (channel ID, last processed comment, etc)."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "channel_id": None,
        "last_comment_id": None,
        "stats": {"total": 0, "auto_responded": 0, "flagged": 0}
    }


def save_config(config):
    """Save config to file."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_channel_id(youtube, channel_name: str = "Concessa Obvius"):
    """Get channel ID from channel name."""
    request = youtube.search().list(
        q=channel_name,
        part="snippet",
        type="channel",
        maxResults=1
    )
    response = request.execute()
    
    if response["items"]:
        return response["items"][0]["snippet"]["channelId"]
    return None


def get_upload_playlist(youtube, channel_id: str):
    """Get the uploads playlist for a channel."""
    request = youtube.channels().list(
        id=channel_id,
        part="contentDetails"
    )
    response = request.execute()
    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def categorize_comment(text: str) -> str:
    """Categorize comment based on keywords."""
    text_lower = text.lower()
    
    # Check in order of specificity: spam first (likely False positives elsewhere)
    for category in ["spam", "question", "praise"]:
        for pattern in CATEGORY_KEYWORDS[category]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return category
    
    return "other"


def get_comment_replies(youtube, parent_id: str) -> list:
    """Get all replies to a comment."""
    replies = []
    request = youtube.comments().list(
        parentId=parent_id,
        part="snippet",
        maxResults=100
    )
    
    while request:
        response = request.execute()
        replies.extend(response.get("items", []))
        request = youtube.comments().list_next(request, response)
    
    return replies


def has_already_responded(youtube, parent_id: str, bot_username: str = "Concessa Obvius") -> bool:
    """Check if we've already replied to this comment."""
    replies = get_comment_replies(youtube, parent_id)
    return any(bot_username.lower() in reply["snippet"]["authorDisplayName"].lower() 
               for reply in replies)


def send_response(youtube, parent_id: str, text: str) -> bool:
    """Send a reply to a YouTube comment."""
    try:
        request = youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": parent_id,
                    "textOriginal": text
                }
            }
        )
        request.execute()
        return True
    except Exception as e:
        print(f"ERROR sending response to {parent_id}: {e}")
        return False


def log_comment(comment_data: dict):
    """Append comment to JSONL log."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(comment_data) + '\n')


def monitor_comments():
    """Main monitoring loop."""
    print(f"[{datetime.now().isoformat()}] Starting YouTube comment monitor...")
    
    # Load config
    config = load_config()
    
    # Authenticate
    creds = authenticate_youtube()
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Get channel ID
    if not config.get("channel_id"):
        channel_id = get_channel_id(youtube, "Concessa Obvius")
        if not channel_id:
            print("ERROR: Could not find Concessa Obvius channel")
            return
        config["channel_id"] = channel_id
        print(f"Found channel: {channel_id}")
    else:
        channel_id = config["channel_id"]
    
    # Get uploads playlist
    uploads_playlist = get_upload_playlist(youtube, channel_id)
    
    # Get recent videos
    request = youtube.playlistItems().list(
        playlistId=uploads_playlist,
        part="contentDetails",
        maxResults=5
    )
    response = request.execute()
    video_ids = [item["contentDetails"]["videoId"] for item in response.get("items", [])]
    
    print(f"Checking {len(video_ids)} recent videos...")
    
    # Check comments on each video
    new_comments = 0
    auto_responses = 0
    flagged = 0
    
    for video_id in video_ids:
        print(f"  Checking video {video_id}...")
        
        request = youtube.commentThreads().list(
            videoId=video_id,
            part="snippet",
            maxResults=100,
            order="relevance",
            searchTerms="",
            textFormat="plainText"
        )
        
        while request:
            response = request.execute()
            
            for thread in response.get("items", []):
                comment = thread["snippet"]["topLevelComment"]["snippet"]
                comment_id = thread["snippet"]["topLevelComment"]["id"]
                
                # Skip if we've seen this before
                if comment_id == config.get("last_comment_id"):
                    break
                
                # Only process newer comments
                if config.get("last_comment_id") and comment_id < config.get("last_comment_id"):
                    continue
                
                # Categorize
                category = categorize_comment(comment["textDisplay"])
                
                # Build log entry
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "comment_id": comment_id,
                    "video_id": video_id,
                    "commenter": comment["authorDisplayName"],
                    "text": comment["textDisplay"],
                    "category": category,
                    "response_status": "pending"
                }
                
                new_comments += 1
                
                # Auto-respond to questions and praise
                if category == "question" and not has_already_responded(youtube, comment_id):
                    if send_response(youtube, comment_id, RESPONSE_TEMPLATES["question"]):
                        log_entry["response_status"] = "sent_question"
                        auto_responses += 1
                        print(f"    ✓ Auto-responded to question from {comment['authorDisplayName']}")
                
                elif category == "praise" and not has_already_responded(youtube, comment_id):
                    if send_response(youtube, comment_id, RESPONSE_TEMPLATES["praise"]):
                        log_entry["response_status"] = "sent_praise"
                        auto_responses += 1
                        print(f"    ✓ Auto-responded to praise from {comment['authorDisplayName']}")
                
                # Flag sales inquiries
                elif category == "sales":
                    log_entry["response_status"] = "flagged_review"
                    flagged += 1
                    print(f"    🚩 Flagged for review (sales): {comment['authorDisplayName']}")
                
                else:
                    print(f"    • [{category}] {comment['authorDisplayName']}: {comment['textDisplay'][:60]}...")
                
                # Log
                log_comment(log_entry)
                
                # Update last seen
                if not config.get("last_comment_id") or comment_id > config.get("last_comment_id"):
                    config["last_comment_id"] = comment_id
            
            # Next page
            request = youtube.commentThreads().list_next(request, response)
    
    # Update and save stats
    config["stats"]["total"] += new_comments
    config["stats"]["auto_responded"] += auto_responses
    config["stats"]["flagged"] += flagged
    save_config(config)
    
    # Report
    print("\n" + "="*60)
    print("REPORT")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"New comments processed: {new_comments}")
    print(f"Auto-responses sent: {auto_responses}")
    print(f"Flagged for review: {flagged}")
    print(f"\nCumulative stats:")
    print(f"  Total comments: {config['stats']['total']}")
    print(f"  Auto-responses: {config['stats']['auto_responded']}")
    print(f"  Flagged: {config['stats']['flagged']}")
    print(f"  Log file: {LOG_FILE}")
    print("="*60)


if __name__ == "__main__":
    monitor_comments()
