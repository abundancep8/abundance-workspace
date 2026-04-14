#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Monitors for new comments, categorizes, and auto-responds.
"""

import os
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Missing Google API libraries. Install with:")
    print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Configuration
WORKSPACE = Path.home() / ".openclaw" / "workspace"
CACHE_DIR = WORKSPACE / ".cache"
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"
SCRIPT_LOG = CACHE_DIR / "youtube-monitor.log"
CHANNEL_ID = "UCkh0NhEcYYqWZMPKk42iU7w"  # Concessa Obvius channel ID
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(SCRIPT_LOG),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Category patterns
CATEGORY_PATTERNS = {
    1: {  # Questions
        "keywords": [
            r"how\s+(do|can|to|should|would)",
            r"what\s+(is|are|should)",
            r"where\s+(do|can|should)",
            r"when\s+(can|should|do)",
            r"cost",
            r"price",
            r"timeline",
            r"how\s+long",
            r"tools?\s+needed",
            r"start",
            r"beginner",
            r"\?",
        ]
    },
    2: {  # Praise
        "keywords": [
            r"amazing",
            r"incredible",
            r"inspiring",
            r"love\s+this",
            r"awesome",
            r"great",
            r"brilliant",
            r"excellent",
            r"fantastic",
            r"thank\s+you",
            r"appreciate",
            r"game.?changer",
            r"life.?changing",
        ]
    },
    3: {  # Spam
        "keywords": [
            r"crypto",
            r"bitcoin",
            r"ethereum",
            r"nft",
            r"mlm",
            r"pyramid",
            r"get\s+rich",
            r"click\s+here",
            r"dm\s+me",
            r"whatsapp",
            r"telegram",
            r"check\s+link",
            r"free\s+money",
            r"earn\s+fast",
        ]
    },
    4: {  # Sales/Partnership
        "keywords": [
            r"partnership",
            r"collaboration",
            r"collab",
            r"brand\s+deal",
            r"sponsorship",
            r"work\s+together",
            r"business\s+opportunity",
            r"interested\s+in\s+working",
            r"promote",
            r"marketing",
            r"growth\s+hacking",
        ]
    },
}

# Response templates
RESPONSES = {
    1: "Thanks for asking! Check out our FAQ and documentation for detailed answers to common questions. Feel free to ask again if you need more help!",
    2: "Thank you so much! 🙏 We really appreciate your support and feedback.",
}


def categorize_comment(text: str) -> int:
    """Categorize a comment based on keyword patterns."""
    text_lower = text.lower()

    # Check each category
    for category in [4, 3, 1, 2]:  # Check sales/spam first (more specific)
        for pattern in CATEGORY_PATTERNS[category]["keywords"]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return category

    return 2  # Default to praise if no match


def load_state() -> Dict:
    """Load monitor state (last check timestamp, etc.)"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_check": None, "total_processed": 0, "total_responses": 0, "total_flagged": 0}


