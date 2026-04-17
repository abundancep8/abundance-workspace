#!/usr/bin/env python3
"""
YouTube Comment Monitor - Log Viewer & Analyzer
Analyze recorded comments from youtube-comments.jsonl
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import sys

JSONL_FILE = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-comments.jsonl"

def load_comments(days=None):
    """Load comments from JSONL file."""
    if not JSONL_FILE.exists():
        print(f"No log file found: {JSONL_FILE}")
        return []
    
    comments = []
    cutoff = None
    if days:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    with open(JSONL_FILE, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            if cutoff and entry['timestamp'] < cutoff:
                continue
            comments.append(entry)
    
    return comments

def print_summary(comments):
    """Print summary statistics."""
    if not comments:
        print("No comments to analyze.")
        return
    
    stats = defaultdict(int)
    by_category = defaultdict(int)
    responses = defaultdict(int)
    
    for comment in comments:
        stats['total'] += 1
        cat = comment['category']
        by_category[cat] += 1
        responses[comment['response_status']] += 1
    
    print("\n" + "="*60)
    print("YOUTUBE COMMENT ANALYSIS")
    print("="*60)
    print(f"Total comments: {stats['total']}")
    print(f"Time range: {comments[0]['timestamp']} to {comments[-1]['timestamp']}")
    
    print(f"\nBy Category:")
    for cat in sorted(by_category.keys()):
        count = by_category[cat]
        pct = (count / stats['total']) * 100
        print(f"  {cat.capitalize():15} {count:3} ({pct:5.1f}%)")
    
    print(f"\nBy Response Status:")
    for status in sorted(responses.keys()):
        count = responses[status]
        pct = (count / stats['total']) * 100
        print(f"  {status.capitalize():20} {count:3} ({pct:5.1f}%)")
    
    print("="*60 + "\n")

def print_flagged(comments):
    """Print comments flagged for review."""
    flagged = [c for c in comments if c['response_status'] == 'flagged_for_review']
    
    if not flagged:
        print("No comments flagged for review.\n")
        return
    
    print(f"\n{len(flagged)} COMMENTS FLAGGED FOR REVIEW")
    print("="*60)
    
    for comment in flagged:
        print(f"\n[{comment['category'].upper()}]")
        print(f"From: {comment['commenter']}")
        print(f"Date: {comment['published_at']}")
        print(f"Text: {comment['text'][:200]}...")
        print(f"Engagement: {comment['like_count']} likes, {comment['reply_count']} replies")
        print("-"*60)

def print_unanswered(comments):
    """Print questions/praise that weren't auto-responded."""
    unanswered = [
        c for c in comments 
        if c['category'] in ['question', 'praise'] 
        and c['response_status'] != 'sent'
    ]
    
    if not unanswered:
        print("All questions and praise have been responded to.\n")
        return
    
    print(f"\n{len(unanswered)} UNANSWERED QUESTIONS/PRAISE")
    print("="*60)
    
    for comment in unanswered:
        print(f"\n[{comment['category'].upper()}] Status: {comment['response_status']}")
        print(f"From: {comment['commenter']}")
        print(f"Date: {comment['published_at']}")
        print(f"Text: {comment['text'][:200]}...")
        print("-"*60)

def export_category(comments, category, output_file=None):
    """Export comments of a specific category."""
    filtered = [c for c in comments if c['category'] == category]
    
    if output_file:
        with open(output_file, 'w') as f:
            for comment in filtered:
                f.write(json.dumps(comment) + '\n')
        print(f"Exported {len(filtered)} {category} comments to {output_file}")
    else:
        print(f"\n{len(filtered)} {category.upper()} COMMENTS")
        print("="*60)
        for comment in filtered:
            print(f"\n{comment['commenter']}: {comment['text']}")
            print(f"Likes: {comment['like_count']} | Replies: {comment['reply_count']}")

def print_help():
    """Print usage instructions."""
    print("""
YouTube Comment Monitor - Log Viewer

Usage:
  python3 youtube-log-viewer.py [command] [options]

Commands:
  summary [days]       - Summary statistics (default: all time)
  flagged              - Show comments flagged for sales review
  unanswered           - Show unanswered questions/praise
  export [category]    - Export comments by category
  questions            - Show all questions
  praise               - Show all praise
  spam                 - Show all spam
  sales                - Show all sales inquiries
  
Examples:
  python3 youtube-log-viewer.py summary          # All-time stats
  python3 youtube-log-viewer.py summary 7        # Last 7 days
  python3 youtube-log-viewer.py flagged          # Sales to review
  python3 youtube-log-viewer.py questions        # All questions
    """)

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print_help()
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'summary':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else None
        comments = load_comments(days=days)
        print_summary(comments)
    
    elif command == 'flagged':
        comments = load_comments()
        print_flagged(comments)
    
    elif command == 'unanswered':
        comments = load_comments()
        print_unanswered(comments)
    
    elif command in ['questions', 'praise', 'spam', 'sales', 'other']:
        comments = load_comments()
        export_category(comments, command)
    
    elif command == 'export':
        category = sys.argv[2] if len(sys.argv) > 2 else None
        if not category:
            print("Usage: export [category] [output_file]")
            sys.exit(1)
        output_file = sys.argv[3] if len(sys.argv) > 3 else f"comments-{category}.jsonl"
        comments = load_comments()
        export_category(comments, category, output_file)
    
    else:
        print(f"Unknown command: {command}")
        print_help()
        sys.exit(1)
