#!/usr/bin/env python3
"""
YouTube Comment Monitor - Report Generator
Analyze logged comments and generate summaries.
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

COMMENTS_LOG = Path("/Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl")
STATE_FILE = Path("/Users/abundance/.openclaw/workspace/.cache/youtube-state.json")

def load_comments():
    """Load all comments from JSONL log."""
    if not COMMENTS_LOG.exists():
        return []
    
    comments = []
    with open(COMMENTS_LOG) as f:
        for line in f:
            if line.strip():
                comments.append(json.loads(line))
    return comments

def generate_report():
    """Generate comprehensive report."""
    comments = load_comments()
    
    if not comments:
        print("No comments logged yet.")
        return
    
    # Load state
    with open(STATE_FILE) as f:
        state = json.load(f)
    
    # Calculate stats
    total = len(comments)
    by_category = defaultdict(int)
    by_status = defaultdict(int)
    auto_responses = 0
    flagged = 0
    
    for comment in comments:
        by_category[comment['category']] += 1
        by_status[comment['response_status']] += 1
        if comment['response_status'] == 'auto_responded':
            auto_responses += 1
        elif comment['response_status'] == 'flagged_review':
            flagged += 1
    
    # Print report
    print("\n" + "="*60)
    print("  YOUTUBE COMMENT MONITOR REPORT")
    print("="*60)
    
    print(f"\n📊 OVERALL STATS")
    print(f"   Total comments processed: {total}")
    print(f"   Auto-responses sent: {auto_responses}")
    print(f"   Flagged for review: {flagged}")
    print(f"   Spam hidden: {by_status.get('spam_hidden', 0)}")
    
    print(f"\n📂 BY CATEGORY")
    for cat in ['question', 'praise', 'spam', 'sales', 'other']:
        count = by_category[cat]
        pct = (count / total * 100) if total else 0
        print(f"   {cat:12} {count:3} ({pct:5.1f}%)")
    
    print(f"\n✅ BY STATUS")
    for status in ['auto_responded', 'flagged_review', 'spam_hidden', 'pending']:
        count = by_status[status]
        pct = (count / total * 100) if total else 0
        if count > 0:
            print(f"   {status:18} {count:3} ({pct:5.1f}%)")
    
    # Recent comments
    print(f"\n📝 RECENT COMMENTS (Last 5)")
    print("-" * 60)
    for comment in comments[-5:]:
        print(f"\n   {comment['commenter']} [{comment['category']}]")
        print(f"   {comment['text'][:60]}...")
        print(f"   Status: {comment['response_status']}")
    
    # Flagged for review
    flagged_comments = [c for c in comments if c['response_status'] == 'flagged_review']
    if flagged_comments:
        print(f"\n🚩 FLAGGED FOR REVIEW ({len(flagged_comments)})")
        print("-" * 60)
        for comment in flagged_comments:
            print(f"\n   {comment['commenter']} ({comment['category']})")
            print(f"   {comment['text']}")
            print(f"   👍 {comment['likes']} likes")
    
    print("\n" + "="*60)
    if state.get('last_run'):
        print(f"Last run: {state['last_run']}")
    print("="*60 + "\n")

if __name__ == "__main__":
    generate_report()
