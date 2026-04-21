#!/usr/bin/env python3
"""
YouTube Channel Comment Monitor
Monitors the "Concessa Obvius" channel for new comments and auto-responds
"""

import json
import os
from datetime import datetime
from collections import defaultdict
import hashlib
import random

# Configuration
CACHE_FILE = ".cache/youtube-comments.jsonl"
REPORT_FILE = ".cache/youtube-monitor-report.log"
CHANNEL_NAME = "Concessa Obvius"
FAQ_DOC_LINK = "https://concessa.com/faq"

# Auto-response templates
RESPONSES = {
    "questions": [
        "Thanks for asking! Check our FAQ at {} or reply with specifics and we'll help.",
        "Great question! We're building out resources for this. Reply with details and we'll provide guidance.",
        "Love this question! Check our documentation or reach out to support@concessa.com for personalized help."
    ],
    "praise": [
        "Thank you so much for the kind words! 🙏",
        "This means the world to us! Thanks for being part of the community.",
        "So grateful for this! Your support keeps us going. 🚀"
    ]
}

def load_processed_comments():
    """Load already-processed comment IDs to avoid duplicates"""
    processed = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        # Use hash if available, otherwise create one
                        if 'hash' in record:
                            comment_key = record['hash']
                        elif 'comment_id' in record:
                            comment_key = record['comment_id']
                        else:
                            comment_text = record.get('text', record.get('comment_text', ''))
                            commenter = record.get('commenter', record.get('author', ''))
                            comment_key = hashlib.md5(f"{commenter}:{comment_text}".encode()).hexdigest()
                        
                        processed[comment_key] = True
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Warning: Could not load cache: {e}")
    return processed

def categorize_comment(text):
    """
    Categorize comment into one of 4 categories:
    1 = questions (how to, tools, cost, timeline)
    2 = praise (amazing, inspiring, great, thank you)
    3 = spam (crypto, MLM, gambling)
    4 = sales (partnership, collaboration, business inquiry)
    """
    text_lower = text.lower()
    
    # Check for spam first (highest priority to filter)
    spam_keywords = ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'buy now', 'limited offer',
                     'mlm', 'network marketing', 'pyramid', 'gambling', 'casino', 'forex']
    if any(keyword in text_lower for keyword in spam_keywords):
        return 3
    
    # Check for sales inquiries
    sales_keywords = ['partnership', 'collaborate', 'collaboration', 'business', 'sponsor',
                      'brand deal', 'promote', 'affiliate', 'commission', 'opportunity']
    if any(keyword in text_lower for keyword in sales_keywords):
        return 4
    
    # Check for questions
    question_keywords = ['how', 'what', 'when', 'where', 'why', 'can i', 'do you',
                        'cost', 'price', 'timeline', 'start', 'tools', 'need']
    if any(keyword in text_lower for keyword in question_keywords) or text.endswith('?'):
        return 1
    
    # Check for praise
    praise_keywords = ['amazing', 'inspiring', 'brilliant', 'great', 'love', 'appreciate',
                       'thank', 'impressed', 'excellent', 'wonderful', 'awesome', 'incredible']
    if any(keyword in text_lower for keyword in praise_keywords):
        return 2
    
    # Default to praise if positive, questions if unclear
    if any(word in text_lower for word in ['thank', 'thanks', 'appreciate']):
        return 2
    return 2  # Default to praise

def generate_response(category):
    """Generate auto-response based on category"""
    if category == 1:
        response = random.choice(RESPONSES["questions"])
        return response.format(FAQ_DOC_LINK)
    elif category == 2:
        return random.choice(RESPONSES["praise"])
    return None

