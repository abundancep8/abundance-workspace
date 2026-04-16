#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
Monitors comments every 30 minutes, categorizes, and auto-responds.
Runs in DEMO mode by default (no YouTube API key needed).
Set YOUTUBE_MODE=production in environment to use real API.
"""

import json
import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import hashlib

# Configuration
CHANNEL_NAME = "Concessa Obvius"
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
LOG_DIR = WORKSPACE_DIR / ".cache"
LOG_FILE = LOG_DIR / "youtube-comments.jsonl"
STATE_FILE = LOG_DIR / "youtube-comment-state.json"
REPORT_FILE = LOG_DIR / "youtube-comments-report.txt"

# Mode: "demo" or "production"
MODE = os.environ.get("YOUTUBE_MODE", "demo")

# Template responses
TEMPLATES = {
    "questions": [
        "Thanks for the question! I'm actively working on more details about this. Stay tuned for updates! 🚀",
        "Great question! This is something I'm exploring. Happy to chat more about it soon.",
        "Love your curiosity! I'll share more info about this soon. Keep an eye out!",
        "Thanks for asking! I'll reach out with more info soon. In the meantime, feel free to check out our recent content.",
        "Great question! Thanks for your interest. I'll have more details about this soon. In the meantime, check out our resources and FAQs!",
    ],
    "praise": [
        "So grateful for this! Your support means the world. 🙏",
        "Thank you! This kind of feedback keeps me going.",
        "Appreciate the kind words! More good stuff coming soon.",
        "So grateful for this! Your support keeps us going. 🚀",
        "This means the world! 💕 Thanks for being part of the community.",
        "Thank you so much for the kind words! 🙏 Really appreciate your support and engagement.",
    ]
}

class CommentAnalyzer:
    """Categorize comments into questions, praise, spam, or sales."""
    
    # Keywords for categorization
    QUESTION_KEYWORDS = {
        "how", "what", "when", "where", "why", "can i", "do you", "is it", "will it",
        "timeline", "cost", "pricing", "tools", "start", "begin", "learn", "teach",
        "question", "wondering", "curious", "confused", "help"
    }
    
    PRAISE_KEYWORDS = {
        "amazing", "awesome", "great", "excellent", "love", "inspired", "inspiring",
        "brilliant", "fantastic", "wonderful", "impressed", "thank you",
        "thanks", "appreciate", "good job", "well done", "well-explained"
    }
    
    SPAM_KEYWORDS = {
        "crypto", "bitcoin", "ethereum", "forex", "trading", "mlm", "network marketing",
        "money", "earn $", "click here", "limited offer", "dm me", "contact me",
        "buy now", "limited time", "guaranteed", "free money"
    }
    
    SALES_KEYWORDS = {
        "partnership", "collaboration", "partner", "collaborate", "business",
        "opportunity", "connect", "work together", "let's talk", "reach out",
        "interested in", "would love to", "b2b", "agency", "sponsor"
    }
    
    @classmethod
    def categorize(cls, text: str) -> str:
        """Categorize comment into: questions, praise, spam, or sales."""
        text_lower = text.lower()
        
        # Check spam first (most aggressive filtering)
        if any(keyword in text_lower for keyword in cls.SPAM_KEYWORDS):
            return "spam"
        
        # Check sales
        if any(keyword in text_lower for keyword in cls.SALES_KEYWORDS):
            return "sales"
        
        # Check questions (contains question marks or question words)
        if "?" in text or any(keyword in text_lower for keyword in cls.QUESTION_KEYWORDS):
            return "questions"
        
        # Check praise
        if any(keyword in text_lower for keyword in cls.PRAISE_KEYWORDS):
            return "praise"
        
        # Default to praise (neutral/positive)
        return "praise"


# Demo data generator
DEMO_COMMENTS = [
    {"author": "Alex Martinez", "text": "This is absolutely brilliant and inspiring! Amazing work on this project. So impressed!", "type": "praise"},
    {"author": "Jordan Chen", "text": "How do I get started with this? What tools do I need to begin?", "type": "questions"},
    {"author": "Casey Williams", "text": "What's the timeline for implementation? When can I start?", "type": "questions"},
    {"author": "Tech Enthusiast", "text": "Love your content! This approach is fantastic and really well-explained. Thank you for sharing!", "type": "praise"},
    {"author": "Sam Rodriguez", "text": "BUY CRYPTO NOW!!! Limited offer, DM me for details", "type": "spam"},
    {"author": "Morgan Park", "text": "Hi! Love your content. Would love to explore a partnership opportunity with you. Let's connect!", "type": "sales"},
    {"author": "Taylor Johnson", "text": "How can I implement something similar? What's the cost and timeline?", "type": "questions"},
    {"author": "Riley Davis", "text": "This is absolutely amazing! So inspiring and well done. Really appreciate the insights!", "type": "praise"},
]


def generate_demo_comments(state: Dict) -> List[Dict]:
    """Generate demo comments that haven't been processed yet."""
    comments = []
    processed_ids = set(state.get("processed_comment_ids", []))
    
    # Randomly select 1-3 comments to "receive" this cycle
    num_new = random.randint(1, 3)
    selected = random.sample(DEMO_COMMENTS, min(num_new, len(DEMO_COMMENTS)))
    
    for i, demo in enumerate(selected):
        # Create consistent ID based on timestamp + content
        timestamp = datetime.utcnow()
        comment_id = f"demo_{i}_{hashlib.md5((demo['text'] + str(timestamp)).encode()).hexdigest()[:8]}"
        
        # Skip if already processed
        if comment_id in processed_ids:
            continue
        
        comments.append({
            "comment_id": comment_id,
            "video_id": f"video_{i}",
            "timestamp": timestamp.isoformat(),
            "author": demo["author"],
            "text": demo["text"],
            "replies_count": random.randint(0, 5)
        })
    
    return comments


