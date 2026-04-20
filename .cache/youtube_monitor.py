#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Fetches, categorizes, responds to, and logs YouTube comments.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import re
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core.errors import GoogleAPIError
from googleapiclient.discovery import build
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
WORKSPACE_ROOT = Path.home() / ".openclaw" / "workspace"
CACHE_DIR = WORKSPACE_ROOT / ".cache"
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"
CREDENTIALS_FILE = CACHE_DIR / "youtube-credentials.json"
TOKEN_FILE = CACHE_DIR / "youtube-token.pickle"

# YouTube API
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CHANNEL_NAME = "Concessa Obvius"  # Will be resolved to channel ID

# Template responses
RESPONSES = {
    1: "Thanks for asking! Check our FAQ or reply for more details.",
    2: "Thanks so much for the kind words! 🙏"
}

# Ensure cache directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class YouTubeCommentMonitor:
    """Monitor and categorize YouTube comments."""
    
    def __init__(self):
        self.service = None
        self.channel_id = None
        self.state = self._load_state()
        
    def authenticate(self) -> bool:
        """Authenticate with YouTube API using OAuth 2.0."""
        try:
            creds = None
            
            # Load existing token
            if TOKEN_FILE.exists():
                with open(TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            
            # Refresh or create new credentials
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif not creds or not creds.valid:
                if not CREDENTIALS_FILE.exists():
                    logger.error(
                        f"❌ Credentials file not found: {CREDENTIALS_FILE}\n"
                        "Run: python3 youtube_monitor.py --setup-auth"
                    )
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token for reuse
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            
            self.service = build('youtube', 'v3', credentials=creds)
            logger.info("✅ Authenticated with YouTube API")
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False
    
    def resolve_channel_id(self) -> Optional[str]:
        """Resolve channel name to channel ID."""
        try:
            request = self.service.search().list(
                part='snippet',
                q=CHANNEL_NAME,
                type='channel',
                maxResults=1
            )
            results = request.execute()
            
            if results['items']:
                channel_id = results['items'][0]['snippet']['channelId']
                logger.info(f"✅ Resolved '{CHANNEL_NAME}' to {channel_id}")
                return channel_id
            else:
                logger.error(f"❌ Channel '{CHANNEL_NAME}' not found")
                return None
                
        except GoogleAPIError as e:
            logger.error(f"❌ Error resolving channel: {e}")
            return None
    
    def fetch_channel_comments(self) -> List[Dict]:
        """Fetch recent comments from the channel."""
        try:
            if not self.channel_id:
                self.channel_id = self.resolve_channel_id()
                if not self.channel_id:
                    return []
            
            # Get uploads playlist
            request = self.service.channels().list(
                part='contentDetails',
                id=self.channel_id
            )
            channel_data = request.execute()
            
            if not channel_data['items']:
                logger.warning(f"❌ No channel data found for {self.channel_id}")
                return []
            
            uploads_playlist_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get recent videos
            videos_request = self.service.playlistItems().list(
                part='contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=5  # Last 5 videos
            )
            videos_data = videos_request.execute()
            
            all_comments = []
            
            # Get comments from each video
            for item in videos_data.get('items', []):
                video_id = item['contentDetails']['videoId']
                comments = self._fetch_video_comments(video_id)
                all_comments.extend(comments)
            
            logger.info(f"📝 Fetched {len(all_comments)} comments")
            return all_comments
            
        except GoogleAPIError as e:
            logger.error(f"❌ Error fetching comments: {e}")
            return []
    
    def _fetch_video_comments(self, video_id: str) -> List[Dict]:
        """Fetch comments from a specific video."""
        try:
            comments = []
            request = self.service.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                maxResults=100,
                order='relevance'
            )
            
            while request and len(comments) < 100:
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'id': item['id'],
                        'video_id': video_id,
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'timestamp': comment['publishedAt'],
                        'reply_count': item['snippet']['totalReplyCount']
                    })
                
                # Pagination
                if 'nextPageToken' in response:
                    request = self.service.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        textFormat='plainText',
                        pageToken=response['nextPageToken'],
                        maxResults=100
                    )
                else:
                    break
            
            return comments
            
        except GoogleAPIError as e:
            logger.error(f"❌ Error fetching video comments for {video_id}: {e}")
            return []
    
    def categorize_comment(self, text: str) -> int:
        """Categorize a comment into 1-4."""
        text_lower = text.lower()
        
        # Category 3: Spam (crypto, MLM, unrelated promotions)
        spam_keywords = [
            r'\bcrypto\b', r'\bbitcoin\b', r'\bethereum\b', r'\bnft\b',
            r'\bmake money\b', r'\bearn money\b', r'\bmlm\b', r'\bnetwork\s+marketing\b',
            r'\bclick here\b', r'\bvisit my\b', r'\bcheck out my\b',
            r'\bfollowing\b.*\bpage\b', r'\bfollow me\b'
        ]
        for pattern in spam_keywords:
            if re.search(pattern, text_lower):
                return 3
        
        # Category 4: Sales (partnership, collaboration requests)
        sales_keywords = [
            r'\bpartner\b', r'\bcollaboration\b', r'\bsponsor\b',
            r'\bpromotion\b', r'\badvertise\b', r'\bproduct\s+placement\b',
            r'\bpaid\s+partnership\b'
        ]
        for pattern in sales_keywords:
            if re.search(pattern, text_lower):
                return 4
        
        # Category 2: Praise (amazing, inspiring, positive feedback)
        praise_keywords = [
            r'\bamazing\b', r'\bamazing\b', r'\binspiring\b', r'\blove\s+this\b',
            r'\brilliant\b', r'\bawesome\b', r'\bincredible\b', r'\bawesome\b',
            r'\bgreat\s+job\b', r'\blovely\b', r'\bbeautiful\b', r'\bthanks\b',
            r'\bthank you\b', r'\bappreciate\b', r'\blove it\b'
        ]
        for pattern in praise_keywords:
            if re.search(pattern, text_lower):
                return 2
        
        # Category 1: Questions (how-to, tools, cost, timeline)
        question_keywords = [
            r'\bhow\s+to\b', r'\bwhat\s+is\b', r'\bcan\s+i\b', r'\bwhere\b',
            r'\bwhy\b', r'\bcost\b', r'\bprice\b', r'\btimeline\b',
            r'\bwhen\b', r'\btool\b', r'\bsoftware\b', r'\bwhich\b'
        ]
        for pattern in question_keywords:
            if re.search(pattern, text_lower):
                return 1
        
        # Default to no_action
        return 0
    
    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        """Send a reply to a comment."""
        try:
            request = self.service.comments().insert(
                part='snippet',
                body={
                    'snippet': {
                        'parentId': comment_id,
                        'textOriginal': text
                    }
                }
            )
            request.execute()
            logger.info(f"✅ Replied to comment {comment_id}")
            return True
        except GoogleAPIError as e:
            logger.warning(f"⚠️  Could not reply to comment {comment_id}: {e}")
            return False
    
    def process_comments(self, comments: List[Dict]) -> Tuple[int, int, int]:
        """Process comments: categorize, respond, log."""
        processed_count = 0
        responded_count = 0
        flagged_count = 0
        
        processed_ids = self.state.get('processed_comment_ids', set())
        
        for comment in comments:
            comment_id = comment['id']
            
            # Skip already processed
            if comment_id in processed_ids:
                continue
            
            category = self.categorize_comment(comment['text'])
            response_status = 'no_action'
            
            # Auto-respond to questions and praise
            if category in [1, 2]:
                if self.reply_to_comment(comment_id, RESPONSES[category]):
                    response_status = 'auto_responded'
                    responded_count += 1
            
            # Flag sales for manual review
            elif category == 4:
                response_status = 'flagged'
                flagged_count += 1
            
            # Log the comment
            log_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'comment_id': comment_id,
                'commenter': comment['author'],
                'text': comment['text'],
                'category': category,
                'response_status': response_status
            }
            
            self._log_comment(log_entry)
            processed_ids.add(comment_id)
            processed_count += 1
            logger.info(f"📌 Processed: {comment['author']} (Cat {category}, {response_status})")
        
        # Update state
        self.state['processed_comment_ids'] = list(processed_ids)
        self.state['last_run'] = datetime.utcnow().isoformat() + 'Z'
        self._save_state()
        
        return processed_count, responded_count, flagged_count
    
    def _log_comment(self, entry: Dict):
        """Append comment to JSONL log."""
        try:
            with open(COMMENTS_LOG, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"❌ Failed to log comment: {e}")
    
    def _load_state(self) -> Dict:
        """Load state file."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load state: {e}")
        return {'processed_comment_ids': [], 'last_run': None}
    
    def _save_state(self):
        """Save state file."""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save state: {e}")
    
    def run(self) -> bool:
        """Run the monitor: fetch, categorize, respond, log."""
        logger.info("🚀 Starting YouTube Comment Monitor")
        
        if not self.authenticate():
            return False
        
        comments = self.fetch_channel_comments()
        if not comments:
            logger.warning("⚠️  No comments fetched")
            return False
        
        processed, responded, flagged = self.process_comments(comments)
        
        logger.info(
            f"✅ Session complete: "
            f"{processed} processed, {responded} responded, {flagged} flagged"
        )
        
        return True


def setup_auth():
    """Setup OAuth 2.0 credentials."""
    print("🔑 YouTube Comment Monitor - OAuth 2.0 Setup")
    print()
    print("1. Go to https://console.developers.google.com")
    print("2. Create a new project")
    print("3. Enable the YouTube Data API v3")
    print("4. Create OAuth 2.0 Desktop credentials")
    print("5. Download credentials as JSON")
    print()
    credentials_path = input(f"Enter path to credentials.json: ").strip()
    
    if os.path.exists(credentials_path):
        import shutil
        shutil.copy(credentials_path, CREDENTIALS_FILE)
        print(f"✅ Credentials saved to {CREDENTIALS_FILE}")
    else:
        print(f"❌ File not found: {credentials_path}")
        sys.exit(1)


def generate_report():
    """Generate session report."""
    try:
        if not COMMENTS_LOG.exists():
            print("❌ No comments log found")
            return
        
        # Parse log
        entries = []
        with open(COMMENTS_LOG, 'r') as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except:
                    pass
        
        if not entries:
            print("❌ No comments in log")
            return
        
        # Aggregate stats
        total = len(entries)
        by_category = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        by_response = {'auto_responded': 0, 'flagged': 0, 'no_action': 0}
        
        for entry in entries:
            by_category[entry['category']] += 1
            by_response[entry['response_status']] += 1
        
        # Print report
        print("\n" + "="*60)
        print("📊 YOUTUBE COMMENT MONITOR - SESSION REPORT")
        print("="*60)
        print(f"\n📈 TOTALS")
        print(f"   Total comments processed: {total}")
        print(f"   Last run: {entries[-1]['timestamp']}")
        print(f"\n📂 BY CATEGORY")
        print(f"   Questions (1): {by_category[1]}")
        print(f"   Praise (2): {by_category[2]}")
        print(f"   Spam (3): {by_category[3]}")
        print(f"   Sales (4): {by_category[4]}")
        print(f"   No Action (0): {by_category[0]}")
        print(f"\n✅ RESPONSES")
        print(f"   Auto-responded: {by_response['auto_responded']}")
        print(f"   Flagged for review: {by_response['flagged']}")
        print(f"   No action: {by_response['no_action']}")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--setup-auth':
            setup_auth()
        elif sys.argv[1] == '--report':
            generate_report()
    else:
        monitor = YouTubeCommentMonitor()
        success = monitor.run()
        sys.exit(0 if success else 1)
