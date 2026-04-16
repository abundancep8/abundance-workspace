#!/usr/bin/env python3
"""
YouTube Comment Monitor
Monitors Concessa Obvius channel for new comments, categorizes, auto-responds, and logs.
Run every 30 minutes via cron.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Optional

# Ensure cache directory exists
CACHE_DIR = Path(__file__).parent.absolute()
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"

# Templates for auto-responses
RESPONSE_TEMPLATES = {
    "question": """Thank you for the question! Here are some resources that might help:
- Check our FAQ: [link to FAQ]
- Getting started guide: [link]
- Feel free to reply with more questions!""",
    
    "praise": """Thank you so much for the kind words! We really appreciate your support and feedback. 😊"""
}

# Category keywords (case-insensitive)
CATEGORY_PATTERNS = {
    "question": [
        r"how\s+(do|can|would|should)",
        r"what\s+(is|are|about)",
        r"where\s+(can|do)",
        r"why\s+(is|do)",
        r"cost\s*(how much|$|\?)",
        r"price",
        r"timeline\s*(when|how long)",
        r"tools?\s+(needed|required)",
        r"help\s+(with|me)",
        r"\?",  # ends with question mark
    ],
    "praise": [
        r"amazing",
        r"inspiring",
        r"love(d)?",
        r"great\s+(job|work|content)",
        r"awesome",
        r"brilliant",
        r"excellent",
        r"fantastic",
        r"incredible",
        r"thank\s+you",
        r"👏|🎉|❤️|💯",
    ],
    "spam": [
        r"(crypto|bitcoin|ethereum|nft|blockchain)",
        r"(mlm|multi.?level|network.?marketing)",
        r"(click\s+here|link\s+below|check\s+bio)",
        r"(buy\s+now|order\s+today|limited.?offer)",
        r"(free\s+money|make\s+money\s+fast)",
        r"(casino|betting|gambling)",
        r"🔗|💰|📈",
    ],
    "sales": [
        r"(partnership|collaborate|collaboration|work\s+with)",
        r"(sponsorship|advertis(e|ing))",
        r"(business\s+opportunity|promote)",
        r"interested\s+in\s+(working|partnering)",
    ]
}

def categorize_comment(text: str) -> str:
    """Categorize a comment based on content."""
    text_lower = text.lower()
    
    # Check in order: sales, spam, question, praise, default to "other"
    for category in ["sales", "spam", "question", "praise"]:
        patterns = CATEGORY_PATTERNS[category]
        if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in patterns):
            return category
    
    return "other"

def load_state() -> dict:
    """Load last checked timestamp and processed comment IDs."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "last_checked": None,
        "processed_ids": set(),
    }

def save_state(state: dict) -> None:
    """Save state to file."""
    # Convert set to list for JSON serialization
    state_copy = state.copy()
    state_copy["processed_ids"] = list(state_copy.get("processed_ids", []))
    with open(STATE_FILE, "w") as f:
        json.dump(state_copy, f, indent=2)

def log_comment(comment_data: dict) -> None:
    """Append comment to JSONL log."""
    COMMENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(COMMENTS_LOG, "a") as f:
        f.write(json.dumps(comment_data) + "\n")

def process_comments() -> dict:
    """
    Fetch and process comments. In production, this would call YouTube API.
    For now, returns mock data structure.
    """
    state = load_state()
    state["processed_ids"] = set(state.get("processed_ids", []))
    
    stats = {
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
        "timestamp": datetime.now().isoformat(),
    }
    
    # TODO: Replace with actual YouTube API call
    # For now, mock implementation shows the structure
    mock_comments = []
    
    for comment in mock_comments:
        comment_id = comment.get("id")
        if comment_id in state["processed_ids"]:
            continue  # Already processed
        
        text = comment.get("text", "")
        category = categorize_comment(text)
        response_status = "pending"
        
        # Auto-respond to questions and praise
        if category in ["question", "praise"]:
            # In production, would call YouTube API to post reply
            response_status = "auto_responded"
            stats["auto_responses_sent"] += 1
        
        # Flag sales inquiries
        if category == "sales":
            response_status = "flagged_for_review"
            stats["flagged_for_review"] += 1
        
        # Log the comment
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "comment_id": comment_id,
            "commenter": comment.get("author", "Unknown"),
            "text": text,
            "category": category,
            "response_status": response_status,
        }
        log_comment(log_entry)
        
        state["processed_ids"].add(comment_id)
        stats["total_processed"] += 1
        stats["by_category"][category] += 1
    
    state["last_checked"] = datetime.now().isoformat()
    save_state(state)
    
    return stats

def main():
    """Run the monitor."""
    try:
        stats = process_comments()
        
        # Print report
        print(f"\n📊 YouTube Comment Monitor Report")
        print(f"Time: {stats['timestamp']}")
        print(f"\nTotal comments processed: {stats['total_processed']}")
        print(f"Auto-responses sent: {stats['auto_responses_sent']}")
        print(f"Flagged for review: {stats['flagged_for_review']}")
        print(f"\nBreakdown by category:")
        for cat, count in stats["by_category"].items():
            print(f"  {cat.capitalize()}: {count}")
        
        # Log stats
        stats_file = CACHE_DIR / "youtube-monitor-stats.jsonl"
        with open(stats_file, "a") as f:
            f.write(json.dumps(stats) + "\n")
        
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
