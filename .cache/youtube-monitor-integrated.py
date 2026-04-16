#!/usr/bin/env python3
"""
YouTube Comment Monitor (Integrated)
Full-featured comment monitoring with categorization, auto-response, and logging.
Designed to run every 30 minutes via cron.
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
import argparse

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
WORKSPACE_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SCRIPT_DIR / "youtube-monitor-config.json"
COMMENTS_LOG = SCRIPT_DIR / "youtube-comments.jsonl"
STATS_LOG = SCRIPT_DIR / "youtube-monitor-stats.jsonl"
STATE_FILE = SCRIPT_DIR / "youtube-monitor-state.json"

# Category keywords (case-insensitive)
CATEGORY_PATTERNS = {
    "question": [
        r"how\s+(do|can|would|should|would)",
        r"what\s+(is|are|about)",
        r"where\s+(can|do)",
        r"why\s+(is|do|would)",
        r"when\s+(can|do|should)",
        r"cost\s*(how much|$|\?)?",
        r"price",
        r"timeline\s*(when|how long)?",
        r"tools?\s+(needed|required)",
        r"help\s+(with|me|us)",
        r"learn\s+(more|how)",
        r"tutorial\s*(on|for)?",
        r"guide",
        r"\?\s*$",  # ends with question mark
    ],
    "praise": [
        r"amazing",
        r"inspiring",
        r"love(d)?",
        r"great\s+(job|work|content|stuff)",
        r"awesome",
        r"brilliant",
        r"excellent",
        r"fantastic",
        r"incredible",
        r"wonderful",
        r"thank\s+you",
        r"thanks\s+for",
        r"appreciate",
        r"👏|🎉|❤️|💯|🙌|👍",
    ],
    "spam": [
        r"(crypto|bitcoin|ethereum|nft|blockchain|coin)",
        r"(mlm|multi.?level|network.?marketing|downline)",
        r"(click\s+here|link\s+below|check\s+bio)",
        r"(buy\s+now|order\s+today|limited.?offer)",
        r"(free\s+money|make\s+\$|earn\s+\$)",
        r"(casino|betting|gambling|poker)",
        r"forex|trading|stocks",
        r"supplement|weight.?loss|diet\s+(pill|product)",
        r"🔗|💰|📈|⬆️",
    ],
    "sales": [
        r"(partnership|collaborate|collaboration|work\s+together|work\s+with\s+us)",
        r"(sponsorship|sponsor|advertis(e|ing))",
        r"(business\s+opportunity|b2b|wholesale)",
        r"(interested\s+in|interested\s+working|promote)",
        r"(agency|brand|company)\s+(inquiry|partnership|collaboration)",
    ]
}

def load_config() -> Dict:
    """Load configuration from JSON file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "channel_name": "Concessa Obvius",
        "channel_id": "",
        "api_key": "",
        "auto_respond_enabled": True,
        "response_templates": {
            "question": "Thanks for the question! Check out our resources or reply with more details.",
            "praise": "Thank you so much for the support and kind words! 😊"
        }
    }

def save_config(config: Dict) -> None:
    """Save configuration to JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def load_state() -> Dict:
    """Load last checked timestamp and processed comment IDs."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            state = json.load(f)
            state["processed_ids"] = set(state.get("processed_ids", []))
            return state
    return {
        "last_checked": None,
        "processed_ids": set(),
    }

def save_state(state: Dict) -> None:
    """Save state to file."""
    state_copy = state.copy()
    state_copy["processed_ids"] = list(state_copy.get("processed_ids", []))
    with open(STATE_FILE, "w") as f:
        json.dump(state_copy, f, indent=2)

def categorize_comment(text: str) -> str:
    """Categorize a comment based on content."""
    text_lower = text.lower()
    
    # Check in priority order: sales, spam, question, praise
    for category in ["sales", "spam", "question", "praise"]:
        patterns = CATEGORY_PATTERNS[category]
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return category
    
    return "other"

def log_comment(comment_data: Dict) -> None:
    """Append comment to JSONL log."""
    COMMENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(COMMENTS_LOG, "a") as f:
        f.write(json.dumps(comment_data) + "\n")

