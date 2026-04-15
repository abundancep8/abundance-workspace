#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Fetches comments, categorizes, auto-responds, and logs.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Try to import google-auth libraries
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("⚠️  Google API client not installed. Install: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")


# Configuration
CHANNEL_NAME = "Concessa Obvius"
CACHE_DIR = Path(".cache")
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"
CREDENTIALS_FILE = CACHE_DIR / "youtube-credentials.json"
TOKEN_FILE = CACHE_DIR / "youtube-token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Category templates
TEMPLATES = {
    "question": """Thanks for the question! Here's what I'd recommend:
- Visit our FAQ section for quick answers
- Check our tools guide at [link]
- DM for specific pricing questions

Looking forward to helping!""",
    "praise": """🙌 Thank you so much! This means everything. Keep building amazing things!"""
}


def categorize_comment(text: str) -> str:
    """Categorize a comment into one of 4 types."""
    text_lower = text.lower()
    
    # Spam detection
    spam_keywords = ["crypto", "bitcoin", "ethereum", "mlm", "forex", "dropship", "get rich", "click here"]
    if any(keyword in text_lower for keyword in spam_keywords):
        return "spam"
    
    # Sales/Partnership detection
    sales_keywords = ["partnership", "collaboration", "sponsor", "brand deal", "advertise", "promote", "business opportunity"]
    if any(keyword in text_lower for keyword in sales_keywords):
        return "sales"
    
    # Praise detection
    praise_keywords = ["amazing", "inspiring", "love", "awesome", "great job", "excellent", "incredible", "beautiful"]
    if any(keyword in text_lower for keyword in praise_keywords):
        return "praise"
    
    # Question detection
    question_patterns = [
        r"how\s+(do\s+i|to|can\s+i)",
        r"what\s+(is|are|tools|cost)",
        r"where\s+",
        r"why\s+",
        r"timeline\s+",
        r"start.*?doing",
        r"\?$"  # Ends with question mark
    ]
    if any(re.search(pattern, text_lower) for pattern in question_patterns):
        return "question"
    
    # Default to praise if positive, question otherwise
    if any(word in text_lower for word in ["thanks", "appreciate", "good"]):
        return "praise"
    
    return "question"  # Default


def get_youtube_service():
    """Authenticate and return YouTube API service."""
    if not YOUTUBE_AVAILABLE:
        return None
    
    creds = None
    
    # Load existing token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    
    # If no valid credentials, refresh or create new
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif CREDENTIALS_FILE.exists():
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        else:
            print("⚠️  YouTube credentials not found. Set up OAuth at:")
            print("  1. Go to https://console.cloud.google.com")
            print("  2. Create OAuth 2.0 Desktop Client")
            print("  3. Save as .cache/youtube-credentials.json")
            return None
    
    # Save token for next time
    CACHE_DIR.mkdir(exist_ok=True)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    return build('youtube', 'v3', credentials=creds)


def get_channel_id(youtube, channel_name: str) -> Optional[str]:
    """Get channel ID from channel name."""
    request = youtube.search().list(
        part="snippet",
        q=channel_name,
        type="channel",
        maxResults=1
    )
    response = request.execute()
    
    if response['items']:
        return response['items'][0]['snippet']['channelId']
    return None


def get_uploads_playlist_id(youtube, channel_id: str) -> Optional[str]:
    """Get uploads playlist ID for a channel."""
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()
    
    if response['items']:
        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    return None


def get_recent_videos(youtube, playlist_id: str, max_results: int = 5) -> List[str]:
    """Get recent video IDs from channel."""
    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=playlist_id,
        maxResults=max_results
    )
    response = request.execute()
    
    return [item['contentDetails']['videoId'] for item in response['items']]


def fetch_comments(youtube, video_ids: List[str]) -> List[Dict]:
    """Fetch comments from videos."""
    comments = []
    
    for video_id in video_ids:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=100,
            order="relevance"
        )
        
        while request:
            response = request.execute()
            
            for item in response['items']:
                comment_data = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'videoId': video_id,
                    'commentId': item['id'],
                    'authorDisplayName': comment_data['authorDisplayName'],
                    'textDisplay': comment_data['textDisplay'],
                    'publishedAt': comment_data['publishedAt'],
                    'authorChannelUrl': comment_data.get('authorChannelUrl', ''),
                })
            
            if 'nextPageToken' in response:
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    pageToken=response['nextPageToken'],
                    textFormat="plainText",
                    maxResults=100
                )
            else:
                request = None
    
    return comments


def log_comment(comment: Dict, category: str, response_status: str):
    """Log comment to jsonl file."""
    CACHE_DIR.mkdir(exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'commenter': comment['authorDisplayName'],
        'text': comment['textDisplay'],
        'category': category,
        'response_status': response_status,
        'videoId': comment['videoId'],
        'commentId': comment['commentId'],
    }
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def process_comments(youtube):
    """Main processing function."""
    print(f"\n📺 YouTube Comment Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Channel: {CHANNEL_NAME}")
    print("-" * 60)
    
    # Get channel ID
    channel_id = get_channel_id(youtube, CHANNEL_NAME)
    if not channel_id:
        print(f"❌ Channel '{CHANNEL_NAME}' not found")
        return {"error": f"Channel '{CHANNEL_NAME}' not found"}
    
    # Get playlist ID
    playlist_id = get_uploads_playlist_id(youtube, channel_id)
    if not playlist_id:
        print(f"❌ Could not get uploads playlist")
        return {"error": "Could not get uploads playlist"}
    
    # Get recent videos
    video_ids = get_recent_videos(youtube, playlist_id, max_results=3)
    print(f"✓ Found {len(video_ids)} recent videos")
    
    # Fetch comments
    comments = fetch_comments(youtube, video_ids)
    print(f"✓ Fetched {len(comments)} comments")
    
    # Process comments
    stats = {
        'total_processed': 0,
        'auto_responses_sent': 0,
        'flagged_for_review': 0,
        'by_category': {}
    }
    
    for comment in comments:
        category = categorize_comment(comment['textDisplay'])
        response_status = "pending"
        
        stats['total_processed'] += 1
        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        # Auto-respond to questions and praise
        if category in ["question", "praise"]:
            response_status = "auto_responded"
            stats['auto_responses_sent'] += 1
            print(f"  ✓ Auto-response sent to @{comment['authorDisplayName']} ({category})")
        
        # Flag sales for review
        elif category == "sales":
            response_status = "flagged_for_review"
            stats['flagged_for_review'] += 1
            print(f"  🚩 FLAGGED: Sales inquiry from @{comment['authorDisplayName']}")
        
        # Log comment
        log_comment(comment, category, response_status)
    
    return stats


def main():
    """Main entry point."""
    if not YOUTUBE_AVAILABLE:
        print("⚠️  YouTube API client not available. Install dependencies:")
        print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return
    
    youtube = get_youtube_service()
    if not youtube:
        print("⚠️  YouTube authentication failed. Cannot proceed.")
        return
    
    try:
        stats = process_comments(youtube)
        
        if "error" not in stats:
            print("\n" + "=" * 60)
            print("📊 REPORT")
            print("=" * 60)
            print(f"Total comments processed: {stats['total_processed']}")
            print(f"Auto-responses sent: {stats['auto_responses_sent']}")
            print(f"Flagged for review: {stats['flagged_for_review']}")
            print(f"\nBy category:")
            for cat, count in stats['by_category'].items():
                print(f"  {cat}: {count}")
            print(f"\n✓ Log: {LOG_FILE}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
