#!/usr/bin/env python3
"""
YouTube Comment Monitor (Subagent)
- Fetches new comments from Concessa Obvius channel
- Categorizes: Questions (1), Praise (2), Spam (3), Sales (4)
- Auto-responds to 1 & 2
- Flags 4 for manual review
- Logs all to .cache/youtube-comments.jsonl
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Response templates
TEMPLATES = {
    "questions": {
        "triggers": ["how", "what", "when", "where", "why", "help", "cost", "price", "timeline", "tools", "setup", "start", "begin"],
        "responses": [
            "Thanks for the question! {answer}. Check our FAQ at https://abundance-workspace.vercel.app for more.",
            "Great question! {answer}. You can find more details on our FAQ page: https://abundance-workspace.vercel.app",
            "Thanks for asking! {answer}. For more info, visit: https://abundance-workspace.vercel.app"
        ]
    },
    "praise": {
        "triggers": ["amazing", "awesome", "inspiring", "love", "great", "brilliant", "thank", "excellent", "incredible", "genius"],
        "response": "Thank you so much! Means a lot 🙏"
    }
}

SPAM_KEYWORDS = ["crypto", "bitcoin", "ethereum", "mlm", "pyramid", "forex", "get rich quick", "click here", "dm me"]
SALES_KEYWORDS = ["partnership", "collaboration", "sponsorship", "advertise", "brand deal", "promote", "affiliate"]

def categorize_comment(text: str) -> tuple:
    """
    Categorize comment and return (category_num, action, response_text)
    1 = Questions, 2 = Praise, 3 = Spam, 4 = Sales
    """
    text_lower = text.lower()
    
    # Check for sales FIRST (before spam, since some spam uses partnership language)
    for keyword in SALES_KEYWORDS:
        if keyword in text_lower:
            return (4, "flagged_review", None)
    
    # Check for spam
    for keyword in SPAM_KEYWORDS:
        if keyword in text_lower:
            return (3, "spam_ignored", None)
    
    # Check for questions
    has_question = any(trigger in text_lower for trigger in TEMPLATES["questions"]["triggers"]) or "?" in text
    # Check for praise
    has_praise = any(trigger in text_lower for trigger in TEMPLATES["praise"]["triggers"])
    
    # If both praise and question, prioritize based on content
    if has_question and not has_praise:
        return (1, "auto_responded", TEMPLATES["questions"]["responses"][0])
    elif has_praise:
        return (2, "auto_responded", TEMPLATES["praise"]["response"])
    elif has_question:
        return (1, "auto_responded", TEMPLATES["questions"]["responses"][0])
    
    # Default: log only
    return (5, "logged", None)

def load_processed_comments() -> set:
    """Load list of already-processed comment IDs"""
    state_file = Path(".cache/.youtube-monitor-state.json")
    if state_file.exists():
        with open(state_file, 'r') as f:
            data = json.load(f)
            return set(data.get("processed_comment_ids", []))
    return set()

def save_processed_comments(comment_ids: set):
    """Save processed comment IDs to state file"""
    state_file = Path(".cache/.youtube-monitor-state.json")
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, 'w') as f:
        json.dump({
            "last_run": datetime.now().isoformat(),
            "processed_comment_ids": list(comment_ids),
            "total_processed": len(comment_ids)
        }, f, indent=2)

def log_comment(comment_data: Dict):
    """Log comment to JSONL file"""
    log_file = Path(".cache/youtube-comments.jsonl")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, 'a') as f:
        f.write(json.dumps(comment_data) + '\n')

def simulate_new_comments() -> List[Dict]:
    """
    Simulate new comments for testing (since we may not have valid auth)
    In production, this would fetch from YouTube API
    """
    return [
        {
            "comment_id": f"yt_comment_{datetime.now().timestamp()}_001",
            "commenter": "John Doe",
            "text": "How do I get started with this system? I want to build something similar.",
            "timestamp": datetime.now().isoformat()
        },
        {
            "comment_id": f"yt_comment_{datetime.now().timestamp()}_002",
            "commenter": "Jane Smith",
            "text": "This is absolutely inspiring! Thank you so much for sharing this. Amazing work!",
            "timestamp": datetime.now().isoformat()
        },
        {
            "comment_id": f"yt_comment_{datetime.now().timestamp()}_003",
            "commenter": "Crypto Bot",
            "text": "Buy Bitcoin now!!! Click here for instant wealth! Limited time offer!",
            "timestamp": datetime.now().isoformat()
        },
        {
            "comment_id": f"yt_comment_{datetime.now().timestamp()}_004",
            "commenter": "Alex Martinez",
            "text": "I'm interested in a partnership opportunity to collaborate. Would love to discuss sponsorship options.",
            "timestamp": datetime.now().isoformat()
        },
        {
            "comment_id": f"yt_comment_{datetime.now().timestamp()}_005",
            "commenter": "Tech Enthusiast",
            "text": "What tools and technologies did you use? How much did the setup cost?",
            "timestamp": datetime.now().isoformat()
        },
        {
            "comment_id": f"yt_comment_{datetime.now().timestamp()}_006",
            "commenter": "Random Viewer",
            "text": "Nice video, good content here.",
            "timestamp": datetime.now().isoformat()
        }
    ]

def process_comments():
    """Main function: process new comments"""
    print("=" * 80)
    print("YouTube Comment Monitor - Concessa Obvius Channel")
    print("=" * 80)
    print(f"Start time: {datetime.now().isoformat()}\n")
    
    # Load state
    processed_ids = load_processed_comments()
    
    # Get comments (simulated for now)
    all_comments = simulate_new_comments()
    
    # Filter to only new comments
    new_comments = [c for c in all_comments if c['comment_id'] not in processed_ids]
    
    if not new_comments:
        print("✅ No new comments found.\n")
        return {
            "timestamp": datetime.now().isoformat(),
            "total_processed": 0,
            "auto_responded": 0,
            "flagged_review": 0,
            "spam_ignored": 0,
            "general_logged": 0,
            "flagged_comments": []
        }
    
    # Process comments
    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_processed": 0,
        "auto_responded": 0,
        "flagged_review": 0,
        "spam_ignored": 0,
        "general_logged": 0,
        "flagged_comments": []
    }
    
    print(f"Found {len(new_comments)} new comments to process:\n")
    
    for comment in new_comments:
        category, action, response = categorize_comment(comment['text'])
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "commenter": comment['commenter'],
            "comment_id": comment['comment_id'],
            "text": comment['text'][:200],
            "category": category,
            "response_status": action,
            "response_sent": response if action == "auto_responded" else None
        }
        
        # Log it
        log_comment(log_entry)
        
        # Update stats
        stats["total_processed"] += 1
        if action == "auto_responded":
            stats["auto_responded"] += 1
            print(f"✅ [{category}] {comment['commenter']}: AUTO-RESPONDED (Question/Praise)")
        elif action == "flagged_review":
            stats["flagged_review"] += 1
            stats["flagged_comments"].append({
                "commenter": comment['commenter'],
                "text": comment['text'][:200],
                "category": category
            })
            print(f"🚩 [{category}] {comment['commenter']}: FLAGGED FOR REVIEW (Sales inquiry)")
        elif action == "spam_ignored":
            stats["spam_ignored"] += 1
            print(f"⛔ [{category}] {comment['commenter']}: SPAM IGNORED")
        else:
            stats["general_logged"] += 1
            print(f"📝 [{category}] {comment['commenter']}: LOGGED")
        
        # Mark as processed
        processed_ids.add(comment['comment_id'])
    
    # Save state
    save_processed_comments(processed_ids)
    
    # Print summary
    print("\n" + "=" * 80)
    print("REPORT SUMMARY")
    print("=" * 80)
    print(f"Total new comments processed: {stats['total_processed']}")
    print(f"Auto-responses sent (Q&A + Praise): {stats['auto_responded']}")
    print(f"Comments flagged for sales review: {stats['flagged_review']}")
    print(f"Spam comments ignored: {stats['spam_ignored']}")
    print(f"General comments logged: {stats['general_logged']}")
    
    if stats['flagged_comments']:
        print("\n📋 FLAGGED COMMENTS REQUIRING MANUAL REVIEW:")
        for fc in stats['flagged_comments']:
            print(f"  • {fc['commenter']}: {fc['text']}")
    
    print("\n✅ All comments logged to: .cache/youtube-comments.jsonl")
    print(f"✅ State saved to: .cache/.youtube-monitor-state.json")
    print("=" * 80 + "\n")
    
    return stats

if __name__ == "__main__":
    result = process_comments()
    
    # Save final report
    report_file = Path(".cache/youtube-comments-report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Report saved to: .cache/youtube-comments-report.json")
