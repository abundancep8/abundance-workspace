#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Monitors new comments, categorizes them, auto-responds, and logs all activity.
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Dict, List, Tuple
import subprocess

# Configuration
CHANNEL_USERNAME = "ConcessaObvious"  # Update if different
CHANNEL_ID = None  # Will be looked up or set via env
LOG_FILE = Path(".cache/youtube-comments.jsonl")
STATS_FILE = Path(".cache/youtube-monitor-stats.json")
LAST_CHECK_FILE = Path(".cache/youtube-last-check.json")

# Ensure cache directory exists
LOG_FILE.parent.mkdir(exist_ok=True)

# Category definitions
CATEGORIES = {
    "question": {
        "patterns": [
            r"how\s+(do|can|to)\s+", r"what\s+(is|are|do|should)", r"where\s+(is|can|to)",
            r"when\s+(should|can|do)", r"why\s+(not|don't|can't)", r"\?",
            r"tools?", r"cost", r"price", r"timeline", r"start"
        ],
        "response": "Thank you for your question! We appreciate your interest. Here are some resources that might help: [Insert relevant link]. Feel free to reach out with any other questions!"
    },
    "praise": {
        "patterns": [
            r"amazing", r"inspiring", r"incredible", r"awesome", r"love\s+this",
            r"thank\s+you", r"grateful", r"best", r"excellent", r"wonderful",
            r"great\s+work", r"impressed", r"❤️", r"👏", r"🙌"
        ],
        "response": "Thank you so much for the kind words! We're thrilled you found this valuable. Your support means everything to us! 💜"
    },
    "spam": {
        "patterns": [
            r"crypto", r"bitcoin", r"nft", r"mlm", r"multi.level", r"forex",
            r"get rich", r"earn.*fast", r"click.*link", r"dm.*dm", r"dm me",
            r"buy now", r"limited offer", r"subscribe.*channel"
        ],
        "response": None  # Don't respond to spam
    },
    "sales": {
        "patterns": [
            r"partnership", r"collaboration", r"sponsor", r"advertis",
            r"promote", r"affiliate", r"business\s+opportunity", r"would\s+love\s+to\s+work",
            r"interested\s+in\s+partnering", r"brand\s+deal"
        ],
        "response": None  # Flag for review instead
    }
}

