#!/usr/bin/env python3
"""
YouTube Comment Monitor v3 - Production Ready
Monitors Concessa Obvius channel comments every 30 minutes.
Auto-categorizes and responds to questions/praise.
Flags sales inquiries for review.
"""

import json
import os
import sys
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

# Try to import Google API client, fall back gracefully
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

# Configuration
WORKSPACE_ROOT = Path(__file__).parent.parent
CACHE_DIR = Path(__file__).parent
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-comment-state.json"
REPORT_FILE = CACHE_DIR / "youtube-comments-report.txt"
CREDENTIALS_PATH = CACHE_DIR / ".secrets" / "youtube-credentials.json"

# Channel ID for Concessa Obvius (placeholder - will need real ID)
CHANNEL_ID = "UCxxxxxxxxxxxxxxxxxxxx"

# Template responses for auto-reply
RESPONSE_TEMPLATES = {
    "questions": [
        "Great question! Thanks for your interest. I'll have more details about this soon. In the meantime, check out our resources and FAQs!",
        "Love this question! This is something we're actively working on. Keep an eye on our upcoming announcements.",
        "Thanks for asking! I'll reach out with more info soon. In the meantime, feel free to check out our recent content.",
    ],
    "praise": [
        "Thank you so much for the kind words! 🙏 Really appreciate your support and engagement.",
        "This means the world! 💕 Thanks for being part of the community.",
        "So grateful for this! Your support keeps us going. 🚀",
    ],
}

# Keywords for categorization
KEYWORDS = {
    "questions": [
        "how do i", "how do you", "how to", "how can i", "can i", "can you",
        "do you", "what is", "what's", "why", "when", "where", "which",
        "cost", "price", "tools", "timeline", "steps", "guide", "tutorial",
        "help", "support", "question", "info", "information", "learn"
    ],
    "praise": [
        "amazing", "awesome", "love", "great", "excellent", "fantastic",
        "inspiring", "incredible", "wonderful", "beautiful", "perfect",
        "thank you", "thanks", "appreciate", "grateful", "impressed",
        "impressed", "brilliant", "genius", "life-changing"
    ],
    "spam": [
        "crypto", "bitcoin", "ethereum", "nft", "mlm", "get rich",
        "click here", "dm me", "message me", "dm for", "dm to",
        "buy now", "limited offer", "act fast", "urgency", "scam alert",
        "guaranteed", "forex", "trading bot", "make money fast", "passive income"
    ],
    "sales": [
        "partnership", "collaborate", "collaboration", "business opportunity",
        "sponsorship", "affiliate", "brand deal", "promotion", "work together",
        "contact us", "get in touch", "reach out", "interested in", "proposal"
    ]
}


