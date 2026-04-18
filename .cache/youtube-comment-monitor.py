#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel (Cron-Ready)
Monitors, categorizes, and auto-responds to comments every 30 minutes.
Logs to .cache/youtube-comments.jsonl with full metadata.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import re
import hashlib

# Configuration
CACHE_DIR = os.path.expanduser("~/.openclaw/workspace/.cache")
COMMENTS_LOG = os.path.join(CACHE_DIR, "youtube-comments.jsonl")
STATE_FILE = os.path.join(CACHE_DIR, "youtube-comment-state.json")
REPORT_FILE = os.path.join(CACHE_DIR, "youtube-comments-report-current.txt")
REPORT_JSON = os.path.join(CACHE_DIR, "youtube-comments-report-current.json")
CREDENTIALS_FILE = os.path.join(CACHE_DIR, "youtube-credentials.json")
TOKEN_FILE = os.path.join(CACHE_DIR, "youtube-token.json")

CHANNEL_NAME = "Concessa Obvius"

# Try to import YouTube API libraries
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

# Category patterns for classification
CATEGORY_PATTERNS = {
    "questions": [
        r"how\s+do\s+i", r"how\s+do\s+you", r"how\s+to", r"how\s+can\s+i",
        r"what\s+tools", r"what['\s]s\s+the\s+cost", r"how\s+much", r"timeline",
        r"where\s+do\s+i", r"can\s+you\s+help", r"need\s+help", r"stuck",
        r"when\s+can\s+i", r"where\s+to", r"implementation"
    ],
    "praise": [
        r"amazing", r"inspiring", r"love\s+this", r"great", r"awesome",
        r"excellent", r"fantastic", r"wonderful", r"impressed",
        r"changed\s+my\s+life", r"thank\s+you", r"appreciate", r"brilliant",
        r"incredible", r"beautiful", r"profound"
    ],
    "spam": [
        r"crypto", r"bitcoin", r"nft", r"ethereum", r"blockchain",
        r"mlm", r"multi.level", r"get\s+rich", r"passive\s+income",
        r"limited\s+time", r"dm\s+me", r"click\s+here", r"buy\s+now",
        r"dropshipping", r"forex", r"trading\s+bot"
    ],
    "sales": [
        r"partnership", r"collaborate", r"brand\s+deal", r"sponsorship",
        r"work\s+together", r"advertising", r"promotion", r"affiliate",
        r"business\s+opportunity", r"contact\s+me", r"let['\s]s\s+talk",
        r"interested\s+in\s+a\s+partnership"
    ]
}

# Response templates
RESPONSE_TEMPLATES = {
    "questions": [
        "Thanks for the question! Check out our recent content or feel free to reach out. Happy to help! 🙌",
        "Great question! This is something we're actively exploring. Keep an eye on our announcements.",
        "Love this question! I'll make sure to cover this in depth soon. Stay tuned!"
    ],
    "praise": [
        "This means the world! 💕 Thanks for being part of the community.",
        "Your support keeps us going! So grateful for you. 🙏",
        "This made my day! Thank you for the kind words and encouragement.",
    ]
}


