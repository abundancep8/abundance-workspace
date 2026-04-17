#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Fetches, categorizes, and auto-responds to comments
"""

import os
import json
import sys
from datetime import datetime, timedelta
import requests
from pathlib import Path

# Configuration
CACHE_DIR = Path(".cache")
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
PROCESSED_FILE = CACHE_DIR / "youtube-processed.json"
ERRORS_LOG = CACHE_DIR / "youtube-errors.log"
REPORT_FILE = CACHE_DIR / f"youtube-report-{datetime.now().isoformat().replace(':', '-')}.txt"

CHANNEL_NAME = "Concessa Obvius"
API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"

# Category definitions
CATEGORIES = {
    1: "Questions",
    2: "Praise",
    3: "Spam",
    4: "Sales"
}

# Template responses
TEMPLATES = {
    1: "Thanks for the question! Check our FAQ at https://concessa.obvius.io/faq or reply with specifics.",
    2: "Thank you so much! Really appreciate the support 🙏"
}

# Keyword mappings for categorization
CATEGORY_KEYWORDS = {
    1: ["how", "how to", "tutorial", "tool", "cost", "price", "timeline", "startup", "where", "what", "when", "help", "question", "?"],
    2: ["amazing", "inspiring", "great", "love", "awesome", "excellent", "fantastic", "brilliant", "wonderful", "thanks", "thank you", "appreciated", "👏", "🙌", "❤️"],
    3: ["crypto", "bitcoin", "nft", "mlm", "multi-level", "blackhat", "hack", "get rich quick", "guaranteed", "dm for details", "click here", "spam", "scam"],
    4: ["partnership", "collaborate", "sponsorship", "business inquiry", "inquiry", "business opportunity", "let's work together", "interested in", "collaboration"]
}


def log_error(message: str):
    """Log error to errors log file"""
    CACHE_DIR.mkdir(exist_ok=True)
    with open(ERRORS_LOG, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")
    print(f"❌ ERROR: {message}", file=sys.stderr)


def get_channel_id(channel_name: str) -> str:
    """Get channel ID from channel name"""
    if not API_KEY:
        log_error("YOUTUBE_API_KEY environment variable is not set")
        sys.exit(1)
    
    try:
        response = requests.get(
            f"{YOUTUBE_API_URL}/search",
            params={
                "part": "snippet",
                "q": channel_name,
                "type": "channel",
                "key": API_KEY,
                "maxResults": 1
            }
        )
        
        if response.status_code != 200:
            log_error(f"YouTube API error: {response.status_code} - {response.text}")
            sys.exit(1)
        
        data = response.json()
        if not data.get("items"):
            log_error(f"Channel '{channel_name}' not found")
            sys.exit(1)
        
        return data["items"][0]["id"]["channelId"]
    except Exception as e:
        log_error(f"Failed to fetch channel ID: {str(e)}")
        sys.exit(1)


def get_uploads_playlist_id(channel_id: str) -> str:
    """Get uploads playlist ID from channel ID"""
    try:
        response = requests.get(
            f"{YOUTUBE_API_URL}/channels",
            params={
                "part": "contentDetails",
                "id": channel_id,
                "key": API_KEY
            }
        )
        
        if response.status_code != 200:
            log_error(f"YouTube API error: {response.status_code}")
            sys.exit(1)
        
        data = response.json()
        return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except Exception as e:
        log_error(f"Failed to fetch uploads playlist: {str(e)}")
        sys.exit(1)


def get_recent_videos(playlist_id: str, minutes: int = 30) -> list:
    """Get recent videos from channel (from last N minutes)"""
    try:
        response = requests.get(
            f"{YOUTUBE_API_URL}/playlistItems",
            params={
                "part": "snippet,contentDetails",
                "playlistId": playlist_id,
                "key": API_KEY,
                "maxResults": 50
            }
        )
        
        if response.status_code != 200:
            log_error(f"YouTube API error: {response.status_code}")
            sys.exit(1)
        
        data = response.json()
        videos = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        for item in data.get("items", []):
            published = item["contentDetails"]["videoPublishedAt"]
            pub_time = datetime.fromisoformat(published.replace("Z", "+00:00"))
            
            if pub_time >= cutoff_time:
                videos.append(item["snippet"]["resourceId"]["videoId"])
        
        return videos
    except Exception as e:
        log_error(f"Failed to fetch recent videos: {str(e)}")
        return []


def get_comments(video_id: str) -> list:
    """Get all comments from a video"""
    try:
        comments = []
        next_page = None
        
        while True:
            params = {
                "part": "snippet",
                "videoId": video_id,
                "key": API_KEY,
                "maxResults": 100,
                "textFormat": "plainText",
                "order": "relevance"
            }
            
            if next_page:
                params["pageToken"] = next_page
            
            response = requests.get(
                f"{YOUTUBE_API_URL}/commentThreads",
                params=params
            )
            
            if response.status_code != 200:
                log_error(f"YouTube API error fetching comments: {response.status_code}")
                break
            
            data = response.json()
            
            for item in data.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "id": item["id"],
                    "commenter": comment["authorDisplayName"],
                    "text": comment["textDisplay"],
                    "timestamp": comment["publishedAt"],
                    "channel_id": comment["authorChannelId"]["value"] if comment.get("authorChannelId") else None
                })
            
            next_page = data.get("nextPageToken")
            if not next_page:
                break
        
        return comments
    except Exception as e:
        log_error(f"Failed to fetch comments from {video_id}: {str(e)}")
        return []


def categorize_comment(text: str) -> int:
    """Categorize comment based on keywords (1-4)"""
    text_lower = text.lower()
    
    # Check spam first (usually most specific)
    for keyword in CATEGORY_KEYWORDS[3]:
        if keyword.lower() in text_lower:
            return 3
    
    # Check sales
    for keyword in CATEGORY_KEYWORDS[4]:
        if keyword.lower() in text_lower:
            return 4
    
    # Check questions
    for keyword in CATEGORY_KEYWORDS[1]:
        if keyword.lower() in text_lower:
            return 1
    
    # Check praise
    for keyword in CATEGORY_KEYWORDS[2]:
        if keyword.lower() in text_lower:
            return 2
    
    # Default to other/questions if unclear
    return 1


def load_processed_comments() -> set:
    """Load set of already-processed comment IDs"""
    if PROCESSED_FILE.exists():
        try:
            with open(PROCESSED_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("comment_ids", []))
        except:
            return set()
    return set()


def save_processed_comments(comment_ids: set):
    """Save processed comment IDs"""
    CACHE_DIR.mkdir(exist_ok=True)
    with open(PROCESSED_FILE, "w") as f:
        json.dump({"comment_ids": list(comment_ids)}, f, indent=2)


def respond_to_comment(comment_id: str, text: str) -> bool:
    """Post a reply to a comment"""
    try:
        response = requests.post(
            f"{YOUTUBE_API_URL}/comments",
            params={
                "part": "snippet",
                "key": API_KEY
            },
            json={
                "snippet": {
                    "textOriginal": text,
                    "parentId": comment_id
                }
            }
        )
        
        return response.status_code == 200
    except Exception as e:
        log_error(f"Failed to post reply to {comment_id}: {str(e)}")
        return False


def log_comment(comment_data: dict):
    """Log comment to JSONL file"""
    CACHE_DIR.mkdir(exist_ok=True)
    with open(COMMENTS_LOG, "a") as f:
        f.write(json.dumps(comment_data) + "\n")


def main():
    print(f"🎬 YouTube Comment Monitor for {CHANNEL_NAME}")
    print(f"Started: {datetime.now().isoformat()}\n")
    
    # Verify API key
    if not API_KEY:
        log_error("YOUTUBE_API_KEY environment variable is not set")
        sys.exit(1)
    
    # Create cache directory
    CACHE_DIR.mkdir(exist_ok=True)
    
    # Get channel ID
    print("📺 Finding channel...")
    channel_id = get_channel_id(CHANNEL_NAME)
    print(f"✅ Found channel: {channel_id}\n")
    
    # Get uploads playlist
    print("📋 Fetching uploads playlist...")
    playlist_id = get_uploads_playlist_id(channel_id)
    print(f"✅ Uploads playlist: {playlist_id}\n")
    
    # Get recent videos
    print("🎥 Fetching recent videos (last 30 minutes)...")
    video_ids = get_recent_videos(playlist_id)
    print(f"✅ Found {len(video_ids)} recent videos\n")
    
    if not video_ids:
        print("⚠️  No recent videos found. Exiting.")
        print_report({})
        return
    
    # Load processed comments
    processed = load_processed_comments()
    
    # Process comments
    stats = {
        "total_processed": 0,
        "by_category": {1: 0, 2: 0, 3: 0, 4: 0},
        "auto_responded": {1: 0, 2: 0},
        "flagged_for_review": 0,
        "spam_filtered": 0,
        "errors": 0
    }
    
    print("📝 Processing comments...\n")
    
    for video_id in video_ids:
        comments = get_comments(video_id)
        
        for comment in comments:
            comment_id = comment["id"]
            
            # Skip if already processed
            if comment_id in processed:
                continue
            
            # Categorize
            category = categorize_comment(comment["text"])
            stats["by_category"][category] += 1
            stats["total_processed"] += 1
            
            # Determine response status
            response_status = "skipped"
            
            if category == 1 or category == 2:
                # Auto-respond
                template = TEMPLATES[category]
                if respond_to_comment(comment_id, template):
                    response_status = "sent"
                    stats["auto_responded"][category] += 1
                else:
                    response_status = "skipped"
                    stats["errors"] += 1
            elif category == 4:
                # Flag for manual review
                response_status = "flagged"
                stats["flagged_for_review"] += 1
            elif category == 3:
                # Spam - skip
                response_status = "skipped"
                stats["spam_filtered"] += 1
            
            # Log comment
            log_entry = {
                "timestamp": comment["timestamp"],
                "comment_id": comment_id,
                "commenter": comment["commenter"],
                "text": comment["text"],
                "category": category,
                "response_status": response_status
            }
            log_comment(log_entry)
            
            # Mark as processed
            processed.add(comment_id)
            
            print(f"  [{CATEGORIES[category]}] {comment['commenter']}: {comment['text'][:60]}...")
    
    # Save processed comments
    save_processed_comments(processed)
    
    print("\n✅ Processing complete.\n")
    print_report(stats)


def print_report(stats: dict):
    """Generate and print report"""
    report = f"""