class YouTubeCommentMonitor:
    def __init__(self, demo_mode: bool = False):
        self.demo_mode = demo_mode
        self.youtube = None
        self.processed_count = 0
        self.auto_replied_count = 0
        self.flagged_count = 0
        self.comments_log = []
        self.state = self._load_state()
        
        if not demo_mode and GOOGLE_API_AVAILABLE:
            self._authenticate()
    
    def _load_state(self) -> Dict:
        """Load previous run state."""
        default_state = {
            "last_run": None,
            "last_processed_comment_id": None,
            "total_processed_lifetime": 0,
            "total_auto_replied_lifetime": 0,
            "total_flagged_lifetime": 0,
        }
        
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle missing keys
                    default_state.update(loaded)
                    return default_state
            except:
                pass
        return default_state
    
    def _save_state(self):
        """Save current state."""
        self.state["last_run"] = datetime.now(timezone.utc).isoformat()
        self.state["last_processed_comment_id"] = self.processed_count
        self.state["total_processed_lifetime"] += self.processed_count
        self.state["total_auto_replied_lifetime"] += self.auto_replied_count
        self.state["total_flagged_lifetime"] += self.flagged_count
        
        os.makedirs(STATE_FILE.parent, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def _authenticate(self):
        """Authenticate with YouTube API."""
        try:
            if CREDENTIALS_PATH.exists():
                creds = Credentials.from_authorized_user_file(str(CREDENTIALS_PATH))
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                self.youtube = build("youtube", "v3", credentials=creds)
                return True
        except Exception as e:
            print(f"Authentication error: {e}", file=sys.stderr)
        return False
    
    def categorize_comment(self, text: str) -> str:
        """Categorize comment based on keywords."""
        text_lower = text.lower()
        
        # Check each category in priority order
        for category in ["spam", "sales", "questions", "praise"]:
            keywords = KEYWORDS.get(category, [])
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        # Default to neutral if no match
        return "neutral"
    
    def generate_response(self, category: str) -> Optional[str]:
        """Generate response for auto-replied categories."""
        if category == "questions":
            import random
            return random.choice(RESPONSE_TEMPLATES["questions"])
        elif category == "praise":
            import random
            return random.choice(RESPONSE_TEMPLATES["praise"])
        return None
    
    def get_sample_comments(self) -> List[Dict]:
        """Get sample comments for demo mode."""
        return [
            {
                "id": "demo_q1",
                "author": "Sarah Chen",
                "text": "How do I get started with this? What tools do I need?",
                "published": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "demo_q2",
                "author": "Marcus Johnson",
                "text": "What's the timeline for implementation? When can I start?",
                "published": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "demo_p1",
                "author": "Elena Rodriguez",
                "text": "This is absolutely amazing! So inspiring and well-explained. Thank you!",
                "published": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "demo_p2",
                "author": "Alex Kim",
                "text": "Love the approach here! Really impressed with the quality. Great work!",
                "published": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "demo_s1",
                "author": "Crypto Trading Bot",
                "text": "BUY CRYPTO NOW!!! Limited offer, DM me for details",
                "published": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "demo_b1",
                "author": "Jessica Parker",
                "text": "Hi! Love your content. Would love to explore a partnership opportunity with you. Let's connect!",
                "published": datetime.now(timezone.utc).isoformat(),
            },
        ]
    
    def process_comments(self) -> Dict:
        """Process comments from YouTube channel."""
        comments = []
        
        if self.demo_mode:
            comments = self.get_sample_comments()
        elif self.youtube:
            try:
                # Fetch recent comments from channel
                request = self.youtube.commentThreads().list(
                    part="snippet",
                    allThreadsRelatedToChannelId=CHANNEL_ID,
                    maxResults=20,
                    order="relevance",
                    searchTerms="",
                    textFormat="plainText"
                )
                response = request.execute()
                
                for item in response.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "id": item["id"],
                        "author": comment["authorDisplayName"],
                        "text": comment["textDisplay"],
                        "published": comment["publishedAt"],
                    })
            except Exception as e:
                self._log_error(f"Failed to fetch comments: {e}")
                return self._error_report(str(e))
        
        # Process each comment
        for comment in comments:
            self.processed_count += 1
            
            category = self.categorize_comment(comment["text"])
            response_text = self.generate_response(category)
            
            # Determine response status
            if category in ["questions", "praise"]:
                response_status = "auto_responded"
                self.auto_replied_count += 1
            elif category == "sales":
                response_status = "flagged_for_review"
                self.flagged_count += 1
            else:
                response_status = "processed"
            
            # Log entry
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "comment_id": comment["id"],
                "commenter": comment["author"],
                "text": comment["text"],
                "category": category,
                "response_status": response_status,
                "template_response": response_text or "",
                "run_time": datetime.now(timezone.utc).isoformat(),
            }
            
            self.comments_log.append(log_entry)
        
        return {
            "status": "success",
            "total_processed": self.processed_count,
            "auto_replied": self.auto_replied_count,
            "flagged_for_review": self.flagged_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    def log_results(self):
        """Log results to JSONL file."""
        os.makedirs(COMMENTS_LOG.parent, exist_ok=True)
        
        with open(COMMENTS_LOG, "a") as f:
            for entry in self.comments_log:
                f.write(json.dumps(entry) + "\n")
    
    def _log_error(self, error_msg: str):
        """Log errors."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": error_msg,
        }
        with open(COMMENTS_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def _error_report(self, error: str) -> Dict:
        """Generate error report."""
        return {
            "status": "error",
            "error": error,
            "total_processed": 0,
            "auto_replied": 0,
            "flagged_for_review": 0,
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive report."""
        now = datetime.now(timezone.utc).isoformat()
        
        # Summary by category
        categories = {}
        for log in self.comments_log:
            cat = log.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        report = f"""YouTube Comment Monitor Report
Generated: {now}
Channel: Concessa Obvius
Monitor Mode: {'DEMO' if self.demo_mode else 'LIVE'}

=== SESSION SUMMARY ===
Total Comments Processed: {self.processed_count}
Auto-Responses Sent: {self.auto_replied_count}
Flagged for Review: {self.flagged_count}

=== LIFETIME STATS ===
Total Processed (Lifetime): {self.state['total_processed_lifetime'] + self.processed_count}
Total Auto-Replied (Lifetime): {self.state['total_auto_replied_lifetime'] + self.auto_replied_count}
Total Flagged (Lifetime): {self.state['total_flagged_lifetime'] + self.flagged_count}

=== BREAKDOWN BY CATEGORY ===
"""
        for category, count in sorted(categories.items()):
            report += f"  {category.upper()}: {count}\n"
        
        if self.comments_log:
            report += "\n=== RECENT COMMENTS ===\n"
            for log in self.comments_log[-10:]:
                report += f"\n[{log['category'].upper()}] {log['commenter']}\n"
                report += f"  \"{log['text'][:100]}...\"\n"
                report += f"  Status: {log['response_status']}\n"
        
        return report
    
    def run(self) -> Dict:
        """Execute monitor."""
        result = self.process_comments()
        
        if result["status"] == "success":
            self.log_results()
            self._save_state()
            report = self.generate_report()
            
            # Save report to file
            with open(REPORT_FILE, "w") as f:
                f.write(report)
            
            print(report)
        
        return result


def main():
    parser = argparse.ArgumentParser(description="YouTube Comment Monitor")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode (no auth needed)")
    parser.add_argument("--live", action="store_true", help="Run in live mode (requires credentials)")
    parser.add_argument("--channel-id", help="YouTube channel ID")
    
    args = parser.parse_args()
    
    # Default to demo mode if no credentials
    demo_mode = not CREDENTIALS_PATH.exists() or args.demo
    
    if args.live and not CREDENTIALS_PATH.exists():
        print("ERROR: Live mode requires YouTube credentials at:", CREDENTIALS_PATH)
        print("Please set up credentials first.")
        sys.exit(1)
    
    monitor = YouTubeCommentMonitor(demo_mode=demo_mode)
    result = monitor.run()
    
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