def save_state(state: Dict):
    """Save monitor state."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_youtube_service():
    """Authenticate and return YouTube API service."""
    creds = None
    token_file = CACHE_DIR / "youtube_token.json"

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Need to set up credentials via API key or OAuth
            api_key = os.environ.get("YOUTUBE_API_KEY")
            if not api_key:
                logger.error("YOUTUBE_API_KEY environment variable not set")
                raise RuntimeError("YOUTUBE_API_KEY required")
            return build("youtube", "v3", developerKey=api_key)

        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def fetch_video_ids(youtube, channel_id: str, max_results: int = 10) -> List[str]:
    """Fetch latest video IDs from channel."""
    try:
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            order="date",
            maxResults=max_results,
            type="video",
        )
        response = request.execute()
        return [item["id"]["videoId"] for item in response.get("items", [])]
    except HttpError as e:
        logger.error(f"Failed to fetch videos: {e}")
        return []


def fetch_comments(youtube, video_id: str, published_after: Optional[str] = None) -> List[Dict]:
    """Fetch comments from a video."""
    comments = []
    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        textFormat="plainText",
        maxResults=100,
        publishedAfter=published_after,
        order="relevance",
    )

    try:
        while request:
            response = request.execute()

            for item in response.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append(
                    {
                        "video_id": video_id,
                        "author": comment["authorDisplayName"],
                        "text": comment["textDisplay"],
                        "timestamp": comment["publishedAt"],
                        "comment_id": comment["parentId"],
                    }
                )

            if "nextPageToken" in response:
                request = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    textFormat="plainText",
                    maxResults=100,
                    publishedAfter=published_after,
                    order="relevance",
                    pageToken=response["nextPageToken"],
                )
            else:
                break
    except HttpError as e:
        logger.error(f"Failed to fetch comments: {e}")

    return comments


def log_comment(comment: Dict, category: int, response_status: str):
    """Log comment to JSONL file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "comment_timestamp": comment["timestamp"],
        "commenter": comment["author"],
        "text": comment["text"],
        "category": category,
        "response_status": response_status,
        "video_id": comment["video_id"],
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def reply_to_comment(youtube, parent_id: str, text: str) -> bool:
    """Post a reply to a comment."""
    try:
        request = youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": parent_id,
                    "textOriginal": text,
                }
            },
        )
        request.execute()
        logger.info(f"Replied to comment {parent_id}")
        return True
    except HttpError as e:
        logger.error(f"Failed to reply to comment: {e}")
        return False


def run_monitor():
    """Main monitoring loop."""
    logger.info("Starting YouTube comment monitor...")

    try:
        youtube = get_youtube_service()
    except RuntimeError as e:
        logger.error(str(e))
        return

    state = load_state()
    last_check = state.get("last_check")
    published_after = None

    if last_check:
        published_after = last_check
    else:
        # First run: check last 24 hours
        published_after = (datetime.utcnow() - timedelta(hours=24)).isoformat() + "Z"

    run_stats = {
        "comments_processed": 0,
        "auto_responses": 0,
        "flagged_for_review": 0,
    }

    try:
        video_ids = fetch_video_ids(youtube, CHANNEL_ID)
        if not video_ids:
            logger.warning("No videos found")
            return

        for video_id in video_ids:
            comments = fetch_comments(youtube, video_id, published_after)

            for comment in comments:
                category = categorize_comment(comment["text"])
                response_status = "pending"

                if category in [1, 2]:
                    # Auto-respond
                    response_text = RESPONSES[category]
                    if reply_to_comment(youtube, comment["comment_id"], response_text):
                        response_status = "auto-responded"
                        run_stats["auto_responses"] += 1
                elif category == 4:
                    # Flag for review
                    response_status = "flagged"
                    run_stats["flagged_for_review"] += 1

                log_comment(comment, category, response_status)
                run_stats["comments_processed"] += 1

    except Exception as e:
        logger.error(f"Monitor error: {e}")
        return

    # Update state
    state["last_check"] = datetime.utcnow().isoformat() + "Z"
    state["total_processed"] += run_stats["comments_processed"]
    state["total_responses"] += run_stats["auto_responses"]
    state["total_flagged"] += run_stats["flagged_for_review"]
    save_state(state)

    # Print summary
    print("\n" + "=" * 60)
    print("YOUTUBE COMMENT MONITOR SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"\nThis Run:")
    print(f"  Comments processed: {run_stats['comments_processed']}")
    print(f"  Auto-responses sent: {run_stats['auto_responses']}")
    print(f"  Flagged for review: {run_stats['flagged_for_review']}")
    print(f"\nCumulative:")
    print(f"  Total processed: {state['total_processed']}")
    print(f"  Total responses: {state['total_responses']}")
    print(f"  Total flagged: {state['total_flagged']}")
    print("=" * 60 + "\n")

    logger.info("Monitor run complete")


if __name__ == "__main__":
    run_monitor()
