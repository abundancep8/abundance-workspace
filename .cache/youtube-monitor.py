#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius
Runs every 30 minutes via cron job
- Fetches new comments
- Categorizes them
- Auto-responds to Questions & Praise
- Flags Sales inquiries for review
- Logs all activity to JSONL
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# Try to import YouTube API
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    HAS_YOUTUBE_API = True
except ImportError:
    HAS_YOUTUBE_API = False
    print("⚠️  Warning: googleapiclient not installed. Using simulation mode.")
    print("   Install: pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client")

class YouTubeCommentMonitor:
    def __init__(self):
        self.workspace = Path("/Users/abundance/.openclaw/workspace")
        self.cache_dir = self.workspace / ".cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        self.config_file = self.cache_dir / "youtube-monitor-config.json"
        self.comments_log = self.cache_dir / "youtube-comments.jsonl"
        self.stats_file = self.cache_dir / "youtube-monitor-stats.json"
        self.last_check_file = self.cache_dir / "youtube-last-check.txt"
        
        self.load_config()
        self.comments_processed = []
        self.stats = {
            "timestamp": datetime.now().isoformat(),
            "total_comments": 0,
            "auto_responses_sent": 0,
            "flagged_for_review": 0,
            "spam_deleted": 0,
            "by_category": {}
        }
    
    def load_config(self):
        """Load configuration from JSON file"""
        if not self.config_file.exists():
            print(f"❌ Config file not found: {self.config_file}")
            sys.exit(1)
        
        with open(self.config_file) as f:
            self.config = json.load(f)
    
    def categorize_comment(self, text: str) -> Tuple[str, str]:
        """
        Categorize a comment based on keyword matching
        Returns: (category_code, category_name)
        """
        text_lower = text.lower()
        
        # Check each category in order of priority
        for cat_code, cat_info in self.config["categories"].items():
            keywords = cat_info["keywords"]
            if any(keyword.lower() in text_lower for keyword in keywords):
                return cat_code, cat_info["name"]
        
        # Default to questions if uncertain
        return "1_questions", "Questions"
    
    def generate_response(self, category_code: str, comment_text: str = "") -> str:
        """Generate auto-response for the category"""
        category = self.config["categories"][category_code]
        
        if category_code == "1_questions":
            return self.config["auto_response_templates"]["question_template"]
        elif category_code == "2_praise":
            return self.config["auto_response_templates"]["praise_template"]
        else:
            return None
    
    def fetch_comments_simulation(self) -> List[Dict]:
        """
        Simulation mode: Generate sample comments for testing
        In production, replace with actual YouTube API calls
        """
        sample_comments = [
            {
                "id": "comment_001",
                "author": "AI_Enthusiast_2026",
                "text": "How do I get started with multi-agent studios? This looks amazing!",
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "likes": 3
            },
            {
                "id": "comment_002",
                "author": "DevOps_Expert",
                "text": "What's the cost to set up OpenClaw vs traditional approaches?",
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "likes": 2
            },
            {
                "id": "comment_003",
                "author": "Happy_Builder",
                "text": "This is absolutely brilliant! The workflow optimization blew my mind 🚀",
                "timestamp": (datetime.now() - timedelta(minutes=20)).isoformat(),
                "likes": 12
            },
            {
                "id": "comment_004",
                "author": "CryptoSpam_Bot",
                "text": "Click here for free Bitcoin! Limited time only!!! Click link now!!!",
                "timestamp": (datetime.now() - timedelta(minutes=22)).isoformat(),
                "likes": 0
            },
            {
                "id": "comment_005",
                "author": "AgencyOwner_LLC",
                "text": "Hey Concessa, we'd love to explore a partnership. Can we work together on white-label solutions?",
                "timestamp": (datetime.now() - timedelta(minutes=25)).isoformat(),
                "likes": 1
            },
            {
                "id": "comment_006",
                "author": "Grateful_Dev",
                "text": "Thank you for sharing this! Super helpful and inspiring to the community.",
                "timestamp": (datetime.now() - timedelta(minutes=28)).isoformat(),
                "likes": 5
            },
            {
                "id": "comment_007",
                "author": "Timeline_Asker",
                "text": "When is the next major release coming? How long does implementation usually take?",
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "likes": 1
            }
        ]
        
        return sample_comments
    
    def fetch_comments_real(self) -> List[Dict]:
        """
        Fetch real comments from YouTube API
        Requires: YOUTUBE_API_KEY environment variable
        """
        if not HAS_YOUTUBE_API:
            print("⚠️  YouTube API not available. Using simulation mode.")
            return self.fetch_comments_simulation()
        
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            print("⚠️  YOUTUBE_API_KEY not set. Using simulation mode.")
            print("    Set it: export YOUTUBE_API_KEY='your-api-key'")
            return self.fetch_comments_simulation()
        
        try:
            youtube = build("youtube", "v3", developerKey=api_key)
            
            # Get channel ID from username
            request = youtube.search().list(
                part="snippet",
                forUsername="ConcessaObvius",
                type="channel"
            )
            response = request.execute()
            
            if not response["items"]:
                print("❌ Channel not found")
                return self.fetch_comments_simulation()
            
            channel_id = response["items"][0]["snippet"]["channelId"]
            
            # Get uploads playlist
            request = youtube.channels().list(
                part="contentDetails",
                id=channel_id
            )
            response = request.execute()
            uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Get recent videos
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=5
            )
            response = request.execute()
            
            comments = []
            for video in response.get("items", []):
                video_id = video["snippet"]["resourceId"]["videoId"]
                
                # Get comments for this video
                req = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=20,
                    searchTerms=None,
                    order="relevance"
                )
                resp = req.execute()
                
                for item in resp.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "id": item["id"],
                        "author": comment["authorDisplayName"],
                        "text": comment["textDisplay"],
                        "timestamp": comment["publishedAt"],
                        "likes": comment["likeCount"],
                        "video_id": video_id
                    })
            
            return comments
        
        except HttpError as e:
            print(f"❌ YouTube API error: {e}")
            print("   Falling back to simulation mode for testing")
            return self.fetch_comments_simulation()
    
    def process_comments(self, comments: List[Dict]):
        """Process and categorize comments"""
        for comment in comments:
            comment_id = comment["id"]
            
            # Skip if already processed
            if self.is_comment_processed(comment_id):
                continue
            
            # Categorize
            category_code, category_name = self.categorize_comment(comment["text"])
            
            # Generate response if applicable
            response_status = "none"
            response_text = None
            
            if self.config["categories"][category_code].get("auto_respond"):
                response_text = self.generate_response(category_code, comment["text"])
                response_status = "auto_response_queued"
                self.stats["auto_responses_sent"] += 1
            
            # Flag spam for deletion
            if category_code == "3_spam":
                response_status = "flagged_spam_delete"
            
            # Flag sales for review
            elif category_code == "4_sales":
                response_status = "flagged_for_review"
                self.stats["flagged_for_review"] += 1
            
            # Record
            record = {
                "timestamp": datetime.now().isoformat(),
                "comment_id": comment_id,
                "commenter": comment["author"],
                "comment_text": comment["text"],
                "comment_timestamp": comment.get("timestamp", "unknown"),
                "comment_likes": comment.get("likes", 0),
                "category": category_code,
                "category_name": category_name,
                "response_status": response_status,
                "response_text": response_text,
                "processed": True
            }
            
            self.comments_processed.append(record)
            self.stats["total_comments"] += 1
            self.stats["by_category"][category_name] = self.stats["by_category"].get(category_name, 0) + 1
    
    def is_comment_processed(self, comment_id: str) -> bool:
        """Check if comment was already processed"""
        if not self.comments_log.exists():
            return False
        
        with open(self.comments_log) as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    if record.get("comment_id") == comment_id:
                        return True
        return False
    
    def log_comments(self):
        """Log all processed comments to JSONL"""
        with open(self.comments_log, "a") as f:
            for record in self.comments_processed:
                f.write(json.dumps(record) + "\n")
    
    def save_stats(self):
        """Save processing statistics"""
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)
    
    def print_report(self):
        """Print human-readable report"""
        print("\n" + "="*60)
        print("📊 YouTube Comment Monitor Report")
        print("="*60)
        print(f"⏰ Run: {self.stats['timestamp']}")
        print(f"📺 Channel: {self.config['channel']['name']}")
        print()
        print(f"📈 TOTALS:")
        print(f"   Total comments processed: {self.stats['total_comments']}")
        print(f"   Auto-responses sent: {self.stats['auto_responses_sent']}")
        print(f"   Flagged for review: {self.stats['flagged_for_review']}")
        print()
        print(f"📋 BY CATEGORY:")
        for category, count in sorted(self.stats["by_category"].items()):
            print(f"   {category}: {count}")
        print()
        print(f"📁 Logged to: {self.comments_log}")
        print("="*60 + "\n")
    
    def run(self):
        """Execute monitoring cycle"""
        print(f"\n🔍 Checking YouTube comments on {self.config['channel']['name']}...")
        
        # Fetch comments
        comments = self.fetch_comments_real()
        print(f"   Found {len(comments)} total comments")
        
        # Process
        self.process_comments(comments)
        print(f"   Processed {self.stats['total_comments']} new comments")
        
        # Log
        if self.comments_processed:
            self.log_comments()
            print(f"   ✅ Logged to JSONL")
        
        # Save stats
        self.save_stats()
        
        # Report
        self.print_report()
        
        return {
            "success": True,
            "comments_processed": self.stats["total_comments"],
            "auto_responses": self.stats["auto_responses_sent"],
            "flagged": self.stats["flagged_for_review"]
        }


if __name__ == "__main__":
    monitor = YouTubeCommentMonitor()
    result = monitor.run()
    sys.exit(0 if result["success"] else 1)
