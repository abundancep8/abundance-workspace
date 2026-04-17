#!/usr/bin/env python3
"""
Query YouTube comment logs by category, date, or commenter
Useful for finding specific comments
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

COMMENTS_LOG = Path(".cache/youtube-comments.jsonl")

def load_comments():
    if not COMMENTS_LOG.exists():
        print("No comments logged yet.")
        return []
    
    comments = []
    for line in COMMENTS_LOG.read_text().strip().split('\n'):
        if line:
            comments.append(json.loads(line))
    return comments

def show_help():
    print("""
Usage: python3 youtube-query.py [command] [args]

Commands:
  category CATEGORY       Show all comments in a category
    Categories: question, praise, spam, sales
    
  status STATUS          Show comments with a response status
    Statuses: sent, flagged, none, failed
    
  from DATE              Show comments from a specific date (YYYY-MM-DD)
  
  since DAYS             Show comments from the last N days
  
  commenter NAME         Show all comments from a user
  
  flagged                Show all flagged comments (sales inquiries)
  
  unanswered             Show comments without responses
  
  all                    Show all comments
  
  stats                  Show brief statistics

Examples:
  python3 youtube-query.py category question
  python3 youtube-query.py commenter "John Doe"
  python3 youtube-query.py flagged
  python3 youtube-query.py since 7
""")

def format_comment(comment):
    print(f"\n  {comment['commenter']} ({comment['category'].upper()})")
    print(f"  Response: {comment['response_status']}")
    print(f"  Time: {comment['timestamp']}")
    print(f"  Text: {comment['text'][:100]}")
    if len(comment['text']) > 100:
        print(f"        {comment['text'][100:200]}")

def main():
    comments = load_comments()
    
    if not comments:
        print("No comments logged yet.")
        return
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    arg = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else None
    
    results = []
    
    if command == "category" and arg:
        results = [c for c in comments if c['category'] == arg]
        print(f"\n📂 {arg.upper()} COMMENTS ({len(results)}):")
    
    elif command == "status" and arg:
        results = [c for c in comments if c['response_status'] == arg]
        print(f"\n📌 {arg.upper()} COMMENTS ({len(results)}):")
    
    elif command == "from" and arg:
        results = [c for c in comments if c['timestamp'].startswith(arg)]
        print(f"\n📅 COMMENTS FROM {arg} ({len(results)}):")
    
    elif command == "since" and arg:
        try:
            days = int(arg)
            cutoff = datetime.utcnow().timestamp() - (days * 86400)
            results = [c for c in comments 
                      if datetime.fromisoformat(c['timestamp'].replace('Z', '+00:00')).timestamp() > cutoff]
            print(f"\n📅 COMMENTS FROM LAST {days} DAYS ({len(results)}):")
        except ValueError:
            print(f"Invalid number of days: {arg}")
            return
    
    elif command == "commenter" and arg:
        results = [c for c in comments if arg.lower() in c['commenter'].lower()]
        print(f"\n👤 COMMENTS FROM '{arg}' ({len(results)}):")
    
    elif command == "flagged":
        results = [c for c in comments if c['response_status'] == 'flagged']
        print(f"\n🚩 FLAGGED COMMENTS ({len(results)}):")
    
    elif command == "unanswered":
        results = [c for c in comments if c['response_status'] == 'none']
        print(f"\n❓ UNANSWERED COMMENTS ({len(results)}):")
    
    elif command == "all":
        results = comments
        print(f"\n📋 ALL COMMENTS ({len(results)}):")
    
    elif command == "stats":
        by_cat = defaultdict(int)
        by_status = defaultdict(int)
        for c in comments:
            by_cat[c['category']] += 1
            by_status[c['response_status']] += 1
        
        print(f"\nTotal: {len(comments)} comments")
        print("\nBy category:")
        for cat, count in sorted(by_cat.items()):
            print(f"  {cat}: {count}")
        print("\nBy response status:")
        for status, count in sorted(by_status.items()):
            print(f"  {status}: {count}")
        return
    
    else:
        show_help()
        return
    
    # Display results
    print("-" * 70)
    if not results:
        print("No comments found.")
    else:
        for comment in results[:20]:  # Limit to 20
            format_comment(comment)
        
        if len(results) > 20:
            print(f"\n... and {len(results) - 20} more")

if __name__ == '__main__':
    main()
