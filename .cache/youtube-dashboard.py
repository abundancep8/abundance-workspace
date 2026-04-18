#!/usr/bin/env python3
"""
YouTube Comment Monitor Dashboard
Displays summary of comments and responses
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

def print_dashboard():
    """Print a formatted dashboard of YouTube comments"""
    
    workspace = Path("/Users/abundance/.openclaw/workspace")
    cache_dir = workspace / ".cache"
    jsonl_file = cache_dir / "youtube-comments.jsonl"
    
    if not jsonl_file.exists():
        print("❌ No comments logged yet. Run youtube-monitor.py first.")
        return
    
    # Parse comments
    comments = []
    try:
        with open(jsonl_file) as f:
            for line in f:
                if line.strip():
                    try:
                        comments.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"❌ Error reading JSONL: {e}")
        return
    
    if not comments:
        print("❌ No valid comments in log")
        return
    
    # Aggregate stats
    stats = defaultdict(int)
    response_stats = defaultdict(int)
    category_stats = defaultdict(int)
    recent_comments = []
    
    for comment in comments:
        cat = comment.get("category_name", "Unknown")
        resp = comment.get("response_status", "unknown")
        
        stats["total"] += 1
        category_stats[cat] += 1
        response_stats[resp] += 1
        
        # Collect recent comments (last 5)
        if len(recent_comments) < 5:
            recent_comments.append(comment)
    
    # Get latest stats file
    stats_file = cache_dir / "youtube-monitor-stats.json"
    latest_stats = {}
    if stats_file.exists():
        try:
            with open(stats_file) as f:
                latest_stats = json.load(f)
        except:
            pass
    
    # Print dashboard
    print("\n" + "="*70)
    print("📺 YOUTUBE COMMENT MONITOR DASHBOARD")
    print("="*70)
    print(f"Channel: Concessa Obvius (@ConcessaObvius)")
    print(f"📊 Total Comments Processed: {stats['total']}")
    print(f"⏰ Last Update: {latest_stats.get('timestamp', 'Never')}")
    print()
    
    # Category breakdown
    print("📋 BY CATEGORY:")
    for cat in sorted(category_stats.keys()):
        count = category_stats[cat]
        pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
        emoji = {
            "Questions": "❓",
            "Praise": "🙌",
            "Spam": "🚫",
            "Sales": "🤝",
            "1_questions": "❓",
            "2_praise": "🙌",
            "3_spam": "🚫",
            "4_sales": "🤝",
        }.get(cat, "📌")
        print(f"   {emoji} {cat}: {count} ({pct:.1f}%)")
    print()
    
    # Response breakdown
    print("💬 RESPONSE STATUS:")
    for resp in sorted(response_stats.keys()):
        count = response_stats[resp]
        emoji = {
            "auto_response_queued": "✅",
            "auto_responded": "✅",
            "flagged_for_review": "🚩",
            "flagged_spam_delete": "🗑️",
            "none": "⏭️"
        }.get(resp, "❓")
        print(f"   {emoji} {resp}: {count}")
    print()
    
    # Summary
    auto_responses = response_stats.get("auto_response_queued", 0) + response_stats.get("auto_responded", 0)
    flagged = response_stats.get("flagged_for_review", 0)
    print("📈 SUMMARY:")
    print(f"   Auto-responses: {auto_responses}")
    print(f"   Flagged for review: {flagged}")
    print(f"   Spam/deleted: {response_stats.get('flagged_spam_delete', 0)}")
    print()
    
    # Recent comments
    if recent_comments:
        print("🕐 RECENT COMMENTS:")
        for i, comment in enumerate(recent_comments, 1):
            commenter = comment.get("commenter", "Unknown")
            text = comment.get("comment_text", "")[:60]
            cat = comment.get("category_name", "?")
            print(f"   {i}. [{cat}] {commenter}: {text}...")
        print()
    
    print("="*70)
    print(f"📁 Full log: {jsonl_file}")
    print(f"📊 Stats: {cache_dir}/youtube-monitor-stats.json")
    print("="*70 + "\n")


def count_by_date():
    """Show comment counts by date"""
    workspace = Path("/Users/abundance/.openclaw/workspace")
    cache_dir = workspace / ".cache"
    jsonl_file = cache_dir / "youtube-comments.jsonl"
    
    if not jsonl_file.exists():
        return
    
    dates = defaultdict(int)
    try:
        with open(jsonl_file) as f:
            for line in f:
                if line.strip():
                    try:
                        comment = json.loads(line)
                        ts = comment.get("timestamp", "")
                        if ts:
                            date = ts.split("T")[0]
                            dates[date] += 1
                    except:
                        continue
    except:
        return
    
    if dates:
        print("📅 COMMENTS BY DATE:")
        for date in sorted(dates.keys(), reverse=True)[:10]:
            print(f"   {date}: {dates[date]} comments")
        print()


if __name__ == "__main__":
    print_dashboard()
    count_by_date()