╔════════════════════════════════════════════════════════════════════╗
║          YouTube Comment Monitor Report                            ║
║          Channel: {CHANNEL_NAME}{''.ljust(27 - len(CHANNEL_NAME))}║
║          {datetime.now().isoformat()}{' ' * (32 - len(datetime.now().isoformat()))}║
╚════════════════════════════════════════════════════════════════════╝

📊 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Comments Processed:      {stats.get('total_processed', 0)}

📂 CATEGORIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Questions (1):               {stats.get('by_category', {}).get(1, 0)}
  Praise (2):                  {stats.get('by_category', {}).get(2, 0)}
  Spam (3):                    {stats.get('by_category', {}).get(3, 0)}
  Sales Inquiries (4):         {stats.get('by_category', {}).get(4, 0)}

🤖 AUTO-RESPONSES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Sent to Questions:           {stats.get('auto_responded', {}).get(1, 0)}
  Sent to Praise:              {stats.get('auto_responded', {}).get(2, 0)}
  Total Auto-Responses:        {sum(stats.get('auto_responded', {}).values())}

🚨 MANUAL REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Flagged for Review:          {stats.get('flagged_for_review', 0)}

⚠️  FILTERING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Spam Filtered:               {stats.get('spam_filtered', 0)}

🔧 SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Errors:                      {stats.get('errors', 0)}
  Comments Log:                {COMMENTS_LOG}
  Processed Log:               {PROCESSED_FILE}
  Errors Log:                  {ERRORS_LOG}

────────────────────────────────────────────────────────────────────
Report generated: {datetime.now().isoformat()}
    """
    
    print(report)
    
    # Save report to file
    CACHE_DIR.mkdir(exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    
    print(f"📄 Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
