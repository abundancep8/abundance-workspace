"""YouTube Comment Monitor Helper Module

Provides classification, auto-response templating, and logging functions.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Classification keywords
KEYWORDS = {
    "QUESTION": ["how", "tools", "cost", "timeline", "where", "what", "can i", "do i", "should i", "help", "?"],
    "PRAISE": ["amazing", "inspiring", "love", "great", "awesome", "incredible", "thank you", "thanks", "brilliant", "excellent"],
    "SPAM": ["crypto", "nft", "bitcoin", "mlm", "affiliate", "click here", "link in bio", "casino", "poker", "forex"],
    "SALES": ["partnership", "collaboration", "sponsorship", "promote", "interested in working", "brand deal", "sponsor"]
}

# Auto-response templates
RESPONSE_TEMPLATES = {
    "QUESTION": "Thanks for the great question! Check our FAQ or feel free to ask for specifics. We're here to help! 🙌",
    "PRAISE": "Thank you so much! We're thrilled this resonated with you. Your support means everything! 🙏",
    "SALES": "[Flagged for review]",  # No auto-response for SALES
    "SPAM": "[Skipped]"  # No auto-response for SPAM
}


def classify_comment(text: str) -> str:
    """Classify a comment into QUESTION, PRAISE, SPAM, or SALES.
    
    Args:
        text: The comment text to classify
        
    Returns:
        One of: QUESTION, PRAISE, SPAM, SALES
    """
    text_lower = text.lower()
    
    # Check SPAM first (high priority to filter)
    for keyword in KEYWORDS["SPAM"]:
        if keyword in text_lower:
            return "SPAM"
    
    # Check SALES (high priority for manual review)
    for keyword in KEYWORDS["SALES"]:
        if keyword in text_lower:
            return "SALES"
    
    # Check QUESTION
    for keyword in KEYWORDS["QUESTION"]:
        if keyword in text_lower:
            return "QUESTION"
    
    # Check PRAISE
    for keyword in KEYWORDS["PRAISE"]:
        if keyword in text_lower:
            return "PRAISE"
    
    # Default: treat as PRAISE if none match
    return "PRAISE"


def get_response_text(category: str) -> str:
    """Get auto-response text for a category.
    
    Args:
        category: One of QUESTION, PRAISE, SALES, SPAM
        
    Returns:
        The response text or None if no auto-response for this category
    """
    return RESPONSE_TEMPLATES.get(category)


def should_respond(category: str) -> bool:
    """Determine if we should auto-respond to this category.
    
    Args:
        category: One of QUESTION, PRAISE, SALES, SPAM
        
    Returns:
        True if we should auto-respond, False otherwise
    """
    return category in ["QUESTION", "PRAISE"]


def log_comment(
    timestamp: str,
    comment_id: str,
    commenter: str,
    text: str,
    category: str,
    response_status: str = "pending",
    response_text: Optional[str] = None,
    log_file: str = ".cache/youtube-comments.jsonl"
) -> bool:
    """Log a comment to the JSONL file.
    
    Args:
        timestamp: ISO format timestamp
        comment_id: Unique comment ID from YouTube
        commenter: Commenter name
        text: Comment text
        category: Classification category
        response_status: "pending", "sent", "skipped", "flagged"
        response_text: The response text if sent
        log_file: Path to JSONL log file
        
    Returns:
        True if logged successfully, False otherwise
    """
    try:
        record = {
            "timestamp": timestamp,
            "comment_id": comment_id,
            "commenter": commenter,
            "text": text,
            "category": category,
            "response_status": response_status,
            "response_text": response_text
        }
        
        # Ensure .cache directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Append to JSONL (each line is a JSON object)
        with open(log_file, "a") as f:
            f.write(json.dumps(record) + "\n")
        
        return True
    except Exception as e:
        print(f"Error logging comment {comment_id}: {e}")
        return False


def read_comments_log(log_file: str = ".cache/youtube-comments.jsonl") -> List[Dict]:
    """Read all logged comments from JSONL file.
    
    Args:
        log_file: Path to JSONL log file
        
    Returns:
        List of comment records
    """
    records = []
    
    if not Path(log_file).exists():
        return records
    
    try:
        with open(log_file, "r") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    except Exception as e:
        print(f"Error reading log file: {e}")
    
    return records


def load_state(state_file: str = ".cache/youtube-monitor-state.json") -> Dict:
    """Load monitor state.
    
    Args:
        state_file: Path to state JSON file
        
    Returns:
        State dict with keys: last_check, last_comment_id, processed_count
    """
    if not Path(state_file).exists():
        return {
            "last_check": None,
            "last_comment_id": None,
            "processed_count": 0
        }
    
    try:
        with open(state_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading state: {e}")
        return {
            "last_check": None,
            "last_comment_id": None,
            "processed_count": 0
        }


def save_state(state: Dict, state_file: str = ".cache/youtube-monitor-state.json") -> bool:
    """Save monitor state.
    
    Args:
        state: State dict
        state_file: Path to state JSON file
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        Path(state_file).parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving state: {e}")
        return False


def get_stats(log_file: str = ".cache/youtube-comments.jsonl") -> Dict:
    """Get statistics from the comments log.
    
    Args:
        log_file: Path to JSONL log file
        
    Returns:
        Dict with stats: total, by_category, responses_sent
    """
    comments = read_comments_log(log_file)
    
    stats = {
        "total": len(comments),
        "by_category": {
            "QUESTION": 0,
            "PRAISE": 0,
            "SALES": 0,
            "SPAM": 0
        },
        "responses_sent": 0
    }
    
    for comment in comments:
        category = comment.get("category", "PRAISE")
        if category in stats["by_category"]:
            stats["by_category"][category] += 1
        
        if comment.get("response_status") == "sent":
            stats["responses_sent"] += 1
    
    return stats
