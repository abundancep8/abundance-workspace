#!/usr/bin/env python3
"""
YouTube Comment Monitor - Report Generator
Generates summaries from the YouTube comments log.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

COMMENTS_LOG = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-comments.jsonl"


def load_comments(since_hours=None):
    """Load comments from JSONL log, optionally filtered by time."""
    comments = []
    
    if not COMMENTS_LOG.exists():
        print(f"❌ Log file not found: {COMMENTS_LOG}")
        return []
    
    cutoff_time = None
    if since_hours:
        cutoff_time = datetime.utcnow() - timedelta(hours=since_hours)
    
    with open(COMMENTS_LOG, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                if cutoff_time:
                    entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    if entry_time < cutoff_time:
                        continue
                comments.append(entry)
            except json.JSONDecodeError:
                continue
    
    return comments


def generate_summary(comments):
    """Generate summary statistics."""
    if not comments:
        print("No comments to report on.")
        return
    
    # Aggregations
    by_category = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    by_response = defaultdict(int)
    by_commenter = defaultdict(int)
    
    for comment in comments:
        by_category[comment['category']] += 1
        by_response[comment['response_status']] += 1
        by_commenter[comment['commenter']] += 1
    
    # Generate report
    print("\n" + "="*70)
    print("📊 YOUTUBE COMMENT MONITOR - SESSION REPORT")
    print("="*70)
    
    print(f"\n📈 OVERVIEW")
    print(f"   Total comments processed: {len(comments)}")
    if comments:
        print(f"   First comment: {comments[0]['timestamp']}")
        print(f"   Latest comment: {comments[-1]['timestamp']}")
    
    print(f"\n📂 COMMENTS BY CATEGORY")
    print(f"   ├─ Category 1 (Questions): {by_category[1]}")
    print(f"   ├─ Category 2 (Praise): {by_category[2]}")
    print(f"   ├─ Category 3 (Spam): {by_category[3]}")
    print(f"   ├─ Category 4 (Sales): {by_category[4]}")
    print(f"   └─ Category 0 (No Action): {by_category[0]}")
    
    print(f"\n✅ ACTIONS TAKEN")
    print(f"   Auto-responded: {by_response['auto_responded']}")
    print(f"   Flagged for review: {by_response['flagged']}")
    print(f"   No action taken: {by_response['no_action']}")
    
    print(f"\n👥 TOP COMMENTERS")
    top_commenters = sorted(by_commenter.items(), key=lambda x: x[1], reverse=True)[:5]
    for commenter, count in top_commenters:
        print(f"   {commenter}: {count} comment{'s' if count > 1 else ''}")
    
    print("\n" + "="*70 + "\n")


def show_flagged(comments):
    """Show flagged comments that need review."""
    flagged = [c for c in comments if c['response_status'] == 'flagged']
    
    if not flagged:
        print("✅ No flagged comments.")
        return
    
    print("\n" + "="*70)
    print("🚩 FLAGGED FOR REVIEW (Sales & Partnerships)")
    print("="*70 + "\n")
    
    for comment in flagged:
        print(f"👤 {comment['commenter']}")
        print(f"   📅 {comment['timestamp']}")
        print(f"   💬 {comment['text'][:150]}...")
        print()


def interactive_report():
    """Interactive report generator."""
    print("\n🎯 YouTube Comment Monitor - Report Generator\n")
    
    print("Options:")
    print("  1. Full report (all time)")
    print("  2. Last hour")
    print("  3. Last 24 hours")
    print("  4. Last 7 days")
    print("  5. Show flagged comments")
    print("  6. Exit")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    if choice == '1':
        comments = load_comments()
        generate_summary(comments)
    elif choice == '2':
        comments = load_comments(since_hours=1)
        print("\n📊 REPORT - LAST HOUR\n")
        generate_summary(comments)
    elif choice == '3':
        comments = load_comments(since_hours=24)
        print("\n📊 REPORT - LAST 24 HOURS\n")
        generate_summary(comments)
    elif choice == '4':
        comments = load_comments(since_hours=168)
        print("\n📊 REPORT - LAST 7 DAYS\n")
        generate_summary(comments)
    elif choice == '5':
        comments = load_comments()
        show_flagged(comments)
    elif choice == '6':
        print("Goodbye!")
        return
    else:
        print("❌ Invalid option")
    
    # Repeat
    input("\nPress Enter to continue...")
    interactive_report()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--full':
            generate_summary(load_comments())
        elif sys.argv[1] == '--flagged':
            show_flagged(load_comments())
        elif sys.argv[1] == '--hours':
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            generate_summary(load_comments(since_hours=hours))
    else:
        interactive_report()
