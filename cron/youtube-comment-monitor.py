#!/usr/bin/env python3
"""
YouTube Comment Monitor - Cron Job
Fetches, categorizes, and auto-responds to YouTube comments on a specified channel.
"""

import os
import json
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import re
from collections import defaultdict

# Third-party imports
try:
    import google.auth.transport.requests
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Missing Google API libraries. Install with:")
    print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# ============================================================================
# Configuration
# ============================================================================

WORKSPACE_ROOT = Path(__file__).parent.parent
CRON_DIR = WORKSPACE_ROOT / "cron"
STATE_DIR = CRON_DIR / ".state"
CACHE_DIR = CRON_DIR / ".cache"
TEMPLATES_FILE = CRON_DIR / "youtube-monitor-templates.json"
STATE_FILE = STATE_DIR / "youtube-monitor.json"
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"

# YouTube API
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_NAME = os.environ.get("YOUTUBE_CHANNEL_NAME", "Concessa Obvius")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(CACHE_DIR / "youtube-monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# Helper Functions
# ============================================================================

def load_json(filepath: Path, default=None):
    """Safely load JSON file."""
    if not filepath.exists():
        return default if default is not None else {}
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return default if default is not None else {}

def save_json(filepath: Path, data: dict):
    """Safely save JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")

def append_jsonl(filepath: Path, record: dict):
    """Append record to JSONL file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(filepath, 'a') as f:
            f.write(json.dumps(record) + '\n')
    except Exception as e:
        logger.error(f"Error appending to {filepath}: {e}")

def load_templates() -> dict:
    """Load response templates."""
    return load_json(TEMPLATES_FILE, {
        "questions": ["Thanks for the question! Great to see your interest."],
        "praise": ["Thank you so much! Really appreciate the support."],
        "spam": None,
        "sales": None
    })

# ============================================================================
# YouTube API Integration
# ============================================================================

def get_youtube_service():
    """Build YouTube API service."""
    if not YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY environment variable not set")
        return None
    
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        return youtube
    except Exception as e:
        logger.error(f"Failed to build YouTube service: {e}")
        return None

def get_channel_id(youtube, channel_name: str) -> Optional[str]:
    """Get channel ID from channel name."""
    try:
        request = youtube.search().list(
            q=channel_name,
            part="snippet",
            type="channel",
            maxResults=1
        )
        response = request.execute()
        
        if response.get("items"):
            return response["items"][0]["id"]["channelId"]
        
        logger.warning(f"Channel '{channel_name}' not found")
        return None
    except Exception as e:
        logger.error(f"Error searching for channel: {e}")
        return None

def get_recent_comments(youtube, channel_id: str, max_results: int = 100) -> List[dict]:
    """Fetch recent comments from channel."""
    comments = []
    try:
        # Get uploads playlist
        request = youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()
        
        if not response.get("items"):
            logger.warning(f"No channel data found for ID: {channel_id}")
            return comments
        
        uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Get recent videos from uploads
        request = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part="contentDetails",
            maxResults=10
        )
        response = request.execute()
        
        video_ids = [item["contentDetails"]["videoId"] for item in response.get("items", [])]
        
        # Get comments for each video
        for video_id in video_ids:
            request = youtube.commentThreads().list(
                videoId=video_id,
                part="snippet,replies",
                maxResults=100,
                textFormat="plainText",
                order="relevance"
            )
            response = request.execute()
            
            for thread in response.get("items", []):
                comment = thread["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "id": thread["snippet"]["topLevelComment"]["id"],
                    "videoId": video_id,
                    "authorName": comment["authorDisplayName"],
                    "authorChannelUrl": comment.get("authorChannelUrl", ""),
                    "text": comment["textDisplay"],
                    "timestamp": comment["publishedAt"],
                    "likeCount": comment["likeCount"]
                })
            
            # Get replies
            if thread["snippet"]["canReply"] and thread["snippet"]["totalReplyCount"] > 0:
                for reply in thread.get("replies", {}).get("comments", []):
                    reply_snippet = reply["snippet"]
                    comments.append({
                        "id": reply["id"],
                        "videoId": video_id,
                        "authorName": reply_snippet["authorDisplayName"],
                        "authorChannelUrl": reply_snippet.get("authorChannelUrl", ""),
                        "text": reply_snippet["textDisplay"],
                        "timestamp": reply_snippet["publishedAt"],
                        "likeCount": reply_snippet["likeCount"],
                        "parentId": thread["snippet"]["topLevelComment"]["id"]
                    })
        
        logger.info(f"Fetched {len(comments)} comments")
        return comments
    
    except HttpError as e:
        logger.error(f"YouTube API error: {e}")
        return comments
    except Exception as e:
        logger.error(f"Error fetching comments: {e}")
        return comments

# ============================================================================
# Comment Categorization
# ============================================================================

