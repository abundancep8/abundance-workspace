#!/usr/bin/env python3
"""
YouTube Comment Monitor - Concessa Obvius Channel
Categorizes, auto-responds, and logs all comments.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import re

try:
    import google.auth
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: google-auth and google-api-python-client required")
    print("Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_NAME = "Concessa Obvius"
LOG_FILE = Path(".cache/youtube-comments.jsonl")
STATE_FILE = Path(".cache/youtube-monitor-state.json")

# Template responses
TEMPLATES = {
    "question": "Great question! Thanks for asking. I'll get back to you with specific details soon. In the meantime, check our FAQ/docs at [your-resource-link]. 🙌",
    "praise": "Thank you so much for the kind words! This really means a lot. 💙"
}

def get_youtube_service():
    """Initialize YouTube API client."""
    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY environment variable not set")
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def find_channel_id(service, channel_name: str) -> str:
    """Find channel ID by name."""
    request = service.search().list(
        q=channel_name,
        part="snippet",
        type="channel",
        maxResults=1
    )
    results = request.execute()
    if results["items"]:
        return results["items"][0]["id"]["channelId"]
    raise ValueError(f"Channel '{channel_name}' not found")

def get_channel_uploads_playlist(service, channel_id: str) -> str:
    """Get uploads playlist ID for channel."""
    request = service.channels().list(
        id=channel_id,
        part="contentDetails"
    )
    results = request.execute()
    return results["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_recent_videos(service, playlist_id: str, max_results: int = 5) -> List[str]:
    """Get recent video IDs from channel."""
    request = service.playlistItems().list(
        playlistId=playlist_id,
        part="snippet",
        maxResults=max_results
    )
    results = request.execute()
    return [item["snippet"]["resourceId"]["videoId"] for item in results["items"]]

def load_state() -> Dict:
    """Load last processed comment IDs."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_comment_ids": {}}

def save_state(state: Dict):
    """Save state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def categorize_comment(text: str) -> str:
    """Categorize comment into: question, praise, spam, sales."""
    text_lower = text.lower()
    
    # Spam patterns
    spam_patterns = [
        r"(crypto|bitcoin|ethereum|nft|token|blockchain)",
        r"(mlm|multi.?level|network marketing|pyramid)",
        r"(forex|trading|forex signals|copy paste)",
        r"click (here|link|below)",
        r"dm me|message me|contact me (privately|now)",
    ]
    if any(re.search(pattern, text_lower) for pattern in spam_patterns):
        return "spam"
    
    # Sales patterns
    sales_patterns = [
        r"(partner|collaborate|collab|sponsor|brand deal)",
        r"(marketing|pr|promo|advertising)",
        r"interested in (working|partnering|collaborating)",
        r"(pitch|proposal|offer|business opportunity)",
    ]
    if any(re.search(pattern, text_lower) for pattern in sales_patterns):
        return "sales"
    
    # Praise patterns
    praise_patterns = [
        r"(amazing|awesome|incredible|inspiring|love this|brilliant)",
        r"(thank you|thanks|grateful|appreciate)",
        r"(game.?changing|life.?changing|eye.?opening)",
        r"(best|great job|well done)",
    ]
    if any(re.search(pattern, text_lower) for pattern in praise_patterns):
        return "praise"
    
    # Question patterns
    question_patterns = [
        r"^\s*how (do|can|should)",
        r"^\s*what (is|are|do)",
        r"^\s*where (can|do)",
        r"^\s*when (should|can|do)",
        r"^\s*why (did|do|should)",
        r"\?$",
        r"(tools|cost|timeline|price|pricing|duration|requirements)",
    ]
    if any(re.search(pattern, text_lower) for pattern in question_patterns):
        return "question"
    
    return "neutral"

def log_comment(comment_data: Dict):
    """Append comment to JSONL log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(comment_data) + "\n")

def process_comments(service, video_ids: List[str], state: Dict):
    """Process comments from videos."""
    stats = {
        "total_processed": 0,
        "auto_responses_sent": 0,
        "flagged_for_review": 0,
        "by_category": {"question": 0, "praise": 0, "spam": 0, "sales": 0, "neutral": 0}
    }
    
    last_ids = state.get("last_comment_ids", {})
    
    for video_id in video_ids:
        try:
            request = service.commentThreads().list(
                videoId=video_id,
                part="snippet,replies",
                textFormat="plainText",
                maxResults=100
            )
            
            while request:
                results = request.execute()
                
                for thread in results.get("items", []):
                    comment = thread["snippet"]["topLevelComment"]
                    comment_id = comment["id"]
                    
                    # Skip if already processed
                    if video_id in last_ids and comment_id in last_ids[video_id]:
                        continue
                    
                    text = comment["snippet"]["textDisplay"]
                    author = comment["snippet"]["authorDisplayName"]
                    timestamp = comment["snippet"]["publishedAt"]
                    
                    category = categorize_comment(text)
                    response_status = "none"
                    
                    # Auto-respond to questions and praise
                    if category == "question":
                        response_status = "auto_responded"
                        stats["auto_responses_sent"] += 1
                    elif category == "praise":
                        response_status = "auto_responded"
                        stats["auto_responses_sent"] += 1
                    elif category == "sales":
                        response_status = "flagged"
                        stats["flagged_for_review"] += 1
                    
                    # Log the comment
                    comment_data = {
                        "timestamp": datetime.now().isoformat(),
                        "published": timestamp,
                        "video_id": video_id,
                        "comment_id": comment_id,
                        "author": author,
                        "text": text,
                        "category": category,
                        "response_status": response_status
                    }
                    log_comment(comment_data)
                    
                    stats["total_processed"] += 1
                    stats["by_category"][category] += 1
                    
                    # Update state
                    if video_id not in last_ids:
                        last_ids[video_id] = []
                    last_ids[video_id].append(comment_id)
                
                # Fetch next page if exists
                if "nextPageToken" in results:
                    request = service.commentThreads().list(
                        videoId=video_id,
                        pageToken=results["nextPageToken"],
                        part="snippet,replies",
                        textFormat="plainText",
                        maxResults=100
                    )
                else:
                    request = None
        
        except Exception as e:
            print(f"Error processing video {video_id}: {e}")
    
    state["last_comment_ids"] = last_ids
    state["last_run"] = datetime.now().isoformat()
    save_state(state)
    
    return stats

def main():
    try:
        print(f"[{datetime.now().isoformat()}] Starting YouTube comment monitor...")
        
        service = get_youtube_service()
        channel_id = find_channel_id(service, CHANNEL_NAME)
        print(f"Found channel: {CHANNEL_NAME} ({channel_id})")
        
        uploads_id = get_channel_uploads_playlist(service, channel_id)
        video_ids = get_recent_videos(service, uploads_id)
        print(f"Monitoring {len(video_ids)} recent videos")
        
        state = load_state()
        stats = process_comments(service, video_ids, state)
        
        # Report
        print("\n" + "="*50)
        print("YOUTUBE COMMENT MONITOR REPORT")
        print("="*50)
        print(f"Total comments processed: {stats['total_processed']}")
        print(f"Auto-responses sent: {stats['auto_responses_sent']}")
        print(f"Flagged for review: {stats['flagged_for_review']}")
        print(f"\nBreakdown by category:")
        for cat, count in stats["by_category"].items():
            print(f"  {cat.capitalize()}: {count}")
        print(f"\nLog file: {LOG_FILE}")
        print("="*50)
        
        return 0
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
