#!/usr/bin/env python3
"""
YouTube Comment Monitor - Cron Job
Monitors Concessa Obvius channel for new comments every 30 minutes.
Categorizes, auto-responds, and logs to .cache/youtube-comments.jsonl
"""

import json
import os
import sys
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Literal

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: YouTube API libraries not installed. Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Configuration
CHANNEL_HANDLE = "ConcessaObvius"  # Will be looked up via API
CACHE_DIR = Path(".cache")
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Auto-response templates
RESPONSE_TEMPLATES = {
    "questions": [
        "Great question! I'd recommend checking out our documentation and guides for a detailed walkthrough. Feel free to follow up if you need more specific help!",
        "Thanks for asking! We have resources available that cover this topic. Feel free to DM us if you need personalized guidance.",
        "Love this question! This is something we cover in our guides. Happy to help if you have follow-ups!",
    ],
    
    "praise": [
        "Thank you! 🙏 We really appreciate the support and kind words. Keep building!",
        "This means so much! 🙌 Thanks for the encouragement — it fuels everything we do.",
        "You're amazing! 💜 Thank you for the love and support!",
    ]
}

# Comment categories
CommentCategory = Literal["questions", "praise", "spam", "sales"]

def authenticate_youtube():
    """Authenticate with YouTube API."""
    creds = None
    token_file = CACHE_DIR / "youtube_token.json"
    credentials_file = Path("youtube_credentials.json")  # Download from Google Cloud Console
    
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_file.exists():
                print(f"ERROR: {credentials_file} not found")
                print("Download OAuth2 credentials from: https://console.cloud.google.com/")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
            creds = flow.run_local_server(port=0)
        
        token_file.parent.mkdir(exist_ok=True)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    
    return build("youtube", "v3", credentials=creds)

def get_channel_id(youtube, channel_handle: str) -> str:
    """Look up channel ID from handle."""
    response = youtube.search().list(
        part="snippet",
        q=channel_handle,
        type="channel",
        maxResults=1
    ).execute()
    
    if response["items"]:
        return response["items"][0]["id"]["channelId"]
    raise ValueError(f"Channel not found: {channel_handle}")

def categorize_comment(text: str) -> CommentCategory:
    """Categorize a comment using keyword matching + simple heuristics."""
    text_lower = text.lower()
    
    # Spam keywords - high confidence patterns
    spam_keywords = ["crypto", "bitcoin", "ethereum", "mlm", "business opportunity", "work from home", "make money fast", "click here", "free money", "dm for", "dm me", "check my link"]
    if any(keyword in text_lower for keyword in spam_keywords):
        return "spam"
    
    # Sales keywords - partnership/collaboration
    sales_keywords = ["partnership", "collaboration", "brand deal", "sponsorship", "work together", "let's collaborate", "business inquiry", "investment", "collab", "pr opportunity"]
    if any(keyword in text_lower for keyword in sales_keywords):
        return "sales"
    
    # Praise keywords - strong emotional/positive signals
    praise_keywords = ["amazing", "inspiring", "great", "love", "awesome", "fantastic", "incredible", "brilliant", "thank you", "appreciate", "well done", "impressed", "motivat", "grateful", "beautiful", "powerful"]
    if any(keyword in text_lower for keyword in praise_keywords):
        return "praise"
    
    # Question keywords - seeking information
    question_keywords = ["how", "what", "when", "where", "why", "can i", "how do i", "tool", "cost", "price", "timeline", "start", "begin", "?", "help", "which", "does"]
    if any(keyword in text_lower for keyword in question_keywords):
        return "questions"
    
    # Default to praise if it's short and seems positive
    if len(text) < 50 and any(word in text_lower for word in ["great", "good", "nice", "love", "cool"]):
        return "praise"
    
    # Default to questions if unclear
    return "questions"

