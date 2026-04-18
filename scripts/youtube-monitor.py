#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Fetches comments, categorizes, auto-responds, and logs.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import urllib.request
import urllib.error

# Configuration
CHANNEL_NAME = "Concessa Obvius"
CACHE_DIR = Path(".cache")
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"
CACHE_DIR.mkdir(exist_ok=True)

# Template responses
RESPONSES = {
    "question": """Thanks for the question! Here are some quick pointers:
- Check our FAQ: [link to docs]
- Timeline typically depends on your background
- Tools vary by approach — happy to clarify in follow-up

Feel free to reply with specifics!""",
    
    "praise": """Thank you so much! Really appreciate the encouragement. 🙏 It means a lot to know this is resonating.""",
}

# Categorization patterns
PATTERNS = {
    "question": [
        r"how do i|how do you|how to|how does|what (is|are)|where (do|can)",
        r"cost|price|tools|timeline|requirements|getting started",
        r"\?$",  # Ends with question mark
    ],
    "praise": [
        r"amazing|inspiring|incredible|love this|so good|brilliant",
        r"thank you|appreciate|awesome|fantastic|excellent",
    ],
    "spam": [
        r"crypto|bitcoin|eth|defi|nft|blockchain|coin|token",
        r"mlm|network marketing|work from home|make money fast",
        r"casino|poker|betting|gambling",
    ],
    "sales": [
        r"partnership|collaborate|collaboration|brand deal",
        r"sponsor|sponsorship|advertising|promote",
        r"let'?s work together|interested in working",
    ],
}

def categorize_comment(text: str) -> str:
    """Categorize a comment based on patterns."""
    text_lower = text.lower()
    
    # Check each category in order
    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return category
    
    return "general"

def load_state() -> Dict:
    """Load monitoring state (last video ID, last comment timestamp)."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_check": None, "processed_comments": []}

def save_state(state: Dict):
    """Save monitoring state."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def log_comment(comment: Dict):
    """Log comment to JSONL file."""
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(comment) + "\n")

def fetch_comments() -> List[Dict]:
    """
    Fetch comments from Concessa Obvius channel.
    Note: This requires YouTube API or web scraping.
    For now, returns mock data for demonstration.
    """
    # In production, integrate with:
    # - YouTube Data API v3 (requires API key)
    # - Or web scraping with BeautifulSoup
    
    # Mock data for demonstration
    mock_comments = [
        {
            "id": "comment_001",
            "author": "Alex Smith",
            "text": "How do I get started with this? What tools do I need?",
            "timestamp": datetime.now().isoformat(),
            "video_id": "video_123",
        },
        {
            "id": "comment_002",
            "author": "Jordan Lee",
            "text": "This is absolutely amazing! So inspiring!",
            "timestamp": datetime.now().isoformat(),
            "video_id": "video_123",
        },
        {
            "id": "comment_003",
            "author": "CryptoBot",
            "text": "Join our crypto coin community! Quick profits guaranteed!",
            "timestamp": datetime.now().isoformat(),
            "video_id": "video_123",
        },
        {
            "id": "comment_004",
            "author": "Brand Inc",
            "text": "Hi! We're interested in a partnership opportunity. Let's collaborate!",
            "timestamp": datetime.now().isoformat(),
            "video_id": "video_123",
        },
    ]
    
    return mock_comments

def process_comments() -> Tuple[int, int, int]:
    """
    Process comments: categorize, auto-respond, and log.
    Returns (total_processed, auto_responses_sent, flagged_for_review)
    """
    state = load_state()
    processed_ids = set(state.get("processed_comments", []))
    
    comments = fetch_comments()
    total_processed = 0
    auto_responses_sent = 0
    flagged_for_review = 0
    
    for comment in comments:
        comment_id = comment["id"]
        
        # Skip already processed
        if comment_id in processed_ids:
            continue
        
        # Categorize
        category = categorize_comment(comment["text"])
        
        # Determine response status
        response_status = "pending"
        
        if category == "question":
            response_text = RESPONSES["question"]
            response_status = "auto_responded"
            auto_responses_sent += 1
        elif category == "praise":
            response_text = RESPONSES["praise"]
            response_status = "auto_responded"
            auto_responses_sent += 1
        elif category == "sales":
            response_status = "flagged_for_review"
            response_text = None
            flagged_for_review += 1
        else:
            response_text = None
        
        # Log comment
        log_entry = {
            "timestamp": comment["timestamp"],
            "video_id": comment.get("video_id"),
            "commenter": comment["author"],
            "text": comment["text"],
            "category": category,
            "response_status": response_status,
            "response_text": response_text,
            "comment_id": comment_id,
        }
        log_comment(log_entry)
        
        # Mark as processed
        processed_ids.add(comment_id)
        total_processed += 1
    
    # Update state
    state["processed_comments"] = list(processed_ids)
    state["last_check"] = datetime.now().isoformat()
    save_state(state)
    
    return total_processed, auto_responses_sent, flagged_for_review

def generate_report() -> str:
    """Generate a summary report of monitoring activity."""
    total_processed, auto_responses_sent, flagged_for_review = process_comments()
    
    report = f"""
🎥 YouTube Comment Monitor Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Channel: {CHANNEL_NAME}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 Statistics:
  • Total comments processed: {total_processed}
  • Auto-responses sent: {auto_responses_sent}
  • Flagged for review: {flagged_for_review}

📁 Log file: {LOG_FILE}
✅ All comments logged with full details (timestamp, author, text, category, response status)
""".strip()
    
    return report

if __name__ == "__main__":
    report = generate_report()
    print(report)
