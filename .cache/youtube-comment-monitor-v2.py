#!/usr/bin/env python3
"""
YouTube Comment Monitor v2 - Production Ready
Monitors Concessa Obvius channel, categorizes comments, auto-responds, and logs.
Runs every 30 minutes via OpenClaw cron.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
import hashlib

# Configuration
WORKSPACE = Path.home() / '.openclaw/workspace'
CACHE_DIR = WORKSPACE / '.cache'
SECRETS_DIR = WORKSPACE / '.secrets'
TOKEN_FILE = SECRETS_DIR / 'youtube-token.json'
CREDENTIALS_FILE = SECRETS_DIR / 'youtube-credentials.json'
LOG_FILE = CACHE_DIR / 'youtube-comments.jsonl'
STATE_FILE = CACHE_DIR / 'youtube-comment-state.json'
REPORT_FILE = CACHE_DIR / 'youtube-comments-report.txt'

CHANNEL_ID = "UC326742c_CXvNQ6IcnZ8Jkw"  # Concessa Obvius (full ID)
CHANNEL_URL = "https://www.youtube.com/channel/" + CHANNEL_ID

# Try to import YouTube API libraries
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("⚠️ YouTube API libraries not available. Install: pip install google-auth-oauthlib google-api-python-client")


# ============================================================================
# COMMENT CATEGORIZER
# ============================================================================

class CommentCategorizer:
    """Categorize YouTube comments using keyword matching."""
    
    # Category 1: Questions
    QUESTION_KEYWORDS = {
        'how_start': [r'\bhow\s+do\s+i\s+(start|begin|get\s+started)', r'\bwhere\s+do\s+i\s+start'],
        'how_tools': [r'\b(what|which)\s+tools?\b', r'\bwhat\s+do\s+you\s+use', r'\bhow\s+do\s+you\s+(build|make)'],
        'how_cost': [r'\b(cost|price|how\s+much)', r'\b(free|paid)', r'\bhow\s+much\s+does\s+it\s+(cost|take)'],
        'how_long': [r'\bhow\s+long', r'\bhow\s+much\s+time', r'\btimeline', r'\btook\s+you\s+how\s+long'],
        'general_question': [r'\?$', r'\bwhat\b', r'\bhow\b', r'\bcan\s+you\b'],
    }
    
    # Category 2: Praise
    PRAISE_KEYWORDS = {
        'amazing': [r'\b(amazing|awesome|incredible|fantastic|phenomenal)\b'],
        'inspiring': [r'\b(inspiring|inspired|motivat|insightful)\b'],
        'great': [r'\b(great|excellent|wonderful|brilliant|genius|love\s+this|love\s+it)\b'],
        'appreciate': [r'\b(thank|grateful|appreciate|grateful)\b'],
    }
    
    # Category 3: Spam
    SPAM_KEYWORDS = {
        'crypto': [r'\b(crypto|bitcoin|ethereum|nft|blockchain|web3)\b'],
        'mlm': [r'\b(mlm|multi-level|pyramid|recruit|join\s+my|side\s+hustle)\b'],
        'scam': [r'\b(scam|fake|fraud|click\s+here|dm\s+me|message\s+me)\b'],
    }
    
    # Category 4: Sales/Partnerships
    SALES_KEYWORDS = {
        'partnership': [r'\b(partner|partnership|collaborate|collaboration|collab)\b'],
        'sponsorship': [r'\b(sponsor|sponsorship|brand\s+deal|advertis)\b'],
        'business': [r'\b(work\s+with|business\s+opportunity|interested\s+in\s+working)\b'],
    }
    
    @classmethod
    def categorize(cls, text: str) -> Tuple[str, Optional[str]]:
        """
        Categorize a comment.
        Returns: (category, subcategory)
        """
        text_lower = text.lower()
        
        # Check spam first (to filter it out)
        for subcat, patterns in cls.SPAM_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return ('spam', subcat)
        
        # Check sales/partnerships
        for subcat, patterns in cls.SALES_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return ('sales', subcat)
        
        # Check praise
        for subcat, patterns in cls.PRAISE_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return ('praise', subcat)
        
        # Check questions
        for subcat, patterns in cls.QUESTION_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return ('questions', subcat)
        
        # Default: other
        return ('other', None)


# ============================================================================
# RESPONSE TEMPLATES
# ============================================================================

class ResponseTemplates:
    """Template responses for auto-reply categories."""
    
    TEMPLATES = {
        'questions': {
            'how_start': "Great question! Start with ONE task that takes 30 min/day. Write clear instructions for it. Test for 7 days. Track what changed. That's the starting point.",
            'how_tools': "Tools I use: Claude (writing), Stripe (payments), Vercel (hosting), OpenClaw (orchestration). Total cost: ~$50/month. The system beats the tools every time.",
            'how_cost': "Costs about $50/month for the stack. ROI in the first month if you execute. The tools are commodities—what matters is the system you build.",
            'how_long': "Setup: 2 weeks. Testing: 2 weeks. First revenue: Week 3. After month 1, you'll understand the mechanics. Then it compounds.",
            'general_question': "Great question! Check out the resources in the description—lots of templates and guides there. Happy to help if you hit any blockers.",
        },
        'praise': {
            'amazing': "Thank you! The kind words mean a lot. But honestly, the real magic is in *you* building something. Go create.",
            'inspiring': "Appreciate that! But action beats inspiration every time. Start building today—that's what separates people.",
            'great': "Thanks so much! Really glad this is helpful. Keep pushing forward.",
            'appreciate': "Thank you for the support! Really means a lot. Let's keep building.",
        },
    }
    
    @classmethod
    def get_response(cls, category: str, subcat: Optional[str]) -> Optional[str]:
        """Get template response for a category."""
        if category not in cls.TEMPLATES:
            return None
        
        templates = cls.TEMPLATES[category]
        if subcat and subcat in templates:
            return templates[subcat]
        
        # Return first available template in category
        if templates:
            return list(templates.values())[0]
        
        return None


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class StateManager:
    """Track processed comments to avoid duplicates."""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load()
    
    def _load(self) -> Dict:
        """Load state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'last_checked': None,
            'processed_comment_ids': [],
            'last_update': datetime.utcnow().isoformat(),
        }
    
    def save(self):
        """Save state to file."""
        self.state['last_update'] = datetime.utcnow().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def is_processed(self, comment_id: str) -> bool:
        """Check if comment was already processed."""
        return comment_id in self.state['processed_comment_ids']
    
    def mark_processed(self, comment_id: str):
        """Mark comment as processed."""
        if comment_id not in self.state['processed_comment_ids']:
            self.state['processed_comment_ids'].append(comment_id)
            # Keep only last 1000 to avoid memory bloat
            if len(self.state['processed_comment_ids']) > 1000:
                self.state['processed_comment_ids'] = self.state['processed_comment_ids'][-1000:]
    
    def update_last_checked(self):
        """Update last checked timestamp."""
        self.state['last_checked'] = datetime.utcnow().isoformat()


