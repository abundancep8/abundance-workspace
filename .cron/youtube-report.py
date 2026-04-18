#!/usr/bin/env python3
"""
YouTube Comment Monitor - Report Generator
Generates summaries from the comments log.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

COMMENTS_LOG = Path(".cache/youtube-comments.jsonl")

def load_comments():
    """Load all logged comments."""
    comments = []
    if COMMENTS_LOG.exists():
        with open(COMMENTS_LOG) as f:
            for line in f:
                try:
                    comments.append(json.loads(line))
                except:
                    pass
    return comments

def generate_report():
    """Generate a comprehensive report."""
    comments = load_comments()
    
    if not comments:
        print("No comments logged yet.")
        return
    
    # Stats
    total = len(comments)
    by_category = defaultdict(int)
    by_status = defaultdict(int)
    auto_responses = 0
    flagged = 0
    
    for comment in comments:
        by_category[comment.get("category", "unknown")] += 1
        status = comment.get("response_status", "unknown")
        by_status[status] += 1
        if status == "sent":
            auto_responses += 1
        elif status == "flagged":
            flagged += 1
    
    # Print report
    print("\n" + "="*60)
    print("YouTube Comment Monitor - Summary Report")
    print("="*60)
    print(f"\n📊 Overall Statistics")
    print(f"  Total comments processed: {total}")
    print(f"  Auto-responses sent: {auto_responses}")
    print(f"  Flagged for review: {flagged}")
    
    print(f"\n📋 By Category")
    for category in ["questions", "praise", "spam", "sales"]:
        count = by_category[category]
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {category:12} {count:3d} ({pct:5.1f}%)")
    
    print(f"\n💬 By Response Status")
    for status, count in sorted(by_status.items()):
        print(f"  {status:12} {count:3d}")
    
    # Recent comments
    print(f"\n📝 Recent Comments (last 10)")
    print("-" * 60)
    for comment in comments[-10:]:
        ts = comment.get("timestamp", "?")
        author = comment.get("commenter", "?")
        text = comment.get("text", "")[:50]
        category = comment.get("category", "?")
        status = comment.get("response_status", "?")
        print(f"[{ts[:10]}] {author:15} ({category:8}) {text}...")
        print(f"  Status: {status}")
        print()
    
    # Flagged for review
    flagged_comments = [c for c in comments if c.get("response_status") == "flagged"]
    if flagged_comments:
        print(f"\n🚩 Flagged for Review ({len(flagged_comments)})")
        print("-" * 60)
        for comment in flagged_comments:
            author = comment.get("commenter", "?")
            text = comment.get("text", "")
            print(f"{author}: {text}")
            print()
    
    print("="*60)

if __name__ == "__main__":
    generate_report()
