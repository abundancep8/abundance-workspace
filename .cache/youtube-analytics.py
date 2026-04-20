#!/usr/bin/env python3
"""
YouTube Comment Monitor - Analytics & Reporting
Reads youtube-comments.jsonl and generates detailed reports.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

JSONL_PATH = Path(".cache/youtube-comments.jsonl")

CATEGORY_NAMES = {
    1: "Questions",
    2: "Praise",
    3: "Spam",
    4: "Sales",
}

def load_comments():
    """Load all comments from JSONL."""
    comments = []
    if not JSONL_PATH.exists():
        return comments
    
    with open(JSONL_PATH) as f:
        for line in f:
            if line.strip():
                try:
                    comments.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    
    return comments

def print_report(comments):
    """Generate and print detailed report."""
    if not comments:
        print("📭 No comments logged yet.")
        return
    
    # Filter out system messages
    comments = [c for c in comments if c.get("category", 0) != 0]
    
    if not comments:
        print("📭 No comments logged yet (excluding system messages).")
        return
    
    # Summary stats
    print("\n" + "="*60)
    print("📊 YOUTUBE COMMENT MONITOR - DETAILED REPORT")
    print("="*60)
    
    print(f"\n📈 Overall Statistics")
    print(f"   Total comments: {len(comments)}")
    print(f"   Date range: {comments[0]['timestamp'][:10]} → {comments[-1]['timestamp'][:10]}")
    
    # By category
    by_category = defaultdict(int)
    by_status = defaultdict(int)
    
    for c in comments:
        cat = c.get("category", 0)
        if cat > 0:
            by_category[cat] += 1
        by_status[c.get("response_status", "none")] += 1
    
    print(f"\n📂 By Category")
    for cat in sorted(by_category.keys()):
        name = CATEGORY_NAMES.get(cat, f"Unknown({cat})")
        count = by_category[cat]
        pct = (count / len(comments)) * 100
        print(f"   {name:15} {count:3d}  ({pct:5.1f}%)")
    
    # By response status
    print(f"\n💬 By Response Status")
    for status in sorted(by_status.keys()):
        count = by_status[status]
        pct = (count / len(comments)) * 100
        print(f"   {status:20} {count:3d}  ({pct:5.1f}%)")
    
    # Activity timeline (last 7 days)
    print(f"\n📅 Last 7 Days Activity")
    now = datetime.fromisoformat(comments[-1]['timestamp'].replace('Z', '+00:00'))
    week_ago = now - timedelta(days=7)
    
    by_day = defaultdict(int)
    for c in comments:
        ts = datetime.fromisoformat(c['timestamp'].replace('Z', '+00:00'))
        if ts >= week_ago:
            day = ts.strftime("%a %m/%d")
            by_day[day] += 1
    
    for day in sorted(by_day.keys()):
        count = by_day[day]
        bar = "█" * (count // 2) if count > 0 else "  -  "
        print(f"   {day}  {count:3d}  {bar}")
    
    # Top commenters
    print(f"\n👥 Top Commenters")
    by_commenter = defaultdict(int)
    for c in comments:
        by_commenter[c.get("commenter", "Unknown")] += 1
    
    top_commenters = sorted(by_commenter.items(), key=lambda x: x[1], reverse=True)[:5]
    for commenter, count in top_commenters:
        print(f"   {commenter:30} {count:3d} comments")
    
    # Recent comments needing action
    print(f"\n🚩 Recent Comments Flagged for Review (Sales)")
    flagged = [c for c in comments if c.get("response_status") == "flagged_for_review"][-3:]
    if flagged:
        for c in reversed(flagged):
            ts = datetime.fromisoformat(c['timestamp'].replace('Z', '+00:00'))
            print(f"\n   [{ts.strftime('%m/%d %H:%M')}] {c.get('commenter', 'Unknown')}")
            print(f"   \"{c.get('text', '')[:80]}...\"")
    else:
        print("   None")
    
    print("\n" + "="*60)

def print_json_export(comments, limit=None):
    """Export comments as pretty JSON."""
    if limit:
        comments = comments[-limit:]
    
    print(json.dumps(comments, indent=2))

def main():
    """Main analytics runner."""
    import sys
    
    comments = load_comments()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--json":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
            print_json_export(comments, limit)
        elif sys.argv[1] == "--csv":
            # CSV export
            print("timestamp,commenter,category,text,response_status")
            for c in comments:
                if c.get("category", 0) > 0:
                    ts = c['timestamp'][:19].replace('T', ' ')
                    commenter = c.get('commenter', 'Unknown').replace('"', '""')
                    category = c.get('category', 0)
                    text = c.get('text', '').replace('"', '""')[:100]
                    status = c.get('response_status', 'none')
                    print(f'"{ts}","{commenter}",{category},"{text}","{status}"')
    else:
        print_report(comments)

if __name__ == "__main__":
    main()
