#!/usr/bin/env python3
"""
YouTube Comment Monitor - Dashboard
Display stats and recent comments from the monitoring logs
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

WORKSPACE = Path.home() / ".openclaw" / "workspace"
COMMENTS_LOG = WORKSPACE / ".cache" / "youtube-comments.jsonl"
STATE_FILE = WORKSPACE / ".cache" / "youtube-monitor-state.json"

def load_comments():
    """Load all comments from log file."""
    comments = []
    if COMMENTS_LOG.exists():
        try:
            with open(COMMENTS_LOG) as f:
                for line in f:
                    if line.strip():
                        comments.append(json.loads(line))
        except Exception as e:
            print(f"Error loading comments: {e}")
    return comments

def print_header(text):
    """Print header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")

def print_stats():
    """Print comment statistics."""
    comments = load_comments()
    
    if not comments:
        print("No comments recorded yet.")
        return
    
    # Calculate stats
    stats = defaultdict(int)
    response_stats = defaultdict(int)
    
    for comment in comments:
        stats[comment.get('category', 'unknown')] += 1
        response_stats[comment.get('response_status', 'unknown')] += 1
    
    # Get time range
    timestamps = [c.get('timestamp') for c in comments if c.get('timestamp')]
    if timestamps:
        first = min(timestamps)
        last = max(timestamps)
        print(f"📊 Comment Statistics ({first} to {last})")
    else:
        print(f"📊 Comment Statistics ({len(comments)} total)")
    
    print(f"\n  Total comments: {len(comments)}\n")
    
    print("  By Category:")
    for category in ['question', 'praise', 'spam', 'sales', 'other']:
        count = stats.get(category, 0)
        if count > 0:
            pct = (count / len(comments)) * 100
            bar = "█" * int(pct / 5)
            print(f"    • {category.ljust(10)} {count:3d} ({pct:5.1f}%) {bar}")
    
    print("\n  By Response Status:")
    for status in ['auto_responded', 'flagged_for_review', 'none']:
        count = response_stats.get(status, 0)
        if count > 0:
            pct = (count / len(comments)) * 100
            print(f"    • {status.ljust(20)} {count:3d} ({pct:5.1f}%)")
    
    # Show top commenters
    commenters = defaultdict(int)
    for comment in comments:
        commenters[comment.get('commenter', 'Unknown')] += 1
    
    if commenters:
        print("\n  Top Commenters:")
        for name, count in sorted(commenters.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    • {name}: {count} comment{'s' if count != 1 else ''}")

def print_recent(limit=10):
    """Print recent comments."""
    comments = load_comments()
    
    if not comments:
        print("No comments recorded yet.")
        return
    
    # Sort by timestamp (newest first)
    comments_sorted = sorted(
        comments,
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )[:limit]
    
    print(f"\n📝 Recent Comments (last {limit})\n")
    
    for i, comment in enumerate(comments_sorted, 1):
        category = comment.get('category', 'unknown').upper()
        status = comment.get('response_status', 'none')
        author = comment.get('commenter', 'Unknown')
        text = comment.get('text', '')[:70]
        timestamp = comment.get('timestamp', '')[:10]
        
        # Status emoji
        if status == 'auto_responded':
            status_emoji = "✅"
        elif status == 'flagged_for_review':
            status_emoji = "🚩"
        else:
            status_emoji = "➖"
        
        # Category colors (visual)
        category_color = {
            'QUESTION': '❓',
            'PRAISE': '🌟',
            'SPAM': '🚫',
            'SALES': '💼',
            'OTHER': '❔'
        }.get(category, '?')
        
        print(f"{i}. [{timestamp}] {category_color} {status_emoji}")
        print(f"   {author}: {text}...")
        print(f"   [{category}] {status}\n")

def print_flagged():
    """Print flagged (sales) comments."""
    comments = load_comments()
    flagged = [c for c in comments if c.get('category') == 'sales' or c.get('response_status') == 'flagged_for_review']
    
    if not flagged:
        print("No flagged comments.")
        return
    
    print(f"\n🚩 Flagged for Review ({len(flagged)} total)\n")
    
    for i, comment in enumerate(flagged, 1):
        author = comment.get('commenter', 'Unknown')
        text = comment.get('text', '')
        timestamp = comment.get('timestamp', '')[:10]
        
        print(f"{i}. [{timestamp}] {author}")
        print(f"   {text}\n")

def print_last_run():
    """Print last run time."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
                last_check = state.get('last_check', 'Unknown')
                print(f"⏱️  Last check: {last_check}\n")
        except:
            pass

def main():
    """Main dashboard."""
    print_header("YouTube Comment Monitor Dashboard")
    
    print_last_run()
    print_stats()
    print_recent(limit=5)
    
    # Check for flagged comments
    comments = load_comments()
    flagged_count = len([c for c in comments if c.get('response_status') == 'flagged_for_review'])
    if flagged_count > 0:
        print(f"\n⚠️  {flagged_count} comment{'s' if flagged_count != 1 else ''} flagged for review!")
        response = input("\nView flagged comments? [y/N] ")
        if response.lower() == 'y':
            print_flagged()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
