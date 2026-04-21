#!/usr/bin/env python3
"""
YouTube Comment Monitor - Statistics Dashboard
Reads the comment log and displays current stats.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

CACHE_FILE = Path(__file__).parent.parent / '.cache' / 'youtube-comments.jsonl'

def load_comments():
    """Load all logged comments."""
    comments = []
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            for line in f:
                if line.strip():
                    comments.append(json.loads(line))
    return comments

def generate_report():
    """Generate statistics report."""
    comments = load_comments()
    
    if not comments:
        print("No comments logged yet.")
        return
    
    # Calculate stats
    total = len(comments)
    auto_sent = sum(1 for c in comments if c['response_status'] == 'auto_sent')
    flagged = sum(1 for c in comments if c['response_status'] == 'flagged')
    
    categories = defaultdict(int)
    for c in comments:
        categories[c['category']] += 1
    
    # Group by date
    by_date = defaultdict(list)
    for c in comments:
        date = c['timestamp'][:10]
        by_date[date].append(c)
    
    latest_date = max(by_date.keys()) if by_date else None
    today_count = len(by_date[latest_date]) if latest_date else 0
    
    # Print report
    print(f"\n{'='*70}")
    print(f"YouTube Comment Monitor - Statistics Dashboard")
    print(f"{'='*70}")
    print(f"Generated: {datetime.now().isoformat()}\n")
    
    print(f"📊 Overall Stats")
    print(f"  Total comments processed: {total}")
    print(f"  Auto-responses sent: {auto_sent}")
    print(f"  Flagged for review: {flagged}")
    print(f"  Latest activity: {latest_date} ({today_count} comments)")
    
    print(f"\n📂 Breakdown by Category")
    for cat in ['question', 'praise', 'spam', 'sales', 'other']:
        count = categories.get(cat, 0)
        pct = f" ({count/total*100:.1f}%)" if total > 0 else ""
        print(f"  {cat.capitalize():12} {count:3}{pct}")
    
    print(f"\n📅 Last 7 Days Activity")
    sorted_dates = sorted(by_date.keys(), reverse=True)[:7]
    for date in sorted_dates:
        count = len(by_date[date])
        auto = sum(1 for c in by_date[date] if c['response_status'] == 'auto_sent')
        print(f"  {date}: {count:3} comments ({auto} auto-responses)")
    
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    generate_report()