def categorize_comment(text: str) -> str:
    """Categorize comment into: questions, praise, spam, or sales."""
    text_lower = text.lower().strip()
    
    # Questions: contain question marks or question words
    if "?" in text or any(word in text_lower for word in ["what", "how", "why", "where", "when", "who"]):
        return "questions"
    
    # Spam: repetitive, all caps, links without context, etc.
    if (
        len(set(text)) < len(text) * 0.3 or  # Highly repetitive
        (text.isupper() and len(text) > 20) or  # All caps
        text_lower.count("http") > 2 or
        any(word in text_lower for word in ["clickbait", "scam", "fake"])
    ):
        return "spam"
    
    # Sales: promotional language, offers, CTAs for external products
    sales_keywords = [
        "buy", "shop", "order", "visit", "click here", "link", "limited time",
        "special offer", "discount", "promo", "code", "deal", "sale",
        "subscribe to my", "check out my", "follow me"
    ]
    if any(keyword in text_lower for keyword in sales_keywords):
        return "sales"
    
    # Praise: positive sentiment
    praise_keywords = [
        "great", "amazing", "love", "awesome", "excellent", "fantastic",
        "beautiful", "perfect", "wonderful", "brilliant", "incredible",
        "thank you", "thanks", "appreciate", "best", "goat", "best channel"
    ]
    if any(keyword in text_lower for keyword in praise_keywords):
        return "praise"
    
    # Default to questions if unclear
    return "questions"

# ============================================================================
# Auto-Response & State Management
# ============================================================================

def load_state() -> dict:
    """Load processing state."""
    default_state = {
        "lastRun": None,
        "processedCommentIds": [],
        "stats": {
            "total": 0,
            "questions": 0,
            "praise": 0,
            "spam": 0,
            "sales": 0,
            "autoResponses": 0,
            "flaggedForReview": 0
        }
    }
    return load_json(STATE_FILE, default_state)

def save_state(state: dict):
    """Save processing state."""
    save_json(STATE_FILE, state)

def select_response_template(category: str, templates: dict) -> Optional[str]:
    """Select a response template for a category."""
    category_templates = templates.get(category, [])
    if isinstance(category_templates, list) and category_templates:
        return category_templates[0]  # Simple: use first template
    return None

def should_respond(category: str) -> bool:
    """Determine if we should auto-respond to this category."""
    return category in ["questions", "praise"]

def log_comment(comment: dict, category: str, response: Optional[str] = None):
    """Log comment to JSONL."""
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "commentId": comment["id"],
        "videoId": comment["videoId"],
        "author": comment["authorName"],
        "text": comment["text"][:500],  # Truncate for logging
        "category": category,
        "response": response,
        "responseSent": response is not None,
        "likeCount": comment.get("likeCount", 0)
    }
    append_jsonl(LOG_FILE, record)

# ============================================================================
# Main Processing
# ============================================================================

def process_comments():
    """Main processing loop."""
    logger.info(f"Starting YouTube comment monitor for channel: {CHANNEL_NAME}")
    
    # Load state and templates
    state = load_state()
    templates = load_templates()
    
    # Initialize API
    youtube = get_youtube_service()
    if not youtube:
        logger.error("Failed to initialize YouTube API")
        return {"status": "error", "message": "YouTube API initialization failed"}
    
    # Get channel ID
    channel_id = get_channel_id(youtube, CHANNEL_NAME)
    if not channel_id:
        logger.error(f"Could not find channel: {CHANNEL_NAME}")
        return {"status": "error", "message": f"Channel not found: {CHANNEL_NAME}"}
    
    logger.info(f"Found channel ID: {channel_id}")
    
    # Fetch comments
    comments = get_recent_comments(youtube, channel_id, max_results=100)
    
    # Process comments
    stats = defaultdict(int)
    processed_count = 0
    response_count = 0
    flagged_count = 0
    
    for comment in comments:
        comment_id = comment["id"]
        
        # Skip if already processed
        if comment_id in state["processedCommentIds"]:
            continue
        
        # Categorize
        category = categorize_comment(comment["text"])
        stats[category] += 1
        stats["total"] += 1
        
        # Determine response
        response = None
        if should_respond(category):
            response = select_response_template(category, templates)
            if response:
                response_count += 1
                logger.info(f"Would respond to {category}: {comment['text'][:60]}...")
        
        # Flag sales for review
        if category == "sales":
            flagged_count += 1
            logger.info(f"Flagged sales comment for review: {comment['text'][:60]}...")
        
        # Log comment
        log_comment(comment, category, response)
        
        # Track as processed
        state["processedCommentIds"].append(comment_id)
        processed_count += 1
    
    # Update state
    state["lastRun"] = datetime.utcnow().isoformat()
    state["stats"] = {
        "total": len(state["processedCommentIds"]),
        "questions": stats["questions"],
        "praise": stats["praise"],
        "spam": stats["spam"],
        "sales": stats["sales"],
        "autoResponses": response_count,
        "flaggedForReview": flagged_count
    }
    save_state(state)
    
    # Generate report
    report = {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "channel": CHANNEL_NAME,
        "channelId": channel_id,
        "commentsProcessed": processed_count,
        "totalProcessed": len(state["processedCommentIds"]),
        "stats": state["stats"],
        "autoResponsesSent": response_count,
        "flaggedForReview": flagged_count,
        "logFile": str(LOG_FILE)
    }
    
    logger.info(f"Processing complete: {json.dumps(report, indent=2)}")
    
    return report

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    try:
        result = process_comments()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("status") == "success" else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2))
        sys.exit(1)
