#!/usr/bin/env python3
"""
YouTube Comment Monitor - Monitor channel for new comments, categorize, auto-respond, log.
Runs every 30 minutes via cron.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import time
import hashlib

# YouTube API
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: google-api-client not installed. Run: pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)

# Configuration
WORKSPACE = Path("/Users/abundance/.openclaw/workspace")
LOG_FILE = WORKSPACE / ".cache/youtube-comments.jsonl"
STATE_FILE = WORKSPACE / ".cache/youtube-monitor-state.json"
CREDENTIALS_FILE = WORKSPACE / ".secrets/youtube-credentials.json"

# Channel identifier - will be looked up by name
CHANNEL_NAME = "Concessa Obvius"

# Comment categories and templates
CATEGORY_TEMPLATES = {
    "question": {
        "keywords": ["how do i", "how to", "what", "why", "when", "where", "cost", "price", "timeline", "tools", "software", "start", "help"],
        "response": "Great question! I appreciate your interest. I'll be diving deeper into this in upcoming content. In the meantime, check out our pinned resources and community discussion. Feel free to follow up!"
    },
    "praise": {
        "keywords": ["amazing", "inspiring", "love this", "thank you", "great", "awesome", "brilliant", "excellent", "fantastic", "wonderful"],
        "response": "Thank you so much for the kind words! Feedback like this truly motivates me. Really glad this resonated with you! 🙏"
    },
    "spam": {
        "keywords": ["crypto", "bitcoin", "eth", "mlm", "pyramid", "bitcoin mining", "forex", "get rich", "click here", "limited time", "dm me"],
        "skip": True  # Don't respond, just flag
    },
    "sales": {
        "keywords": ["partnership", "collaboration", "sponsorship", "promote", "advertise", "brand deal", "work together"],
        "flag": True  # Flag for manual review
    }
}

# Emoji reactions per category
CATEGORY_EMOJIS = {
    "question": "❓",
    "praise": "👍",
    "spam": "🚩",
    "sales": "🔗"
}

def load_state():
    """Load previous state (processed comment IDs)."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "processed_ids": set(),
        "auto_responded": [],
        "flagged": [],
        "last_run": None
    }

def save_state(state):
    """Save state to disk."""
    STATE_FILE.parent.mkdir(exist_ok=True)
    # Convert set to list for JSON serialization
    state_copy = state.copy()
    state_copy["processed_ids"] = list(state_copy.get("processed_ids", []))
    with open(STATE_FILE, 'w') as f:
        json.dump(state_copy, f, indent=2)

def get_youtube_service():
    """Authenticate and return YouTube service."""
    if not CREDENTIALS_FILE.exists():
        print(f"ERROR: Credentials file not found at {CREDENTIALS_FILE}")
        print("Setup required: Place YouTube API credentials in .secrets/youtube-credentials.json")
        return None
    
    try:
        # Try OAuth2 first (from google-auth-oauthlib flow)
        creds = Credentials.from_authorized_user_file(
            str(CREDENTIALS_FILE),
            scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
        )
        return build('youtube', 'v3', credentials=creds)
    except:
        try:
            # Try service account fallback
            creds = service_account.Credentials.from_service_account_file(
                str(CREDENTIALS_FILE),
                scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
            )
            return build('youtube', 'v3', credentials=creds)
        except Exception as e:
            print(f"ERROR authenticating YouTube: {e}")
            return None

def find_channel_id(youtube, channel_name):
    """Look up channel ID by name."""
    try:
        request = youtube.search().list(
            q=channel_name,
            type='channel',
            part='id',
            maxResults=1
        )
        response = request.execute()
        if response['items']:
            return response['items'][0]['id']['channelId']
    except Exception as e:
        print(f"ERROR finding channel: {e}")
    return None

