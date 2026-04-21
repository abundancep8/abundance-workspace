#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Monitors channel for new comments, categorizes them, and auto-responds.
"""

import json
import os
import sys
from datetime import datetime
import re
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.exceptions import RefreshError
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Google API client not installed. Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Configuration
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CACHE_FILE = Path(__file__).parent.parent / '.cache' / 'youtube-comments.jsonl'
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
TOKEN_FILE = Path(__file__).parent.parent / '.cache' / 'youtube-token.json'
CREDENTIALS_FILE = Path(__file__).parent.parent / '.cache' / 'youtube-credentials.json'
STATE_FILE = Path(__file__).parent.parent / '.cache' / 'youtube-state.json'

# Channel handle/name to monitor
CHANNEL_NAME = "Concessa Obvius"

# Auto-response templates
RESPONSES = {
    'question': "Thanks for the question! I'm glad you're interested. Check our FAQ at [link] or reply here if you need more specific info.",
    'praise': "Thank you so much! This means a lot. Keep an eye out for more content coming soon! 🙌"
}

def get_youtube_service():
    """Authenticate and return YouTube API service."""
    creds = None
    
    # Load cached token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    
    # Refresh or request new token
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            creds = None
    
    # If no valid creds, get new ones
    if not creds or not creds.valid:
        if not CREDENTIALS_FILE.exists():
            print("ERROR: YouTube credentials not found.")
            print(f"Place your oauth2 credentials JSON at: {CREDENTIALS_FILE}")
            print("Get it from: https://console.cloud.google.com/apis/credentials")
            sys.exit(1)
        
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save token for next run
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    
    return build('youtube', 'v3', credentials=creds)

def find_channel_id(youtube, channel_name):
    """Find channel ID by channel name/handle."""
    try:
        # Try to find by custom URL (handle)
        request = youtube.search().list(
            q=channel_name,
            type='channel',
            part='snippet',
            maxResults=1
        )
        response = request.execute()
        
        if response['items']:
            return response['items'][0]['id']['channelId']
    except HttpError as e:
        print(f"ERROR: Failed to find channel: {e}")
    
    return None

def categorize_comment(text):
    """Categorize comment into: question, praise, spam, or sales."""
    text_lower = text.lower()
    
    # Spam patterns
    spam_keywords = ['bitcoin', 'crypto', 'mlm', 'scheme', 'forex', 'nft', 'token', 'presale']
    if any(keyword in text_lower for keyword in spam_keywords):
        return 'spam'
    
    # Sales/Partnership patterns
    sales_keywords = ['partnership', 'collaboration', 'sponsor', 'brand deal', 'ad', 'promote', 'business opportunity']
    if any(keyword in text_lower for keyword in sales_keywords):
        return 'sales'
    
    # Question patterns
    question_keywords = ['how', 'what', 'where', 'when', 'why', 'which', 'can i', 'do you', 'tools', 'cost', 'timeline', 'start']
    if any(keyword in text_lower for keyword in question_keywords) or text.rstrip().endswith('?'):
        return 'question'
    
    # Praise patterns
    praise_keywords = ['amazing', 'inspiring', 'love', 'great', 'awesome', 'fantastic', 'brilliant', 'incredible', 'thanks', 'thank you', '❤️', '🙌']
    if any(keyword in text_lower for keyword in praise_keywords):
        return 'praise'
    
    # Default: neutral/other
    return 'other'

def load_state():
    """Load last checked timestamp."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {'last_check': None, 'processed_ids': []}

def save_state(state):
    """Save state for next run."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def log_comment(comment_data):
    """Log comment to JSONL file."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'a') as f:
        f.write(json.dumps(comment_data) + '\n')

def post_reply(youtube, parent_id, reply_text):
    """Post reply to a comment."""
    try:
        request = youtube.comments().insert(
            part='snippet',
            body={
                'snippet': {
                    'parentId': parent_id,
                    'textOriginal': reply_text
                }
            }
        )
        response = request.execute()
        return response.get('id')
    except HttpError as e:
        print(f"ERROR: Failed to post reply: {e}")
        return None

