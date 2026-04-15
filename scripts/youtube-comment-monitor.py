#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Monitors for new comments, categorizes, auto-responds, and logs.
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import google.oauth2.credentials
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configuration
WORKSPACE = Path("/Users/abundance/.openclaw/workspace")
SECRETS_DIR = WORKSPACE / ".secrets"
CACHE_DIR = WORKSPACE / ".cache"
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / ".youtube-monitor-state.json"

# YouTube API
YOUTUBE_API_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CHANNEL_NAME = "Concessa Obvius"  # Will be queried to get channel ID

# Response templates
RESPONSE_TEMPLATES = {
    "question": """Thanks for the question! 🎯

{question_summary}

For detailed answers and resources, visit our help center or feel free to reach out. We're here to help!

—Concessa Team""",
    
    "praise": """Thank you so much for the kind words! 🙏 We're thrilled you found this valuable. Comments like yours keep us motivated to keep creating great content. 

—Concessa Team""",
}

# Category patterns
PATTERNS = {
    "question": {
        "keywords": r"(?:how|what|when|where|why|which|can i|do i|should i|help|question|need|looking for|cost|price|timeline|tools|start)",
        "weight": 0.8
    },
    "praise": {
        "keywords": r"(?:amazing|awesome|incredible|inspiring|love|great|brilliant|thanks|thank you|so helpful|exactly what|perfect)",
        "weight": 0.8
    },
    "spam": {
        "keywords": r"(?:crypto|bitcoin|ethereum|nft|mlm|pyramid|forex|trading bot|click here|dm me|link in bio|free money|guaranteed profit|work from home)",
        "weight": 0.9
    },
    "sales": {
        "keywords": r"(?:partnership|collaboration|sponsorship|advertise|promote|affiliate|business opportunity|marketing|promotion|brand deal)",
        "weight": 0.7
    }
}


def load_state():
    """Load last-checked timestamp."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_check": None, "processed_comment_ids": []}


def save_state(state):
    """Save state for next run."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_youtube_service():
    """Authenticate and return YouTube API service."""
    token_path = SECRETS_DIR / "youtube-token.json"
    creds_path = SECRETS_DIR / "youtube-credentials.json"
    
    creds = None
    
    # Try loading existing token
    if token_path.exists():
        try:
            creds = google.oauth2.credentials.Credentials.from_authorized_user_file(
                str(token_path), YOUTUBE_API_SCOPES
            )
            
            # Try to refresh if expired
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    with open(token_path, "w") as f:
                        f.write(creds.to_json())
                except Exception as refresh_err:
                    print(f"⚠️  Token refresh failed: {refresh_err}")
                    creds = None
        except Exception as e:
            print(f"⚠️  Token load failed: {e}")
            creds = None
    
    # Full auth flow if no valid creds (requires interactive terminal)
    if not creds or not creds.valid:
        print("⚠️  Re-authenticating with YouTube API...")
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(creds_path), YOUTUBE_API_SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open(token_path, "w") as f:
                f.write(creds.to_json())
            print("✓ Authentication successful")
        except Exception as e:
            raise RuntimeError(f"YouTube authentication failed: {e}")
    
    return build("youtube", "v3", credentials=creds)


def get_channel_id(youtube, channel_name):
    """Find channel ID by name."""
    request = youtube.search().list(
        q=channel_name,
        type="channel",
        part="id",
        maxResults=1
    )
    response = request.execute()
    
    if response["items"]:
        return response["items"][0]["id"]["channelId"]
    raise ValueError(f"Channel '{channel_name}' not found")


def fetch_new_comments(youtube, channel_id, last_check_time, processed_ids):
    """Fetch comments since last check."""
    # Get uploads playlist ID
    channel_req = youtube.channels().list(
        id=channel_id,
        part="contentDetails"
    )
    channel_resp = channel_req.execute()
    uploads_playlist_id = channel_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    # Get recent videos
    videos_req = youtube.playlistItems().list(
        playlistId=uploads_playlist_id,
        part="contentDetails",
        maxResults=10
    )
    videos_resp = videos_req.execute()
    video_ids = [item["contentDetails"]["videoId"] for item in videos_resp.get("items", [])]
    
    new_comments = []
    
    # Fetch comments from each video
    for video_id in video_ids:
        comments_req = youtube.commentThreads().list(
            videoId=video_id,
            part="snippet",
            maxResults=100,
            textFormat="plainText",
            order="relevance"
        )
        
        while comments_req:
            comments_resp = comments_req.execute()
            
            for item in comments_resp.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comment_id = item["id"]
                
                # Skip if already processed
                if comment_id in processed_ids:
                    continue
                
                # Parse comment time
                published_at = datetime.fromisoformat(
                    comment["publishedAt"].replace("Z", "+00:00")
                )
                
                # Skip if before last check (if set)
                if last_check_time:
                    last_check_dt = datetime.fromisoformat(last_check_time.replace("Z", "+00:00"))
                    if published_at < last_check_dt:
                        continue
                
                new_comments.append({
                    "comment_id": comment_id,
                    "video_id": video_id,
                    "author": comment["authorDisplayName"],
                    "text": comment["textDisplay"],
                    "timestamp": comment["publishedAt"],
                    "author_channel_url": comment.get("authorChannelUrl", ""),
                })
            
            # Fetch next page if available
            comments_req = youtube.commentThreads().list_next(comments_req, comments_resp) if "nextPageToken" in comments_resp else None
    
    return new_comments


