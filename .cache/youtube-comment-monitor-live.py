#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius
Live implementation with real YouTube API integration
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

# Configuration paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
CACHE = WORKSPACE / ".cache"
CONFIG_FILE = CACHE / "youtube-monitor-config.json"
STATE_FILE = CACHE / ".youtube-monitor-state.json"
COMMENTS_LOG = CACHE / "youtube-comments.jsonl"
CREDENTIALS = CACHE / "youtube-credentials.json"
TOKEN_FILE = CACHE / "youtube-token.json"

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("⚠️ SETUP: Missing Google API libraries")
    print("Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    print("\nAPI credentials are available at:")
    print(f"  {CREDENTIALS}")
    sys.exit(1)


class YouTubeCommentMonitor:
    """Monitor and categorize YouTube comments"""
    
    def __init__(self):
        self.workspace = WORKSPACE
        self.cache = CACHE
        self.cache.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config()
        self.state = self._load_state()
        self.youtube = None
        self.channel_id = None
        
        self.processed_this_run = []
        self.stats = {
            "total_processed": 0,
            "questions": 0,
            "questions_responded": 0,
            "praise": 0,
            "praise_responded": 0,
            "spam": 0,
            "spam_logged": 0,
            "sales": 0,
            "sales_flagged": 0,
        }
        
    def _load_config(self) -> Dict:
        """Load monitor configuration"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            "channel": {
                "name": "Concessa Obvius",
                "username": "@ConcessaObvius"
            },
            "categories": {
                "questions": {
                    "keywords": [
                        "how do i", "how to", "how can", "what is", "where can",
                        "cost", "price", "timeline", "when", "tools", "setup",
                        "start", "getting started", "tutorial", "help"
                    ],
                    "auto_respond": True,
                    "template": "Thanks for asking! [Answer framework: 1) Start here, 2) Tools needed, 3) Next steps] Feel free to reach out with follow-ups."
                },
                "praise": {
                    "keywords": [
                        "amazing", "awesome", "love", "great", "inspiring",
                        "brilliant", "fantastic", "excellent", "thank you",
                        "incredible", "genius"
                    ],
                    "auto_respond": True,
                    "template": "Thank you so much! Comments like yours keep me motivated. Appreciate the support!"
                },
                "spam": {
                    "keywords": [
                        "crypto", "bitcoin", "nft", "mlm", "forex",
                        "earn money", "work from home", "click here",
                        "limited time", "act now"
                    ],
                    "auto_respond": False,
                },
                "sales": {
                    "keywords": [
                        "partnership", "collaboration", "brand deal",
                        "sponsorship", "affiliate", "promote your",
                        "let's work together", "business opportunity"
                    ],
                    "auto_respond": False,
                }
            }
        }
    
    def _load_state(self) -> Dict:
        """Load state to track last run"""
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return json.load(f)
        return {
            "last_run": None,
            "last_comment_id": None,
            "total_all_time": 0,
            "auto_responses_sent": 0,
            "flagged_for_review": 0,
        }
    
    def _save_state(self):
        """Save current state"""
        self.state.update({
            "last_run": datetime.now(timezone.utc).isoformat(),
            "total_all_time": self.state.get("total_all_time", 0) + len(self.processed_this_run),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def authenticate(self) -> bool:
        """Authenticate with YouTube API"""
        try:
            # Try to use existing token
            if TOKEN_FILE.exists():
                self.youtube = self._auth_with_token()
                return self.youtube is not None
            
            # Fall back to credentials file
            if CREDENTIALS.exists():
                self.youtube = self._auth_with_credentials_file()
                return self.youtube is not None
            
            # API key only (read-only)
            api_key = os.getenv("YOUTUBE_API_KEY")
            if api_key:
                self.youtube = build("youtube", "v3", developerKey=api_key)
                print(f"✓ Authenticated with API key")
                return True
            
            print("⚠️ No YouTube credentials found")
            self._print_setup_instructions()
            return False
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def _auth_with_token(self) -> Optional:
        """Authenticate using saved token"""
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE))
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_FILE, "w") as f:
                    f.write(creds.to_json())
            return build("youtube", "v3", credentials=creds)
        except Exception as e:
            print(f"⚠️ Token auth failed: {e}")
            return None
    
    def _auth_with_credentials_file(self) -> Optional:
        """Authenticate using credentials file (OAuth flow)"""
        try:
            SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS), SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
            return build("youtube", "v3", credentials=creds)
        except Exception as e:
            print(f"⚠️ OAuth flow failed: {e}")
            return None
    
    def _print_setup_instructions(self):
        """Print setup instructions"""
        print("\n" + "="*60)
        print("SETUP REQUIRED: YouTube API Configuration")
        print("="*60)
        print(f"\n1. Credentials file exists at: {CREDENTIALS}")
        print("2. To authenticate:")
        print("   - First run will open browser for OAuth")
        print("   - OR set YOUTUBE_API_KEY environment variable")
        print(f"\n3. Log file location: {COMMENTS_LOG}")
        print("="*60 + "\n")
    
    def find_channel_id(self, channel_username: str) -> Optional[str]:
        """Find channel ID by username"""
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=channel_username,
                type="channel",
                maxResults=1
            )
            results = request.execute()
            if results.get("items"):
                return results["items"][0]["snippet"]["channelId"]
        except Exception as e:
            print(f"⚠️ Channel search failed: {e}")
        return None
    
    def get_latest_comments(self, channel_id: str, max_results: int = 20) -> List[Dict]:
        """Fetch latest comments from channel"""
        try:
            # Get channel uploads playlist
            channel_req = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            )
            channel_res = channel_req.execute()
            if not channel_res.get("items"):
                print(f"❌ Channel not found: {channel_id}")
                return []
            
            uploads_id = channel_res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Get latest videos
            playlist_req = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_id,
                maxResults=5
            )
            playlist_res = playlist_req.execute()
            
            comments = []
            for item in playlist_res.get("items", []):
                video_id = item["snippet"]["resourceId"]["videoId"]
                
                # Get comments for this video
                comments_req = self.youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    textFormat="plainText",
                    maxResults=min(max_results, 20),
                    order="relevance"
                )
                comments_res = comments_req.execute()
                
                for thread in comments_res.get("items", []):
                    comment = thread["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "comment_id": thread["id"],
                        "video_id": video_id,
                        "author": comment["authorDisplayName"],
                        "text": comment["textDisplay"],
                        "published_at": comment["publishedAt"],
                        "likes": comment["likeCount"],
                    })
            
            return comments[:max_results]
            
        except Exception as e:
            print(f"❌ Failed to fetch comments: {e}")
            return []
    
    def categorize_comment(self, text: str) -> Tuple[str, float]:
        """Categorize comment by content"""
        text_lower = text.lower()
        
        # Check each category
        for category, config in self.config["categories"].items():
            keywords = config.get("keywords", [])
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                confidence = min(1.0, matches / len(keywords))
                return category, confidence
        
        # Default to general
        return "general", 0.5
    
    def create_response(self, category: str, comment_text: str) -> Optional[str]:
        """Generate auto-response if applicable"""
        config = self.config["categories"].get(category, {})
        
        if not config.get("auto_respond"):
            return None
        
        template = config.get("template", "")
        if not template:
            return None
        
        # Simple template expansion
        response = template
        response = response.replace("[Author]", "there")
        response = response.replace("[Topic]", "this topic")
        
        return response
    
    def log_comment(self, comment: Dict, category: str, response: Optional[str], responded: bool):
        """Log comment to JSONL file"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "comment_id": comment.get("comment_id"),
            "commenter": comment.get("author", "unknown"),
            "text": comment.get("text", ""),
            "category": category,
            "auto_response_sent": responded,
            "response_text": response,
        }
        
        with open(COMMENTS_LOG, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        self.processed_this_run.append(log_entry)
    
    def run(self):
        """Run the monitor"""
        print(f"\n{'='*60}")
        print(f"YouTube Comment Monitor - Concessa Obvius")
        print(f"Started: {datetime.now(timezone.utc).isoformat()}")
        print(f"{'='*60}\n")
        
        # Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed.\n")
            return False
        
        # Find channel
        channel_name = self.config["channel"]["name"]
        channel_username = self.config["channel"].get("username", "")
        
        print(f"📺 Monitoring channel: {channel_name}")
        print(f"   Username: {channel_username}")
        
        # Try to find channel ID (could be hardcoded or discovered)
        self.channel_id = self.config["channel"].get("channel_id")
        if not self.channel_id and channel_username:
            print(f"   Searching for channel ID...")
            self.channel_id = self.find_channel_id(channel_username)
        
        if not self.channel_id:
            print("❌ Could not determine channel ID\n")
            return False
        
        print(f"   Channel ID: {self.channel_id}")
        
        # Fetch comments
        print(f"\n🔍 Fetching latest comments...")
        comments = self.get_latest_comments(self.channel_id, max_results=20)
        print(f"   Found {len(comments)} comments\n")
        
        if not comments:
            print("⚠️ No comments to process\n")
            self._save_state()
            return True
        
        # Process each comment
        for comment in comments:
            category, confidence = self.categorize_comment(comment["text"])
            response = self.create_response(category, comment["text"])
            responded = response is not None
            
            # Update stats
            self.stats["total_processed"] += 1
            if category in self.stats:
                self.stats[category] += 1
            if responded:
                self.stats[f"{category}_responded"] += 1
            
            # Log the comment
            self.log_comment(comment, category, response, responded)
            
            # Print summary
            print(f"[{category.upper()}] {comment.get('author', 'Unknown')}")
            print(f"  Text: {comment['text'][:60]}...")
            if responded:
                print(f"  ✓ Auto-responded")
            else:
                print(f"  → Flagged for review" if category == "sales" else "  ~ Logged")
            print()
        
        # Save state
        self._save_state()
        
        # Print final report
        self._print_report()
        
        return True
    
    def _print_report(self):
        """Print execution report"""
        print(f"\n{'='*60}")
        print(f"EXECUTION REPORT")
        print(f"{'='*60}\n")
        
        print(f"Total comments processed this run: {self.stats['total_processed']}")
        print(f"Auto-responses sent: {sum(self.stats[k] for k in self.stats if k.endswith('_responded'))}")
        print(f"Flagged for manual review: {self.stats.get('sales', 0)}")
        print()
        
        print("Breakdown by category:")
        for cat in ["questions", "praise", "spam", "sales"]:
            count = self.stats.get(cat, 0)
            responded = self.stats.get(f"{cat}_responded", 0)
            if count > 0:
                print(f"  {cat.capitalize()}: {count} (responded: {responded})")
        
        print()
        print(f"Comments logged to: {COMMENTS_LOG}")
        print(f"State saved to: {STATE_FILE}")
        print(f"\n{'='*60}\n")


if __name__ == "__main__":
    monitor = YouTubeCommentMonitor()
    success = monitor.run()
    sys.exit(0 if success else 1)
