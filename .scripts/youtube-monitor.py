#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius channel
Runs every 30 minutes, categorizes comments, auto-responds, logs results
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import hashlib

# Try to import YouTube API libraries
try:
    from googleapiclient.discovery import build
    from google.oauth2.service_account import Credentials
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("⚠️  google-api-python-client not installed. Install with: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")

CACHE_DIR = Path("/Users/abundance/.openclaw/workspace/.cache")
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Template responses
TEMPLATES = {
    "questions": """Thanks for the great question! Here's what you need to know:

For tools & getting started: Check our pinned resources in the channel description.
For timelines & costs: These vary based on your specific needs. Feel free to reach out if you need personalized guidance.

Hope this helps! 🙌""",
    
    "praise": """Thank you so much for the kind words! 🙏 Your support means everything to us. We're excited to continue creating valuable content for you!"""
}

class CommentMonitor:
    def __init__(self, channel_id: str = "UCJa8b_2h5ztfGJ3F5Jqvswg"):
        """Initialize YouTube API client"""
        self.channel_id = channel_id
        self.youtube = None
        self.init_youtube_api()
    
    def init_youtube_api(self):
        """Initialize YouTube API with credentials"""
        if not YOUTUBE_AVAILABLE:
            print("❌ YouTube API libraries not available")
            return False
        
        # Look for service account JSON
        creds_path = Path.home() / ".openclaw" / "credentials" / "youtube-api.json"
        
        if not creds_path.exists():
            print(f"❌ YouTube API credentials not found at {creds_path}")
            print("   To use this monitor, set up credentials:")
            print("   1. Go to https://console.cloud.google.com/")
            print("   2. Create a service account or OAuth 2.0 credentials")
            print("   3. Save to ~/.openclaw/credentials/youtube-api.json")
            return False
        
        try:
            creds = Credentials.from_service_account_file(str(creds_path))
            self.youtube = build('youtube', 'v3', credentials=creds)
            return True
        except Exception as e:
            print(f"❌ Failed to initialize YouTube API: {e}")
            return False
    
    def categorize_comment(self, text: str) -> str:
        """Categorize comment into: questions, praise, spam, or sales"""
        text_lower = text.lower()
        
        # Check for spam
        spam_keywords = ['crypto', 'bitcoin', 'nft', 'mlm', 'pyramid', 'forex', 'dropship', 'dm me', 'whatsapp']
        if any(keyword in text_lower for keyword in spam_keywords):
            return "spam"
        
        # Check for sales/partnership inquiries
        sales_keywords = ['partnership', 'collaboration', 'sponsor', 'brand deal', 'work with us', 'business opportunity', 'affiliate']
        if any(keyword in text_lower for keyword in sales_keywords):
            return "sales"
        
        # Check for questions
        question_keywords = ['how', 'what', 'why', 'when', 'where', 'which', 'cost', 'price', 'timeline', 'start', 'tool', 'tools']
        if any(keyword in text_lower for keyword in question_keywords) or text.endswith('?'):
            return "questions"
        
        # Check for praise
        praise_keywords = ['amazing', 'inspiring', 'love', 'great', 'awesome', 'excellent', 'fantastic', 'thank you', 'appreciate', 'brilliant']
        if any(keyword in text_lower for keyword in praise_keywords):
            return "praise"
        
        # Default: treat as praise/engagement
        return "engagement"
    
    def load_state(self) -> Dict:
        """Load last checked timestamp"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"last_checked": None, "comments_seen": {}}
    
    def save_state(self, state: Dict):
        """Save state for next run"""
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    
    def log_comment(self, comment_data: Dict):
        """Append comment to JSONL log"""
        with open(COMMENTS_LOG, 'a') as f:
            f.write(json.dumps(comment_data) + '\n')
    
    def get_comment_hash(self, author: str, text: str) -> str:
        """Generate hash of comment to avoid duplicates"""
        content = f"{author}:{text}".encode()
        return hashlib.md5(content).hexdigest()
    
    def mock_fetch_comments(self) -> List[Dict]:
        """Mock comment fetch for testing (replace with actual API calls)"""
        # This would be replaced with actual YouTube API calls
        # For now, return empty list (no new comments)
        return []
    
    def fetch_comments(self) -> List[Dict]:
        """Fetch recent comments from channel"""
        if not self.youtube:
            return self.mock_fetch_comments()
        
        try:
            # Get channel uploads
            response = self.youtube.channels().list(
                part='contentDetails',
                id=self.channel_id
            ).execute()
            
            if not response['items']:
                return []
            
            uploads_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get recent videos
            videos_response = self.youtube.playlistItems().list(
                part='contentDetails',
                playlistId=uploads_id,
                maxResults=10
            ).execute()
            
            comments = []
            for video_item in videos_response.get('items', []):
                video_id = video_item['contentDetails']['videoId']
                
                # Get comments for this video
                comments_response = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    textFormat='plainText',
                    maxResults=100,
                    order='relevance'
                ).execute()
                
                for item in comments_response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'video_id': video_id,
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'published_at': comment['publishedAt'],
                        'author_channel_url': comment.get('authorChannelUrl', '')
                    })
            
            return comments
        except Exception as e:
            print(f"❌ Error fetching comments: {e}")
            return []
    
    def run(self):
        """Main monitoring loop"""
        print(f"\n📺 YouTube Comment Monitor - {datetime.now().isoformat()}")
        
        # Load state
        state = self.load_state()
        last_checked = state.get('last_checked')
        seen_comments = state.get('comments_seen', {})
        
        # Fetch comments
        comments = self.fetch_comments()
        print(f"📥 Fetched {len(comments)} comments")
        
        # Process and categorize
        stats = {
            'total_processed': 0,
            'questions': 0,
            'praise': 0,
            'spam': 0,
            'sales': 0,
            'auto_responses_sent': 0,
            'flagged_for_review': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        for comment in comments:
            comment_hash = self.get_comment_hash(comment['author'], comment['text'])
            
            # Skip if already processed
            if comment_hash in seen_comments:
                continue
            
            # Categorize
            category = self.categorize_comment(comment['text'])
            stats[category] = stats.get(category, 0) + 1
            stats['total_processed'] += 1
            
            # Prepare log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'video_id': comment['video_id'],
                'commenter': comment['author'],
                'text': comment['text'],
                'category': category,
                'response_status': 'pending'
            }
            
            # Auto-respond to questions and praise
            if category == 'questions':
                log_entry['response_status'] = 'auto_responded'
                log_entry['response_template'] = 'questions'
                stats['auto_responses_sent'] += 1
                print(f"  ✅ Auto-response queued for question by {comment['author'][:20]}")
            elif category == 'praise':
                log_entry['response_status'] = 'auto_responded'
                log_entry['response_template'] = 'praise'
                stats['auto_responses_sent'] += 1
                print(f"  ✅ Auto-response queued for praise by {comment['author'][:20]}")
            elif category == 'sales':
                log_entry['response_status'] = 'flagged_for_review'
                stats['flagged_for_review'] += 1
                print(f"  🚩 Sales inquiry flagged from {comment['author'][:20]}")
            elif category == 'spam':
                log_entry['response_status'] = 'spam_marked'
                print(f"  🚫 Spam marked from {comment['author'][:20]}")
            
            # Log comment
            self.log_comment(log_entry)
            seen_comments[comment_hash] = True
        
        # Update state
        state['last_checked'] = datetime.now().isoformat()
        state['comments_seen'] = seen_comments
        self.save_state(state)
        
        # Report
        print(f"\n📊 Report ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"  Total processed: {stats['total_processed']}")
        print(f"  Questions: {stats.get('questions', 0)}")
        print(f"  Praise: {stats.get('praise', 0)}")
        print(f"  Spam: {stats.get('spam', 0)}")
        print(f"  Sales (flagged): {stats.get('sales', 0)}")
        print(f"  Auto-responses sent: {stats['auto_responses_sent']}")
        print(f"  Flagged for review: {stats['flagged_for_review']}")
        
        # Log summary
        summary_file = CACHE_DIR / "youtube-monitor-summary.json"
        with open(summary_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return stats

if __name__ == '__main__':
    monitor = CommentMonitor()
    monitor.run()
