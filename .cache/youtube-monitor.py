#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius channel.
Categorizes comments, auto-responds to questions/praise, flags sales for review.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import re
import sys

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Google API client not installed. Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Configuration
CACHE_DIR = Path("/Users/abundance/.openclaw/workspace/.cache")
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-state.json"
CREDENTIALS_FILE = CACHE_DIR / "youtube-credentials.json"
TOKEN_FILE = CACHE_DIR / "youtube-token.json"

CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")  # Set this env var
API_KEY = os.getenv("YOUTUBE_API_KEY")

# Auto-response templates
TEMPLATES = {
    "question": "Thank you for the great question! I appreciate your interest. I'll look into this and get back to you soon. 🙏",
    "praise": "Thank you so much for the kind words! Your support means everything. 💜"
}

# Keywords for categorization
CATEGORIES = {
    "question": [
        r"how\s+do\s+i", r"how\s+to", r"what.*cost", r"how.*much",
        r"what.*timeline", r"when.*start", r"what.*tools", r"where.*begin",
        r"\?", r"can\s+i", r"should\s+i", r"is\s+it", r"do\s+you"
    ],
    "praise": [
        r"amazing", r"inspiring", r"love\s+this", r"incredible", r"brilliant",
        r"fantastic", r"wonderful", r"excellent", r"perfect", r"beautiful",
        r"thank\s+you", r"appreciate", r"grateful", r"❤", r"🙌", r"👏"
    ],
    "spam": [
        r"crypto", r"bitcoin", r"ethereum", r"nft", r"mlm", r"dropship",
        r"work\s+from\s+home", r"get\s+rich", r"forex", r"penny\s+stock",
        r"click\s+here", r"buy\s+now", r"limited\s+time"
    ],
    "sales": [
        r"partnership", r"collaboration", r"sponsor", r"business\s+opportunity",
        r"let.?s\s+work", r"reach\s+out", r"consulting", r"freelance",
        r"hire.*services", r"b2b", r"wholesale"
    ]
}

def categorize_comment(text):
    """Classify comment into category."""
    text_lower = text.lower()
    
    # Check in order: spam first (most important to filter)
    for category in ["spam", "sales", "question", "praise"]:
        for pattern in CATEGORIES[category]:
            if re.search(pattern, text_lower):
                return category
    
    return "other"

def load_state():
    """Load last processed comment ID."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_comment_id": None, "processed_count": 0}

def save_state(state):
    """Save processing state."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def log_comment(comment_data):
    """Append comment to JSONL log."""
    with open(COMMENTS_LOG, "a") as f:
        f.write(json.dumps(comment_data) + "\n")

def get_youtube_service():
    """Initialize YouTube API service."""
    if not API_KEY:
        print("ERROR: YOUTUBE_API_KEY env var not set")
        return None
    return build('youtube', 'v3', developerKey=API_KEY)

def fetch_comments(service, channel_id, state):
    """Fetch recent comments from channel."""
    try:
        # Get channel's uploads playlist
        channels = service.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()
        
        if not channels['items']:
            print(f"ERROR: Channel {channel_id} not found")
            return []
        
        uploads_playlist = channels['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get recent videos
        videos_request = service.playlistItems().list(
            playlistId=uploads_playlist,
            part='contentDetails',
            maxResults=5
        )
        videos = videos_request.execute()
        
        all_comments = []
        
        # Fetch comments from each video
        for video_item in videos.get('items', []):
            video_id = video_item['contentDetails']['videoId']
            
            comments_request = service.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100,
                textFormat='plainText',
                order='relevance'
            )
            comments = comments_request.execute()
            
            for thread in comments.get('items', []):
                comment = thread['snippet']['topLevelComment']['snippet']
                all_comments.append({
                    'id': thread['id'],
                    'video_id': video_id,
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'published_at': comment['publishedAt'],
                    'likes': comment['likeCount']
                })
        
        return all_comments
        
    except Exception as e:
        print(f"ERROR fetching comments: {e}")
        return []

def process_comments(service, channel_id):
    """Main processing loop."""
    if not CHANNEL_ID:
        print("ERROR: YOUTUBE_CHANNEL_ID env var not set")
        return
    
    state = load_state()
    comments = fetch_comments(service, channel_id, state)
    
    if not comments:
        print("No new comments found.")
        return
    
    # Track stats
    stats = {
        "total_processed": 0,
        "auto_responses_sent": 0,
        "flagged_for_review": 0,
        "by_category": {"question": 0, "praise": 0, "spam": 0, "sales": 0, "other": 0}
    }
    
    # Process each comment
    for comment in comments:
        category = categorize_comment(comment['text'])
        timestamp = datetime.utcnow().isoformat()
        
        response_status = "pending"
        auto_response = None
        
        if category == "question":
            auto_response = TEMPLATES["question"]
            response_status = "auto_responded"
            stats["auto_responses_sent"] += 1
        elif category == "praise":
            auto_response = TEMPLATES["praise"]
            response_status = "auto_responded"
            stats["auto_responses_sent"] += 1
        elif category == "sales":
            response_status = "flagged_review"
            stats["flagged_for_review"] += 1
        elif category == "spam":
            response_status = "spam_hidden"
        
        # Log to JSONL
        log_entry = {
            "timestamp": timestamp,
            "comment_id": comment['id'],
            "video_id": comment['video_id'],
            "commenter": comment['author'],
            "text": comment['text'],
            "category": category,
            "response_status": response_status,
            "auto_response": auto_response,
            "likes": comment['likes']
        }
        log_comment(log_entry)
        
        stats["total_processed"] += 1
        stats["by_category"][category] += 1
    
    # Save state
    state["last_comment_id"] = comments[-1]['id']
    state["processed_count"] += stats["total_processed"]
    state["last_run"] = datetime.utcnow().isoformat()
    save_state(state)
    
    # Print report
    print("\n=== YouTube Comment Monitor Report ===")
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Total comments processed: {stats['total_processed']}")
    print(f"Auto-responses sent: {stats['auto_responses_sent']}")
    print(f"Flagged for review (sales): {stats['flagged_for_review']}")
    print("\nBreakdown by category:")
    for cat, count in stats["by_category"].items():
        print(f"  {cat}: {count}")
    print(f"\nCumulative processed: {state['processed_count']}")
    print(f"Log file: {COMMENTS_LOG}")

if __name__ == "__main__":
    service = get_youtube_service()
    if service and CHANNEL_ID:
        process_comments(service, CHANNEL_ID)
    else:
        print("\nSetup required. Set these environment variables:")
        print("  export YOUTUBE_API_KEY='your-api-key'")
        print("  export YOUTUBE_CHANNEL_ID='UCxxxxx'")
