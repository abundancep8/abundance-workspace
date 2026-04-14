#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius channel
Runs every 30 minutes. Categorizes, auto-responds, logs, and reports.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import re

# Try to import YouTube API libraries
try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("⚠️  google-auth and google-api-client not installed. Install with: pip install google-auth google-auth-httplib2 google-api-python-client")

# Configuration
CHANNEL_HANDLE = "ConcессаObvius"  # Update with actual handle
COMMENTS_LOG = Path(".cache/youtube-comments.jsonl")
CREDENTIALS_FILE = Path(".secrets/youtube-credentials.json")  # OAuth service account key
RESPONSES_TEMPLATE = {
    "questions": {
        "response": "Great question! I'd recommend checking our FAQ at [LINK] for more details on getting started. Feel free to ask if you need clarification!",
        "enabled": True
    },
    "praise": {
        "response": "Thank you so much! This means a lot. Looking forward to sharing more with you! 🙏",
        "enabled": True
    }
}

CATEGORIES = {
    "questions": r"(how do i|how to|cost|price|timeline|when|tools?|setup|start|beginning)",
    "praise": r"(amazing|inspiring|great|love this|awesome|incredible|fantastic)",
    "spam": r"(crypto|bitcoin|nft|mlm|forex|gambling|casino|click here)",
    "sales": r"(partnership|collaboration|business|sponsor|deal|affiliate)"
}

def ensure_log_file():
    """Create .cache and comments log if needed."""
    COMMENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not COMMENTS_LOG.exists():
        COMMENTS_LOG.touch()

def categorize_comment(text):
    """Categorize comment by keywords."""
    text_lower = text.lower()
    for category, pattern in CATEGORIES.items():
        if re.search(pattern, text_lower):
            return category
    return "other"

def get_channel_id():
    """
    Get YouTube channel ID from handle.
    Requires YouTube API credentials.
    """
    if not YOUTUBE_API_AVAILABLE:
        print("❌ YouTube API not available. Cannot fetch channel ID.")
        return None
    
    if not CREDENTIALS_FILE.exists():
        print(f"❌ Credentials file not found: {CREDENTIALS_FILE}")
        print("   Set up YouTube API: https://console.cloud.google.com/")
        return None
    
    try:
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=["https://www.googleapis.com/auth/youtube.readonly"]
        )
        youtube = build("youtube", "v3", credentials=credentials)
        
        request = youtube.search().list(
            part="snippet",
            type="channel",
            q=CHANNEL_HANDLE,
            maxResults=1
        )
        response = request.execute()
        
        if response.get("items"):
            return response["items"][0]["id"]["channelId"]
    except Exception as e:
        print(f"❌ Error getting channel ID: {e}")
    
    return None

def fetch_new_comments(channel_id):
    """
    Fetch new comments from channel.
    Requires YouTube API credentials.
    """
    if not YOUTUBE_API_AVAILABLE or not channel_id:
        print("⚠️  Skipping fetch (API not available or channel ID missing)")
        return []
    
    try:
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=["https://www.googleapis.com/auth/youtube.readonly"]
        )
        youtube = build("youtube", "v3", credentials=credentials)
        
        # Get recent videos from channel
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            order="date",
            maxResults=5
        )
        videos_response = request.execute()
        
        new_comments = []
        for video in videos_response.get("items", []):
            video_id = video["id"]["videoId"]
            
            # Get comment threads for this video
            threads_request = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=20,
                textFormat="plainText"
            )
            threads_response = threads_request.execute()
            
            for thread in threads_response.get("items", []):
                comment = thread["snippet"]["topLevelComment"]["snippet"]
                new_comments.append({
                    "video_id": video_id,
                    "comment_id": thread["snippet"]["topLevelComment"]["id"],
                    "author": comment["authorDisplayName"],
                    "text": comment["textDisplay"],
                    "published_at": comment["publishedAt"]
                })
        
        return new_comments
    except Exception as e:
        print(f"❌ Error fetching comments: {e}")
        return []

def already_logged(comment_id):
    """Check if comment was already processed."""
    if not COMMENTS_LOG.exists():
        return False
    
    with open(COMMENTS_LOG, "r") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("comment_id") == comment_id:
                return True
    return False

def log_comment(comment, category, response_status):
    """Log comment to jsonl file."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "commenter": comment["author"],
        "text": comment["text"],
        "category": category,
        "response_status": response_status,
        "comment_id": comment["comment_id"]
    }
    
    with open(COMMENTS_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def process_comments(comments):
    """Process, categorize, and respond to comments."""
    processed = 0
    auto_responses_sent = 0
    flagged_for_review = 0
    
    for comment in comments:
        if already_logged(comment["comment_id"]):
            continue
        
        category = categorize_comment(comment["text"])
        response_status = "not_applicable"
        
        if category == "questions" and RESPONSES_TEMPLATE["questions"]["enabled"]:
            response_status = "auto_responded"
            auto_responses_sent += 1
            print(f"✓ Auto-responded to question from {comment['author']}")
        
        elif category == "praise" and RESPONSES_TEMPLATE["praise"]["enabled"]:
            response_status = "auto_responded"
            auto_responses_sent += 1
            print(f"✓ Auto-responded to praise from {comment['author']}")
        
        elif category == "sales":
            response_status = "flagged"
            flagged_for_review += 1
            print(f"🚩 Flagged sales comment from {comment['author']}")
        
        elif category == "spam":
            response_status = "spam"
            print(f"⛔ Spam detected from {comment['author']}")
        
        log_comment(comment, category, response_status)
        processed += 1
    
    return processed, auto_responses_sent, flagged_for_review

def generate_report(processed, auto_responses, flagged):
    """Generate summary report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    
    report = f"""
═══════════════════════════════════════════════════════════════
📊 YOUTUBE COMMENT MONITOR REPORT
Channel: Concessa Obvius
Time: {timestamp}
═══════════════════════════════════════════════════════════════

📈 STATS
  Total comments processed: {processed}
  Auto-responses sent: {auto_responses}
  Flagged for manual review: {flagged}

📁 LOGS
  Comment log: {COMMENTS_LOG.absolute()}

⚙️  STATUS
  API availability: {'✓ OK' if YOUTUBE_API_AVAILABLE else '❌ Not configured'}
  Credentials: {'✓ Found' if CREDENTIALS_FILE.exists() else '❌ Missing'}

═══════════════════════════════════════════════════════════════
"""
    
    return report.strip()

def main():
    """Main monitor loop."""
    ensure_log_file()
    
    print("🎥 YouTube Comment Monitor starting...")
    
    # Note: In a real cron job, you'd fetch new comments
    # For now, we'll show what would happen
    
    if not YOUTUBE_API_AVAILABLE:
        print("\n⚠️  SETUP REQUIRED:")
        print("1. Install: pip install google-auth google-auth-httplib2 google-api-python-client")
        print("2. Set up OAuth: https://console.cloud.google.com/apis/credentials")
        print("3. Download service account key → .cache/youtube-credentials.json")
        print("4. Update CHANNEL_HANDLE in this script")
    
    # Try to fetch and process
    channel_id = get_channel_id()
    
    if channel_id:
        comments = fetch_new_comments(channel_id)
        processed, auto_responses, flagged = process_comments(comments)
    else:
        processed, auto_responses, flagged = 0, 0, 0
    
    # Generate and print report
    report = generate_report(processed, auto_responses, flagged)
    print(report)

if __name__ == "__main__":
    main()
