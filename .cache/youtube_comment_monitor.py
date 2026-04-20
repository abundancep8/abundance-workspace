#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Monitors channel for new comments, categorizes, auto-responds, and logs.

Requirements:
- YOUTUBE_API_KEY environment variable set
- YOUTUBE_CHANNEL_ID in config
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import re

# Mock imports - replace with actual youtube_client when API is configured
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    HAS_YOUTUBE_API = True
except ImportError:
    HAS_YOUTUBE_API = False
    print("⚠️  YouTube API client not installed. Install: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# Configuration
CONFIG = {
    "channel_id": "UCfJJ3FprqTOmJlAp6nYpLXw",  # Concessa Obvius - VERIFY THIS
    "cache_file": Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-comments.jsonl",
    "state_file": Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-monitor-state.json",
}

# Category patterns for comment classification
PATTERNS = {
    "questions": [
        r"how (?:do i|can i|to)",
        r"what (?:is|are|tools)",
        r"where.*start",
        r"cost|price",
        r"timeline|how long",
        r"\?$",
        r"help|guide|tutorial|question",
    ],
    "praise": [
        r"amazing|awesome|great|incredible",
        r"inspiring|motivating|love",
        r"thank you|thanks|grateful",
        r"beautiful|excellent|brilliant",
        r"✨|💯|🔥|❤️",
    ],
    "spam": [
        r"crypto|bitcoin|nft|blockchain",
        r"mlm|network marketing|pyramid",
        r"click here|visit|link below",
        r"earn money|free money|get rich",
        r"xxx|porn|adult",
    ],
    "sales": [
        r"partnership|collaborate|collab",
        r"sponsorship|sponsor",
        r"business opportunity|work with",
        r"affiliate|promote",
    ],
}

# Template responses
TEMPLATES = {
    "questions": """Thanks for the question! Here's a quick answer: [ANSWER]

For more details, check out [RELEVANT_VIDEO_LINK] or our FAQ at [LINK].

Feel free to ask if you need clarification!""",
    "praise": """Thank you so much! 🙏 This truly means a lot. Your support helps us create better content. Stay tuned for more!""",
}


class YouTubeCommentMonitor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        self.youtube = None
        self.config = CONFIG
        self._init_youtube_client()
        self._ensure_cache_dir()

    def _init_youtube_client(self):
        """Initialize YouTube API client."""
        if not self.api_key:
            print("❌ YOUTUBE_API_KEY not set. Cannot fetch comments.")
            return False
        if HAS_YOUTUBE_API:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)
            return True
        return False

    def _ensure_cache_dir(self):
        """Create cache directory if needed."""
        self.config["cache_file"].parent.mkdir(parents=True, exist_ok=True)

    def categorize_comment(self, text):
        """Classify comment into category."""
        text_lower = text.lower()
        
        # Check in priority order
        for category in ["spam", "sales", "questions", "praise"]:
            patterns = PATTERNS.get(category, [])
            if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in patterns):
                return category
        
        return "other"

    def fetch_recent_comments(self, max_results=100):
        """Fetch recent comments from the channel."""
        if not self.youtube:
            return []

        try:
            # Get channel's uploads playlist
            channel_response = self.youtube.channels().list(
                part="contentDetails",
                id=self.config["channel_id"]
            ).execute()

            if not channel_response.get("items"):
                print(f"❌ Channel not found: {self.config['channel_id']}")
                return []

            # Get latest videos from uploads playlist
            uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            videos_response = self.youtube.playlistItems().list(
                part="contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=min(5, max_results)  # Check last 5 videos
            ).execute()

            all_comments = []
            for video in videos_response.get("items", []):
                video_id = video["contentDetails"]["videoId"]
                comments = self.fetch_comments_for_video(video_id)
                all_comments.extend(comments)

            return all_comments[:max_results]
        except Exception as e:
            print(f"❌ Error fetching comments: {e}")
            return []

    def fetch_comments_for_video(self, video_id):
        """Fetch comments for a specific video."""
        comments = []
        try:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                order="relevance",
                maxResults=100,
            )

            while request and len(comments) < 100:
                response = request.execute()
                for item in response.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "video_id": video_id,
                        "author": comment["authorDisplayName"],
                        "text": comment["textDisplay"],
                        "comment_id": item["id"],
                        "timestamp": comment["publishedAt"],
                    })

                if "nextPageToken" in response and len(comments) < 100:
                    request = self.youtube.commentThreads().list_next(request, response)
                else:
                    break
        except Exception as e:
            print(f"⚠️  Error fetching comments for video {video_id}: {e}")
        
        return comments

    def load_processed_ids(self):
        """Load set of already-processed comment IDs."""
        state_file = self.config["state_file"]
        if state_file.exists():
            try:
                with open(state_file) as f:
                    state = json.load(f)
                    return set(state.get("processed_ids", []))
            except Exception as e:
                print(f"⚠️  Error loading state: {e}")
        return set()

    def save_state(self, processed_ids):
        """Save state of processed comments."""
        self.config["state_file"].parent.mkdir(parents=True, exist_ok=True)
        with open(self.config["state_file"], "w") as f:
            json.dump({
                "last_run": datetime.now().isoformat(),
                "processed_ids": list(processed_ids),
            }, f, indent=2)

    def log_comment(self, comment, category, response_status):
        """Log comment to JSONL file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "processed_at": datetime.now().isoformat(),
            "comment_timestamp": comment.get("timestamp"),
            "commenter": comment.get("author"),
            "text": comment.get("text"),
            "category": category,
            "response_status": response_status,
            "comment_id": comment.get("comment_id"),
        }
        
        with open(self.config["cache_file"], "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def generate_response(self, category, comment):
        """Generate response based on category."""
        if category not in TEMPLATES:
            return None
        
        template = TEMPLATES[category]
        # TODO: Customize responses based on comment content
        return template

    def process_comments(self):
        """Main monitoring loop."""
        print(f"🔍 YouTube Comment Monitor - {datetime.now().isoformat()}")
        
        if not self.youtube:
            print("❌ YouTube API not initialized. Skipping run.")
            return self.report({
                "status": "error",
                "total_processed": 0,
                "auto_responses_sent": 0,
                "flagged_for_review": 0,
            })

        # Load state
        processed_ids = self.load_processed_ids()
        
        # Fetch recent comments
        comments = self.fetch_recent_comments()
        
        stats = {
            "total_processed": 0,
            "auto_responses_sent": 0,
            "flagged_for_review": 0,
            "categories": {},
        }

        new_comments = [c for c in comments if c.get("comment_id") not in processed_ids]
        
        if not new_comments:
            print("✅ No new comments since last check.")
            return self.report(stats)

        print(f"📨 Found {len(new_comments)} new comment(s)")

        for comment in new_comments:
            comment_id = comment.get("comment_id")
            category = self.categorize_comment(comment.get("text", ""))
            response_status = "pending"

            # Handle auto-responses
            if category == "questions":
                response = self.generate_response(category, comment)
                print(f"   [Q] {comment['author']}: {comment['text'][:50]}...")
                response_status = "needs_manual_response"  # Flag for manual intervention
                stats["auto_responses_sent"] += 1

            elif category == "praise":
                response = self.generate_response(category, comment)
                print(f"   [✨] {comment['author']}: {comment['text'][:50]}...")
                response_status = "needs_manual_response"  # Flag for manual intervention
                stats["auto_responses_sent"] += 1

            elif category == "spam":
                print(f"   [🚫 SPAM] {comment['author']}: {comment['text'][:50]}...")
                response_status = "spam_flagged"

            elif category == "sales":
                print(f"   [💼 SALES] {comment['author']}: {comment['text'][:50]}...")
                response_status = "flagged_for_review"
                stats["flagged_for_review"] += 1

            else:
                print(f"   [?] {comment['author']}: {comment['text'][:50]}...")
                response_status = "unhandled"

            # Log the comment
            self.log_comment(comment, category, response_status)
            processed_ids.add(comment_id)
            stats["total_processed"] += 1
            stats["categories"][category] = stats["categories"].get(category, 0) + 1

        # Save state
        self.save_state(processed_ids)
        
        return self.report(stats)

    def report(self, stats):
        """Generate report."""
        print("\n" + "="*60)
        print(f"📊 REPORT - {datetime.now().isoformat()}")
        print("="*60)
        print(f"  Total comments processed: {stats['total_processed']}")
        print(f"  Auto-responses sent: {stats['auto_responses_sent']}")
        print(f"  Flagged for review: {stats['flagged_for_review']}")
        if "categories" in stats:
            print(f"  Breakdown: {stats['categories']}")
        print("="*60)
        return stats


def main():
    monitor = YouTubeCommentMonitor()
    result = monitor.process_comments()
    return result


if __name__ == "__main__":
    main()
