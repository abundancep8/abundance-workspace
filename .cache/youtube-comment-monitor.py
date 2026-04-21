#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Monitors for new comments every 30 minutes, categorizes, and auto-responds.
"""

import json
import os
from datetime import datetime, timedelta
import sys

# ===== CONFIGURATION =====
CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"  # Replace with Concessa Obvius channel ID
CACHE_FILE = os.path.expanduser("~/.openclaw/workspace/.cache/youtube-comments.jsonl")
STATE_FILE = os.path.expanduser("~/.openclaw/workspace/.cache/youtube-monitor-state.json")

# Template responses
TEMPLATES = {
    "questions": """Thanks for the great question! Here are some resources that might help:
- [Add resource/link]
- [Add resource/link]

Feel free to ask if you need clarification!""",
    
    "praise": """Thank you so much! Comments like this mean the world to us. Really glad it resonated! 💙"""
}

# ===== CATEGORY RULES =====
QUESTION_KEYWORDS = ["how", "why", "what", "where", "when", "cost", "price", "timeline", "start", "tools", "tutorial", "help"]
PRAISE_KEYWORDS = ["amazing", "inspiring", "love", "great", "awesome", "brilliant", "excellent", "thanks", "grateful"]
SPAM_KEYWORDS = ["crypto", "nft", "mlm", "bitcoin", "forex", "dm", "link in bio", "click here", "buy now", "limited offer"]

# ===== YOUTUBE API SETUP =====
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    print("ERROR: YouTube API not installed. Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    YOUTUBE_API_AVAILABLE = False


def categorize_comment(text):
    """Categorize a comment based on keywords."""
    text_lower = text.lower()
    
    # Check for spam first (highest priority)
    if any(keyword in text_lower for keyword in SPAM_KEYWORDS):
        return "spam"
    
    # Check for sales/partnership mentions
    if any(word in text_lower for word in ["partnership", "collaborate", "collab", "business", "sponsor", "campaign"]):
        return "sales"
    
    # Check for questions
    if any(keyword in text_lower for keyword in QUESTION_KEYWORDS):
        return "questions"
    
    # Check for praise
    if any(keyword in text_lower for keyword in PRAISE_KEYWORDS):
        return "praise"
    
    return "other"


def load_state():
    """Load the last checked comment ID from state file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            return {"last_comment_id": None, "last_checked": None}
    return {"last_comment_id": None, "last_checked": None}


def save_state(state):
    """Save state file."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def log_comment(comment_id, commenter, text, category, response_status, reply_text=None):
    """Log comment to JSONL file."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "comment_id": comment_id,
        "commenter": commenter,
        "text": text,
        "category": category,
        "response_status": response_status,
        "reply_text": reply_text
    }
    
    with open(CACHE_FILE, 'a') as f:
        f.write(json.dumps(entry) + "\n")


def get_youtube_service():
    """Authenticate and return YouTube API service."""
    if not YOUTUBE_API_AVAILABLE:
        return None
    
    # You'll need to set up OAuth credentials
    # Instructions: https://developers.google.com/youtube/v3/getting-started
    # For now, this is a placeholder
    try:
        service = build('youtube', 'v3', credentials=None)  # Placeholder
        return service
    except:
        print("WARNING: Could not authenticate with YouTube API")
        return None


def monitor_comments():
    """Main monitoring function."""
    state = load_state()
    print(f"[{datetime.now().isoformat()}] Starting comment monitor...")
    
    stats = {
        "total_comments": 0,
        "auto_responses_sent": 0,
        "flagged_for_review": 0,
        "by_category": {}
    }
    
    # Placeholder: In real implementation, fetch comments from YouTube API
    # For now, showing the structure
    
    # Example comment processing:
    # for comment in fetched_comments:
    #     category = categorize_comment(comment['text'])
    #     stats['total_comments'] += 1
    #     stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
    #     
    #     if category == "questions":
    #         response_status = "auto_responded"
    #         stats['auto_responses_sent'] += 1
    #         reply_text = TEMPLATES['questions']
    #     elif category == "praise":
    #         response_status = "auto_responded"
    #         stats['auto_responses_sent'] += 1
    #         reply_text = TEMPLATES['praise']
    #     elif category == "sales":
    #         response_status = "flagged_for_review"
    #         stats['flagged_for_review'] += 1
    #         reply_text = None
    #     else:
    #         response_status = "logged_only"
    #         reply_text = None
    #     
    #     log_comment(
    #         comment['id'],
    #         comment['commenter'],
    #         comment['text'],
    #         category,
    #         response_status,
    #         reply_text
    #     )
    
    # Save state
    state['last_checked'] = datetime.utcnow().isoformat()
    save_state(state)
    
    # Print report
    print(f"\n📊 YouTube Comment Monitor Report ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"Total comments processed: {stats['total_comments']}")
    print(f"Auto-responses sent: {stats['auto_responses_sent']}")
    print(f"Flagged for review: {stats['flagged_for_review']}")
    print(f"By category: {stats['by_category']}")
    print(f"Log file: {CACHE_FILE}")


if __name__ == "__main__":
    monitor_comments()
