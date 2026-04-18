#!/usr/bin/env python3
"""
Generate reports from YouTube comment monitor log
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

LOG_FILE = Path.home() / ".openclaw/workspace/.cache/youtube-comments.jsonl"

def load_comments(limit_hours: int = 24) -> list:
    """Load comments from log file."""
    if not LOG_FILE.exists():
        print(f"Log file not found: {LOG_FILE}")
        return []
    
    cutoff = datetime.utcnow() - timedelta(hours=limit_hours)
    comments = []
    
    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                comment = json.loads(line)
                timestamp = datetime.fromisoformat(comment.get("processed_at", ""))
                if timestamp >= cutoff:
                    comments.append(comment)
            except json.JSONDecodeError:
                continue
    
    return comments

def generate_report(limit_hours: int = 24):
    """Generate summary report."""
    comments = load_comments(limit_hours)
    
    if not comments:
        print(f"No comments found in the last {limit_hours} hours")
        return
    
    # Statistics
    stats = {
        "total": len(comments),
        "by_category": defaultdict(int),
        "by_status": defaultdict(int),
        "commenters": set()
    }
    
    for comment in comments:
        stats["by_category"][comment.get("category", "unknown")] += 1
        stats["by_status"][comment.get("response_status", "unknown")] += 1
        stats["commenters"].add(comment.get("commenter", "Unknown"))
    
    # Print report
    print(f"\n{'='*50}")
    print(f"YouTube Comment Monitor Report")
    print(f"Last {limit_hours} hours | Generated: {datetime.utcnow().isoformat()}")
    print(f"{'='*50}\n")
    
    print(f"Total Comments: {stats['total']}")
    print(f"Unique Commenters: {len(stats['commenters'])}\n")
    
    print("By Category:")
    for category, count in sorted(stats["by_category"].items()):
        pct = (count / stats["total"]) * 100
        print(f"  {category:15} {count:3} ({pct:5.1f}%)")
    
    print("\nResponse Status:")
    for status, count in sorted(stats["by_status"].items()):
        pct = (count / stats["total"]) * 100
        print(f"  {status:20} {count:3} ({pct:5.1f}%)")
    
    print(f"\nDetailed log: {LOG_FILE}")
    print(f"{'='*50}\n")
    
    # List comments flagged for review
    flagged = [c for c in comments if c.get("response_status") == "flagged_review"]
    if flagged:
        print(f"\n⚠️  {len(flagged)} Comments Flagged for Review:\n")
        for c in flagged:
            print(f"From: {c.get('commenter', 'Unknown')}")
            print(f"Text: {c.get('text', '')[:100]}...")
            print(f"Time: {c.get('timestamp', 'Unknown')}\n")

if __name__ == "__main__":
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    generate_report(hours)
