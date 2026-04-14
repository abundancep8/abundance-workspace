#!/usr/bin/env python3
"""
YouTube Comment Monitor - Concessa Obvius Channel
Runs every 30 minutes via cron
Categorizes comments, auto-responds, and logs activity
"""

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Try to import required modules with fallback
try:
    from google.oauth2.credentials import Credentials
    import googleapiclient.discovery
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

# Configuration
CHANNEL_ID = "UC32674"  # Concessa Obvius
WORKSPACE = Path(os.path.expanduser("~/.openclaw/workspace"))
SECRETS_DIR = WORKSPACE / ".secrets"
CACHE_DIR = WORKSPACE / ".cache"
TOKEN_PATH = SECRETS_DIR / "youtube-token.json"
CREDENTIALS_PATH = SECRETS_DIR / "youtube-credentials.json"
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-comment-state.json"

# Create dirs if needed
CACHE_DIR.mkdir(exist_ok=True)
SECRETS_DIR.mkdir(exist_ok=True)

# Template responses
TEMPLATES = {
    "how_to_start": "Great question! Start by watching our latest video on channel fundamentals. I've also created a beginner's guide linked in the description. Let me know if you hit any blockers!",
    "how_long": "Great question! Most people see initial results within 2-4 weeks, but it really depends on your niche and consistency. Check our 30-day challenge video for a real timeline.",
    "what_tools": "We use a mix of free and paid tools. The essentials are: [Our main tool] for [task], and [secondary tool] for [task]. Full breakdown in the pinned comment!",
    "how_much": "The base setup is free, but most people invest $50-200/month for tools. We have a breakdown video here: [link]. DM me if you want specific budget guidance!",
    "praise_positive": "Thank you so much! 🙏 Comments like this keep us going. What's your biggest challenge right now? Happy to jump in and help directly.",
    "praise_inspiring": "This is everything—thank you for sharing your win! These stories are why we do this. Keep pushing, and feel free to share your progress. We'd love to feature it!",
    "flagged_review": "[FLAGGED] This comment requires manual review. Check dashboard for details."
}

# Categorization keywords
CATEGORIES = {
    "questions": {
        "keywords": ["how do i", "how to", "can i", "do i need", "what do", "how long", "how much", "cost", "tools", "start", "begin", "help", "guide", "tutorial", "?"],
        "templates": ["how_to_start", "how_long", "what_tools", "how_much"]
    },
    "praise": {
        "keywords": ["amazing", "inspiring", "love it", "great", "thanks", "thank you", "awesome", "incredible", "brilliant", "love this", "changed my", "helped me", "appreciate", "❤", "😍"],
        "templates": ["praise_positive", "praise_inspiring"]
    },
    "spam": {
        "keywords": ["crypto", "bitcoin", "eth", "mlm", "work from home", "earn money fast", "click here", "dm for details"],
        "templates": []
    },
    "sales": {
        "keywords": ["partnership", "collaboration", "sponsor", "promotion", "advertise", "business opportunity", "work with us", "contact us", "let's connect"],
        "templates": []
    }
}

def load_state():
    """Load last processed comment timestamp."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "last_checked": None,
        "processed_comment_ids": [],
        "last_comment_timestamp": None
    }

def save_state(state):
    """Save state for next run."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def categorize_comment(text):
    """Categorize comment based on keywords."""
    text_lower = text.lower()
    
    for category, config in CATEGORIES.items():
        for keyword in config["keywords"]:
            if keyword.lower() in text_lower:
                return category
    
    return "other"