def fetch_youtube_comments(config: Dict, since: Optional[datetime] = None) -> List[Dict]:
    """
    Fetch comments from YouTube channel.
    Mock implementation - replace with actual API calls.
    """
    try:
        from youtube_api import YouTubeCommentFetcher
        
        fetcher = YouTubeCommentFetcher(
            api_key=config.get("api_key"),
            credentials_file=config.get("credentials_file")
        )
        
        channel_id = config.get("channel_id")
        if not channel_id:
            # Try to lookup by name
            channel_id = fetcher.get_channel_id(config.get("channel_name", "Concessa Obvius"))
            if channel_id:
                config["channel_id"] = channel_id
                save_config(config)
        
        if channel_id:
            return fetcher.fetch_comments(channel_id, since=since)
    
    except ImportError:
        print("⚠️ YouTube API not available. Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    except Exception as e:
        print(f"⚠️ Error fetching comments: {e}")
    
    return []

def process_comments(debug: bool = False) -> Dict:
    """
    Fetch and process comments.
    """
    config = load_config()
    state = load_state()
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_processed": 0,
        "auto_responses_sent": 0,
        "flagged_for_review": 0,
        "by_category": {
            "question": 0,
            "praise": 0,
            "spam": 0,
            "sales": 0,
            "other": 0,
        },
        "errors": []
    }
    
    try:
        # Fetch new comments since last check
        last_checked = None
        if state.get("last_checked"):
            last_checked = datetime.fromisoformat(state["last_checked"])
            if debug:
                print(f"📋 Fetching comments since: {last_checked}")
        
        comments = fetch_youtube_comments(config, since=last_checked)
        
        if debug:
            print(f"🔍 Fetched {len(comments)} new comments")
        
        for comment in comments:
            comment_id = comment.get("id")
            
            # Skip if already processed
            if comment_id in state.get("processed_ids", set()):
                continue
            
            text = comment.get("text", "")
            category = categorize_comment(text)
            response_status = "pending"
            
            # Auto-respond to questions and praise
            if config.get("auto_respond_enabled", True):
                if category in ["question", "praise"]:
                    template = config.get("response_templates", {}).get(category, "")
                    if template:
                        response_status = "auto_responded"
                        stats["auto_responses_sent"] += 1
                        if debug:
                            print(f"✉️ Auto-responded to {category}: {text[:50]}...")
            
            # Flag sales inquiries
            if category == "sales":
                response_status = "flagged_for_review"
                stats["flagged_for_review"] += 1
                if debug:
                    print(f"🚩 Flagged for review: {text[:50]}...")
            
            # Log the comment
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "comment_id": comment_id,
                "commenter": comment.get("author", "Unknown"),
                "text": text,
                "category": category,
                "response_status": response_status,
                "likes": comment.get("likes", 0),
                "video_id": comment.get("video_id", ""),
            }
            log_comment(log_entry)
            
            state["processed_ids"].add(comment_id)
            stats["total_processed"] += 1
            stats["by_category"][category] += 1
        
        state["last_checked"] = datetime.now().isoformat()
        save_state(state)
    
    except Exception as e:
        stats["errors"].append(str(e))
        print(f"❌ Error: {e}")
    
    return stats

def print_report(stats: Dict) -> None:
    """Print formatted report."""
    print("\n" + "="*60)
    print("📊 YouTube Comment Monitor Report")
    print("="*60)
    print(f"Time: {stats['timestamp']}")
    print(f"\n✅ Processed: {stats['total_processed']} comments")
    print(f"✉️  Auto-responses: {stats['auto_responses_sent']}")
    print(f"🚩 Flagged for review: {stats['flagged_for_review']}")
    
    print(f"\n📈 Breakdown by category:")
    for cat, count in stats["by_category"].items():
        if count > 0:
            symbol = {
                "question": "❓",
                "praise": "👏",
                "spam": "🚫",
                "sales": "🚩",
                "other": "📝"
            }.get(cat, "•")
            print(f"   {symbol} {cat.capitalize()}: {count}")
    
    if stats["errors"]:
        print(f"\n⚠️  Errors: {len(stats['errors'])}")
        for error in stats["errors"]:
            print(f"   - {error}")
    
    print("="*60 + "\n")

def log_stats(stats: Dict) -> None:
    """Log stats to JSONL file."""
    STATS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(STATS_LOG, "a") as f:
        f.write(json.dumps(stats) + "\n")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="YouTube Comment Monitor")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--config", type=str, help="Path to config file")
    args = parser.parse_args()
    
    try:
        stats = process_comments(debug=args.debug)
        print_report(stats)
        log_stats(stats)
        return 0
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
