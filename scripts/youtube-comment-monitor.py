#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius channel.
Runs every 30 minutes: categorizes comments, auto-responds, and logs results.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import re

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Google API libraries not installed. Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Configuration
CHANNEL_NAME = "Concessa Obvius"
CACHE_DIR = Path(".cache")
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
CREDENTIALS_FILE = Path.home() / ".openclaw" / "youtube-credentials.json"
TOKEN_FILE = Path.home() / ".openclaw" / "youtube-token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Auto-response templates
TEMPLATES = {
    "question": """Thanks for the question! 🙌 We cover this in detail at [link to relevant resource]. Feel free to reach out if you need more help!""",
    "praise": """Thank you so much! 💙 Your support means everything. We're building something special here.""",
}

# Category patterns
PATTERNS = {
    "question": [
        r"how\s+(?:do|can|should)\s+[a-z]+",
        r"what\s+(?:is|are)\s+",
        r"where\s+(?:do|can)",
        r"cost|price|fee|pricing",
        r"timeline|how\s+long|duration",
        r"tools?(?:\s+to|:|for)?",
        r"\?$",
    ],
    "praise": [
        r"amazing|awesome|incredible|brilliant|genius|love\s+this",
        r"inspiring|motivated|changed\s+my",
        r"thank\s+you|thanks|grateful",
        r"brilliant|beautiful|perfect",
    ],
    "spam": [
        r"bitcoin|crypto|nft|blockchain",
        r"mlm|multi.?level|pyramid",
        r"casino|poker|gambling",
        r"click\s+here|buy\s+now|limited\s+time",
    ],
    "sales": [
        r"partnership|collaborate|collab",
        r"sponsor|sponsorship|advertising",
        r"affiliate|commission",
        r"business\s+opportunity|growth\s+hacking",
    ],
}


def authenticate_youtube():
    """Authenticate with YouTube API."""
    creds = None
    
    # Load existing token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    
    # Refresh or create new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print(f"ERROR: YouTube credentials not found at {CREDENTIALS_FILE}")
                print("Set up OAuth2 credentials via Google Cloud Console and save to that path.")
                sys.exit(1)
            
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save token for reuse
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    
    return build("youtube", "v3", credentials=creds)


def get_channel_id(youtube, channel_name):
    """Get channel ID from channel name."""
    request = youtube.search().list(
        part="snippet",
        q=channel_name,
        type="channel",
        maxResults=1
    )
    response = request.execute()
    
    if response["items"]:
        return response["items"][0]["snippet"]["channelId"]
    raise ValueError(f"Channel '{channel_name}' not found")


def get_recent_comments(youtube, channel_id, since_timestamp=None):
    """Fetch recent comments from channel."""
    # Get uploads playlist
    request = youtube.channels().list(part="contentDetails", id=channel_id)
    response = request.execute()
    uploads_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    # Get recent videos
    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=uploads_id,
        maxResults=10
    )
    response = request.execute()
    video_ids = [item["contentDetails"]["videoId"] for item in response.get("items", [])]
    
    comments = []
    for video_id in video_ids:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=20,
            textFormat="plainText",
            order="relevance"
        )
        response = request.execute()
        
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comment_time = datetime.fromisoformat(comment["publishedAt"].replace("Z", "+00:00"))
            
            if since_timestamp and comment_time <= since_timestamp:
                continue
            
            comments.append({
                "timestamp": comment["publishedAt"],
                "commenter": comment["authorDisplayName"],
                "text": comment["textDisplay"],
                "video_id": video_id,
                "comment_id": item["id"],
            })
    
    return comments


def categorize_comment(text):
    """Categorize a comment into one of four types."""
    text_lower = text.lower()
    
    # Check each category (spam first to avoid false positives)
    for category in ["spam", "sales", "question", "praise"]:
        for pattern in PATTERNS[category]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return category
    
    return "other"


def auto_respond(youtube, video_id, comment_id, category):
    """Post an auto-response to a comment."""
    if category not in TEMPLATES:
        return False
    
    try:
        response_text = TEMPLATES[category]
        youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": response_text,
                }
            }
        ).execute()
        return True
    except Exception as e:
        print(f"Failed to post response: {e}")
        return False


def load_seen_comments():
    """Load set of already-processed comment IDs."""
    if not COMMENTS_LOG.exists():
        return set()
    
    seen = set()
    try:
        with open(COMMENTS_LOG, "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    seen.add(entry.get("comment_id"))
    except Exception as e:
        print(f"Warning: Could not load seen comments: {e}")
    
    return seen


def log_comment(entry):
    """Append comment entry to JSONL log."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(COMMENTS_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    """Main monitor loop."""
    print(f"[{datetime.now().isoformat()}] Starting YouTube Comment Monitor")
    
    try:
        youtube = authenticate_youtube()
        channel_id = get_channel_id(youtube, CHANNEL_NAME)
        print(f"Channel ID for '{CHANNEL_NAME}': {channel_id}")
        
        seen_ids = load_seen_comments()
        print(f"Previously seen: {len(seen_ids)} comments")
        
        comments = get_recent_comments(youtube, channel_id)
        print(f"Fetched: {len(comments)} recent comments")
        
        processed = 0
        auto_responded = 0
        flagged = 0
        
        for comment in comments:
            comment_id = comment["comment_id"]
            
            # Skip already-processed comments
            if comment_id in seen_ids:
                continue
            
            # Categorize
            category = categorize_comment(comment["text"])
            
            # Auto-respond or flag
            response_status = "none"
            if category == "question" or category == "praise":
                if auto_respond(youtube, comment["video_id"], comment_id, category):
                    response_status = "responded"
                    auto_responded += 1
                else:
                    response_status = "failed"
            elif category == "sales":
                response_status = "flagged_for_review"
                flagged += 1
            
            # Log entry
            entry = {
                "timestamp": comment["timestamp"],
                "commenter": comment["commenter"],
                "text": comment["text"][:200],  # Truncate for brevity
                "category": category,
                "response_status": response_status,
                "comment_id": comment_id,
            }
            log_comment(entry)
            processed += 1
        
        # Report
        print(f"\n--- Report ---")
        print(f"Total comments processed: {processed}")
        print(f"Auto-responses sent: {auto_responded}")
        print(f"Flagged for review: {flagged}")
        print(f"Log: {COMMENTS_LOG}")
        
        return 0
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
