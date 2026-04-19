#!/usr/bin/env python3
"""
YouTube Comment Monitor - Concessa Obvius Channel
Monitors for new comments, categorizes, auto-responds, and logs.
"""

import os
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import logging

# Configure logging
log_dir = Path(".cache")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "youtube-monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import YouTube API
try:
    from google.auth.transport.requests import Request
    from google.oauth2.service_account import Credentials
    from google.auth.oauthlib.flow import InstalledAppFlow
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False
    logger.warning("Google API libraries not installed. Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")


# ============================================================================
# CONFIGURATION
# ============================================================================

CHANNEL_ID = "UCa_mZVVqV5Aq48a0MnIjS-w"  # Concessa Obvius (update with actual ID)
CREDENTIALS_FILE = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube_credentials.json"
TOKEN_FILE = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube_token.json"
COMMENTS_LOG = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-comments.jsonl"
STATE_FILE = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-monitor-state.json"

# Auto-response templates
RESPONSE_TEMPLATES = {
    "question": """Thanks for the question! Here are some resources to help:
• Visit our website for detailed guides: [link]
• Check our FAQ section for common topics
• Feel free to ask more specific questions!""",
    
    "praise": """Thank you so much for the kind words! 🙏 We're thrilled you found value in this. Your support means everything to us!"""
}

# Category patterns (simple regex-based; can upgrade to LLM-based)
PATTERNS = {
    "spam": [
        r"crypto|bitcoin|ethereum|nft|web3|blockchain",
        r"mlm|multi.level|network marketing",
        r"earn money fast|click here|limited time",
        r"♻|💰|📱|🔗",  # Spam emoji patterns
    ],
    "sales": [
        r"partnership|collaboration|sponsor|brand deal",
        r"influencer|promotion|affiliate",
        r"business opportunity|invest|roi",
    ],
    "question": [
        r"how (do|can|to|would)",
        r"what.*cost|price|pricing",
        r"timeline|how long|when",
        r"which.*tool|recommend",
        r"can you|could you|would you",
        r"\?$",  # Ends with question mark
    ],
    "praise": [
        r"amazing|awesome|incredible|fantastic|great|love|excellent",
        r"inspiring|motivating|helpful|useful|brilliant",
        r"thank you|thanks|appreciate|grateful",
        r"changed my life|game.?changer",
    ]
}


# ============================================================================
# YOUTUBE API INTEGRATION
# ============================================================================

def get_youtube_service():
    """Authenticate and return YouTube API service."""
    if not HAS_GOOGLE_API:
        logger.error("Google API libraries required. Install: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return None
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
    
    # Try to use existing token
    if TOKEN_FILE.exists():
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            if credentials and credentials.valid:
                return build('youtube', 'v3', credentials=credentials)
        except Exception as e:
            logger.warning(f"Token file invalid: {e}")
    
    # Need to set up OAuth flow (requires user interaction)
    logger.error("""
    ❌ No valid YouTube credentials found.
    
    To set up:
    1. Go to https://console.cloud.google.com
    2. Create a project and enable YouTube Data API v3
    3. Create OAuth 2.0 credentials (Desktop app)
    4. Download JSON and save to: {creds}
    5. Run this script again to complete authorization
    """.format(creds=CREDENTIALS_FILE))
    return None


def get_channel_id_from_handle(service, handle: str) -> Optional[str]:
    """Convert @handle to channel ID."""
    try:
        request = service.search().list(
            part='snippet',
            q=f"@{handle}",
            type='channel',
            maxResults=1
        )
        response = request.execute()
        if response['items']:
            return response['items'][0]['snippet']['channelId']
    except Exception as e:
        logger.error(f"Error looking up channel: {e}")
    return None


def fetch_new_comments(service) -> List[Dict]:
    """Fetch new comments since last check."""
    if not service:
        logger.error("No YouTube service available")
        return []
    
    # Load state
    state = load_state()
    last_check = datetime.fromisoformat(state.get('last_check', (datetime.utcnow() - timedelta(minutes=35)).isoformat()))
    
    new_comments = []
    try:
        # Get channel uploads
        request = service.channels().list(
            part='contentDetails',
            id=CHANNEL_ID
        )
        response = request.execute()
        
        if not response['items']:
            logger.warning(f"Channel {CHANNEL_ID} not found")
            return []
        
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get recent videos
        request = service.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=5
        )
        videos = request.execute()
        
        # Fetch comments from each video
        for video_item in videos.get('items', []):
            video_id = video_item['snippet']['resourceId']['videoId']
            
            request = service.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100,
                order='relevance',
                textFormat='plainText'
            )
            
            while request:
                response = request.execute()
                
                for thread in response.get('items', []):
                    comment = thread['snippet']['topLevelComment']['snippet']
                    comment_time = datetime.fromisoformat(
                        comment['publishedAt'].replace('Z', '+00:00')
                    )
                    
                    # Only include comments since last check
                    if comment_time > last_check:
                        new_comments.append({
                            'videoId': video_id,
                            'commentId': thread['id'],
                            'authorName': comment['authorDisplayName'],
                            'authorChannelId': comment.get('authorChannelId', {}).get('value', 'unknown'),
                            'text': comment['textDisplay'],
                            'publishedAt': comment['publishedAt'],
                            'timestamp': datetime.utcnow().isoformat(),
                        })
                
                # Check for next page
                if 'nextPageToken' in response:
                    request = service.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        pageToken=response['nextPageToken'],
                        maxResults=100,
                        order='relevance',
                        textFormat='plainText'
                    )
                else:
                    request = None
        
        logger.info(f"Found {len(new_comments)} new comments")
        
    except Exception as e:
        logger.error(f"Error fetching comments: {e}")
    
    return new_comments


