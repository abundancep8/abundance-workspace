#!/usr/bin/env python3
"""
YouTube Comment Monitor - Analytics Dashboard
View logs, generate reports, and analyze comment trends
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

WORKSPACE_ROOT = Path.home() / ".openclaw" / "workspace"
CACHE_DIR = WORKSPACE_ROOT / ".cache"
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"

def load_logs():
    """Load all comments from JSONL file."""
    comments = []
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            for line in f:
                try:
                    comments.append(json.loads(line))
                except:
                    pass
    return comments

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def analyze_by_category(comments):
    """Analyze comments by category."""
    categories = Counter(c.get("category", "unknown") for c in comments)
    print_header("COMMENTS BY CATEGORY")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        pct = (count / len(comments) * 100) if comments else 0
        emoji = {"questions": "❓", "praise": "👏", "spam": "🚫", "sales": "🚩"}.get(cat, "•")
        print(f"  {emoji} {cat:15} : {count:5} ({pct:5.1f}%)")

def analyze_by_status(comments):
    """Analyze responses by status."""
    statuses = Counter(c.get("response_status", "unknown") for c in comments)
    print_header("RESPONSE STATUS")
    for status, count in sorted(statuses.items(), key=lambda x: -x[1]):
        pct = (count / len(comments) * 100) if comments else 0
        print(f"  • {status:20} : {count:5} ({pct:5.1f}%)")

def analyze_time(comments):
    """Analyze comments over time."""
    print_header("COMMENTS OVER TIME")
    
    # Group by hour
    hourly = Counter()
    for comment in comments:
        ts = comment.get("timestamp", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                hour = dt.strftime("%Y-%m-%d %H:00")
                hourly[hour] += 1
            except:
                pass
    
    for hour in sorted(hourly.keys()):
        count = hourly[hour]
        bar = "█" * min(count, 30)
        print(f"  {hour} | {bar} ({count})")

def find_flagged(comments):
    """Find sales inquiries flagged for review."""
    print_header("FLAGGED FOR REVIEW (SALES INQUIRIES)")
    flagged = [c for c in comments if c.get("response_status") == "flagged_for_review"]
    
    if not flagged:
        print("  ✅ No flagged comments - all clear!")
        return
    
    for comment in flagged[-10:]:  # Last 10
        commenter = comment.get("commenter", "Unknown")
        text = comment.get("text", "")[:60]
        ts = comment.get("timestamp", "")
        print(f"\n  👤 {commenter}")
        print(f"     💬 {text}...")
        print(f"     📅 {ts[:10]}")

def find_questions(comments):
    """Find unanswered questions."""
    print_header("RECENT QUESTIONS")
    questions = [c for c in comments if c.get("category") == "questions"]
    
    if not questions:
        print("  No questions found")
        return
    
    for comment in questions[-5:]:  # Last 5
        commenter = comment.get("commenter", "Unknown")
        text = comment.get("text", "")[:70]
        responded = "✅" if comment.get("response_status") == "auto_responded" else "⏳"
        print(f"\n  {responded} {commenter}")
        print(f"     {text}...")

def summary(comments):
    """Print summary stats."""
    print_header("SUMMARY STATISTICS")
    
    total = len(comments)
    auto_responded = len([c for c in comments if c.get("response_status") == "auto_responded"])
    flagged = len([c for c in comments if c.get("response_status") == "flagged_for_review"])
    spam = len([c for c in comments if c.get("category") == "spam"])
    
    print(f"  📊 Total comments logged    : {total}")
    print(f"  ✅ Auto-responses sent      : {auto_responded} ({auto_responded/total*100:.1f}%)" if total else "  ✅ Auto-responses sent      : 0")
    print(f"  🚩 Flagged for review       : {flagged}")
    print(f"  🚫 Spam filtered            : {spam}")
    print(f"  📅 Last update              : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Run analytics."""
    comments = load_logs()
    
    if not comments:
        print("📭 No comments logged yet. Run the monitor to collect data.")
        print(f"    Log file: {LOG_FILE}")
        return
    
    # Print reports
    summary(comments)
    analyze_by_category(comments)
    analyze_by_status(comments)
    analyze_time(comments)
    find_questions(comments)
    find_flagged(comments)
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
