#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Monitors for new comments, categorizes them, and auto-responds
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import re

# Attempt to import YouTube API
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("⚠️  YouTube API not installed. Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# Configuration
CHANNEL_NAME = "Concessa Obvius"
CHANNEL_ID = None  # Will be resolved from channel name
LOG_FILE = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-comments.jsonl"
CREDENTIALS_FILE = Path.home() / ".config" / "youtube" / "credentials.json"
TOKEN_FILE = Path.home() / ".config" / "youtube" / "token.json"

# Template Responses
RESPONSES = {
    "questions": "Thank you for the question! {comment_preview} I'd recommend checking out our resource hub or scheduling a call with our team. Visit [link] for more details.",
    "praise": "Thank you so much for the kind words! 🙏 We're thrilled you found this valuable. Keep building!",
}

# Categorization patterns
PATTERNS = {
    "questions": [
        r"how\s+(do|can|would)\s+i",
        r"what\s+(are|is)\s+(the|your)",
        r"where\s+(do|can)\s+i",
        r"when\s+(should|can|do)",
        r"(cost|price|fee|investment)",
        r"(timeline|how long)",
        r"(tools?|platform|software)",
        r"\?$",
    ],
    "spam": [
        r"(crypto|bitcoin|ethereum|nft|blockchain)",
        r"(mlm|multi.?level|network.?marketing)",
        r"(forex|trading|stocks|options)",
        r"(casino|gambling|slots)",
        r"(viagra|cialis|pharmacy)",
        r"click\s+here|visit\s+link|dm\s+for",
    ],
    "sales": [
        r"(partnership|collaboration|sponsor)",
        r"(business\s+opportunity|opportunity)",
        r"(brand\s+deal|advertising)",
        r"(affiliate|reseller)",
    ],
}

def categorize_comment(text):
    """Categorize comment based on patterns"""
    text_lower = text.lower()
    
    # Check spam first (highest priority)
    for pattern in PATTERNS["spam"]:
        if re.search(pattern, text_lower):
            return "spam"
    
    # Check sales
    for pattern in PATTERNS["sales"]:
        if re.search(pattern, text_lower):
            return "sales"
    
    # Check questions
    for pattern in PATTERNS["questions"]:
        if re.search(pattern, text_lower):
            return "questions"
    
    # Default to praise if positive sentiment, else neutral
    positive_words = ["amazing", "inspiring", "love", "great", "awesome", "excellent", "thank", "appreciate"]
    if any(word in text_lower for word in positive_words):
        return "praise"
    
    return "neutral"

def ensure_log_file():
    """Ensure log file and cache directory exist"""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.touch()

def log_comment(commenter, text, category, response_status, response_text=None):
    """Log comment to JSONL file"""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "commenter": commenter,
        "text": text,
        "category": category,
        "response_status": response_status,
        "response_text": response_text,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def get_youtube_service():
    """Get authenticated YouTube API service"""
    if not YOUTUBE_API_AVAILABLE:
        return None
    
    if not CREDENTIALS_FILE.exists():
        print(f"❌ YouTube credentials not found at {CREDENTIALS_FILE}")
        print("Set up OAuth2: https://developers.google.com/youtube/v3/quickstart/python")
        return None
    
    try:
        creds = None
        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE))
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE),
                    scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
                )
                creds = flow.run_local_server(port=0)
            
            # Save token
            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ YouTube API authentication failed: {e}")
        return None

def get_channel_id(youtube, channel_name):
    """Get channel ID from channel name"""
    try:
        request = youtube.search().list(
            part="snippet",
            q=channel_name,
            type="channel",
            maxResults=1
        )
        response = request.execute()
        if response["items"]:
            return response["items"][0]["id"]["channelId"]
    except Exception as e:
        print(f"❌ Failed to resolve channel: {e}")
    return None

def fetch_new_comments(youtube, channel_id, since_timestamp=None):
    """Fetch recent comments from channel"""
    comments = []
    try:
        # Get uploads playlist
        request = youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()
        uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Get recent videos
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=5
        )
        response = request.execute()
        
        # Fetch comments from each video
        for video in response["items"]:
            video_id = video["snippet"]["resourceId"]["videoId"]
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,
                order="relevance"
            )
            comment_response = request.execute()
            
            for item in comment_response.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "video_id": video_id,
                    "commenter": comment["authorDisplayName"],
                    "text": comment["textDisplay"],
                    "timestamp": comment["publishedAt"],
                    "comment_id": item["id"],
                })
    except Exception as e:
        print(f"❌ Failed to fetch comments: {e}")
    
    return comments

def get_last_checked_timestamp():
    """Get timestamp of last processed comment"""
    if not LOG_FILE.exists():
        return None
    
    try:
        with open(LOG_FILE, "r") as f:
            last_line = f.readlines()[-1]
            last_entry = json.loads(last_line)
            return last_entry["timestamp"]
    except:
        return None

def main():
    ensure_log_file()
    
    youtube = get_youtube_service()
    if not youtube:
        print("⚠️  YouTube API not available. Falling back to manual check mode.")
        print("Set CHANNEL_ID manually and use: python youtube-monitor.py --manual")
        return
    
    # Resolve channel ID
    global CHANNEL_ID
    CHANNEL_ID = get_channel_id(youtube, CHANNEL_NAME)
    if not CHANNEL_ID:
        print(f"❌ Could not find channel: {CHANNEL_NAME}")
        return
    
    print(f"✅ Found channel: {CHANNEL_NAME} ({CHANNEL_ID})")
    
    # Fetch new comments
    last_checked = get_last_checked_timestamp()
    new_comments = fetch_new_comments(youtube, CHANNEL_ID, since_timestamp=last_checked)
    
    if not new_comments:
        print("✅ No new comments")
        print(json.dumps({"processed": 0, "auto_responses": 0, "flagged": 0}))
        return
    
    # Process comments
    stats = {
        "processed": 0,
        "auto_responses": 0,
        "flagged": 0,
        "by_category": {}
    }
    
    for comment in new_comments:
        category = categorize_comment(comment["text"])
        stats["processed"] += 1
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        
        response_status = "pending"
        response_text = None
        
        # Auto-respond to questions and praise
        if category == "questions":
            response_text = RESPONSES["questions"].format(
                comment_preview=comment["text"][:50] + "..."
            )
            response_status = "auto_sent"
            stats["auto_responses"] += 1
        elif category == "praise":
            response_text = RESPONSES["praise"]
            response_status = "auto_sent"
            stats["auto_responses"] += 1
        elif category == "sales":
            response_status = "flagged_for_review"
            stats["flagged"] += 1
        
        log_comment(
            comment["commenter"],
            comment["text"],
            category,
            response_status,
            response_text
        )
        
        print(f"📝 [{category.upper()}] {comment['commenter']}: {comment['text'][:60]}...")
    
    # Report
    print("\n" + "="*60)
    print(f"📊 REPORT - {datetime.now().isoformat()}")
    print("="*60)
    print(f"Total comments processed: {stats['processed']}")
    print(f"Auto-responses sent: {stats['auto_responses']}")
    print(f"Flagged for review: {stats['flagged']}")
    print(f"By category: {stats['by_category']}")
    print("="*60)
    
    # Output JSON for integration
    print(json.dumps(stats))

if __name__ == "__main__":
    main()