# ============================================================================
# CATEGORIZATION
# ============================================================================

def categorize_comment(text: str) -> str:
    """Categorize comment: spam, sales, question, praise, or other."""
    text_lower = text.lower()
    
    # Check patterns in order of priority
    for category in ['spam', 'sales', 'question', 'praise']:
        for pattern in PATTERNS[category]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return category
    
    return 'other'


# ============================================================================
# AUTO-RESPONSES
# ============================================================================

def should_auto_respond(category: str) -> bool:
    """Determine if comment should get auto-response."""
    return category in ['question', 'praise']


def post_response(service, comment_id: str, text: str) -> bool:
    """Post a reply to a comment."""
    if not service:
        return False
    
    try:
        request = service.comments().insert(
            part='snippet',
            body={
                'snippet': {
                    'parentId': comment_id,
                    'textOriginal': text
                }
            }
        )
        request.execute()
        logger.info(f"Posted response to {comment_id}")
        return True
    except Exception as e:
        logger.warning(f"Could not post response: {e}")
        return False


# ============================================================================
# LOGGING & STATE
# ============================================================================

def load_state() -> Dict:
    """Load monitor state."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load state: {e}")
    
    return {'last_check': (datetime.utcnow() - timedelta(hours=1)).isoformat()}


def save_state(state: Dict):
    """Save monitor state."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Could not save state: {e}")


def log_comment(comment: Dict, category: str, response_status: str):
    """Log comment to JSONL file."""
    try:
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'videoId': comment['videoId'],
            'commentId': comment['commentId'],
            'commenter': comment['authorName'],
            'authorChannelId': comment['authorChannelId'],
            'text': comment['text'],
            'publishedAt': comment['publishedAt'],
            'category': category,
            'response_status': response_status,
        }
        
        COMMENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(COMMENTS_LOG, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
    except Exception as e:
        logger.error(f"Could not log comment: {e}")


# ============================================================================
# REPORTING
# ============================================================================

def generate_report(stats: Dict) -> str:
    """Generate monitoring report."""
    report = f"""
📊 YouTube Comment Monitor Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Channel: Concessa Obvius
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}

📈 Stats:
  • Comments processed: {stats['total_comments']}
  • Questions: {stats['questions']}
  • Praise: {stats['praise']}
  • Spam: {stats['spam']}
  • Sales (flagged): {stats['sales']}
  • Other: {stats['other']}

✅ Auto-responses sent: {stats['auto_responses_sent']}
🚩 Flagged for review: {stats['flagged_for_review']}

Last run: {stats.get('last_run', 'N/A')}
"""
    return report


# ============================================================================
# MAIN LOOP
# ============================================================================

def run_monitor():
    """Main monitoring loop."""
    logger.info("=" * 60)
    logger.info("YouTube Comment Monitor Starting")
    logger.info("=" * 60)
    
    # Initialize stats
    stats = {
        'total_comments': 0,
        'questions': 0,
        'praise': 0,
        'spam': 0,
        'sales': 0,
        'other': 0,
        'auto_responses_sent': 0,
        'flagged_for_review': 0,
        'last_run': datetime.now().isoformat(),
    }
    
    # Get YouTube service
    service = get_youtube_service()
    if not service:
        logger.error("Failed to authenticate with YouTube API")
        return stats
    
    # Fetch new comments
    comments = fetch_new_comments(service)
    stats['total_comments'] = len(comments)
    
    if not comments:
        logger.info("No new comments found")
        save_state({'last_check': datetime.utcnow().isoformat()})
        return stats
    
    # Process each comment
    for comment in comments:
        category = categorize_comment(comment['text'])
        stats[category] = stats.get(category, 0) + 1
        
        response_status = 'none'
        
        if should_auto_respond(category):
            template = RESPONSE_TEMPLATES.get(category, '')
            if template and post_response(service, comment['commentId'], template):
                response_status = 'auto_responded'
                stats['auto_responses_sent'] += 1
        elif category == 'sales':
            response_status = 'flagged_for_review'
            stats['flagged_for_review'] += 1
        
        # Log the comment
        log_comment(comment, category, response_status)
        
        logger.info(f"[{category.upper()}] {comment['authorName']}: {comment['text'][:60]}...")
    
    # Update state
    save_state({'last_check': datetime.utcnow().isoformat()})
    
    # Generate and log report
    report = generate_report(stats)
    logger.info(report)
    
    print(report)
    
    return stats


if __name__ == '__main__':
    stats = run_monitor()
    sys.exit(0 if stats.get('total_comments', 0) >= 0 else 1)