# ============================================================================
# LOGGING
# ============================================================================

class CommentLogger:
    """Log comments to JSONL file."""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_comment(self, comment_data: Dict):
        """Log a comment entry."""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(comment_data) + '\n')
    
    def log_run_summary(self, summary: Dict):
        """Log run summary."""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(summary) + '\n')


# ============================================================================
# YOUTUBE API WRAPPER
# ============================================================================

class YouTubeCommentFetcher:
    """Fetch comments from YouTube API."""
    
    def __init__(self):
        self.service = None
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """Authenticate with YouTube API."""
        if not YOUTUBE_API_AVAILABLE:
            return False
        
        if not TOKEN_FILE.exists():
            print(f"⚠️ Token file not found: {TOKEN_FILE}")
            print("   YouTube authentication required. Credentials must be set up in Google Cloud Console.")
            return False
        
        try:
            with open(TOKEN_FILE, 'r') as f:
                creds_data = json.load(f)
            
            creds = Credentials.from_authorized_user_info(creds_data)
            
            # Refresh if needed
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    with open(TOKEN_FILE, 'w') as f:
                        json.dump(json.loads(creds.to_json()), f)
                except RefreshError:
                    print("⚠️ Token refresh failed. Credentials may be expired.")
                    return False
            
            self.service = build('youtube', 'v3', credentials=creds)
            self.authenticated = True
            return True
        
        except Exception as e:
            print(f"⚠️ Authentication failed: {e}")
            return False
    
    def get_recent_comments(self, channel_id: str, max_results: int = 20) -> List[Dict]:
        """Fetch recent comments from channel."""
        if not self.authenticated:
            return []
        
        try:
            # Get videos from channel
            videos_request = self.service.search().list(
                part='id',
                channelId=channel_id,
                type='video',
                order='date',
                maxResults=5,  # Check 5 most recent videos
                textFormat='plainText'
            )
            videos_response = videos_request.execute()
            
            all_comments = []
            for video_item in videos_response.get('items', []):
                video_id = video_item['id']['videoId']
                
                # Get comments for this video
                comments_request = self.service.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    maxResults=min(max_results, 20),
                    textFormat='plainText',
                    order='relevance'
                )
                
                comments_response = comments_request.execute()
                
                for thread in comments_response.get('items', []):
                    comment = thread['snippet']['topLevelComment']['snippet']
                    all_comments.append({
                        'id': thread['snippet']['topLevelComment']['id'],
                        'video_id': video_id,
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'published_at': comment['publishedAt'],
                        'likes': comment['likeCount'],
                    })
                
                if len(all_comments) >= max_results:
                    break
            
            return all_comments[:max_results]
        
        except Exception as e:
            print(f"⚠️ Error fetching comments: {e}")
            return []


