#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Monitors, categorizes, auto-responds, and logs comments every 30 minutes.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import re

# YouTube API imports
try:
    from google.oauth2.service_account import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Install google-auth-oauthlib and google-api-python-client")
    print("pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
CACHE_DIR = Path(".cache")
STATE_FILE = CACHE_DIR / "youtube-monitor.json"
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"
REVIEW_FILE = CACHE_DIR / "youtube-review.txt"
CACHE_DIR.mkdir(exist_ok=True)

# Category keywords
CATEGORIES = {
    1: {
        "name": "Questions",
        "keywords": [
            "how", "how do i", "how to", "where", "when", "what is",
            "start", "tools", "cost", "price", "timeline", "free",
            "setup", "install", "requirements", "help", "tutorial"
        ],
        "template": "Thanks for the question! I appreciate your interest. Check our resources or community for detailed answers, or feel free to ask for clarification. 💡"
    },
    2: {
        "name": "Praise",
        "keywords": [
            "amazing", "inspiring", "great", "love", "awesome", "incredible",
            "beautiful", "wonderful", "fantastic", "excellent", "brilliant",
            "impressed", "mindblown", "life-changing", "thank you", "grateful"
        ],
        "template": "Thank you so much for the kind words! 💙 Your support means the world to us. We hope to keep creating great content for you!"
    },
    3: {
        "name": "Spam",
        "keywords": [
            "crypto", "bitcoin", "ethereum", "nft", "mlm", "multi-level",
            "affiliate", "forex", "trading", "gambling", "casino", "slots",
            "doubling", "passive income", "click here", "dm for", "dm me"
        ]
    },
    4: {
        "name": "Sales/Partnerships",
        "keywords": [
            "partnership", "collaboration", "business", "work together",
            "sponsor", "promote", "promote your", "interested in working",
            "brand deal", "sponsorship", "collab", "contact me", "let's work"
        ]
    }
}

def get_youtube_service():
    """Initialize YouTube API client."""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        logger.error("YOUTUBE_API_KEY environment variable not set")
        sys.exit(1)
    
    return build("youtube", "v3", developerKey=api_key)

def get_channel_id() -> str:
    """Get Concessa Obvius channel ID."""
    # This is a known channel ID - update if needed
    return os.environ.get("YOUTUBE_CHANNEL_ID", "UCyourChannelIdHere")

def load_state() -> Dict:
    """Load last checked timestamp and processed comment IDs."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    
    return {
        "last_checked": (datetime.now() - timedelta(hours=1)).isoformat(),
        "processed_comments": set()
    }

def save_state(state: Dict):
    """Save state to file."""
    # Convert set to list for JSON serialization
    save_data = {
        "last_checked": state["last_checked"],
        "processed_comments": list(state["processed_comments"])
    }
    STATE_FILE.write_text(json.dumps(save_data, indent=2))

def categorize_comment(text: str) -> Tuple[int, str]:
    """
    Categorize comment based on keywords.
    Returns: (category_number, category_name)
    """
    text_lower = text.lower()
    
    # Check each category
    scores = {}
    for category, info in CATEGORIES.items():
        keyword_matches = sum(1 for kw in info["keywords"] if kw in text_lower)
        if keyword_matches > 0:
            scores[category] = keyword_matches
    
    if not scores:
        return 0, "Uncategorized"  # Default category
    
    # Return highest scoring category
    best_category = max(scores, key=scores.get)
    return best_category, CATEGORIES[best_category]["name"]

def fetch_comments(service, channel_id: str, since_time: str) -> List[Dict]:
    """Fetch comments from channel since last check."""
    try:
        comments = []
        
        # Get channel uploads playlist
        channels_response = service.channels().list(
            part="contentDetails",
            id=channel_id
        ).execute()
        
        if not channels_response.get("items"):
            logger.warning(f"Channel {channel_id} not found")
            return []
        
        uploads_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Get recent videos
        playlist_items = service.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_id,
            maxResults=50
        ).execute()
        
        video_ids = [item["contentDetails"]["videoId"] 
                     for item in playlist_items.get("items", [])]
        
        # Fetch comments from each video
        for video_id in video_ids:
            try:
                comments_response = service.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    searchTerms="",
                    textFormat="plainText"
                ).execute()
                
                for item in comments_response.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "comment_id": item["id"],
                        "video_id": video_id,
                        "author": comment["authorDisplayName"],
                        "text": comment["textDisplay"],
                        "published_at": comment["publishedAt"],
                        "reply_count": item["snippet"]["totalReplyCount"]
                    })
            except HttpError as e:
                logger.warning(f"Error fetching comments for video {video_id}: {e}")
                continue
        
        return comments
    
    except HttpError as e:
        if e.resp.status == 429:
            logger.error("YouTube API rate limited")
        else:
            logger.error(f"YouTube API error: {e}")
        return []

def auto_respond(service, comment_id: str, text: str, category: int) -> bool:
    """Post reply to comment."""
    if category not in [1, 2]:
        return False  # Only auto-respond to Q and Praise
    
    try:
        template = CATEGORIES[category]["template"]
        response_text = f"{template}"
        
        service.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": response_text
                }
            }
        ).execute()
        
        logger.info(f"Replied to comment {comment_id}")
        return True
    
    except HttpError as e:
        if e.resp.status == 403:
            logger.warning(f"Permission denied - channel may need OAuth setup for replies")
        else:
            logger.warning(f"Could not reply to comment: {e}")
        return False

def log_comment(comment: Dict, category: int, category_name: str, response_sent: bool):
    """Log comment to JSONL file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "comment_id": comment["comment_id"],
        "video_id": comment["video_id"],
        "author": comment["author"],
        "text": comment["text"],
        "published_at": comment["published_at"],
        "category": category,
        "category_name": category_name,
        "response_sent": response_sent,
        "reply_count": comment["reply_count"]
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def flag_for_review(comment: Dict, category_name: str):
    """Flag partnership/sales comments for manual review."""
    with open(REVIEW_FILE, "a") as f:
        f.write(f"\n--- {datetime.now().isoformat()} ---\n")
        f.write(f"Author: {comment['author']}\n")
        f.write(f"Video: {comment['video_id']}\n")
        f.write(f"Category: {category_name}\n")
        f.write(f"Text: {comment['text']}\n")
        f.write(f"Comment ID: {comment['comment_id']}\n")

def run_monitor():
    """Main monitoring loop."""
    logger.info("Starting YouTube Comment Monitor")
    
    # Load state
    state = load_state()
    last_checked = datetime.fromisoformat(state["last_checked"])
    processed_ids = set(state["processed_comments"])
    
    logger.info(f"Last checked: {last_checked}")
    
    # Initialize API
    service = get_youtube_service()
    channel_id = get_channel_id()
    
    # Fetch comments
    comments = fetch_comments(service, channel_id, last_checked.isoformat())
    logger.info(f"Found {len(comments)} total comments")
    
    # Process comments
    stats = {
        "total_processed": 0,
        "questions": 0,
        "praise": 0,
        "spam": 0,
        "sales": 0,
        "uncategorized": 0,
        "auto_responses_sent": 0,
        "flagged_for_review": 0
    }
    
    for comment in comments:
        comment_id = comment["comment_id"]
        
        # Skip already processed
        if comment_id in processed_ids:
            continue
        
        # Categorize
        category, category_name = categorize_comment(comment["text"])
        stats["total_processed"] += 1
        stats[{
            0: "uncategorized",
            1: "questions",
            2: "praise",
            3: "spam",
            4: "sales"
        }[category]] += 1
        
        # Auto-respond to Q and Praise
        response_sent = False
        if category in [1, 2]:
            response_sent = auto_respond(service, comment_id, comment["text"], category)
            if response_sent:
                stats["auto_responses_sent"] += 1
        
        # Flag sales/partnerships
        if category == 4:
            flag_for_review(comment, category_name)
            stats["flagged_for_review"] += 1
        
        # Log comment
        log_comment(comment, category, category_name, response_sent)
        processed_ids.add(comment_id)
    
    # Save state
    state["last_checked"] = datetime.now().isoformat()
    state["processed_comments"] = processed_ids
    save_state(state)
    
    # Print report
    logger.info("\n" + "="*60)
    logger.info("YOUTUBE COMMENT MONITOR REPORT")
    logger.info("="*60)
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Channel: {channel_id}")
    logger.info(f"\nComments Processed: {stats['total_processed']}")
    logger.info(f"  - Questions: {stats['questions']}")
    logger.info(f"  - Praise: {stats['praise']}")
    logger.info(f"  - Spam (filtered): {stats['spam']}")
    logger.info(f"  - Sales/Partnerships: {stats['sales']}")
    logger.info(f"  - Uncategorized: {stats['uncategorized']}")
    logger.info(f"\nAuto-Responses Sent: {stats['auto_responses_sent']}")
    logger.info(f"Flagged for Review: {stats['flagged_for_review']}")
    logger.info(f"Log File: {LOG_FILE}")
    logger.info(f"Review File: {REVIEW_FILE}")
    logger.info("="*60 + "\n")
    
    return stats

if __name__ == "__main__":
    try:
        run_monitor()
    except Exception as e:
        logger.error(f"Monitor failed: {e}", exc_info=True)
        sys.exit(1)
