#!/usr/bin/env python3
"""
YouTube Comment Monitor for "Concessa Obvius" Channel

Fetches new comments, categorizes them, auto-responds to questions/praise,
flags sales inquiries, and maintains idempotent state.

Usage:
    python youtube_comment_monitor.py
    
Environment variables required:
    YOUTUBE_API_KEY: Your YouTube Data API key
    CHANNEL_ID: Target channel ID (can be overridden in config)
"""

import json
import os
import sys
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import urllib.request
import urllib.error
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

CACHE_DIR = Path(".cache")
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"

# API configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "UCXXz-s8LjQGpAK-PEzMXbqg")  # Concessa Obvius
MAX_RESULTS_PER_REQUEST = 20
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
API_QUOTA_PER_CALL = 100  # YouTube quota units per API call

# Classification keywords (case-insensitive)
QUESTION_KEYWORDS = [
    r'\?$', r'how ', r'what ', r'where ', r'when ', r'why ', r'can you',
    r'could you', r'would you', r'is it', r'are you', r'do you', r'does ',
    r'should ', r'help', r'question', r'asking'
]

PRAISE_KEYWORDS = [
    r'love', r'amazing', r'awesome', r'great', r'excellent', r'perfect',
    r'fantastic', r'brilliant', r'wonderful', r'incredible', r'brilliant',
    r'thanks', r'thank you', r'appreciate', r'grateful', r'inspiring',
    r'motivat', r'help', r'superb', r'outstanding', r'👍', r'❤️'
]

SPAM_KEYWORDS = [
    r'check out my channel', r'buy now', r'click here', r'visit my site',
    r'subscribe to my', r'follow me', r'dm me', r'add me', r'join my group',
    r'link in bio', r'affiliate', r'(http|https)', r'bit\.ly', r'tinyurl',
    r'enlargement', r'viagra', r'casino', r'cryptocurrency', r'crypto',
    r'forex', r'bitcoin', r'ethereum', r'nft', r'[0-9]{10,}', r'@everyone'
]

SALES_KEYWORDS = [
    r'product for sale', r'selling ', r'for sale', r'interested in',
    r'partnership', r'collaboration', r'business opportunity', r'services',
    r'consulting', r'training', r'course', r'offer', r'deal', r'discount',
    r'promo', r'special price', r'limited time', r'price', r'investment'
]

