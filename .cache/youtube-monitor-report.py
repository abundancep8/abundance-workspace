#!/usr/bin/env python3
"""
Generate reports from YouTube comment monitoring log
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

WORKSPACE = Path.home() / ".openclaw" / "workspace"
CACHE_DIR = WORKSPACE / ".cache"
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"


def load_comments(since_minutes=None):
    """Load comments from log, optionally filtering by time."""
    if not COMMENTS_LOG.exists():
        return []
    
    comments = []
    cutoff = None
    if since_minutes:
        cutoff = datetime.utcnow() - timedelta(minutes=since_minutes)
    
    with open(COMMENTS_LOG) as f:
        for line in f:
            try:
                comment = json.loads(line)
                if cutoff:
                    ts = datetime.fromisoformat(comment['timestamp'].replace('Z', '+00:00'))
                    if ts < cutoff:
                        continue
                comments.append(comment)
            except:
                continue
    
    return comments


def report_summary(minutes=None):
    """Generate summary report."""
    comments = load_comments(minutes)
    
    if not comments:
        print("No comments in log")
        return
    
    timeframe = f"last {minutes} minutes" if minutes else "all time"
    print(f"\n📊 YouTube Comment Monitor Report ({timeframe})")
    print("=" * 60)
    
    # Total stats
    print(f"Total comments: {len(comments)}")
    print(f"Auto-responses sent: {sum(1 for c in comments if c['response_sent'])}")
    print(f"Flagged for review: {sum(1 for c in comments if c['category'] == 'sales')}")
    
    # By category
    print("\nBy Category:")
    by_cat = defaultdict(int)
    for comment in comments:
        by_cat[comment['category']] += 1
    
    for category in sorted(by_cat.keys()):
        count = by_cat[category]
        emoji = {"questions": "❓", "praise": "👍", "spam": "🚫", "sales": "🚩", "neutral": "ℹ️"}.get(category, "•")
        print(f"  {emoji} {category}: {count}")
    
    # Top commenters
    print("\nTop Commenters:")
    by_author = defaultdict(int)
    for comment in comments:
        by_author[comment['commenter']] += 1
    
    for author, count in sorted(by_author.items(), key=lambda x: -x[1])[:5]:
        print(f"  • {author}: {count} comments")
    
    # Recent sales inquiries
    sales = [c for c in comments if c['category'] == 'sales']
    if sales:
        print(f"\n🚩 Sales Inquiries ({len(sales)}):")
        for sale in sales[-5:]:  # Last 5
            print(f"  • {sale['commenter']}: {sale['text'][:70]}...")
    
    print("=" * 60 + "\n")


if __name__ == '__main__':
    import sys
    minutes = None
    if len(sys.argv) > 1:
        try:
            minutes = int(sys.argv[1])
        except:
            pass
    
    report_summary(minutes)