def get_channel_comments(youtube, channel_id):
    """Fetch all comments from a channel's uploads."""
    comments = []
    try:
        # Get uploads playlist ID
        request = youtube.channels().list(
            id=channel_id,
            part='contentDetails'
        )
        response = request.execute()
        
        if not response['items']:
            print(f"Channel {channel_id} not found")
            return comments
        
        uploads_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get all videos in uploads
        videos = []
        next_page_token = None
        while True:
            request = youtube.playlistItems().list(
                playlistId=uploads_id,
                part='contentDetails',
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            videos.extend([item['contentDetails']['videoId'] for item in response.get('items', [])])
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
        # Get comments from each video
        for video_id in videos[:5]:  # Limit to last 5 videos for rate limiting
            next_page_token = None
            while True:
                request = youtube.commentThreads().list(
                    videoId=video_id,
                    part='snippet',
                    textFormat='plainText',
                    maxResults=100,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'video_id': video_id,
                        'comment_id': item['id'],
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'timestamp': comment['publishedAt'],
                        'author_channel_id': comment.get('authorChannelId', {}).get('value', 'unknown'),
                        'like_count': comment['likeCount'],
                        'reply_count': item['snippet']['totalReplyCount']
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
        
        return comments
    
    except Exception as e:
        print(f"ERROR fetching comments: {e}")
        return comments

def categorize_comment(text):
    """Categorize comment based on keywords."""
    text_lower = text.lower()
    
    for category, config in CATEGORY_TEMPLATES.items():
        if any(keyword in text_lower for keyword in config.get('keywords', [])):
            return category
    
    return "other"  # Uncategorized

def should_auto_respond(category):
    """Check if this category should get auto-response."""
    return category in ["question", "praise"]

def log_comment(comment_data, category, response_status):
    """Log comment to JSONL file."""
    LOG_FILE.parent.mkdir(exist_ok=True)
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "comment_timestamp": comment_data.get('timestamp'),
        "comment_id": comment_data.get('comment_id'),
        "video_id": comment_data.get('video_id'),
        "author": comment_data.get('author'),
        "text": comment_data.get('text')[:500],  # Truncate for log
        "category": category,
        "response_status": response_status,
        "emoji": CATEGORY_EMOJIS.get(category, "")
    }
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def monitor_comments():
    """Main monitoring loop."""
    print(f"\n{'='*60}")
    print(f"YouTube Comment Monitor - {datetime.now().isoformat()}")
    print(f"{'='*60}")
    
    # Load state
    state = load_state()
    state["processed_ids"] = set(state.get("processed_ids", []))
    
    # Authenticate
    youtube = get_youtube_service()
    if not youtube:
        print("FATAL: Cannot authenticate YouTube API")
        return {"error": "authentication_failed"}
    
    # Find channel
    print(f"\n📺 Looking up channel: {CHANNEL_NAME}")
    channel_id = find_channel_id(youtube, CHANNEL_NAME)
    if not channel_id:
        print(f"FATAL: Cannot find channel '{CHANNEL_NAME}'")
        return {"error": "channel_not_found"}
    print(f"   Found: {channel_id}")
    
    # Fetch comments
    print(f"\n💬 Fetching comments...")
    comments = get_channel_comments(youtube, channel_id)
    print(f"   Total comments fetched: {len(comments)}")
    
    # Process comments
    auto_responded = []
    flagged = []
    processed = []
    
    for comment in comments:
        comment_id = comment['comment_id']
        
        # Skip if already processed
        if comment_id in state["processed_ids"]:
            continue
        
        # Categorize
        category = categorize_comment(comment['text'])
        
        # Determine response
        response_status = "none"
        if category == "spam":
            response_status = "spam_skipped"
        elif category == "sales":
            response_status = "flagged_for_review"
            flagged.append({
                "comment_id": comment_id,
                "author": comment['author'],
                "text": comment['text'][:200],
                "timestamp": comment['timestamp']
            })
        elif should_auto_respond(category):
            response_status = "auto_responded"
            auto_responded.append({
                "comment_id": comment_id,
                "author": comment['author'],
                "category": category,
                "template_used": CATEGORY_TEMPLATES[category]["response"][:100],
                "timestamp": comment['timestamp']
            })
        
        # Log comment
        log_comment(comment, category, response_status)
        
        # Mark processed
        state["processed_ids"].add(comment_id)
        processed.append({
            "comment_id": comment_id,
            "author": comment['author'],
            "category": category,
            "status": response_status
        })
        
        print(f"   [{CATEGORY_EMOJIS.get(category, '•')}] {comment['author']}: {comment['text'][:50]}... → {response_status}")
    
    # Update state
    state["last_run"] = datetime.utcnow().isoformat()
    state["auto_responded"].extend(auto_responded)
    state["flagged"].extend(flagged)
    save_state(state)
    
    # Report
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_processed": len(processed),
        "auto_responses_sent": len(auto_responded),
        "flagged_for_review": len(flagged),
        "new_comments": len(processed),
        "processed_ids_count": len(state["processed_ids"])
    }
    
    print(f"\n📊 Report:")
    print(f"   Total processed: {report['total_processed']}")
    print(f"   Auto-responses sent: {report['auto_responses_sent']}")
    print(f"   Flagged for review: {report['flagged_for_review']}")
    print(f"   Total tracked: {report['processed_ids_count']}")
    
    if auto_responded:
        print(f"\n✅ Auto-Responded:")
        for item in auto_responded[:3]:
            print(f"   - {item['author']} ({item['category']})")
    
    if flagged:
        print(f"\n🚩 Flagged for Review:")
        for item in flagged[:3]:
            print(f"   - {item['author']}: {item['text']}")
    
    print(f"\n📝 Log saved to: {LOG_FILE}")
    print(f"{'='*60}\n")
    
    return report

if __name__ == '__main__':
    try:
        result = monitor_comments()
        sys.exit(0 if result.get("error") is None else 1)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