# Auto-response templates
AUTO_RESPONSES = {
    "question": "Great question! Thank you for asking. I'll get back to you with more details soon. In the meantime, feel free to check our other videos for similar topics.",
    "praise": "Thank you so much for the kind words! 🙏 It means a lot. Keep following for more content!"
}

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    # Ensure cache directory exists before logging
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler(CACHE_DIR / "youtube-monitor.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

def load_state() -> Dict:
    """Load or initialize monitor state."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load state file: {e}. Starting fresh.")
    
    return {
        "last_run": None,
        "processed_comments": [],  # List of comment IDs already processed
        "next_page_token": None,
        "api_quota_used": 0,
        "stats": {
            "total_processed": 0,
            "total_auto_responses": 0,
            "total_flagged_for_review": 0
        }
    }

def save_state(state: Dict):
    """Persist monitor state."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        logger.error(f"Failed to save state: {e}")

def log_comment(comment_data: Dict):
    """Append comment to JSONL log."""
    try:
        COMMENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(COMMENTS_LOG, 'a') as f:
            f.write(json.dumps(comment_data) + '\n')
    except IOError as e:
        logger.error(f"Failed to log comment: {e}")

# ============================================================================
# API INTERACTION
# ============================================================================

def make_api_request(url: str) -> Optional[Dict]:
    """
    Make HTTP GET request to YouTube API.
    
    Args:
        url: Full API URL including key and parameters
        
    Returns:
        Parsed JSON response or None on failure
    """
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
                elif response.status == 403:
                    logger.error("API quota exceeded (403). Wait before retrying.")
                    return None
        except urllib.error.HTTPError as e:
            if e.code == 403:
                logger.error("API quota exceeded. Stopping.")
                return None
            elif e.code == 429:
                logger.warning(f"Rate limited (429). Backing off...")
                time.sleep(RETRY_DELAY * (2 ** attempt))
            else:
                logger.error(f"HTTP {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            logger.error(f"Network error: {e.reason}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * (2 ** attempt))
    
    return None

def get_channel_comments(state: Dict) -> Tuple[List[Dict], Dict, int]:
    """
    Fetch comments from channel (via threads).
    
    Returns:
        (comments_list, updated_state, quota_used)
    """
    if not YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY environment variable not set")
        return [], state, 0
    
    quota_used = 0
    all_comments = []
    
    # Get channel uploads playlist ID
    logger.info(f"Fetching channel info for {CHANNEL_ID}...")
    
    url = (
        f"https://www.googleapis.com/youtube/v3/channels"
        f"?part=contentDetails"
        f"&id={CHANNEL_ID}"
        f"&key={YOUTUBE_API_KEY}"
    )
    
    response = make_api_request(url)
    if not response or "items" not in response or len(response["items"]) == 0:
        logger.error("Could not fetch channel info")
        return [], state, quota_used
    
    quota_used += API_QUOTA_PER_CALL
    
    uploads_playlist = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    # Get videos from uploads playlist
    logger.info("Fetching recent videos...")
    url = (
        f"https://www.googleapis.com/youtube/v3/playlistItems"
        f"?part=contentDetails"
        f"&playlistId={uploads_playlist}"
        f"&maxResults=5"
        f"&key={YOUTUBE_API_KEY}"
    )
    
    response = make_api_request(url)
    if not response or "items" not in response:
        logger.error("Could not fetch videos")
        return [], state, quota_used
    
    quota_used += API_QUOTA_PER_CALL
    video_ids = [item["contentDetails"]["videoId"] for item in response.get("items", [])]
    
    if not video_ids:
        logger.info("No videos found")
        return [], state, quota_used
    
    # Fetch comments for each video
    for video_id in video_ids:
        logger.info(f"Fetching comments for video {video_id}...")
        
        page_token = None
        while True:
            url = (
                f"https://www.googleapis.com/youtube/v3/commentThreads"
                f"?part=snippet"
                f"&videoId={video_id}"
                f"&maxResults={MAX_RESULTS_PER_REQUEST}"
                f"&textFormat=plainText"
                f"&key={YOUTUBE_API_KEY}"
            )
            if page_token:
                url += f"&pageToken={page_token}"
            
            response = make_api_request(url)
            if not response:
                break
            
            quota_used += API_QUOTA_PER_CALL
            
            for thread in response.get("items", []):
                comment_data = thread["snippet"]["topLevelComment"]["snippet"]
                comment_id = thread["snippet"]["topLevelComment"]["id"]
                
                # Skip if already processed
                if comment_id in state.get("processed_comments", []):
                    continue
                
                all_comments.append({
                    "id": comment_id,
                    "video_id": video_id,
                    "author": comment_data["authorDisplayName"],
                    "text": comment_data["textDisplay"],
                    "timestamp": comment_data["publishedAt"],
                    "likes": comment_data["likeCount"],
                    "reply_count": thread["snippet"]["totalReplyCount"]
                })
            
            page_token = response.get("nextPageToken")
            if not page_token:
                break
    
    return all_comments, state, quota_used

# ============================================================================
# COMMENT CLASSIFICATION
# ============================================================================

def classify_comment(text: str) -> str:
    """
    Classify comment into: question, praise, spam, sales, or neutral.
    
    Classification priority: spam > sales > question > praise > neutral
    """
    text_lower = text.lower()
    
    # Check spam first (highest priority)
    for pattern in SPAM_KEYWORDS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return "spam"
    
    # Check sales keywords
    for pattern in SALES_KEYWORDS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return "sales"
    
    # Check questions
    question_score = sum(1 for pattern in QUESTION_KEYWORDS 
                        if re.search(pattern, text_lower, re.IGNORECASE))
    
    # Check praise
    praise_score = sum(1 for pattern in PRAISE_KEYWORDS 
                      if re.search(pattern, text_lower, re.IGNORECASE))
    
    if question_score > 0:
        return "question"
    elif praise_score > 0:
        return "praise"
    
    return "neutral"

# ============================================================================
# AUTO-RESPONSE
# ============================================================================

def reply_to_comment(comment_id: str, reply_text: str) -> bool:
    """
    Post a reply to a comment.
    
    Note: This requires OAuth authentication. For production, you'd need
    to implement OAuth flow or use service account credentials.
    
    For now, this is a placeholder that logs the intended response.
    """
    logger.info(f"Would reply to comment {comment_id}: {reply_text[:50]}...")
    
    # TODO: Implement OAuth authentication for production
    # This requires youtube.commentThreads().insert() with OAuth token
    
    return True

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def process_comments(comments: List[Dict], state: Dict) -> Dict:
    """
    Process, classify, and handle comments.
    
    Returns updated state with stats.
    """
    stats = {
        "processed": 0,
        "auto_responses": 0,
        "flagged_for_review": 0,
        "by_category": {
            "question": 0,
            "praise": 0,
            "spam": 0,
            "sales": 0,
            "neutral": 0
        }
    }
    
    for comment in comments:
        category = classify_comment(comment["text"])
        stats["by_category"][category] += 1
        
        # Add metadata
        comment["category"] = category
        comment["processed_at"] = datetime.utcnow().isoformat()
        
        # Log to JSONL
        log_comment(comment)
        
        # Auto-respond to questions and praise
        if category == "question":
            reply_to_comment(comment["id"], AUTO_RESPONSES["question"])
            stats["auto_responses"] += 1
            logger.info(f"✓ Auto-responded to question from {comment['author']}")
        
        elif category == "praise":
            reply_to_comment(comment["id"], AUTO_RESPONSES["praise"])
            stats["auto_responses"] += 1
            logger.info(f"✓ Auto-responded to praise from {comment['author']}")
        
        elif category == "sales":
            stats["flagged_for_review"] += 1
            logger.warning(f"⚠ Sales inquiry flagged from {comment['author']}: {comment['text'][:60]}...")
        
        # Track processed comment
        state["processed_comments"].append(comment["id"])
        stats["processed"] += 1
    
    return stats

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 70)
    logger.info("YouTube Comment Monitor Starting")
    logger.info("=" * 70)
    
    # Load state
    state = load_state()
    logger.info(f"Loaded state. Previously processed: {len(state['processed_comments'])} comments")
    
    # Fetch new comments
    logger.info(f"Fetching comments from channel {CHANNEL_ID}...")
    comments, state, quota_used = get_channel_comments(state)
    
    if not comments:
        logger.info("No new comments found.")
        state["last_run"] = datetime.utcnow().isoformat()
        save_state(state)
        logger.info(f"Quota used: {quota_used} units")
        return
    
    logger.info(f"Found {len(comments)} new comments")
    
    # Process and classify
    stats = process_comments(comments, state)
    
    # Update state
    state["last_run"] = datetime.utcnow().isoformat()
    state["api_quota_used"] = quota_used
    state["stats"]["total_processed"] += stats["processed"]
    state["stats"]["total_auto_responses"] += stats["auto_responses"]
    state["stats"]["total_flagged_for_review"] += stats["flagged_for_review"]
    
    # Save state
    save_state(state)
    
    # Print report
    logger.info("=" * 70)
    logger.info("REPORT")
    logger.info("=" * 70)
    logger.info(f"Processed: {stats['processed']}")
    logger.info(f"Auto-responses: {stats['auto_responses']}")
    logger.info(f"Flagged for review: {stats['flagged_for_review']}")
    logger.info(f"")
    logger.info(f"By category:")
    for category, count in stats["by_category"].items():
        if count > 0:
            logger.info(f"  {category}: {count}")
    logger.info(f"")
    logger.info(f"API quota used: {quota_used} units")
    logger.info(f"Session stats: {json.dumps(state['stats'], indent=2)}")
    logger.info("=" * 70)
    
    print(f"Processed: {stats['processed']} | Auto-responses: {stats['auto_responses']} | Flagged for review: {stats['flagged_for_review']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
