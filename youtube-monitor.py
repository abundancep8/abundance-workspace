#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Fetches, categorizes, auto-responds, and logs comments
"""

import json
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.oauthlib.flow import InstalledAppFlow
from google.api_core.exceptions import TooManyRequests as QuotaExceeded, NotFound
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ============================================================================
# CONFIG
# ============================================================================

YOUTUBE_API_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
CREDENTIALS_PATH = WORKSPACE_DIR / ".secrets" / "youtube-credentials.json"
TOKEN_PATH = WORKSPACE_DIR / ".secrets" / "youtube-token.json"
CACHE_DIR = WORKSPACE_DIR / ".cache"
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"
CHANNEL_NAME = "Concessa Obvius"

# Keyword matching for categorization
KEYWORDS = {
    "questions": ["how", "help", "tools", "cost", "timeline", "tutorial", "start"],
    "praise": ["amazing", "inspiring", "love", "great", "awesome", "thank", "brilliant"],
    "spam": ["crypto", "bitcoin", "mlm", "forex", "dm me", "click here"],
    "sales": ["partnership", "collaboration", "sponsor", "work with", "brand deal"],
}

# Auto-response templates
RESPONSES = {
    "questions": "Thanks for the question! Check out our FAQ at [link] or email support@concessa.com",
    "praise": "Thank you so much! We love the support 💙",
}

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(CACHE_DIR / "youtube-monitor.log"),
    ],
)
logger = logging.getLogger(__name__)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def ensure_cache_dir():
    """Ensure .cache directory exists"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> Dict:
    """Load last run state (timestamp of last checked comment)"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not load state file: {e}")
    return {"last_check": None, "processed_ids": set()}


def save_state(state: Dict):
    """Save state for next run"""
    state["processed_ids"] = list(state.get("processed_ids", set()))
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        logger.error(f"Could not save state: {e}")


def load_seen_comments() -> set:
    """Load set of already-processed comment IDs from log"""
    seen = set()
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        seen.add(record.get("comment_id"))
                    except json.JSONDecodeError:
                        continue
        except IOError as e:
            logger.warning(f"Could not read log file: {e}")
    return seen


def log_comment(comment_id: str, timestamp: str, commenter: str, text: str, category: str, response_status: str):
    """Append comment to JSONL log (idempotent via deduplication)"""
    try:
        with open(LOG_FILE, "a") as f:
            record = {
                "timestamp": timestamp,
                "commenter": commenter,
                "text": text,
                "category": category,
                "response_status": response_status,
                "comment_id": comment_id,
            }
            f.write(json.dumps(record) + "\n")
    except IOError as e:
        logger.error(f"Could not write to log: {e}")


def categorize_comment(text: str) -> str:
    """Categorize comment by keyword matching"""
    text_lower = text.lower()

    # Check spam first (highest priority to filter)
    if any(keyword in text_lower for keyword in KEYWORDS["spam"]):
        return "spam"

    # Check sales
    if any(keyword in text_lower for keyword in KEYWORDS["sales"]):
        return "sales"

    # Check praise
    if any(keyword in text_lower for keyword in KEYWORDS["praise"]):
        return "praise"

    # Check questions
    if any(keyword in text_lower for keyword in KEYWORDS["questions"]):
        return "questions"

    return "other"


# ============================================================================
# YOUTUBE API
# ============================================================================


def authenticate_youtube() -> Optional:
    """Authenticate with YouTube API using OAuth2"""
    creds = None
    
    # Try loading from token file first
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, YOUTUBE_API_SCOPES)
            logger.info("Loaded credentials from token file")
        except Exception as e:
            logger.warning(f"Could not load from token file: {e}")
            creds = None
    
    # If no token file or it failed, try credentials file (OAuth flow)
    if not creds and CREDENTIALS_PATH.exists():
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, YOUTUBE_API_SCOPES
            )
            creds = flow.run_local_server(port=0)
            logger.info("Obtained new credentials via OAuth")
        except Exception as e:
            logger.error(f"OAuth flow failed: {e}")
            return None
    
    if not creds:
        logger.error(
            f"No credentials found. Please set up authentication first."
        )
        return None

    try:
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logger.info("Refreshed expired credentials")

        return build("youtube", "v3", credentials=creds)

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return None


def get_channel_id(youtube) -> Optional[str]:
    """Get channel ID for Concessa Obvius"""
    try:
        request = youtube.search().list(
            q=CHANNEL_NAME,
            part="snippet",
            type="channel",
            maxResults=1,
        )
        response = request.execute()

        if response.get("items"):
            return response["items"][0]["id"]["channelId"]
        else:
            logger.error(f"Channel '{CHANNEL_NAME}' not found")
            return None

    except HttpError as e:
        logger.error(f"Failed to get channel ID: {e}")
        return None


def get_uploads_playlist_id(youtube, channel_id: str) -> Optional[str]:
    """Get 'Uploads' playlist ID for channel"""
    try:
        request = youtube.channels().list(
            id=channel_id,
            part="contentDetails",
        )
        response = request.execute()

        if response.get("items"):
            return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        else:
            logger.error(f"Could not find uploads playlist for channel {channel_id}")
            return None

    except HttpError as e:
        logger.error(f"Failed to get uploads playlist: {e}")
        return None


def get_video_ids(youtube, playlist_id: str, max_results: int = 50) -> List[str]:
    """Get recent video IDs from channel's uploads playlist"""
    video_ids = []
    try:
        request = youtube.playlistItems().list(
            playlistId=playlist_id,
            part="contentDetails",
            maxResults=min(max_results, 50),
        )

        while request and len(video_ids) < max_results:
            response = request.execute()

            for item in response.get("items", []):
                video_ids.append(item["contentDetails"]["videoId"])

            if len(video_ids) >= max_results:
                break

            request = youtube.playlistItems().list_next(request, response)

    except HttpError as e:
        logger.error(f"Failed to get video IDs: {e}")

    return video_ids[:max_results]