def categorize_comment(text):
    """Categorize a comment based on patterns."""
    text_lower = text.lower()
    scores = {}
    
    for category, pattern_info in PATTERNS.items():
        if re.search(pattern_info["keywords"], text_lower):
            scores[category] = pattern_info["weight"]
        else:
            scores[category] = 0
    
    # Assign category with highest score, or default to "general"
    if scores:
        top_category = max(scores, key=scores.get)
        if scores[top_category] > 0:
            return top_category
    
    return "general"


def generate_response(category, comment_text):
    """Generate auto-response if applicable."""
    if category == "question":
        # Extract question summary
        question_match = re.search(r"^[^?]+\??", comment_text)
        question_summary = (question_match.group(0) if question_match else comment_text[:100]).strip()
        return RESPONSE_TEMPLATES["question"].format(question_summary=question_summary)
    
    elif category == "praise":
        return RESPONSE_TEMPLATES["praise"]
    
    return None


def post_reply(youtube, parent_comment_id, reply_text):
    """Post a reply to a comment."""
    try:
        request = youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "textOriginal": reply_text,
                    "parentId": parent_comment_id
                }
            }
        )
        response = request.execute()
        return response["id"]
    except Exception as e:
        print(f"Error posting reply: {e}")
        return None


def log_comment(comment_data, category, response_id=None):
    """Log comment to JSONL file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "comment_id": comment_data["comment_id"],
        "video_id": comment_data["video_id"],
        "commenter": comment_data["author"],
        "text": comment_data["text"],
        "category": category,
        "response_status": "auto_replied" if response_id else "flagged" if category == "sales" else "logged",
        "response_id": response_id,
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return log_entry


def generate_report(processed_count, auto_responses, flagged):
    """Generate summary report."""
    report = f"""
📊 YouTube Comment Monitor Report
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Pacific)

📈 Statistics:
  • Total comments processed: {processed_count}
  • Auto-responses sent: {auto_responses}
  • Flagged for review (sales): {flagged}
  • Net logged: {processed_count - auto_responses - flagged}

🔄 Next check: In 30 minutes

Log file: {LOG_FILE}
"""
    return report


def main():
    """Main monitoring loop."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting YouTube comment monitor...")
    
    try:
        # Initialize
        youtube = get_youtube_service()
        state = load_state()
        channel_id = get_channel_id(youtube, CHANNEL_NAME)
        
        print(f"  Channel ID: {channel_id}")
        
        # Fetch new comments
        new_comments = fetch_new_comments(
            youtube,
            channel_id,
            state.get("last_check"),
            state.get("processed_comment_ids", [])
        )
        
        print(f"  Found {len(new_comments)} new comments")
        
        if not new_comments:
            print("  No new comments to process. Done.")
            return
        
        # Process each comment
        auto_response_count = 0
        flagged_count = 0
        
        for comment in new_comments:
            category = categorize_comment(comment["text"])
            response_id = None
            
            # Auto-respond to questions and praise
            if category in ["question", "praise"]:
                response_text = generate_response(category, comment["text"])
                if response_text:
                    response_id = post_reply(youtube, comment["comment_id"], response_text)
                    if response_id:
                        auto_response_count += 1
                        print(f"  ✓ Auto-replied to {category}: {comment['author']}")
            
            # Flag sales for manual review
            if category == "sales":
                flagged_count += 1
                print(f"  ⚠️  Flagged for review (sales): {comment['author']}")
            
            # Log comment
            log_comment(comment, category, response_id)
            
            # Update processed IDs
            state["processed_comment_ids"].append(comment["comment_id"])
        
        # Save state
        state["last_check"] = datetime.utcnow().isoformat() + "Z"
        save_state(state)
        
        # Generate and print report
        report = generate_report(len(new_comments), auto_response_count, flagged_count)
        print(report)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitor complete.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
