#!/usr/bin/env python3
"""
Query and analyze YouTube comments log
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

LOG_FILE = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-comments.jsonl"


def load_comments():
    """Load all comments from JSONL log"""
    comments = []
    if not LOG_FILE.exists():
        print(f"Log file not found: {LOG_FILE}")
        return comments

    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                comments.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return comments


def print_stats(comments):
    """Print overall statistics"""
    if not comments:
        print("No comments found.")
        return

    stats = defaultdict(int)
    response_stats = defaultdict(int)

    for c in comments:
        stats[c.get("category", "unknown")] += 1
        response_stats[c.get("response_status", "unknown")] += 1

    print("=" * 70)
    print("COMMENT STATISTICS")
    print("=" * 70)
    print(f"Total comments: {len(comments)}")
    print()
    print("By Category:")
    for cat in ["questions", "praise", "spam", "sales", "other"]:
        count = stats.get(cat, 0)
        pct = (count / len(comments) * 100) if comments else 0
        print(f"  {cat:12} {count:4} ({pct:5.1f}%)")

    print()
    print("By Response Status:")
    for status in ["replied", "flagged", "none", "failed"]:
        count = response_stats.get(status, 0)
        pct = (count / len(comments) * 100) if comments else 0
        print(f"  {status:12} {count:4} ({pct:5.1f}%)")

    print()
    print(f"Auto-responses sent: {response_stats['replied']}")
    print(f"Flagged for review: {response_stats['flagged']}")
    print("=" * 70)


def print_by_category(comments, category):
    """Print all comments in a category"""
    filtered = [c for c in comments if c.get("category") == category]

    if not filtered:
        print(f"No {category} comments found.")
        return

    print("=" * 70)
    print(f"{category.upper()} COMMENTS ({len(filtered)})")
    print("=" * 70)

    for i, c in enumerate(filtered, 1):
        print(f"\n[{i}] {c['commenter']} ({c['timestamp']})")
        print(f"    Status: {c['response_status']}")
        print(f"    Text: {c['text']}")

    print("\n" + "=" * 70)


def print_unanswered(comments):
    """Print questions that weren't auto-responded"""
    unanswered = [
        c for c in comments
        if c.get("category") == "questions" and c.get("response_status") != "replied"
    ]

    if not unanswered:
        print("All questions have been answered!")
        return

    print("=" * 70)
    print(f"UNANSWERED QUESTIONS ({len(unanswered)})")
    print("=" * 70)

    for i, c in enumerate(unanswered, 1):
        print(f"\n[{i}] {c['commenter']} ({c['timestamp']})")
        print(f"    Status: {c['response_status']}")
        print(f"    Text: {c['text']}")

    print("\n" + "=" * 70)


def print_recent(comments, limit=10):
    """Print most recent comments"""
    recent = sorted(comments, key=lambda x: x["timestamp"], reverse=True)[:limit]

    print("=" * 70)
    print(f"MOST RECENT COMMENTS (Last {len(recent)})")
    print("=" * 70)

    for i, c in enumerate(recent, 1):
        print(f"\n[{i}] {c['commenter']} ({c['timestamp']})")
        print(f"    Category: {c['category']}")
        print(f"    Status: {c['response_status']}")
        print(f"    Text: {c['text'][:80]}{'...' if len(c['text']) > 80 else ''}")

    print("\n" + "=" * 70)


def print_export_json(comments):
    """Export all comments as JSON"""
    print(json.dumps(comments, indent=2))


def main():
    comments = load_comments()

    if len(sys.argv) < 2:
        print_stats(comments)
        print("\nUsage:")
        print("  python youtube-monitor-query.py [command] [args]")
        print()
        print("Commands:")
        print("  stats                    - Show overall statistics (default)")
        print("  recent [N]               - Show N most recent comments (default 10)")
        print("  category [name]          - Show all comments in category")
        print("  unanswered               - Show unanswered questions")
        print("  export                   - Export all comments as JSON")
        print()
        print("Categories: questions, praise, spam, sales, other")
        return

    cmd = sys.argv[1]

    if cmd == "stats":
        print_stats(comments)
    elif cmd == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print_recent(comments, limit)
    elif cmd == "category":
        if len(sys.argv) < 3:
            print("Usage: query.py category [name]")
            return
        print_by_category(comments, sys.argv[2])
    elif cmd == "unanswered":
        print_unanswered(comments)
    elif cmd == "export":
        print_export_json(comments)
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
