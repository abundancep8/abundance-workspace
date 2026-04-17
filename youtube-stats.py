#!/usr/bin/env python3
"""
Quick stats viewer for YouTube comment monitor
Shows summary and recent activity
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

CACHE_DIR = Path(".cache")
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"

def load_comments():
    """Load all logged comments"""
    if not COMMENTS_LOG.exists():
        return []
    
    comments = []
    for line in COMMENTS_LOG.read_text().strip().split('\n'):
        if line:
            comments.append(json.loads(line))
    return comments

def main():
    comments = load_comments()
    
    if not comments:
        print("No comments logged yet.")
        return
    
    # Stats
    by_category = defaultdict(int)
    by_response = defaultdict(int)
    by_commenter = defaultdict(int)
    
    for comment in comments:
        by_category[comment['category']] += 1
        by_response[comment['response_status']] += 1
        by_commenter[comment['commenter']] += 1
    
    # Display
    print("\n" + "="*70)
    print("YOUTUBE COMMENT MONITOR - STATISTICS")
    print("="*70)
    
    print(f"\nTotal comments tracked: {len(comments)}")
    print(f"Date range: {comments[0]['timestamp'][:10]} to {comments[-1]['timestamp'][:10]}")
    
    print("\n📊 BY CATEGORY:")
    for cat in ["question", "praise", "spam", "sales"]:
        count = by_category[cat]
        pct = (count / len(comments) * 100) if comments else 0
        bar = "█" * int(pct / 5)
        print(f"  {cat.capitalize():12} {count:3} ({pct:5.1f}%) {bar}")
    
    print("\n📝 BY RESPONSE STATUS:")
    for status in ["sent", "flagged", "none", "failed"]:
        count = by_response[status]
        pct = (count / len(comments) * 100) if comments else 0
        print(f"  {status.capitalize():12} {count:3} ({pct:5.1f}%)")
    
    print("\n👥 TOP COMMENTERS:")
    top = sorted(by_commenter.items(), key=lambda x: x[1], reverse=True)[:5]
    for name, count in top:
        print(f"  {name:30} {count} comments")
    
    print("\n" + "="*70)
    
    # Recent activity
    print("\n📋 RECENT COMMENTS (last 5):")
    print("-" * 70)
    
    for comment in comments[-5:]:
        print(f"\n  {comment['commenter']} ({comment['category'].upper()})")
        print(f"  → {comment['text'][:60]}...")
        print(f"  Status: {comment['response_status']}")
        print(f"  Time: {comment['timestamp']}")

if __name__ == '__main__':
    main()
