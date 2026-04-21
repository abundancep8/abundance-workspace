#!/usr/bin/env python3
"""
YouTube Comment Monitor - Report & Review Tool
Displays stats, flagged comments, and recent activity
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import sys

CACHE_DIR = Path("/Users/abundance/.openclaw/workspace/.cache")
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"

def load_comments():
    """Load all logged comments."""
    comments = []
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r') as f:
            for line in f:
                try:
                    comments.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return comments

def load_state():
    """Load monitoring state."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'━' * 70}")
    print(f"  {title}")
    print(f"{'━' * 70}\n")

def generate_report(limit_days=None):
    """Generate a comprehensive report."""
    comments = load_comments()
    state = load_state()
    
    print_header("📊 YouTube Comment Monitor - Report")
    
    # Overall stats
    print(f"Total Comments Processed: {len(comments)}")
    print(f"Auto-Responses Sent: {state.get('auto_responded', 0)}")
    print(f"Flagged for Review: {state.get('flagged_for_review', 0)}")
    if state.get('last_checked'):
        print(f"Last Checked: {state['last_checked']}")
    
    # Category breakdown
    categories = defaultdict(int)
    responses = defaultdict(int)
    
    for comment in comments:
        categories[comment['category']] += 1
        responses[comment['response_status']] += 1
    
    print_header("📈 By Category")
    for cat in ["questions", "praise", "spam", "sales", "other"]:
        if cat in categories:
            print(f"  {cat.capitalize():15} {categories[cat]:3} ({categories[cat]*100//len(comments):2}%)")
    
    print_header("✉️  Response Status")
    for status in ["auto_responded", "flagged_for_review", "spam_filtered", "none"]:
        if status in responses:
            print(f"  {status.replace('_', ' ').capitalize():25} {responses[status]:3}")
    
    # Flagged comments (Sales)
    flagged = [c for c in comments if c['response_status'] == "flagged_for_review"]
    if flagged:
        print_header("🚩 Flagged for Review (Partnership/Sales Inquiries)")
        for i, comment in enumerate(flagged[-10:], 1):  # Last 10
            print(f"\n  [{i}] {comment['author']}")
            print(f"      {comment['text'][:80]}...")
            print(f"      Category: {comment['category']} | Confidence: {comment['confidence']:.2f}")
            print(f"      Logged: {comment['timestamp']}")
    
    # Spam samples
    spam = [c for c in comments if c['response_status'] == "spam_filtered"]
    if spam:
        print_header("🚫 Spam Examples (Last 5)")
        for i, comment in enumerate(spam[-5:], 1):
            print(f"\n  [{i}] {comment['author']}")
            print(f"      {comment['text'][:80]}...")
    
    # Recent activity
    recent = sorted(comments, key=lambda x: x['timestamp'], reverse=True)[:5]
    if recent:
        print_header("⏱️  Recent Comments (Last 5)")
        for i, comment in enumerate(recent, 1):
            status_icon = {
                "auto_responded": "✅",
                "flagged_for_review": "🚩",
                "spam_filtered": "🚫",
                "none": "•"
            }.get(comment['response_status'], "•")
            
            print(f"  {status_icon} [{comment['category'].capitalize()}] {comment['author']}")
            print(f"     {comment['text'][:70]}...")

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--flagged":
        # Show only flagged comments in detail
        comments = load_comments()
        flagged = [c for c in comments if c['response_status'] == "flagged_for_review"]
        
        if not flagged:
            print("✓ No comments flagged for review")
            return
        
        print_header("🚩 Flagged Comments - Full Details")
        for i, comment in enumerate(flagged, 1):
            print(f"\n[{i}] {comment['author']}")
            print(f"    Text: {comment['text']}")
            print(f"    Category: {comment['category']}")
            print(f"    Confidence: {comment['confidence']:.2%}")
            print(f"    ID: {comment['comment_id']}")
            print(f"    Logged: {comment['timestamp']}")
    else:
        generate_report()

if __name__ == "__main__":
    main()