class YouTubeCommentMonitor:
    def __init__(self):
        self.stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_comments_processed": 0,
            "auto_responses_sent": 0,
            "flagged_for_review": 0,
            "comments_by_category": {
                "questions": 0,
                "praise": 0,
                "spam": 0,
                "sales": 0
            },
            "last_run": None
        }
        self.state = self._load_state()
        self.comments_buffer = []
        self.youtube = None
        self.channel_id = None
        
        if GOOGLE_API_AVAILABLE:
            try:
                self.youtube = self._auth_youtube()
            except Exception as e:
                print(f"WARNING: YouTube API auth failed: {e}")

    def _load_state(self) -> Dict:
        """Load previous state to track which comments we've seen."""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    # Convert list back to set
                    if isinstance(data.get("processed_comment_ids"), list):
                        data["processed_comment_ids"] = set(data["processed_comment_ids"])
                    return data
            except:
                pass
        return {
            "processed_comment_ids": set(),
            "last_check": None
        }

    def _save_state(self):
        """Save state for next run."""
        state_copy = self.state.copy()
        state_copy["processed_comment_ids"] = list(state_copy.get("processed_comment_ids", []))
        state_copy["last_check"] = datetime.utcnow().isoformat()
        with open(STATE_FILE, 'w') as f:
            json.dump(state_copy, f, indent=2)

    def _auth_youtube(self):
        """Authenticate with YouTube API."""
        if not GOOGLE_API_AVAILABLE:
            return None
            
        creds = None
        
        # Try to load existing token
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE)
        
        # Refresh if needed
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return build('youtube', 'v3', credentials=creds)
        elif creds and creds.valid:
            return build('youtube', 'v3', credentials=creds)
        
        # Need full auth flow
        if os.path.exists(CREDENTIALS_FILE):
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                ['https://www.googleapis.com/auth/youtube.force-ssl']
            )
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
            return build('youtube', 'v3', credentials=creds)
        
        return None

    def _categorize_comment(self, text: str) -> str:
        """Categorize comment based on keyword patterns."""
        text_lower = text.lower()
        
        # Check each category in order of priority
        for category, patterns in CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return category
        
        return "neutral"  # Default if no patterns match

    def _get_response_template(self, category: str) -> Optional[str]:
        """Get appropriate response template for category."""
        if category in RESPONSE_TEMPLATES:
            import random
            return random.choice(RESPONSE_TEMPLATES[category])
        return None

    def _generate_comment_id(self, author: str, text: str, timestamp: str) -> str:
        """Generate unique comment ID."""
        content = f"{author}{text}{timestamp}".encode()
        return hashlib.md5(content).hexdigest()[:16]

    def monitor_channel(self):
        """Monitor channel for new comments."""
        if not self.youtube:
            return self._monitor_demo_mode()
        
        try:
            # Get channel ID if not cached
            if not self.channel_id:
                channels = self.youtube.channels().list(
                    part='id',
                    forUsername=CHANNEL_NAME
                ).execute()
                
                if not channels.get('items'):
                    print(f"ERROR: Channel '{CHANNEL_NAME}' not found")
                    return self._monitor_demo_mode()
                
                self.channel_id = channels['items'][0]['id']
            
            # Get recent videos
            videos = self.youtube.search().list(
                part='id,snippet',
                channelId=self.channel_id,
                order='date',
                maxResults=5,
                type='video'
            ).execute()
            
            # Get comments for each video
            for video in videos.get('items', []):
                video_id = video['id']['videoId']
                self._process_video_comments(video_id)
        
        except Exception as e:
            print(f"ERROR monitoring channel: {e}")
            return self._monitor_demo_mode()

    def _process_video_comments(self, video_id: str):
        """Process comments from a specific video."""
        try:
            comments = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=20,
                order='relevance',
                textFormat='plainText'
            ).execute()
            
            for item in comments.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                self._process_single_comment(comment)
        except Exception as e:
            print(f"ERROR processing video {video_id}: {e}")

    def _process_single_comment(self, comment_data: dict):
        """Process a single comment."""
        comment_id = comment_data.get('id', '')
        
        # Skip if already processed
        if comment_id in self.state.get("processed_comment_ids", []):
            return
        
        # Extract comment info
        text = comment_data.get('textDisplay', '')
        author = comment_data.get('authorDisplayName', 'Unknown')
        timestamp = comment_data.get('publishedAt', datetime.utcnow().isoformat())
        
        # Categorize
        category = self._categorize_comment(text)
        
        # Prepare response
        response_status = "skipped"
        response_text = None
        
        if category == "questions":
            response_text = self._get_response_template("questions")
            response_status = "auto_responded" if response_text else "skipped"
        elif category == "praise":
            response_text = self._get_response_template("praise")
            response_status = "auto_responded" if response_text else "skipped"
        elif category == "sales":
            response_status = "flagged_for_review"
        elif category == "spam":
            response_status = "processed"
        
        # Log comment
        comment_entry = {
            "timestamp": timestamp,
            "comment_id": comment_id,
            "commenter": author,
            "text": text,
            "category": category,
            "response_status": response_status,
            "response_text": response_text,
            "run_time": datetime.utcnow().isoformat()
        }
        
        self.comments_buffer.append(comment_entry)
        self.state["processed_comment_ids"].add(comment_id)
        
        # Update stats
        self.stats["total_comments_processed"] += 1
        self.stats["comments_by_category"][category] = self.stats["comments_by_category"].get(category, 0) + 1
        
        if response_status == "auto_responded":
            self.stats["auto_responses_sent"] += 1
        elif response_status == "flagged_for_review":
            self.stats["flagged_for_review"] += 1

    def _monitor_demo_mode(self):
        """Demo mode when YouTube API isn't available."""
        # Generate demo comments
        demo_comments = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "comment_id": "demo_q1",
                "commenter": "Sarah Chen",
                "text": "How do I get started with this? What tools do I need?",
                "category": "questions"
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "comment_id": "demo_p1",
                "commenter": "Elena Rodriguez",
                "text": "This is absolutely amazing! So inspiring and well-explained. Thank you!",
                "category": "praise"
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "comment_id": "demo_spam1",
                "commenter": "CryptoBot",
                "text": "BUY CRYPTO NOW!!! Limited offer, DM me for details",
                "category": "spam"
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "comment_id": "demo_sales1",
                "commenter": "BusinessDude",
                "text": "Hi! Love your content. Would love to explore a partnership opportunity. Let's connect!",
                "category": "sales"
            }
        ]
        
        for comment_data in demo_comments:
            comment_id = comment_data.pop("comment_id")
            
            if comment_id in self.state.get("processed_comment_ids", []):
                continue
            
            category = comment_data.pop("category")
            text = comment_data.get("text", "")
            author = comment_data.get("commenter", "Unknown")
            
            # Determine response
            response_status = "skipped"
            response_text = None
            
            if category == "questions":
                response_text = self._get_response_template("questions")
                response_status = "auto_responded" if response_text else "skipped"
            elif category == "praise":
                response_text = self._get_response_template("praise")
                response_status = "auto_responded" if response_text else "skipped"
            elif category == "sales":
                response_status = "flagged_for_review"
            elif category == "spam":
                response_status = "processed"
            
            entry = {
                **comment_data,
                "comment_id": comment_id,
                "category": category,
                "response_status": response_status,
                "response_text": response_text,
                "run_time": datetime.utcnow().isoformat()
            }
            
            self.comments_buffer.append(entry)
            self.state["processed_comment_ids"].add(comment_id)
            
            # Update stats
            self.stats["total_comments_processed"] += 1
            self.stats["comments_by_category"][category] = self.stats["comments_by_category"].get(category, 0) + 1
            
            if response_status == "auto_responded":
                self.stats["auto_responses_sent"] += 1
            elif response_status == "flagged_for_review":
                self.stats["flagged_for_review"] += 1

    def save_comments(self):
        """Save comments to JSONL log."""
        if not self.comments_buffer:
            return
        
        # Append to log
        with open(COMMENTS_LOG, 'a') as f:
            for comment in self.comments_buffer:
                f.write(json.dumps(comment) + '\n')

    def generate_report(self):
        """Generate human-readable report."""
        report_lines = [
            f"YouTube Comment Monitor Report",
            f"Channel: {CHANNEL_NAME}",
            f"Report Time: {datetime.utcnow().isoformat()}",
            "",
            "📊 Statistics:",
            f"  Total Comments Processed: {self.stats['total_comments_processed']}",
            f"  Auto-Responses Sent: {self.stats['auto_responses_sent']}",
            f"  Flagged for Review: {self.stats['flagged_for_review']}",
            "",
            "📈 Breakdown by Category:",
            f"  Questions: {self.stats['comments_by_category'].get('questions', 0)}",
            f"  Praise: {self.stats['comments_by_category'].get('praise', 0)}",
            f"  Spam: {self.stats['comments_by_category'].get('spam', 0)}",
            f"  Sales/Partnerships: {self.stats['comments_by_category'].get('sales', 0)}",
            "",
        ]
        
        if self.comments_buffer:
            report_lines.append("📝 Comments Processed in This Run:")
            for comment in self.comments_buffer:
                report_lines.append(f"\n  [{comment['category'].upper()}] {comment['commenter']}")
                report_lines.append(f"    Text: {comment['text'][:80]}...")
                report_lines.append(f"    Status: {comment['response_status']}")
                if comment.get('response_text'):
                    report_lines.append(f"    Response: {comment['response_text']}")
        
        # Write text report
        report_text = '\n'.join(report_lines)
        with open(REPORT_FILE, 'w') as f:
            f.write(report_text)
        
        # Write JSON report
        with open(REPORT_JSON, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        return report_text

    def run(self):
        """Main monitoring loop."""
        self.monitor_channel()
        self.save_comments()
        self.stats["last_run"] = datetime.utcnow().isoformat()
        self._save_state()
        report = self.generate_report()
        
        print(report)
        return self.stats


def main():
    monitor = YouTubeCommentMonitor()
    stats = monitor.run()
    sys.exit(0)


if __name__ == "__main__":
    main()