def get_comments(youtube, video_id: str, after: Optional[str] = None) -> List[Dict]:
    """Fetch all top-level comments for a video, optionally after a timestamp"""
    comments = []
    try:
        request = youtube.commentThreads().list(
            videoId=video_id,
            part="snippet",
            textFormat="plainText",
            maxResults=100,
            order="relevance",  # or "time"
        )

        while request:
            response = request.execute()

            for item in response.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]
                published_at = comment["publishedAt"]

                # Skip if before 'after' timestamp
                if after and published_at <= after:
                    continue

                comments.append({
                    "id": item["id"],
                    "text": comment["textDisplay"],
                    "author": comment["authorDisplayName"],
                    "timestamp": published_at,
                    "video_id": video_id,
                })

            request = youtube.commentThreads().list_next(request, response)

    except HttpError as e:
        if e.resp.status == 403 and "commentsDisabled" in str(e):
            logger.info(f"Comments disabled on video {video_id}")
        else:
            logger.error(f"Failed to get comments for video {video_id}: {e}")

    return comments


def reply_to_comment(youtube, comment_id: str, text: str) -> bool:
    """Reply to a comment"""
    try:
        request = youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": text,
                }
            },
        )
        response = request.execute()
        logger.info(f"Replied to comment {comment_id}")
        return True

    except HttpError as e:
        logger.error(f"Failed to reply to comment {comment_id}: {e}")
        return False

    except QuotaExceeded:
        logger.warning("YouTube API quota exceeded, stopping replies")
        return False


# ============================================================================
# MAIN MONITOR LOGIC
# ============================================================================