def get_new_comments(youtube, channel_id: str, since: datetime) -> list:
    """Fetch new comments from channel since timestamp."""
    comments = []
    request = youtube.commentThreads().list(
        part="snippet,replies",
        allThreadsRelatedToChannelId=channel_id,
        textFormat="plainText",
        maxResults=100,
        order="relevance"
    )
    
    while request:
        response = request.execute()
        
        for thread in response.get("items", []):
            comment = thread["snippet"]["topLevelComment"]["snippet"]
            published_at = datetime.fromisoformat(comment["publishedAt"].replace("Z", "+00:00"))
            
            # Only include comments since the checkpoint
            if published_at > since:
                comments.append({
                    "comment_id": comment["id"],
                    "thread_id": thread["id"],
                    "timestamp": published_at.isoformat(),
                    "commenter": comment["authorDisplayName"],
                    "text": comment["textDisplay"],
                    "reply_count": thread["snippet"]["totalReplyCount"]
                })
        
        if "nextPageToken" in response:
            request = youtube.commentThreads().list(
                part="snippet,replies",
                allThreadsRelatedToChannelId=channel_id,
                textFormat="plainText",
                maxResults=100,
                pageToken=response["nextPageToken"]
            )
        else:
            break
    
    return comments

def reply_to_comment(youtube, comment_id: str, text: str) -> bool:
    """Post a reply to a comment."""
    try:
        youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": text
                }
            }
        ).execute()
        return True
    except Exception as e:
        print(f"Failed to reply to comment {comment_id}: {e}")
        return False

def load_state() -> dict:
    """Load last check state."""
    CACHE_DIR.mkdir(exist_ok=True)
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_check": datetime.now(timezone.utc).isoformat()}

def save_state(state: dict):
    """Save last check state."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def load_processed_ids() -> set:
    """Load set of already-processed comment IDs."""
    processed = set()
    if COMMENTS_LOG.exists():
        with open(COMMENTS_LOG) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    processed.add(entry["comment_id"])
                except:
                    pass
    return processed

def log_comment(entry: dict):
    """Append comment to log file."""
    CACHE_DIR.mkdir(exist_ok=True)
    with open(COMMENTS_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def main():
    """Main monitor loop."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] YouTube Comment Monitor starting...")
    
    # Load state
    state = load_state()
    last_check = datetime.fromisoformat(state.get("last_check", datetime.now(timezone.utc).isoformat()))
    processed_ids = load_processed_ids()
    
    try:
        # Authenticate
        youtube = authenticate_youtube()
        
        # Get channel ID
        channel_id = get_channel_id(youtube, CHANNEL_HANDLE)
        print(f"Monitoring channel: {channel_id}")
        
        # Fetch new comments
        comments = get_new_comments(youtube, channel_id, last_check)
        
        if not comments:
            print("No new comments found.")
            save_state({"last_check": datetime.utcnow().isoformat()})
            return {"processed": 0, "auto_responses": 0, "flagged": 0}
        
        # Process comments
        stats = {"processed": 0, "auto_responses": 0, "flagged": 0}
        
        for comment in comments:
            if comment["comment_id"] in processed_ids:
                continue
            
            # Categorize
            category = categorize_comment(comment["text"])
            
            # Determine action
            response_sent = False
            if category == "questions":
                # Auto-respond to questions
                response_text = random.choice(RESPONSE_TEMPLATES["questions"])
                response_sent = reply_to_comment(youtube, comment["comment_id"], response_text)
            
            elif category == "praise":
                # Auto-respond to praise
                response_text = random.choice(RESPONSE_TEMPLATES["praise"])
                response_sent = reply_to_comment(youtube, comment["comment_id"], response_text)
            
            elif category == "sales":
                # Flag for manual review
                stats["flagged"] += 1
            
            # Log
            log_entry = {
                "comment_id": comment["comment_id"],
                "thread_id": comment["thread_id"],
                "timestamp": comment["timestamp"],
                "commenter": comment["commenter"],
                "text": comment["text"][:500],  # Truncate long comments
                "category": category,
                "response_status": "sent" if response_sent else ("pending" if category in ["questions", "praise"] else "flagged")
            }
            log_comment(log_entry)
            
            stats["processed"] += 1
            if response_sent:
                stats["auto_responses"] += 1
            
            print(f"  [{category}] {comment['commenter']}: {comment['text'][:60]}...")
        
        # Update state
        save_state({"last_check": datetime.now(timezone.utc).isoformat()})
        
        return stats
        
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    stats = main()
    print(f"\n📊 Report:")
    print(f"  Processed: {stats['processed']}")
    print(f"  Auto-responses sent: {stats['auto_responses']}")
    print(f"  Flagged for review: {stats['flagged']}")
    print(f"  Log: {COMMENTS_LOG}")