def monitor_comments():
    """Main monitoring function."""
    print(f"[{datetime.now().isoformat()}] Starting YouTube comment monitor...")
    
    youtube = get_youtube_service()
    state = load_state()
    
    # Find channel
    channel_id = find_channel_id(youtube, CHANNEL_NAME)
    if not channel_id:
        print(f"ERROR: Could not find channel '{CHANNEL_NAME}'")
        return
    
    print(f"Found channel ID: {channel_id}")
    
    # Get channel's uploads playlist
    try:
        request = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        )
        channel_response = request.execute()
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    except (HttpError, KeyError, IndexError) as e:
        print(f"ERROR: Failed to get channel details: {e}")
        return
    
    # Fetch recent videos
    stats = {
        'total_processed': 0,
        'auto_responses_sent': 0,
        'flagged_for_review': 0,
        'by_category': {'question': 0, 'praise': 0, 'spam': 0, 'sales': 0, 'other': 0}
    }
    
    try:
        video_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_playlist_id,
            maxResults=5
        )
        video_response = video_request.execute()
        
        for item in video_response.get('items', []):
            video_id = item['contentDetails']['videoId']
            
            # Fetch comments for this video
            comments_request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                maxResults=20,
                order='relevance'
            )
            
            comments_response = comments_request.execute()
            
            for comment_thread in comments_response.get('items', []):
                comment = comment_thread['snippet']['topLevelComment']
                comment_id = comment['id']
                
                # Skip if already processed
                if comment_id in state['processed_ids']:
                    continue
                
                # Extract comment data
                snippet = comment['snippet']
                author = snippet['authorDisplayName']
                text = snippet['textDisplay']
                published = snippet['publishedAt']
                
                # Categorize
                category = categorize_comment(text)
                stats['by_category'][category] += 1
                stats['total_processed'] += 1
                
                # Prepare response
                response_status = 'none'
                response_id = None
                
                # Auto-respond to questions and praise
                if category == 'question':
                    response_text = RESPONSES['question']
                    response_id = post_reply(youtube, comment_id, response_text)
                    if response_id:
                        response_status = 'auto_sent'
                        stats['auto_responses_sent'] += 1
                    else:
                        response_status = 'failed'
                
                elif category == 'praise':
                    response_text = RESPONSES['praise']
                    response_id = post_reply(youtube, comment_id, response_text)
                    if response_id:
                        response_status = 'auto_sent'
                        stats['auto_responses_sent'] += 1
                    else:
                        response_status = 'failed'
                
                # Flag sales for review
                elif category == 'sales':
                    response_status = 'flagged'
                    stats['flagged_for_review'] += 1
                
                # Log comment
                log_comment({
                    'timestamp': datetime.now().isoformat(),
                    'video_id': video_id,
                    'comment_id': comment_id,
                    'author': author,
                    'text': text,
                    'published': published,
                    'category': category,
                    'response_status': response_status,
                    'response_id': response_id
                })
                
                # Mark as processed
                state['processed_ids'].append(comment_id)
                if len(state['processed_ids']) > 1000:  # Keep last 1000
                    state['processed_ids'] = state['processed_ids'][-1000:]
    
    except HttpError as e:
        print(f"ERROR: Failed to fetch comments: {e}")
        return
    
    # Update state
    state['last_check'] = datetime.now().isoformat()
    save_state(state)
    
    # Report
    print(f"\n{'='*60}")
    print(f"YouTube Comment Monitor Report")
    print(f"{'='*60}")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Channel: {CHANNEL_NAME}")
    print(f"{'='*60}")
    print(f"Total comments processed: {stats['total_processed']}")
    print(f"Auto-responses sent: {stats['auto_responses_sent']}")
    print(f"Flagged for review: {stats['flagged_for_review']}")
    print(f"\nBreakdown by category:")
    for cat, count in stats['by_category'].items():
        if count > 0:
            print(f"  {cat.capitalize()}: {count}")
    print(f"{'='*60}\n")
    
    return stats

if __name__ == '__main__':
    monitor_comments()