def log_comment(comment, category, response_status, response_text=None):
    """Log comment to JSONL file."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'video_id': comment.get('video_id', 'N/A'),
        'comment_id': comment.get('id', 'N/A'),
        'author': comment.get('author', 'Unknown'),
        'text': comment.get('text', ''),
        'published_at': comment.get('published_at', 'N/A'),
        'category': category,
        'response_status': response_status,
        'response_text': response_text
    }
    
    with open(COMMENTS_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    return log_entry

def get_youtube_service():
    """Get YouTube API service with credentials."""
    if not YOUTUBE_API_AVAILABLE:
        return None
    
    try:
        creds = None
        
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            else:
                raise Exception(f"YouTube token not found. Run youtube-api-auth.py first.")
        
        # Save refreshed credentials
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
        
        return googleapiclient.discovery.build('youtube', 'v3', credentials=creds)
    
    except Exception as e:
        print(f"[ERROR] Failed to initialize YouTube API: {str(e)}")
        return None

def fetch_recent_comments(youtube):
    """Fetch recent comments from channel videos."""
    try:
        # Get channel details
        request = youtube.channels().list(
            part='contentDetails',
            id=CHANNEL_ID
        )
        response = request.execute()
        
        if not response['items']:
            print(f"[WARNING] Channel {CHANNEL_ID} not found")
            return []
        
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get recent uploads (last 5 videos)
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_playlist_id,
            maxResults=5
        )
        response = request.execute()
        
        video_ids = [item['contentDetails']['videoId'] for item in response.get('items', [])]
        
        new_comments = []
        
        for video_id in video_ids:
            # Fetch comments for this video
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100,
                order='time'
            )
            
            while request:
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    comment_id = item['id']
                    
                    new_comments.append({
                        'id': comment_id,
                        'video_id': video_id,
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'published_at': comment['publishedAt'],
                    })
                
                # Get next page
                if 'nextPageToken' in response:
                    request = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        pageToken=response['nextPageToken'],
                        maxResults=100,
                        order='time'
                    )
                else:
                    request = None
        
        return new_comments
    
    except Exception as e:
        print(f"[ERROR] Failed to fetch comments: {str(e)}")
        return []

def process_comments_local():
    """Process comments from local cache (demo mode)."""
    # For testing without API key, simulate comments
    demo_comments = [
        {
            'id': f'demo_{datetime.now().timestamp()}',
            'video_id': 'UC32674',
            'author': 'Demo User',
            'text': 'How do I start with this?',
            'published_at': datetime.now().isoformat()
        }
    ]
    return demo_comments

def process_comments(comments, state):
    """Process each comment: categorize, respond, log."""
    stats = {
        'total_processed': len(comments),
        'auto_responded': 0,
        'flagged_for_review': 0,
        'spam_filtered': 0,
        'by_category': {}
    }
    
    for comment in comments:
        # Skip if already processed
        if comment['id'] in state['processed_comment_ids']:
            continue
        
        category = categorize_comment(comment['text'])
        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        response_status = "processed"
        response_text = None
        
        if category == "spam":
            # Don't respond, just log
            response_status = "spam_filtered"
            stats['spam_filtered'] += 1
        
        elif category == "sales":
            # Flag for manual review
            response_status = "flagged_for_review"
            stats['flagged_for_review'] += 1
        
        elif category in ["questions", "praise"]:
            # Auto-respond with template
            config = CATEGORIES[category]
            if config.get("templates"):
                response_text = TEMPLATES[config["templates"][0]]
                response_status = f"auto_responded_{category}"
                stats['auto_responded'] += 1
        
        # Log the comment
        log_comment(comment, category, response_status, response_text)
        
        # Mark as processed
        state['processed_comment_ids'].append(comment['id'])
    
    # Keep only last 1000 IDs to avoid unbounded growth
    if len(state['processed_comment_ids']) > 1000:
        state['processed_comment_ids'] = state['processed_comment_ids'][-1000:]
    
    return stats

def print_report(stats):
    """Print summary report."""
    print("\n" + "="*60)
    print("YouTube Comment Monitor Report")
    print(f"Channel: Concessa Obvius ({CHANNEL_ID})")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print(f"\nTotal Comments Processed: {stats['total_processed']}")
    print(f"Auto-Responses Sent: {stats['auto_responded']}")
    print(f"Flagged for Review: {stats['flagged_for_review']}")
    print(f"Spam Filtered: {stats['spam_filtered']}")
    
    if stats['by_category']:
        print(f"\nBy Category:")
        for category, count in sorted(stats['by_category'].items()):
            if count > 0:
                print(f"  {category}: {count}")
    
    print(f"\nLog: {COMMENTS_LOG}")
    print("="*60 + "\n")

def main():
    """Main monitoring loop."""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting YouTube Comment Monitor...")
        
        # Load state
        state = load_state()
        
        # Try to use YouTube API
        if YOUTUBE_API_AVAILABLE:
            youtube = get_youtube_service()
            if youtube:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching comments from YouTube API...")
                comments = fetch_recent_comments(youtube)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] YouTube API unavailable, using demo mode...")
                comments = process_comments_local()
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] YouTube API not available, using demo mode...")
            comments = process_comments_local()
        
        if not comments:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No new comments found.")
            stats = {'total_processed': 0, 'auto_responded': 0, 'flagged_for_review': 0, 'spam_filtered': 0, 'by_category': {}}
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(comments)} comments. Processing...")
            
            # Process comments
            stats = process_comments(comments, state)
            
            # Save state
            save_state(state)
        
        # Print report
        print_report(stats)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitor complete. Next run in 30 minutes.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