def load_state() -> Dict:
    """Load the state of processed comments."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "last_run": None,
        "processed_comment_ids": [],
        "total_processed_lifetime": 0,
        "total_auto_replied_lifetime": 0,
        "total_flagged_lifetime": 0,
    }


def save_state(state: Dict):
    """Save the state of processed comments."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, default=str)


def log_comment(comment: Dict, category: str, response_status: str, response_text: str = ""):
    """Log comment to JSONL file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "comment_id": comment["comment_id"],
        "video_id": comment["video_id"],
        "commenter": comment["author"],
        "text": comment["text"],
        "category": category,
        "response_status": response_status,
        "template_response": response_text,
        "run_time": datetime.utcnow().isoformat(),
    }
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def run_monitor():
    """Run the monitoring cycle."""
    print(f"\n[{datetime.utcnow().isoformat()}] Starting YouTube Comment Monitor")
    print(f"Mode: {MODE.upper()}")
    print(f"Channel: {CHANNEL_NAME}")
    
    session_stats = {
        "total_processed": 0,
        "auto_replied": 0,
        "flagged_for_review": 0,
        "spam_filtered": 0,
        "errors": []
    }
    
    try:
        # Load state
        state = load_state()
        print(f"✓ State loaded (tracked {len(state.get('processed_comment_ids', []))} comments)")
        
        # Generate or fetch comments
        if MODE == "demo":
            comments = generate_demo_comments(state)
            print(f"✓ Generated {len(comments)} demo comments")
        else:
            print(f"✗ Production mode requires YouTube API OAuth setup")
            print(f"  Set credentials at: ~/.openclaw/workspace/.secrets/youtube-credentials.json")
            return False
        
        # Process each comment
        for comment in comments:
            session_stats["total_processed"] += 1
            
            # Categorize
            category = CommentAnalyzer.categorize(comment["text"])
            
            # Determine response
            response_status = "processed"
            response_text = ""
            
            if category == "questions":
                response_text = random.choice(TEMPLATES["questions"])
                response_status = "auto_responded"
                session_stats["auto_replied"] += 1
                print(f"  ✓ Q: {comment['author'][:20]}... → auto-responded")
            
            elif category == "praise":
                response_text = random.choice(TEMPLATES["praise"])
                response_status = "auto_responded"
                session_stats["auto_replied"] += 1
                print(f"  ✓ P: {comment['author'][:20]}... → auto-responded")
            
            elif category == "spam":
                response_status = "blocked"
                session_stats["spam_filtered"] += 1
                print(f"  ✗ S: {comment['author'][:20]}... → spam (ignored)")
            
            elif category == "sales":
                response_status = "flagged_for_review"
                session_stats["flagged_for_review"] += 1
                print(f"  ⚠ Sales: {comment['author'][:20]}... → flagged")
            
            # Log the comment
            log_comment(comment, category, response_status, response_text)
            
            # Update state
            state["processed_comment_ids"].append(comment["comment_id"])
        
        # Update lifetime stats
        state["last_run"] = datetime.utcnow().isoformat()
        state["total_processed_lifetime"] = state.get("total_processed_lifetime", 0) + session_stats["total_processed"]
        state["total_auto_replied_lifetime"] = state.get("total_auto_replied_lifetime", 0) + session_stats["auto_replied"]
        state["total_flagged_lifetime"] = state.get("total_flagged_lifetime", 0) + session_stats["flagged_for_review"]
        state["last_checked"] = datetime.utcnow().isoformat()
        
        # Save state
        save_state(state)
        
        # Generate report
        generate_report(session_stats, state)
        
        print("\n✓ Monitor run completed successfully")
        return True
    
    except Exception as e:
        session_stats["errors"].append(str(e))
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        generate_report(session_stats, {})
        return False


def generate_report(session_stats: Dict, state: Dict):
    """Generate a summary report."""
    report = f"""YouTube Comment Monitor Report
Generated: {datetime.utcnow().isoformat()}
Channel: Concessa Obvius
Mode: {MODE.upper()}

=== THIS SESSION ===
Total Comments Processed: {session_stats["total_processed"]}
Auto-Responses Sent: {session_stats["auto_replied"]}
Spam Filtered: {session_stats.get("spam_filtered", 0)}
Flagged for Review: {session_stats["flagged_for_review"]}

=== LIFETIME STATS ===
Total Processed (All Time): {state.get("total_processed_lifetime", 0)}
Total Auto-Replied (All Time): {state.get("total_auto_replied_lifetime", 0)}
Total Flagged (All Time): {state.get("total_flagged_lifetime", 0)}

=== STATUS ===
Last Run: {state.get("last_run", "Never")}
Total Comments Tracked: {len(state.get("processed_comment_ids", []))}
"""
    
    if session_stats["errors"]:
        report += f"\n=== ERRORS ===\n"
        for error in session_stats["errors"]:
            report += f"- {error}\n"
    
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, 'w') as f:
        f.write(report)
    
    print(report)


if __name__ == "__main__":
    success = run_monitor()
    sys.exit(0 if success else 1)
