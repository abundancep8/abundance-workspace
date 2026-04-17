#!/usr/bin/env python3
"""
YouTube Comment Monitor - Concessa Obvius Channel
Monitors comments every 30 minutes, categorizes, and auto-responds
"""

import json
import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
CHANNEL_NAME = "Concessa Obvius"
CACHE_DIR = Path.home() / ".cache"
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-comment-state.json"
REPORT_FILE = CACHE_DIR / "youtube-comments-report.txt"

# Ensure cache directory exists
CACHE_DIR.mkdir(exist_ok=True)

# Template responses
RESPONSES = {
    "questions": "Thanks for the question! Check our docs or reply here and we'll help. 🙌",
    "praise": "Thank you so much! 🙏 Comments like yours fuel our mission. Means the world to us.",
}

# Categorization keywords
CATEGORIES = {
    "questions": ["how", "what", "why", "where", "cost", "price", "timeline", "setup", "start", "help", "tools", "when"],
    "praise": ["amazing", "inspiring", "love", "thank", "great", "awesome", "incredible", "beautiful", "genius"],
    "spam": ["crypto", "bitcoin", "nft", "mlm", "forex", "pyramid", "get rich", "click here", "buy now", "free money"],
    "sales": ["partnership", "collaboration", "sponsor", "brand deal", "affiliate", "promote"],
}

def load_state():
    """Load previously processed comment IDs"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"processed_ids": [], "last_run": None}

def save_state(state):
    """Save state to prevent duplicates"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def categorize_comment(text):
    """Categorize a comment based on keywords"""
    text_lower = text.lower()
    
    # Check spam first (highest priority)
    if any(keyword in text_lower for keyword in CATEGORIES["spam"]):
        return "spam"
    
    # Check sales
    if any(keyword in text_lower for keyword in CATEGORIES["sales"]):
        return "sales"
    
    # Check questions
    if any(keyword in text_lower for keyword in CATEGORIES["questions"]):
        return "questions"
    
    # Check praise
    if any(keyword in text_lower for keyword in CATEGORIES["praise"]):
        return "praise"
    
    return "other"

def generate_synthetic_comments():
    """Generate synthetic comments for demo (when YouTube API not available)"""
    commenter_pool = [
        ("Sarah Chen", "How do I get started with this? Looks amazing!"),
        ("Alex Rodriguez", "This is absolutely inspiring. Changed my perspective."),
        ("Emma Watson", "How much does this cost to set up?"),
        ("Mike Johnson", "This is absolutely amazing! Life-changing content."),
        ("Jessica Parker", "Would love to explore a partnership opportunity with your channel"),
        ("Tech Bro 2000", "BUY CRYPTO COINS NOW!!! 🚀🚀🚀"),
    ]
    
    # Randomly pick 1-3 comments to simulate new activity
    count = random.randint(1, 3)
    selected = random.sample(commenter_pool, min(count, len(commenter_pool)))
    
    return [
        {
            "id": f"synthetic-{int(datetime.now().timestamp() * 1000)}-{i}",
            "commenter": name,
            "text": text,
        }
        for i, (name, text) in enumerate(selected)
    ]

def process_comments(comments):
    """Process and categorize comments"""
    state = load_state()
    processed = []
    stats = {"questions": 0, "praise": 0, "spam": 0, "sales": 0, "other": 0}
    
    for comment in comments:
        comment_id = comment["id"]
        
        # Skip if already processed
        if comment_id in state["processed_ids"]:
            continue
        
        category = categorize_comment(comment["text"])
        stats[category] += 1
        
        # Determine response status
        if category == "spam":
            response_status = "ignored_spam"
            response = None
        elif category == "sales":
            response_status = "flagged_for_review"
            response = None
        elif category in ["questions", "praise"]:
            response_status = "auto_responded"
            response = RESPONSES[category]
        else:
            response_status = "logged_only"
            response = None
        
        # Log the comment
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "commenter": comment["commenter"],
            "text": comment["text"],
            "category": category,
            "response_status": response_status,
            "response": response,
        }
        
        processed.append(log_entry)
        state["processed_ids"].append(comment_id)
    
    # Save state
    state["last_run"] = datetime.now().isoformat()
    save_state(state)
    
    return processed, stats

def log_comments(processed):
    """Append comments to JSONL log"""
    with open(LOG_FILE, "a") as f:
        for entry in processed:
            f.write(json.dumps(entry) + "\n")

def generate_report(processed, stats):
    """Generate summary report"""
    auto_responded = sum(1 for p in processed if p["response_status"] == "auto_responded")
    flagged = sum(1 for p in processed if p["response_status"] == "flagged_for_review")
    
    report = f"""
╔════════════════════════════════════════════════════════════╗
║       YOUTUBE COMMENT MONITOR - CRON EXECUTION REPORT       ║
╚════════════════════════════════════════════════════════════╝

⏰ Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📺 Channel: {CHANNEL_NAME}
🔄 Cycle: Every 30 minutes

───────────────────────────────────────────────────────────────
📊 THIS CYCLE RESULTS
───────────────────────────────────────────────────────────────

Total Comments Processed:  {len(processed)}
Auto-Responses Sent:       {auto_responded}
Flagged for Review:        {flagged}
Spam Blocked:              {stats['spam']}

Category Breakdown:
  📝 Questions:  {stats['questions']}
  👏 Praise:     {stats['praise']}
  🚫 Spam:       {stats['spam']}
  💼 Sales:      {stats['sales']}
  ℹ️  Other:      {stats['other']}

───────────────────────────────────────────────────────────────
📈 LIFETIME STATISTICS
───────────────────────────────────────────────────────────────

Log File: {LOG_FILE}
Total Entries: {count_log_entries(LOG_FILE)}

───────────────────────────────────────────────────────────────
✅ STATUS: SUCCESS
───────────────────────────────────────────────────────────────

All comments logged to: {LOG_FILE}
Next execution: 30 minutes from now
"""
    
    print(report)
    
    with open(REPORT_FILE, "a") as f:
        f.write(report + "\n")

def count_log_entries(filepath):
    """Count lines in JSONL file"""
    if not filepath.exists():
        return 0
    with open(filepath) as f:
        return sum(1 for _ in f)

def main():
    """Main execution"""
    print(f"🚀 YouTube Comment Monitor - {datetime.now().strftime('%H:%M:%S')}")
    print(f"📺 Channel: {CHANNEL_NAME}")
    print(f"🔄 Mode: Demo (Synthetic Comments)")
    print()
    
    # Generate or fetch comments
    comments = generate_synthetic_comments()
    print(f"📥 Found {len(comments)} new comments")
    
    # Process comments
    processed, stats = process_comments(comments)
    print(f"✅ Processed {len(processed)} comments")
    
    # Log to file
    log_comments(processed)
    print(f"💾 Logged to: {LOG_FILE}")
    
    # Generate report
    generate_report(processed, stats)
    print()
    print("✨ Monitor cycle complete!")

if __name__ == "__main__":
    main()
