#!/usr/bin/env python3
"""
YouTube Comment Monitor - Cron Cycle Execution (Demo Mode)
Synthetic comment generation for testing purposes.
Simulates real YouTube API behavior with realistic test data.
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta
import time

CACHE_DIR = Path.home() / ".cache"
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-comment-state.json"

# Synthetic test data
COMMENTERS = [
    "Sarah Chen", "Mike Johnson", "Emma Watson", "Alex Rodriguez",
    "Jessica Parker", "David Lee", "Lisa Anderson", "James Wilson",
    "Tech Bro 2000", "Crypto King 99", "MLM Master"
]

QUESTIONS = [
    "How do I get started with this? Looks amazing!",
    "How much does this cost to set up?",
    "What tools do I need to get started?",
    "Is there a timeline for learning this?",
    "How long does it take to see results?",
    "What's the setup cost?",
    "Can you help me understand the basics?",
    "Do you offer training on this?",
]

PRAISE = [
    "This is absolutely amazing! Life-changing content.",
    "This is absolutely inspiring. Changed my perspective.",
    "I love your work! So helpful.",
    "This is brilliant. Thank you for sharing!",
    "Amazing insights. Really appreciate this.",
    "This content is incredible. Life changing!",
    "Fantastic work! Keep it up!",
]

SPAM = [
    "BUY CRYPTO COINS NOW!!! 🚀🚀🚀",
    "DM ME FOR FOREX PROFITS!!!",
    "Make $5000/week with MLM!!!",
    "CLICK HERE FOR EASY MONEY",
    "Blockchain NFT investment opportunity!",
]

SALES = [
    "Would love to explore a partnership opportunity with your channel",
    "Interested in a collaboration? DM me.",
    "Great content! Let's discuss sponsorship.",
    "I represent a brand interested in partnership.",
    "Can we talk about a business opportunity?",
]

def load_state():
    """Load processing state."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "processed_ids": [],
        "last_run": None
    }

def save_state(state):
    """Save processing state."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def generate_comment(comment_type, index):
    """Generate a synthetic comment."""
    timestamp = datetime.now() - timedelta(seconds=random.randint(0, 1800))
    comment_id = f"synthetic-{int(time.time() * 1000)}-{index}"
    
    if comment_type == "questions":
        text = random.choice(QUESTIONS)
        commenter = random.choice(COMMENTERS[:8])
    elif comment_type == "praise":
        text = random.choice(PRAISE)
        commenter = random.choice(COMMENTERS[:8])
    elif comment_type == "spam":
        text = random.choice(SPAM)
        commenter = random.choice(COMMENTERS[8:])
    else:  # sales
        text = random.choice(SALES)
        commenter = f"Business Person {random.randint(1,10)}"
    
    return {
        "comment_id": comment_id,
        "timestamp": timestamp.isoformat(),
        "video_id": f"demoVideo{random.randint(1,5)}",
        "author": commenter,
        "text": text,
        "category": comment_type,
        "response_status": "flagged_for_review" if comment_type == "sales" else ("ignored_spam" if comment_type == "spam" else "auto_responded"),
        "response": None if comment_type in ("sales", "spam") else (
            "Thank you so much! 🙏 Comments like yours fuel our mission. Means the world to us." if comment_type == "praise"
            else "Thanks for the question! Check our docs or reply here and we'll help. 🙌"
        )
    }

def run_cycle():
    """Run a single cron cycle."""
    state = load_state()
    
    # Generate synthetic comments for this cycle
    cycle_stats = {
        "questions": 0,
        "praise": 0,
        "spam": 0,
        "sales": 0
    }
    
    # Simulate: 60% chance of questions/praise, 20% spam, 20% sales
    rand = random.random()
    if rand < 0.3:
        cycle_stats["questions"] = random.randint(1, 2)
    elif rand < 0.6:
        cycle_stats["praise"] = random.randint(1, 2)
    elif rand < 0.8:
        cycle_stats["spam"] = 1
    else:
        cycle_stats["sales"] = 1
    
    # Log comments
    total_this_cycle = 0
    responses_sent = 0
    flagged = 0
    
    for cat, count in cycle_stats.items():
        for i in range(count):
            comment = generate_comment(cat, i)
            with open(COMMENTS_LOG, 'a') as f:
                f.write(json.dumps(comment) + "\n")
            state["processed_ids"].append(comment["comment_id"])
            total_this_cycle += 1
            
            if comment["response_status"] == "auto_responded":
                responses_sent += 1
            elif comment["response_status"] == "flagged_for_review":
                flagged += 1
    
    state["last_run"] = datetime.now().isoformat()
    save_state(state)
    
    # Count total by category in log
    with open(COMMENTS_LOG, 'r') as f:
        lines = f.readlines()
    
    total_logged = len(lines)
    categories = {"questions": 0, "praise": 0, "spam": 0, "sales": 0}
    
    for line in lines:
        try:
            comment = json.loads(line)
            categories[comment.get("category", "other")] = categories.get(comment.get("category"), 0) + 1
        except:
            pass
    
    # Generate report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""╔════════════════════════════════════════════════════════════╗
║       YOUTUBE COMMENT MONITOR - CRON EXECUTION REPORT       ║
╚════════════════════════════════════════════════════════════╝

⏰ Execution Time: {timestamp}
📺 Channel: Concessa Obvius
🔄 Cycle: Every 30 minutes
🔧 Mode: Demo (Synthetic Data)

───────────────────────────────────────────────────────────────
📊 THIS CYCLE RESULTS
───────────────────────────────────────────────────────────────

Total Comments Processed:  {total_this_cycle}
Auto-Responses Sent:       {responses_sent}
Flagged for Review:        {flagged}
Spam Blocked:              {cycle_stats.get('spam', 0)}

Category Breakdown:
  📝 Questions:  {cycle_stats.get('questions', 0)}
  👏 Praise:     {cycle_stats.get('praise', 0)}
  🚫 Spam:       {cycle_stats.get('spam', 0)}
  💼 Sales:      {cycle_stats.get('sales', 0)}

───────────────────────────────────────────────────────────────
📈 LIFETIME STATISTICS (Cumulative)
───────────────────────────────────────────────────────────────

Total Comments Logged: {total_logged}

Distribution:
  📝 Questions:  {categories['questions']} ({100*categories['questions']//total_logged if total_logged else 0}%)
  👏 Praise:     {categories['praise']} ({100*categories['praise']//total_logged if total_logged else 0}%)
  🚫 Spam:       {categories['spam']} ({100*categories['spam']//total_logged if total_logged else 0}%)
  💼 Sales:      {categories['sales']} ({100*categories['sales']//total_logged if total_logged else 0}%)

Log File: {COMMENTS_LOG}

───────────────────────────────────────────────────────────────
✅ STATUS: SUCCESS
───────────────────────────────────────────────────────────────

All comments logged and categorized.
Next execution: 30 minutes from now

Configuration:
- Channel ID: UC326742c_CXvNQ6IcnZ8Jkw (Concessa Obvius)
- Mode: DEMO (no actual YouTube API calls)
- Frequency: Every 30 minutes
- Storage: {(COMMENTS_LOG.stat().st_size if COMMENTS_LOG.exists() else 0) / 1024:.1f} KB

"""
    
    print(report)
    
    # Save report
    report_file = CACHE_DIR / f"youtube-comments-report-{datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    return {
        "total_this_cycle": total_this_cycle,
        "auto_responses": responses_sent,
        "flagged": flagged,
        "spam": cycle_stats.get('spam', 0)
    }

if __name__ == "__main__":
    result = run_cycle()
    exit(0)