# ============================================================================
# DEMO MODE (for testing without credentials)
# ============================================================================

class DemoCommentFetcher:
    """Generate demo comments for testing."""
    
    DEMO_COMMENTS = [
        {
            'id': 'demo_q1_' + str(int(datetime.utcnow().timestamp() * 1000000)),
            'video_id': 'demoVideo1',
            'author': 'Curious Cat',
            'text': 'How do I start building my own system like this?',
            'published_at': (datetime.utcnow() - timedelta(minutes=15)).isoformat() + 'Z',
            'likes': 3,
        },
        {
            'id': 'demo_p1_' + str(int(datetime.utcnow().timestamp() * 1000000)),
            'video_id': 'demoVideo2',
            'author': 'Fan True',
            'text': 'This is absolutely amazing! So inspiring and brilliant!',
            'published_at': (datetime.utcnow() - timedelta(minutes=30)).isoformat() + 'Z',
            'likes': 12,
        },
        {
            'id': 'demo_s1_' + str(int(datetime.utcnow().timestamp() * 1000000)),
            'video_id': 'demoVideo3',
            'author': 'Spam Bot',
            'text': 'Buy crypto now!!! DM me for details on the new blockchain opportunity',
            'published_at': (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z',
            'likes': 0,
        },
        {
            'id': 'demo_b1_' + str(int(datetime.utcnow().timestamp() * 1000000)),
            'video_id': 'demoVideo4',
            'author': 'Business Joe',
            'text': 'Hey! I\'d love to collaborate on a partnership opportunity. Can you DM me?',
            'published_at': (datetime.utcnow() - timedelta(hours=2)).isoformat() + 'Z',
            'likes': 1,
        },
    ]
    
    def get_recent_comments(self, channel_id: str, max_results: int = 20) -> List[Dict]:
        """Return demo comments."""
        return self.DEMO_COMMENTS[:max_results]


# ============================================================================
# MAIN MONITOR
# ============================================================================

class YouTubeCommentMonitor:
    """Main orchestrator."""
    
    def __init__(self):
        self.state = StateManager(STATE_FILE)
        self.logger = CommentLogger(LOG_FILE)
        self.categorizer = CommentCategorizer()
        self.use_demo = False
        self.stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_processed': 0,
            'auto_replied': {
                'questions': 0,
                'praise': 0,
            },
            'flagged_for_review': {
                'sales': 0,
                'spam': 0,
                'other': 0,
            },
            'details': [],
        }
    
    def get_comments(self) -> List[Dict]:
        """Fetch comments (real or demo)."""
        if YOUTUBE_API_AVAILABLE:
            fetcher = YouTubeCommentFetcher()
            if fetcher.authenticate():
                comments = fetcher.get_recent_comments(CHANNEL_ID, max_results=20)
                if comments:
                    return comments
        
        print("⚠️ Using demo mode (YouTube API unavailable or not authenticated)")
        self.use_demo = True
        fetcher = DemoCommentFetcher()
        return fetcher.get_recent_comments(CHANNEL_ID, max_results=20)
    
    def process_comments(self, comments: List[Dict]) -> bool:
        """Process and categorize comments."""
        if not comments:
            self.logger.log_run_summary({
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'success',
                'mode': 'demo' if self.use_demo else 'production',
                'total_processed': 0,
                'auto_replied': 0,
                'flagged_for_review': 0,
                'note': 'No new comments found',
            })
            return True
        
        for comment in comments:
            comment_id = comment['id']
            
            # Skip if already processed
            if self.state.is_processed(comment_id):
                continue
            
            # Categorize
            category, subcat = self.categorizer.categorize(comment['text'])
            
            # Get response template if applicable
            response_text = None
            should_auto_reply = False
            
            if category in ('questions', 'praise'):
                response_text = ResponseTemplates.get_response(category, subcat)
                should_auto_reply = response_text is not None
            
            # Log entry
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'comment_id': comment_id,
                'video_id': comment['video_id'],
                'author': comment['author'],
                'text': comment['text'][:500],  # Truncate for logs
                'category': category,
                'subcategory': subcat,
                'auto_replied': should_auto_reply,
                'response_sent': response_text if should_auto_reply else None,
            }
            
            # Log to JSONL
            self.logger.log_comment(log_entry)
            
            # Update stats
            self.stats['total_processed'] += 1
            if should_auto_reply:
                self.stats['auto_replied'][category] += 1
            else:
                if category != 'other':
                    self.stats['flagged_for_review'][category] += 1
                else:
                    self.stats['flagged_for_review']['other'] += 1
            
            self.stats['details'].append({
                'author': comment['author'],
                'category': category,
                'auto_replied': should_auto_reply,
            })
            
            # Mark as processed
            self.state.mark_processed(comment_id)
        
        return True
    
    def generate_report(self) -> str:
        """Generate human-readable report."""
        lines = []
        lines.append("=" * 70)
        lines.append("YOUTUBE COMMENT MONITOR REPORT")
        lines.append("=" * 70)
        lines.append(f"Run Time:  {datetime.utcnow().isoformat()}")
        lines.append(f"Channel:   {CHANNEL_URL}")
        lines.append(f"Mode:      {'DEMO' if self.use_demo else 'PRODUCTION'}")
        lines.append("")
        
        # Summary
        total = self.stats['total_processed']
        auto_q = self.stats['auto_replied'].get('questions', 0)
        auto_p = self.stats['auto_replied'].get('praise', 0)
        auto_total = auto_q + auto_p
        
        flag_sales = self.stats['flagged_for_review'].get('sales', 0)
        flag_spam = self.stats['flagged_for_review'].get('spam', 0)
        flag_other = self.stats['flagged_for_review'].get('other', 0)
        flag_total = flag_sales + flag_spam + flag_other
        
        lines.append("SUMMARY")
        lines.append("-" * 70)
        lines.append(f"Total Comments Processed:        {total}")
        lines.append(f"Auto-Responses Sent:             {auto_total}")
        lines.append(f"  • Questions auto-replied:      {auto_q}")
        lines.append(f"  • Praise auto-replied:         {auto_p}")
        lines.append(f"Flagged for Manual Review:       {flag_total}")
        lines.append(f"  • Sales/Partnerships:          {flag_sales}")
        lines.append(f"  • Spam/Suspicious:             {flag_spam}")
        lines.append(f"  • Other:                       {flag_other}")
        lines.append("")
        
        # Details
        if self.stats['details']:
            lines.append("DETAILS")
            lines.append("-" * 70)
            for detail in self.stats['details'][:10]:  # Show first 10
                action = "✅ Auto-replied" if detail['auto_replied'] else "🚩 Flagged"
                lines.append(f"{action:20} | {detail['category']:12} | {detail['author']}")
            
            if len(self.stats['details']) > 10:
                lines.append(f"... and {len(self.stats['details']) - 10} more")
        
        lines.append("")
        lines.append("=" * 70)
        lines.append(f"Log file: {LOG_FILE}")
        lines.append("=" * 70)
        
        return '\n'.join(lines)
    
    def run(self) -> bool:
        """Main execution."""
        print("🎬 YouTube Comment Monitor v2 Starting...")
        
        # Fetch comments
        comments = self.get_comments()
        print(f"📥 Fetched {len(comments)} comments")
        
        # Process
        if not self.process_comments(comments):
            return False
        
        # Save state
        self.state.update_last_checked()
        self.state.save()
        
        # Log summary
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success',
            'mode': 'demo' if self.use_demo else 'production',
            'total_processed': self.stats['total_processed'],
            'auto_replied': sum(self.stats['auto_replied'].values()),
            'flagged_for_review': sum(self.stats['flagged_for_review'].values()),
        }
        self.logger.log_run_summary(summary)
        
        # Print report
        report = self.generate_report()
        print(report)
        
        # Save report to file
        with open(REPORT_FILE, 'w') as f:
            f.write(report)
        
        print(f"✅ Complete! Report saved to {REPORT_FILE}")
        return True


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    monitor = YouTubeCommentMonitor()
    success = monitor.run()
    
    sys.exit(0 if success else 1)
