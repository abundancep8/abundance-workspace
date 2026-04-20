#!/usr/bin/env python3
"""
YouTube Monitor Report Generator
Analyzes youtube-comments.jsonl and generates insights.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import sys

COMMENTS_LOG = Path(".cache/youtube-comments.jsonl")

def load_comments():
    """Load all comments from JSONL."""
    comments = []
    if not COMMENTS_LOG.exists():
        print(f"No comments log found at {COMMENTS_LOG}")
        return comments
    
    with open(COMMENTS_LOG) as f:
        for line in f:
            try:
                comments.append(json.loads(line))
            except:
                pass
    
    return comments

def report_overall():
    """Generate overall statistics."""
    comments = load_comments()
    
    if not comments:
        print("No comments found.")
        return
    
    total = len(comments)
    by_category = defaultdict(int)
    by_status = defaultdict(int)
    
    for c in comments:
        by_category[c['category']] += 1
        by_status[c['response_status']] += 1
    
    print("=" * 60)
    print("📊 YOUTUBE MONITOR - OVERALL REPORT")
    print("=" * 60)
    print(f"\nTotal comments processed: {total}")
    print(f"Auto-responses sent: {by_status.get('sent', 0)}")
    print(f"Flagged for review: {by_status.get('flagged', 0)}")
    
    print(f"\nBy category:")
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        pct = (count / total) * 100 if total > 0 else 0
        print(f"  {cat:10s} {count:4d} ({pct:5.1f}%)")
    
    print(f"\nBy response status:")
    for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"  {status:10s} {count:4d}")

def report_recent(hours=24):
    """Recent activity (last N hours)."""
    comments = load_comments()
    now = datetime.now()
    cutoff = now - timedelta(hours=hours)
    
    recent = [
        c for c in comments
        if datetime.fromisoformat(c['timestamp']) > cutoff
    ]
    
    if not recent:
        print(f"No comments in the last {hours} hours.")
        return
    
    by_category = defaultdict(int)
    for c in recent:
        by_category[c['category']] += 1
    
    print(f"\n📈 RECENT ({hours}h)")
    print(f"Comments: {len(recent)}")
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

def report_top_commenters(limit=10):
    """Most active commenters."""
    comments = load_comments()
    
    by_commenter = defaultdict(list)
    for c in comments:
        by_commenter[c['commenter']].append(c)
    
    top = sorted(
        by_commenter.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:limit]
    
    print(f"\n👥 TOP COMMENTERS (last {limit})")
    for name, posts in top:
        categories = defaultdict(int)
        for p in posts:
            categories[p['category']] += 1
        cat_str = ", ".join(f"{k}:{v}" for k, v in sorted(categories.items()))
        print(f"  {name:30s} {len(posts):3d} ({cat_str})")

def report_sales_opportunities():
    """List flagged sales/partnership inquiries."""
    comments = load_comments()
    
    sales = [
        c for c in comments
        if c['category'] == 'sales' and c['response_status'] == 'flagged'
    ]
    
    if not sales:
        print("\nNo flagged sales inquiries.")
        return
    
    print(f"\n💼 SALES OPPORTUNITIES ({len(sales)})")
    for c in sorted(sales, key=lambda x: x['timestamp'], reverse=True)[:10]:
        print(f"\n  From: {c['commenter']}")
        print(f"  Date: {c['comment_timestamp']}")
        print(f"  Text: {c['text'][:100]}...")

def report_unanswered_questions():
    """Questions that weren't auto-answered."""
    comments = load_comments()
    
    unanswered = [
        c for c in comments
        if c['category'] == 'questions' and c['response_status'] != 'sent'
    ]
    
    if not unanswered:
        print("\nAll questions were answered!")
        return
    
    print(f"\n❓ UNANSWERED QUESTIONS ({len(unanswered)})")
    for c in sorted(unanswered, key=lambda x: -x['likes'])[:5]:
        print(f"\n  From: {c['commenter']} ({c['likes']} likes)")
        print(f"  Text: {c['text'][:100]}...")

def main():
    """Generate full report."""
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "recent":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            report_recent(hours)
        elif cmd == "commenters":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            report_top_commenters(limit)
        elif cmd == "sales":
            report_sales_opportunities()
        elif cmd == "questions":
            report_unanswered_questions()
        else:
            print(f"Unknown command: {cmd}")
    else:
        # Full report
        report_overall()
        report_recent(24)
        report_top_commenters(5)
        report_sales_opportunities()
        report_unanswered_questions()
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