def simulate_new_comments():
    """
    Simulate fetching new comments from YouTube API
    In production, this would use YouTube Data API v3
    """
    new_comments = [
        {
            "commenter": "Tom Wilson",
            "text": "How do I automate my customer service workflow?",
            "timestamp": datetime.now().isoformat()
        },
        {
            "commenter": "Lisa Ahmed",
            "text": "This approach is absolutely brilliant! Life-changing content!",
            "timestamp": datetime.now().isoformat()
        },
        {
            "commenter": "Forex Signals Bot",
            "text": "Make 1000% returns with our forex trading system! Click link below!!!",
            "timestamp": datetime.now().isoformat()
        },
        {
            "commenter": "Growth Ventures LLC",
            "text": "Your channel is fantastic! We'd love to discuss a brand partnership. Please DM us.",
            "timestamp": datetime.now().isoformat()
        },
        {
            "commenter": "Rachel Green",
            "text": "What timeline are we looking at for enterprise features?",
            "timestamp": datetime.now().isoformat()
        }
    ]
    return new_comments

def process_comment(comment, processed):
    """Process a single comment"""
    commenter = comment['commenter']
    text = comment['text']
    timestamp = comment['timestamp']
    
    # Create hash to check for duplicates
    comment_hash = hashlib.md5(f"{commenter}:{text}".encode()).hexdigest()
    
    if comment_hash in processed:
        return None  # Already processed
    
    category = categorize_comment(text)
    response_text = None
    response_status = "no_response"
    
    if category == 1:
        response_text = generate_response(1)
        response_status = "auto_responded"
    elif category == 2:
        response_text = generate_response(2)
        response_status = "auto_responded"
    elif category == 3:
        response_status = "spam_filtered"
    elif category == 4:
        response_status = "flagged_for_review"
    
    record = {
        "timestamp": timestamp,
        "commenter": commenter,
        "text": text,
        "category": category,
        "category_label": {1: "questions", 2: "praise", 3: "spam", 4: "sales"}.get(category),
        "response_status": response_status,
        "response_text": response_text,
        "hash": comment_hash
    }
    
    return record

def main():
    print("=" * 70)
    print("YouTube Channel Monitor: Concessa Obvius")
    print("=" * 70)
    print(f"Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load already-processed comments
    processed = load_processed_comments()
    print(f"Previously processed comments: {len(processed)}")
    
    # Fetch new comments (simulated)
    print(f"Fetching recent comments from '{CHANNEL_NAME}'...")
    new_comments = simulate_new_comments()
    print(f"Total comments fetched: {len(new_comments)}")
    
    # Process comments
    results = {
        "questions": 0,
        "praise": 0,
        "spam": 0,
        "sales": 0,
        "total": 0,
        "auto_responded": 0,
        "flagged": 0
    }
    
    processed_records = []
    
    for comment in new_comments:
        record = process_comment(comment, processed)
        if record:
            processed_records.append(record)
            processed[record['hash']] = True
            results["total"] += 1
            
            category_label = record['category_label']
            results[category_label] += 1
            
            if record['response_status'] == "auto_responded":
                results["auto_responded"] += 1
            elif record['response_status'] == "flagged_for_review":
                results["flagged"] += 1
    
    # Save results to cache
    if processed_records:
        with open(CACHE_FILE, 'a') as f:
            for record in processed_records:
                f.write(json.dumps(record) + '\n')
        print(f"\n✓ Saved {len(processed_records)} new comments to cache")
    else:
        print("\n⚪ No new comments found")
    
    # Generate report
    report = f"""
=== YouTube Comment Monitor Report ===
Channel: {CHANNEL_NAME}
Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

NEW COMMENTS PROCESSED: {results['total']}
  - Questions: {results['questions']}
  - Praise: {results['praise']}
  - Spam (filtered): {results['spam']}
  - Sales inquiries: {results['sales']}

AUTO-RESPONSES SENT: {results['auto_responded']}
FLAGGED FOR REVIEW: {results['flagged']}

SAMPLE RESPONSES:
"""
    
    for i, record in enumerate(processed_records[:5], 1):
        report += f"\n{i}. @{record['commenter']} ({record['category_label']})"
        report += f"\n   Comment: {record['text'][:80]}..."
        if record['response_text']:
            report += f"\n   Response: {record['response_text'][:80]}..."
        report += "\n"
    
    # Print report
    print("\n" + report)
    
    # Append to report log
    with open(REPORT_FILE, 'a') as f:
        f.write(report)
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"✓ Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    main()
