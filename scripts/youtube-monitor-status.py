#!/usr/bin/env python3
"""
Quick status check for YouTube comment monitor
Shows stats, recent comments, and flagged items
"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace"
COMMENTS_LOG = WORKSPACE / ".cache" / "youtube-comments.jsonl"
STATE_FILE = WORKSPACE / ".cache" / ".youtube-monitor-state.json"

def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def main():
    if not COMMENTS_LOG.exists():
        print("❌ No comments logged yet. Run the monitor first.")
        return

    # Load comments
    comments = []
    with open(COMMENTS_LOG) as f:
        for line in f:
            comments.append(json.loads(line))

    if not comments:
        print("❌ No comments found in log.")
        return

    # Load state
    state = {}
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            state = json.load(f)

    # Calculate stats
    total = len(comments)
    by_category = {1: 0, 2: 0, 3: 0, 4: 0}
    responses_sent = 0
    flagged = []

    for c in comments:
        cat = c.get("category", 1)
        by_category[cat] += 1
        if c.get("auto_response_sent"):
            responses_sent += 1
        if cat == 4:
            flagged.append(c)

    # Print report
    print_header("📊 YOUTUBE COMMENT MONITOR STATUS")

    print(f"📝 Total comments tracked: {total}")
    print(f"⏱️  Last check: {state.get('last_check', 'Never')}")
    print(f"📁 Log file: {COMMENTS_LOG}")

    print_header("📋 COMMENTS BY CATEGORY")
    categories = {
        1: "Questions",
        2: "Praise",
        3: "Spam",
        4: "Sales/Partnerships"
    }

    for cat in [1, 2, 3, 4]:
        count = by_category[cat]
        name = categories[cat]
        bar = "█" * (count // 2) if count > 0 else ""
        print(f"  {name:20} {count:3} {bar}")

    print_header("✅ AUTOMATION STATS")
    print(f"  Auto-responses sent: {responses_sent}")
    print(f"  Questions answered: {by_category[1]}")
    print(f"  Praise acknowledged: {by_category[2]}")
    print(f"  Spam filtered: {by_category[3]}")

    if flagged:
        print_header(f"🚩 FLAGGED FOR REVIEW ({len(flagged)} items)")
        for i, comment in enumerate(flagged[-5:], 1):  # Show last 5
            print(f"\n  [{i}] {comment['commenter']}")
            print(f"      Video: {comment['video_id']}")
            text = comment['text'][:80]
            if len(comment['text']) > 80:
                text += "..."
            print(f"      Text: {text}")
            print(f"      Date: {comment['timestamp']}")

    print_header("📈 RECENT ACTIVITY")
    for i, comment in enumerate(comments[-3:], 1):
        cat_name = categories.get(comment.get("category"), "Unknown")
        print(f"  [{i}] {comment['commenter']} ({cat_name})")
        print(f"      {comment['text'][:70]}...")
        print()

    print(f"\n💡 Tip: Use 'jq' to query the JSONL log:")
    print(f"   jq 'select(.category==4)' {COMMENTS_LOG}  (show flagged items)")
    print(f"   jq '.commenter' {COMMENTS_LOG} | sort | uniq -c  (top commenters)")
    print()

if __name__ == "__main__":
    main()