def run_monitor():
    """Main monitor loop: fetch, categorize, respond, log"""
    ensure_cache_dir()

    logger.info("=" * 70)
    logger.info("YouTube Comment Monitor Started")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info("=" * 70)

    # Load state and seen comments
    state = load_state()
    seen_ids = load_seen_comments()

    # Authenticate
    youtube = authenticate_youtube()
    if not youtube:
        logger.error("Failed to authenticate. Exiting.")
        return

    # Get channel and uploads
    channel_id = get_channel_id(youtube)
    if not channel_id:
        logger.error("Failed to get channel ID. Exiting.")
        return

    uploads_playlist_id = get_uploads_playlist_id(youtube, channel_id)
    if not uploads_playlist_id:
        logger.error("Failed to get uploads playlist. Exiting.")
        return

    # Get recent videos
    logger.info(f"Fetching videos from channel: {CHANNEL_NAME}")
    video_ids = get_video_ids(youtube, uploads_playlist_id, max_results=10)
    logger.info(f"Found {len(video_ids)} recent videos")

    # Fetch and process comments
    stats = {
        "total_processed": 0,
        "by_category": {"questions": 0, "praise": 0, "spam": 0, "sales": 0, "other": 0},
        "auto_responses_sent": 0,
        "flagged_for_review": 0,
        "errors": 0,
    }

    last_check_time = state.get("last_check")
    if last_check_time:
        logger.info(f"Resuming from last check: {last_check_time}")

    for video_id in video_ids:
        try:
            logger.info(f"Fetching comments for video: {video_id}")
            comments = get_comments(youtube, video_id, after=last_check_time)
            logger.info(f"Found {len(comments)} new comments")

            for comment in comments:
                comment_id = comment["id"]

                # Skip if already seen
                if comment_id in seen_ids:
                    logger.debug(f"Skipping already-seen comment {comment_id}")
                    continue

                # Categorize
                category = categorize_comment(comment["text"])
                stats["by_category"][category] += 1
                stats["total_processed"] += 1

                # Auto-respond
                response_status = "none"
                if category == "questions":
                    if reply_to_comment(youtube, comment_id, RESPONSES["questions"]):
                        stats["auto_responses_sent"] += 1
                        response_status = "replied"
                    else:
                        response_status = "failed"

                elif category == "praise":
                    if reply_to_comment(youtube, comment_id, RESPONSES["praise"]):
                        stats["auto_responses_sent"] += 1
                        response_status = "replied"
                    else:
                        response_status = "failed"

                elif category == "sales":
                    stats["flagged_for_review"] += 1
                    response_status = "flagged"

                # Log comment
                log_comment(
                    comment_id=comment_id,
                    timestamp=comment["timestamp"],
                    commenter=comment["author"],
                    text=comment["text"],
                    category=category,
                    response_status=response_status,
                )

                seen_ids.add(comment_id)

                # Rate limiting
                time.sleep(0.1)

        except QuotaExceeded:
            logger.warning("YouTube API quota exceeded, stopping")
            break
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {e}")
            stats["errors"] += 1
            continue

    # Save state
    state["last_check"] = datetime.utcnow().isoformat() + "Z"
    state["processed_ids"] = seen_ids
    save_state(state)

    # Print report
    logger.info("=" * 70)
    logger.info("RUN STATISTICS")
    logger.info("=" * 70)
    logger.info(f"Run completed at: {datetime.now().isoformat()}")
    logger.info(f"Total comments processed: {stats['total_processed']}")
    logger.info(f"  - Questions: {stats['by_category']['questions']}")
    logger.info(f"  - Praise: {stats['by_category']['praise']}")
    logger.info(f"  - Spam: {stats['by_category']['spam']}")
    logger.info(f"  - Sales: {stats['by_category']['sales']}")
    logger.info(f"  - Other: {stats['by_category']['other']}")
    logger.info(f"Auto-responses sent: {stats['auto_responses_sent']}")
    logger.info(f"Flagged for review (sales): {stats['flagged_for_review']}")
    logger.info(f"Errors encountered: {stats['errors']}")
    logger.info(f"Log file: {LOG_FILE}")
    logger.info("=" * 70)

    return stats


if __name__ == "__main__":
    try:
        run_monitor()
    except KeyboardInterrupt:
        logger.info("Monitor interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
