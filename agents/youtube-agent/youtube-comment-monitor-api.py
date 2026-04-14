#!/usr/bin/env python3
"""
YouTube Comment Monitor & Auto-Responder
Monitors Concessa Obvius channel, auto-responds to comments, logs everything
"""

import json
import time
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

CHANNEL_ID = "UC32674"  # Concessa Obvius
TOKEN_FILE = Path.home() / '.openclaw/workspace/.secrets/youtube-token.json'
LOG_FILE = Path('.cache/youtube-comments.jsonl')
BATCH_SIZE = 100

# Comment response templates (from youtube-complete-automation.py)
RESPONSES = {
    "how_start": {
        "triggers": ["how do i start", "how to begin", "where do i start"],
        "response": "Start with ONE task that costs you 30 min/day. Write a clear instruction for it. Test for 7 days. Track what changed. That's the starting point."
    },
    "how_long": {
        "triggers": ["how long", "how much time", "took you how long"],
        "response": "Setup: 2 weeks. Testing: 2 weeks. First revenue: Week 3. Month 1: You'll understand the system. After that it compounds."
    },
    "what_tools": {
        "triggers": ["what tools", "which tools", "what do you use"],
        "response": "Claude (writing), Blotato (videos), Stripe (payments), Vercel (hosting), OpenClaw (orchestration). Total: $50/month. Revenue: $4,200+."
    },
    "what_cost": {
        "triggers": ["how much does it cost", "cost", "price"],
        "response": "$50/month for the stack. ROI in first month. The tools are public. The system I built is what matters."
    },
    "amazing": {
        "triggers": ["amazing", "incredible", "brilliant", "genius"],
        "response": "Wait until you build your own system. Then it gets exciting. Now go build instead of just watching."
    },
    "inspiring": {
        "triggers": ["inspiring", "motivated", "thank you"],
        "response": "Action > inspiration every time. Start building today. That's what separates people."
    }
}

def get_youtube_service():
    """Load YouTube service with saved credentials"""
    if not TOKEN_FILE.exists():
        print("❌ Token file not found. Run: python3 youtube-api-auth.py")
        return None
    
    with open(TOKEN_FILE, 'r') as f:
        creds_data = json.load(f)
    
    creds = Credentials.from_authorized_user_info(creds_data)
    
    # Refresh token if needed
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    
    return build('youtube', 'v3', credentials=creds)

def get_channel_id():
    """Get authenticated user's channel ID"""
    youtube = get_youtube_service()
    if not youtube:
        return None
    
    request = youtube.channels().list(
        part='id',
        mine=True
    )
    response = request.execute()
    
    if response['items']:
        return response['items'][0]['id']
    return None

def get_recent_comments(youtube, max_results=20):
    """Fetch recent comments from channel"""
    try:
        request = youtube.commentThreads().list(
            part='snippet,replies',
            allThreadsRelatedToChannelId=CHANNEL_ID,
            maxResults=max_results,
            searchTerms='',
            order='relevance',
            textFormat='plainText'
        )
        response = request.execute()
        return response.get('items', [])
    except Exception as e:
        print(f"❌ Error fetching comments: {e}")
        return []

def categorize_comment(text):
    """Categorize comment and return response"""
    text_lower = text.lower()
    
    for category, data in RESPONSES.items():
        for trigger in data['triggers']:
            if trigger in text_lower:
                return {
                    "category": category,
                    "response": data['response'],
                    "should_auto_reply": True
                }
    
    # Default: flag for review
    return {
        "category": "review",
        "response": None,
        "should_auto_reply": False
    }

def reply_to_comment(youtube, comment_id, reply_text):
    """Reply to a comment"""
    try:
        request = youtube.comments().insert(
            part='snippet',
            body={
                'snippet': {
                    'textOriginal': reply_text,
                    'parentId': comment_id
                }
            }
        )
        response = request.execute()
        return True
    except Exception as e:
        print(f"⚠️ Could not reply to comment {comment_id}: {e}")
        return False

def process_comments():
    """Main loop: fetch comments, categorize, reply, log"""
    youtube = get_youtube_service()
    if not youtube:
        print("❌ Could not authenticate with YouTube API")
        return False
    
    print("YouTube Comment Monitor Started")
    print(f"Channel: {CHANNEL_ID}")
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    comments = get_recent_comments(youtube, max_results=20)
    
    if not comments:
        print("✅ No new comments to process")
        return True
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_processed": 0,
        "auto_replied": 0,
        "flagged_for_review": 0,
        "comments": []
    }
    
    for thread in comments:
        # Get main comment
        main_comment = thread['snippet']['topLevelComment']
        comment_id = main_comment['id']
        author = main_comment['snippet']['authorDisplayName']
        text = main_comment['snippet']['textDisplay']
        
        # Categorize
        categorization = categorize_comment(text)
        
        # Log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "comment_id": comment_id,
            "author": author,
            "text": text[:200],
            "category": categorization['category'],
            "auto_replied": categorization['should_auto_reply'],
            "response_sent": None
        }
        
        # Reply if applicable
        if categorization['should_auto_reply']:
            success = reply_to_comment(youtube, comment_id, categorization['response'])
            if success:
                print(f"✅ Replied to {author}: {categorization['category']}")
                stats['auto_replied'] += 1
                log_entry['response_sent'] = categorization['response']
            else:
                print(f"⚠️ Failed to reply to {author}")
        else:
            print(f"🚩 Flagged for review: {author} ({categorization['category']})")
            stats['flagged_for_review'] += 1
        
        stats['comments'].append(log_entry)
        stats['total_processed'] += 1
    
    # Log stats
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(stats) + '\n')
    
    print()
    print(f"✅ Processed: {stats['total_processed']}")
    print(f"✅ Auto-replied: {stats['auto_replied']}")
    print(f"🚩 Flagged: {stats['flagged_for_review']}")
    
    return True

if __name__ == "__main__":
    success = process_comments()
    exit(0 if success else 1)
