#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Monitors for new comments, categorizes them, and auto-responds.
Logs all activity to .cache/youtube-comments.jsonl
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import re

try:
    from google.auth.transport.requests import Request
    from google.oauth2.service_account import Credentials
    from google.auth.oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    import google.auth
except ImportError:
    print("Error: Google API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Configuration
CHANNEL_ID = "UCH_YOUR_CHANNEL_ID"  # Replace with actual Concessa Obvius channel ID
CACHE_DIR = Path(".cache")
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"
CREDENTIALS_FILE = Path.home() / ".openclaw" / "youtube-credentials.json"

# Template responses
TEMPLATES = {
    "question": "Thanks for the question! [Auto-response based on category] For more details, check out our FAQ or docs at [link]. Feel free to reach out!",
    "praise": "Thank you so much for the kind words! 🙏 We're so glad you found this valuable. Keep building!",
}

# Category definitions
PATTERNS = {
    "questions": [
        r"how\s+(?:do|can)\s+i",
        r"how\s+to\s+",
        r"what\s+(?:tools|cost|price|timeline)",
        r"where\s+(?:can|do)\s+i",
        r"\?",  # Any question mark
        r"help",
        r"tutorial",
        r"setup",
    ],
    "praise": [
        r"amazing",
        r"inspiring",
        r"great",
        r"excellent",
        r"love",
        r"awesome",
        r"brilliant",
        r"thank\s+you",
        r"thanks",
    ],
    "spam": [
        r"crypto",
        r"bitcoin",
        r"ethereum",
        r"nft",
        r"mlm",
        r"multi.?level",
        r"pyramid",
        r"forex",
        r"gambling",
        r"casino",
    ],
    "sales": [
        r"partnership",
        r"collaboration",
        r"sponsor",
        r"advertis",
        r"promote",
        r"affiliate",
    ],
}

class YouTubeCommentMonitor:
    def __init__(self):
        self.youtube = None
        self.stats = {
            "total_processed": 0,
            "auto_responses_sent": 0,
            "flagged_for_review": 0,
            "errors": 0,
        }
        self._setup_cache()
        self._authenticate()

    def _setup_cache(self):
        """Create cache directory if needed."""
        CACHE_DIR.mkdir(exist_ok=True)

    def _authenticate(self):
        """Authenticate with YouTube API."""
        try:
            if CREDENTIALS_FILE.exists():
                credentials = Credentials.from_service_account_file(CREDENTIALS_FILE)
                self.youtube = build("youtube", "v3", credentials=credentials)
            else:
                print(f"Error: Credentials file not found at {CREDENTIALS_FILE}")
                print("Set up YouTube API credentials and save to:", CREDENTIALS_FILE)
                sys.exit(1)
        except Exception as e:
            print(f"Authentication error: {e}")
            self.stats["errors"] += 1

    def _categorize_comment(self, text: str) -> str:
        """Categorize a comment based on patterns."""
        text_lower = text.lower()
        
        # Check in order: spam first (highest priority to filter), then categories
        for pattern in PATTERNS.get("spam", []):
            if re.search(pattern, text_lower):
                return "spam"
        
        for pattern in PATTERNS.get("sales", []):
            if re.search(pattern, text_lower):
                return "sales"
        
        for pattern in PATTERNS.get("questions", []):
            if re.search(pattern, text_lower):
                return "questions"
        
        for pattern in PATTERNS.get("praise", []):
            if re.search(pattern, text_lower):
                return "praise"
        
        return "other"

    def _load_state(self) -> dict:
        """Load last check timestamp and processed comment IDs."""
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return json.load(f)
        return {"last_checked": None, "processed_ids": []}

    def _save_state(self, state: dict):
        """Save state for next run."""
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)

    def _log_comment(self, comment_data: dict):
        """Log comment to JSONL file."""
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(comment_data) + "\n")

    def fetch_new_comments(self):
        """Fetch new comments from the channel."""
        if not self.youtube:
            print("YouTube API not authenticated")
            return
        
        state = self._load_state()
        processed_ids = set(state.get("processed_ids", []))
        
        try:
            # Get channel ID from username or use configured ID
            request = self.youtube.commentThreads().list(
                part="snippet,replies",
                allThreadsRelatedToChannelId=CHANNEL_ID,
                textFormat="plainText",
                maxResults=100,
                order="relevance",
            )
            
            while request:
                response = request.execute()
                
                for item in response.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    comment_id = item["id"]
                    
                    # Skip already processed comments
                    if comment_id in processed_ids:
                        continue
                    
                    self._process_comment(comment, comment_id, processed_ids)
                    self.stats["total_processed"] += 1
                
                # Get next page of results
                if "nextPageToken" in response:
                    request = self.youtube.commentThreads().list_next(request, response)
                else:
                    request = None
        
        except Exception as e:
            print(f"Error fetching comments: {e}")
            self.stats["errors"] += 1
        
        # Update state
        state["last_checked"] = datetime.now(datetime.timezone.utc).isoformat()
        state["processed_ids"] = list(processed_ids)
        self._save_state(state)

    def _process_comment(self, comment: dict, comment_id: str, processed_ids: set):
        """Process a single comment."""
        try:
            author = comment["authorDisplayName"]
            text = comment["textDisplay"]
            timestamp = comment["publishedAt"]
            
            category = self._categorize_comment(text)
            response_status = "pending"
            
            # Auto-respond to questions and praise
            if category == "questions":
                response_status = self._send_reply(comment_id, TEMPLATES["question"])
                if response_status == "sent":
                    self.stats["auto_responses_sent"] += 1
            elif category == "praise":
                response_status = self._send_reply(comment_id, TEMPLATES["praise"])
                if response_status == "sent":
                    self.stats["auto_responses_sent"] += 1
            elif category == "sales":
                response_status = "flagged_for_review"
                self.stats["flagged_for_review"] += 1
            elif category == "spam":
                response_status = "spam_filtered"
            
            # Log the comment
            log_entry = {
                "timestamp": timestamp,
                "comment_id": comment_id,
                "commenter": author,
                "text": text,
                "category": category,
                "response_status": response_status,
                "logged_at": datetime.now(datetime.timezone.utc).isoformat(),
            }
            self._log_comment(log_entry)
            
            # Track processed
            processed_ids.add(comment_id)
        
        except Exception as e:
            print(f"Error processing comment: {e}")
            self.stats["errors"] += 1

    def _send_reply(self, parent_id: str, reply_text: str) -> str:
        """Send a reply to a comment."""
        try:
            if not self.youtube:
                return "error"
            
            request = self.youtube.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": parent_id,
                        "textOriginal": reply_text,
                    }
                },
            )
            request.execute()
            return "sent"
        except Exception as e:
            print(f"Error sending reply: {e}")
            return "error"

    def generate_report(self) -> dict:
        """Generate a summary report."""
        return {
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "stats": self.stats,
            "log_file": str(LOG_FILE),
            "log_entries": self._count_log_entries(),
        }

    def _count_log_entries(self) -> dict:
        """Count log entries by category."""
        counts = {
            "total": 0,
            "by_category": {},
            "by_status": {},
        }
        
        if LOG_FILE.exists():
            with open(LOG_FILE) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        counts["total"] += 1
                        
                        cat = entry.get("category", "unknown")
                        counts["by_category"][cat] = counts["by_category"].get(cat, 0) + 1
                        
                        status = entry.get("response_status", "unknown")
                        counts["by_status"][status] = counts["by_status"].get(status, 0) + 1
                    except json.JSONDecodeError:
                        pass
        
        return counts

    def run(self):
        """Main execution."""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] YouTube Comment Monitor started")
        self.fetch_new_comments()
        report = self.generate_report()
        print(json.dumps(report, indent=2))
        return report


if __name__ == "__main__":
    monitor = YouTubeCommentMonitor()
    monitor.run()
