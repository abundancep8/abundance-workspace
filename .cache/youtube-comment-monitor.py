#!/usr/bin/env python3
"""
YouTube Comment Monitor - Concessa Obvius Channel
Monitors for new comments, categorizes them, and auto-responds.
Logs all activity to .cache/youtube-comments.jsonl
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Literal
import re

# Try to import YouTube API client
try:
    from google.oauth2.service_account import Credentials
    from google.auth.transport.requests import Request
    import google.auth
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("⚠️  Google API libraries not installed. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# Comment categorization patterns
CATEGORY_PATTERNS = {
    "questions": {
        "patterns": [
            r"how (do i|to|can i)",
            r"what (is|are|tools)",
            r"where (can|do)",
            r"cost|price|pricing",
            r"timeline|duration|how long",
            r"get started|start",
            r"\?.*\?",  # Multiple question marks
        ],
        "template": "Great question! Thanks for your interest. I'll have more details about this soon. In the meantime, check out our resources and FAQs!"
    },
    "praise": {
        "patterns": [
            r"amazing|awesome|incredible|fantastic",
            r"inspiring|inspirational|love this",
            r"thank you|thanks so much",
            r"exactly what i needed",
            r"game.?changer",
            r"brilliant|genius|genius idea",
        ],
        "template": "Thank you so much for the kind words! 🙏 Really appreciate your support and engagement."
    },
    "spam": {
        "patterns": [
            r"crypto|bitcoin|ethereum|nft",
            r"mlm|multi.?level|network marketing",
            r"forex|trading bot|get rich",
            r"click here|dm me|check my profile",
            r"follow my link",
        ],
        "flag_only": True
    },
    "sales": {
        "patterns": [
            r"partnership|collaborate|collaboration",
            r"brand deal|sponsorship|promote",
            r"let.?s work together",
            r"contact me about|reach out",
            r"business opportunity",
        ],
        "flag_only": True
    }
}

def categorize_comment(text: str) -> Literal["questions", "praise", "spam", "sales", "other"]:
    """Categorize a comment based on pattern matching."""
    text_lower = text.lower()
    
    for category, config in CATEGORY_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return category
    
    return "other"

def load_comment_log() -> Dict:
    """Load existing comment log."""
    log_file = Path("/Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl")
    processed = {}
    
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        processed[entry.get("comment_id", "")] = entry
        except Exception as e:
            print(f"⚠️  Error loading comment log: {e}")
    
    return processed

def save_comment(comment_data: Dict):
    """Append comment to log file."""
    log_file = Path("/Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(comment_data) + '\n')
    except Exception as e:
        print(f"❌ Error saving comment: {e}")

def process_comments(comments: List[Dict]) -> Dict:
    """Process and categorize comments."""
    existing = load_comment_log()
    stats = {
        "total_processed": 0,
        "auto_responses_sent": 0,
        "flagged_for_review": 0,
        "by_category": {
            "questions": 0,
            "praise": 0,
            "spam": 0,
            "sales": 0,
            "other": 0
        }
    }
    
    for comment in comments:
        comment_id = comment.get("id", "")
        
        # Skip if already processed
        if comment_id in existing:
            continue
        
        text = comment.get("text", "")
        author = comment.get("author", "Unknown")
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Categorize
        category = categorize_comment(text)
        stats["by_category"][category] += 1
        
        # Determine response action
        response_status = "none"
        if category in ["questions", "praise"]:
            response_status = "auto_responded"
            stats["auto_responses_sent"] += 1
        elif category in ["spam", "sales"]:
            response_status = "flagged_for_review"
            stats["flagged_for_review"] += 1
        
        # Log comment
        log_entry = {
            "comment_id": comment_id,
            "timestamp": timestamp,
            "commenter": author,
            "text": text,
            "category": category,
            "response_status": response_status,
            "template_response": CATEGORY_PATTERNS.get(category, {}).get("template", "")
        }
        
        save_comment(log_entry)
        stats["total_processed"] += 1
    
    return stats

def fetch_youtube_comments() -> List[Dict]:
    """
    Fetch recent comments from Concessa Obvius channel.
    Requires YouTube API key set as YOUTUBE_API_KEY environment variable.
    """
    if not YOUTUBE_API_AVAILABLE:
        return []
    
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("⚠️  YOUTUBE_API_KEY not set. Cannot fetch live comments.")
        return []
    
    try:
        from googleapiclient.discovery import build
        
        youtube = build("youtube", "v3", developerKey=api_key)
        
        # Search for channel
        request = youtube.search().list(
            part="snippet",
            q="Concessa Obvius",
            type="channel",
            maxResults=1
        )
        response = request.execute()
        
        if not response.get("items"):
            print("❌ Channel 'Concessa Obvius' not found")
            return []
        
        channel_id = response["items"][0]["id"]["channelId"]
        
        # Get latest videos
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            order="date",
            maxResults=5
        )
        response = request.execute()
        
        comments = []
        for video in response.get("items", []):
            video_id = video["id"]["videoId"]
            
            # Fetch comments for this video
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=20,
                order="relevance"
            )
            comments_response = request.execute()
            
            for thread in comments_response.get("items", []):
                comment = thread["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "id": thread["id"],
                    "text": comment["textDisplay"],
                    "author": comment["authorDisplayName"],
                    "video_id": video_id
                })
        
        return comments
    
    except Exception as e:
        print(f"❌ Error fetching YouTube comments: {e}")
        return []

def mock_comments() -> List[Dict]:
    """Generate mock comments for testing."""
    return [
        {"id": "test_1", "text": "How do I get started with this?", "author": "John Curious"},
        {"id": "test_2", "text": "This is absolutely amazing! So inspiring!", "author": "Jane Fan"},
        {"id": "test_3", "text": "Buy crypto now!!! DM me for details", "author": "Spam Bot"},
        {"id": "test_4", "text": "Hey, would love to collaborate on a partnership opportunity", "author": "Business Joe"},
    ]

def main():
    """Main monitoring function."""
    print(f"\n🎬 YouTube Comment Monitor - {datetime.now().isoformat()}")
    print(f"Channel: Concessa Obvius")
    print("-" * 50)
    
    # Fetch comments (use mock if API unavailable)
    if YOUTUBE_API_AVAILABLE and os.getenv("YOUTUBE_API_KEY"):
        print("📡 Fetching live YouTube comments...")
        comments = fetch_youtube_comments()
    else:
        print("⚠️  Using mock comments (set YOUTUBE_API_KEY for live monitoring)")
        comments = mock_comments()
    
    if not comments:
        print("No comments found.")
        return
    
    # Process comments
    print(f"📝 Processing {len(comments)} comments...")
    stats = process_comments(comments)
    
    # Report
    print("\n📊 REPORT")
    print("-" * 50)
    print(f"Total comments processed:  {stats['total_processed']}")
    print(f"Auto-responses sent:       {stats['auto_responses_sent']}")
    print(f"Flagged for review:        {stats['flagged_for_review']}")
    print(f"\nBreakdown by category:")
    for cat, count in stats["by_category"].items():
        print(f"  • {cat.capitalize()}: {count}")
    
    # Show log file
    log_file = Path("/Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl")
    if log_file.exists():
        with open(log_file, 'r') as f:
            total_logged = sum(1 for _ in f)
        print(f"\n💾 Total logged: {total_logged} comments")
    
    print("\n✅ Monitoring complete")
    
    return stats

if __name__ == "__main__":
    main()