class YouTubeCommentMonitor:
    def __init__(self):
        self.api_key = os.environ.get("YOUTUBE_API_KEY")
        self.channel_id = CHANNEL_ID or os.environ.get("YOUTUBE_CHANNEL_ID")
        
        if not self.api_key:
            print("ERROR: YOUTUBE_API_KEY environment variable not set")
            print("Setup: export YOUTUBE_API_KEY='your-api-key'")
            print("Get your key: https://console.cloud.google.com/apis/credentials")
            sys.exit(1)
        
        if not self.channel_id:
            print(f"Note: Looking up channel '{CHANNEL_USERNAME}'...")
            self.channel_id = self.lookup_channel(CHANNEL_USERNAME)
            if not self.channel_id:
                print(f"ERROR: Could not find channel '{CHANNEL_USERNAME}'")
                sys.exit(1)
        
        self.comments_processed = 0
        self.auto_responses_sent = 0
        self.flagged_for_review = 0
    
    def lookup_channel(self, username: str) -> str:
        """Look up channel ID by username"""
        import urllib.request
        import json
        
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={username}&type=channel&key={self.api_key}&maxResults=1"
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                if data.get("items"):
                    return data["items"][0]["snippet"]["channelId"]
        except Exception as e:
            print(f"Warning: Could not look up channel: {e}")
        return None
    
    def get_channel_videos(self) -> List[str]:
        """Fetch recent videos from channel"""
        import urllib.request
        import json
        
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={self.channel_id}&type=video&order=date&maxResults=10&key={self.api_key}"
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                return [item["id"]["videoId"] for item in data.get("items", [])]
        except Exception as e:
            print(f"Error fetching videos: {e}")
            return []
    
    def get_new_comments(self) -> List[Dict]:
        """Fetch comments posted since last check"""
        import urllib.request
        import json
        from dateutil import parser as date_parser
        
        # Load last check time
        last_check = self.load_last_check()
        
        new_comments = []
        video_ids = self.get_channel_videos()
        
        for video_id in video_ids:
            url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&textFormat=plainText&maxResults=100&order=relevance&key={self.api_key}"
            try:
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read())
                    
                    for thread in data.get("items", []):
                        comment = thread["snippet"]["topLevelComment"]["snippet"]
                        published = date_parser.isoparse(comment["publishedAt"])
                        
                        # Only include comments since last check
                        if published > last_check:
                            new_comments.append({
                                "video_id": video_id,
                                "author": comment["authorDisplayName"],
                                "text": comment["textDisplay"],
                                "published_at": comment["publishedAt"],
                                "comment_id": thread["id"],
                                "thread_id": thread["snippet"]["topLevelComment"]["id"]
                            })
            except Exception as e:
                print(f"Warning: Could not fetch comments for video {video_id}: {e}")
        
        return new_comments
    
    def categorize_comment(self, text: str) -> Tuple[str, str]:
        """Categorize comment by type, return (category, response)"""
        text_lower = text.lower()
        
        # Check categories in order
        for category, config in CATEGORIES.items():
            patterns = config["patterns"]
            if any(re.search(pattern, text_lower) for pattern in patterns):
                return category, config.get("response", "")
        
        return "other", ""
    
    def load_existing_comments(self) -> set:
        """Load comment IDs already logged"""
        existing = set()
        if LOG_FILE.exists():
            with open(LOG_FILE) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            existing.add(data.get("comment_id"))
                        except:
                            pass
        return existing
    
    def load_last_check(self) -> datetime:
        """Load timestamp of last check"""
        if LAST_CHECK_FILE.exists():
            with open(LAST_CHECK_FILE) as f:
                data = json.load(f)
                # Look back 35 minutes to catch any missed comments (30 min monitor + buffer)
                return datetime.fromisoformat(data["last_check"]) - timedelta(minutes=5)
        # Default to 35 minutes ago
        return datetime.utcnow() - timedelta(minutes=35)
    
    def save_last_check(self):
        """Save current check time"""
        with open(LAST_CHECK_FILE, "w") as f:
            json.dump({"last_check": datetime.utcnow().isoformat()}, f)
    
    def log_comment(self, comment: Dict, category: str, response_status: str):
        """Log comment to JSONL file"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "comment_id": comment.get("comment_id"),
            "video_id": comment.get("video_id"),
            "commenter": comment.get("author"),
            "text": comment.get("text"),
            "published_at": comment.get("published_at"),
            "category": category,
            "response_status": response_status
        }
        
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def send_reply(self, comment_id: str, thread_id: str, response: str) -> bool:
        """Send reply to comment (requires OAuth - currently not implemented)"""
        # Note: Replying to comments requires OAuth 2.0, not just API key
        # This would need to be implemented with proper authentication
        # For now, return False and log for manual response
        return False
    
    def save_stats(self, stats: Dict):
        """Save monitoring stats"""
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f, indent=2)
    
    def run(self):
        """Main monitoring loop"""
        print(f"[{datetime.now().isoformat()}] Starting YouTube comment monitor...")
        
        # Load already-processed comments
        existing = self.load_existing_comments()
        
        # Fetch new comments
        new_comments = self.get_new_comments()
        print(f"Found {len(new_comments)} new comments")
        
        if not new_comments:
            print("No new comments to process")
            self.save_last_check()
            return
        
        # Process each comment
        for comment in new_comments:
            if comment["comment_id"] in existing:
                continue
            
            category, response_template = self.categorize_comment(comment["text"])
            response_status = "skipped"
            
            if category == "question":
                # Try to send response
                if self.send_reply(comment["comment_id"], comment["thread_id"], response_template):
                    response_status = "responded"
                    self.auto_responses_sent += 1
                else:
                    response_status = "pending_oauth"
                self.comments_processed += 1
            
            elif category == "praise":
                # Send appreciation response
                if self.send_reply(comment["comment_id"], comment["thread_id"], response_template):
                    response_status = "responded"
                    self.auto_responses_sent += 1
                else:
                    response_status = "pending_oauth"
                self.comments_processed += 1
            
            elif category == "spam":
                response_status = "spam_ignored"
                self.comments_processed += 1
            
            elif category == "sales":
                response_status = "flagged_review"
                self.flagged_for_review += 1
                self.comments_processed += 1
            
            else:
                response_status = "unclassified"
                self.comments_processed += 1
            
            # Log the comment
            self.log_comment(comment, category, response_status)
            print(f"  [{category}] {comment['author']}: {comment['text'][:50]}...")
        
        # Save stats
        stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_comments_processed": self.comments_processed,
            "auto_responses_sent": self.auto_responses_sent,
            "flagged_for_review": self.flagged_for_review,
            "channel_id": self.channel_id,
            "log_file": str(LOG_FILE)
        }
        self.save_stats(stats)
        
        # Print report
        self.print_report(stats)
        
        # Save last check time
        self.save_last_check()
    
    def print_report(self, stats: Dict):
        """Print monitoring report"""
        print("\n" + "="*60)
        print("YOUTUBE COMMENT MONITOR REPORT")
        print("="*60)
        print(f"Timestamp:              {stats['timestamp']}")
        print(f"Channel:                {CHANNEL_USERNAME} ({stats['channel_id']})")
        print(f"Total Comments:         {stats['total_comments_processed']}")
        print(f"Auto-Responses Sent:    {stats['auto_responses_sent']}")
        print(f"Flagged for Review:     {stats['flagged_for_review']}")
        print(f"Log File:               {stats['log_file']}")
        print("="*60)

def main():
    try:
        monitor = YouTubeCommentMonitor()
        monitor.run()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
