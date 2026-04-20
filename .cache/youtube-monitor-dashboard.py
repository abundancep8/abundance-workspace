#!/usr/bin/env python3
"""
YouTube Comment Monitor Dashboard
Displays summary stats and flagged comments needing review.
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

CACHE_FILE = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-comments.jsonl"

def load_comments():
    """Load all logged comments."""
    if not CACHE_FILE.exists():
        return []
    
    comments = []
    with open(CACHE_FILE) as f:
        for line in f:
            try:
                comments.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return comments

def print_dashboard():
    """Print monitoring dashboard."""
    comments = load_comments()
    
    if not comments:
        print("📊 YouTube Comment Monitor - No data yet")
        print("   Run: python youtube_comment_monitor.py")
        return
    
    # Calculate stats
    total = len(comments)
    last_24h = [c for c in comments if 
                datetime.fromisoformat(c['processed_at']) > datetime.now() - timedelta(days=1)]
    
    categories = defaultdict(int)
    responses = defaultdict(int)
    
    for c in comments:
        categories[c.get('category', 'unknown')] += 1
        responses[c.get('response_status', 'unknown')] += 1
    
    flagged = [c for c in comments if c.get('response_status') == 'flagged_for_review']
    
    # Print dashboard
    print("\n" + "="*70)
    print("📊 YOUTUBE COMMENT MONITOR DASHBOARD")
    print("="*70)
    print(f"\n📈 OVERALL STATS")
    print(f"   Total comments logged: {total}")
    print(f"   Last 24 hours: {len(last_24h)}")
    
    print(f"\n📂 BY CATEGORY")
    for cat in ["praise", "questions", "sales", "spam", "other"]:
        count = categories.get(cat, 0)
        if count > 0:
            bar = "█" * (count // max(1, total // 20))
            print(f"   {cat.capitalize():15} {count:3} {bar}")
    
    print(f"\n✉️  RESPONSE STATUS")
    for status, count in sorted(responses.items(), key=lambda x: -x[1]):
        print(f"   {status:30} {count}")
    
    print(f"\n🚨 FLAGGED FOR REVIEW ({len(flagged)})")
    if flagged:
        for c in flagged[-5:]:  # Show last 5
            ts = c.get('comment_timestamp', c.get('processed_at', '?'))[:10]
            author = c.get('commenter', '?')
            text = c.get('text', '')[:60]
            print(f"   [{ts}] {author}: {text}...")
    else:
        print("   ✅ None — all clear!")
    
    print("\n" + "="*70)
    print("Commands:")
    print("   View all flagged comments:")
    print("   cat .cache/youtube-comments.jsonl | jq 'select(.response_status == \"flagged_for_review\")'")
    print("\n   Export to CSV:")
    print("   cat .cache/youtube-comments.jsonl | jq -r '[.processed_at, .commenter, .category, .text] | @csv' > comments.csv")
    print("="*70 + "\n")

if __name__ == "__main__":
    print_dashboard()
