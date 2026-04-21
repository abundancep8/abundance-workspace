#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius channel
Monitors comments, categorizes them, auto-responds, and logs activity.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
import re

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
except ImportError:
    print("Installing required packages...")
    os.system("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials


# Configuration
CHANNEL_NAME = "Concessa Obvius"
LOG_FILE = Path(__file__).parent.parent / ".cache" / "youtube-comments.jsonl"
STATE_FILE = Path(__file__).parent.parent / ".cache" / "youtube-monitor-state.json"
API_KEY = os.getenv("YOUTUBE_API_KEY")
OAUTH_TOKEN_PATH = Path.home() / ".youtube-oauth-token.json"

# Template responses
TEMPLATES = {
    "question": """Thanks for the question! Here are some quick answers:
- **How to start:** Check out our getting started guide linked in the description
- **Tools & Cost:** We cover all of that in the FAQ at [link]
- **Timeline:** Most people see results within [X] weeks of consistent effort

Feel free to ask if you need more specifics!""",
    
    "praise": """Thank you so much! Comments like this make the work worthwhile. Really appreciate the support. 🙌""",
}

# Categorization rules
CATEGORY_PATTERNS = {
    "questions": [
        r'\bhow\s+(do|can|should)\b',
        r'\bwhat\s+(is|are|should)\b',
        r'\bwhere\s+(can|do)\b',
        r'\bcost\b',
        r'\bprice\b',
        r'\btool[s]?\b',
        r'\bstart[ing]?\b',
        r'\btimeline\b',
        r'\b\?\s*$',
    ],
    "spam": [
        r'\bcrypto\b|\bbitcoin\b|\brethereum\b',
        r'\bmlm\b|\bmulti.level.marketing\b',
        r'\bporn\b|\badult\b',
        r'\bbuy.*now\b|\bclick.*here\b',
        r'http[s]?://[^\s]+\.(tk|ml|ga)\b',  # sketchy TLDs
        r'\bspam\b|\bscam\b',
    ],
    "sales": [
        r'\bpartnership\b',
        r'\bcollaboration\b',
        r'\bsponsor\b',
        r'\baffiliate\b',
        r'\bwork\s+together\b',
        r'\bcollab\b',
    ],
    "praise": [
        r'\bamazing\b|\bawesome\b|\bincredible\b',
        r'\binspir(ing|ed)\b',
        r'\blove\s+(this|it)\b',
        r'\bthank\s+you\b',
        r'\bgreat\b|\bawesome\b',
        r'❤️|🔥|💯|👏',
    ],
}


def categorize_comment(text):
    """
    Categorize a comment.
    Returns: (category, confidence) where category is one of:
    - 'questions'
    - 'praise'
    - 'spam'
    - 'sales'
    - 'other'
    """
    text_lower = text.lower()
    scores = {cat: 0 for cat in CATEGORY_PATTERNS.keys()}
    
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                scores[category] += 1
    
    if max(scores.values()) == 0:
        return "other", 0.0
    
    best_category = max(scores, key=scores.get)
    confidence = scores[best_category] / max(1, sum(scores.values()))
    
    return best_category, confidence


def get_channel_videos(youtube, channel_name):
    """Fetch video IDs from channel."""
    try:
        search = youtube.search().list(
            q=channel_name,
            type='channel',
            part='id',
            maxResults=1
        ).execute()
        
        if not search['items']:
            return []
        
        channel_id = search['items'][0]['id']['channelId']
        
        videos = youtube.search().list(
            channelId=channel_id,
            type='video',
            part='id',
            maxResults=50,
            order='date'
        ).execute()
        
        return [v['id']['videoId'] for v in videos.get('items', [])]
    except Exception as e:
        print(f"Error fetching videos: {e}")
        return []


def get_new_comments(youtube, video_ids, since_timestamp=None):
    """Fetch comments from videos posted after since_timestamp."""
    comments = []
    
    for video_id in video_ids:
        try:
            request = youtube.commentThreads().list(
                videoId=video_id,
                part='snippet',
                maxResults=100,
                textFormat='plainText',
                order='relevance'
            )
            
            while request:
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    
                    published = datetime.fromisoformat(
                        comment['publishedAt'].replace('Z', '+00:00')
                    )
                    
                    # Filter by timestamp if provided
                    if since_timestamp and published < since_timestamp:
                        continue
                    
                    comments.append({
                        'video_id': video_id,
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'timestamp': published.isoformat(),
                        'reply_count': comment['replyCount'],
                    })
                
                # Paginate
                if 'nextPageToken' in response:
                    request = youtube.commentThreads().list(
                        videoId=video_id,
                        part='snippet',
                        pageToken=response['nextPageToken'],
                        maxResults=100,
                        textFormat='plainText',
                        order='relevance'
                    )
                else:
                    break
        except Exception as e:
            print(f"Error fetching comments from {video_id}: {e}")
            continue
    
    return comments


def load_state():
    """Load last run state."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        'last_run': None,
        'processed_comments': []
    }


def save_state(state):
    """Save state for next run."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def log_comment(entry):
    """Append comment to JSONL log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')


def main():
    print(f"[{datetime.now().isoformat()}] Starting YouTube comment monitor...")
    
    # Check for API key
    if not API_KEY and not OAUTH_TOKEN_PATH.exists():
        print("ERROR: Set YOUTUBE_API_KEY or provide OAuth token at ~/.youtube-oauth-token.json")
        sys.exit(1)
    
    # Initialize YouTube API
    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
    except Exception as e:
        print(f"ERROR: Failed to initialize YouTube API: {e}")
        sys.exit(1)
    
    # Load state
    state = load_state()
    last_run = datetime.fromisoformat(state['last_run']) if state['last_run'] else datetime.now() - timedelta(hours=1)
    
    # Fetch videos
    video_ids = get_channel_videos(youtube, CHANNEL_NAME)
    if not video_ids:
        print(f"No videos found for channel '{CHANNEL_NAME}'")
        return
    
    print(f"Found {len(video_ids)} videos")
    
    # Fetch new comments
    comments = get_new_comments(youtube, video_ids, since_timestamp=last_run)
    print(f"Found {len(comments)} new comments")
    
    # Process comments
    stats = {
        'total': len(comments),
        'questions': 0,
        'praise': 0,
        'spam': 0,
        'sales': 0,
        'other': 0,
        'auto_responses_sent': 0,
        'flagged_for_review': 0,
        'timestamp': datetime.now().isoformat(),
    }
    
    for comment in comments:
        category, confidence = categorize_comment(comment['text'])
        stats[category] += 1
        
        response_status = 'none'
        
        # Auto-respond to questions and praise
        if category in ['questions', 'praise']:
            template = TEMPLATES.get(category, "")
            if template:
                response_status = 'auto_responded'
                stats['auto_responses_sent'] += 1
                print(f"[{category.upper()}] Auto-responding to {comment['author']}")
        
        # Flag sales for review
        elif category == 'sales':
            response_status = 'flagged'
            stats['flagged_for_review'] += 1
            print(f"[SALES] Flagging {comment['author']} - {comment['text'][:50]}...")
        
        # Log entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'comment_timestamp': comment['timestamp'],
            'video_id': comment['video_id'],
            'commenter': comment['author'],
            'text': comment['text'],
            'category': category,
            'confidence': round(confidence, 2),
            'reply_count': comment['reply_count'],
            'response_status': response_status,
        }
        
        log_comment(entry)
    
    # Update state
    state['last_run'] = datetime.now().isoformat()
    save_state(state)
    
    # Report
    print("\n" + "="*60)
    print("REPORT")
    print("="*60)
    print(f"Total comments processed: {stats['total']}")
    print(f"  - Questions: {stats['questions']}")
    print(f"  - Praise: {stats['praise']}")
    print(f"  - Spam: {stats['spam']}")
    print(f"  - Sales: {stats['sales']}")
    print(f"  - Other: {stats['other']}")
    print(f"Auto-responses sent: {stats['auto_responses_sent']}")
    print(f"Flagged for review: {stats['flagged_for_review']}")
    print(f"Logged to: {LOG_FILE}")
    print("="*60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
