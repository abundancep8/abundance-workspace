#!/usr/bin/env python3
"""
Query and analyze YouTube comments log
Usage: python3 query-comments.py [--category CATEGORY] [--today] [--flagged] [--stats]
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

LOG_FILE = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-comments.jsonl"

def load_comments(filter_today=False):
    """Load comments from log file"""
    comments = []
    if not LOG_FILE.exists():
        print(f"❌ Log file not found: {LOG_FILE}")
        return []
    
    today = datetime.now().date() if filter_today else None
    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if filter_today:
                    entry_date = datetime.fromisoformat(entry.get("timestamp", "")).date()
                    if entry_date != today:
                        continue
                comments.append(entry)
            except json.JSONDecodeError:
                continue
    
    return comments

def show_stats(comments):
    """Show summary statistics"""
    if not comments:
        print("No comments to analyze")
        return
    
    categories = defaultdict(int)
    responses = defaultdict(int)
    
    for c in comments:
        cat = c.get("category", "unknown")
        categories[cat] += 1
        resp = c.get("response_status", "unknown")
        responses[resp] += 1
    
    print("\n📊 STATISTICS")
    print("=" * 60)
    print(f"Total Comments: {len(comments)}\n")
    
    print("BY CATEGORY:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  • {cat.capitalize()}: {count}")
    
    print("\nBY RESPONSE STATUS:")
    for resp, count in sorted(responses.items(), key=lambda x: -x[1]):
        print(f"  • {resp.replace('_', ' ').title()}: {count}")
    
    print("=" * 60)

def show_flagged(comments):
    """Show sales inquiries flagged for review"""
    flagged = [c for c in comments if c.get("response_status") == "flagged_for_manual_review"]
    
    if not flagged:
        print("✅ No items flagged for review")
        return
    
    print(f"\n⚠️  REQUIRES MANUAL ACTION ({len(flagged)} items)")
    print("=" * 60)
    for i, c in enumerate(flagged, 1):
        print(f"\n{i}. @{c.get('commenter', 'Unknown')}")
        print(f"   Time: {c.get('timestamp', 'N/A')}")
        print(f"   Message: {c.get('text', 'N/A')[:100]}...")
        if c.get('response_text'):
            print(f"   Note: {c.get('response_text', '')[:80]}...")
    print("\n" + "=" * 60)

def show_by_category(comments, category):
    """Show comments by category"""
    filtered = [c for c in comments if c.get("category") == category]
    
    if not filtered:
        print(f"No comments in category: {category}")
        return
    
    print(f"\n{category.upper()} ({len(filtered)} comments)")
    print("=" * 60)
    for i, c in enumerate(filtered, 1):
        print(f"\n{i}. @{c.get('commenter', 'Unknown')}")
        print(f"   {c.get('text', '')[:80]}...")
        print(f"   Response: {c.get('response_status', 'N/A')}")
    print("\n" + "=" * 60)

def main():
    """Parse arguments and run queries"""
    if len(sys.argv) < 2:
        print("YouTube Comments Query Tool")
        print("\nUsage:")
        print("  python3 query-comments.py --stats [--today]")
        print("  python3 query-comments.py --flagged [--today]")
        print("  python3 query-comments.py --category CATEGORY [--today]")
        print("\nExamples:")
        print("  python3 query-comments.py --stats")
        print("  python3 query-comments.py --flagged --today")
        print("  python3 query-comments.py --category question")
        return
    
    # Parse arguments
    filter_today = "--today" in sys.argv
    
    # Load comments
    comments = load_comments(filter_today=filter_today)
    print(f"📁 Loaded {len(comments)} comments {('(today)' if filter_today else '')}")
    
    # Show stats
    if "--stats" in sys.argv:
        show_stats(comments)
    
    # Show flagged
    elif "--flagged" in sys.argv:
        show_flagged(comments)
    
    # Show by category
    elif "--category" in sys.argv:
        idx = sys.argv.index("--category")
        if idx + 1 < len(sys.argv):
            category = sys.argv[idx + 1]
            show_by_category(comments, category)

if __name__ == "__main__":
    main()
