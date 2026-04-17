#!/usr/bin/env python3
"""
YouTube Comment Monitor - DEMO/SIMULATION VERSION
Shows how the system works with realistic mock data.
"""

import json
import os
from datetime import datetime, timedelta

# Mock comment data for demonstration
MOCK_COMMENTS = [
    {
        'comment_id': 'Ugz_B1A2C3D4',
        'video_id': 'dQw4w9WgXcQ',
        'author': 'Sarah Johnson',
        'text': 'This is amazing! The way you explained this was so inspiring. Love your work! ❤️',
        'timestamp': (datetime.now() - timedelta(hours=2)).isoformat() + 'Z',
        'likes': 12,
        'expected_category': 'praise'
    },
    {
        'comment_id': 'Ugx_A2B3C4D5',
        'video_id': 'dQw4w9WgXcQ',
        'author': 'Mike Chen',
        'text': 'How much did this cost to set up? What tools do you use?',
        'timestamp': (datetime.now() - timedelta(hours=5)).isoformat() + 'Z',
        'likes': 8,
        'expected_category': 'questions'
    },
    {
        'comment_id': 'Ugb_C3D4E5F6',
        'video_id': 'xyzABC123456',
        'author': 'Alex Rodriguez',
        'text': 'How long did the timeline take you? What was your workflow?',
        'timestamp': (datetime.now() - timedelta(hours=8)).isoformat() + 'Z',
        'likes': 3,
        'expected_category': 'questions'
    },
    {
        'comment_id': 'Ugc_D4E5F6G7',
        'video_id': 'xyzABC123456',
        'author': 'Emma Wilson',
        'text': 'Interested in partnership? We have a brand collaboration opportunity. DM us!',
        'timestamp': (datetime.now() - timedelta(hours=12)).isoformat() + 'Z',
        'likes': 1,
        'expected_category': 'sales'
    },
    {
        'comment_id': 'Ugd_E5F6G7H8',
        'video_id': 'defGHI456789',
        'author': 'Bitcoin Bro',
        'text': 'Make money fast! Join my crypto MLM! Click here now!!!',
        'timestamp': (datetime.now() - timedelta(days=1)).isoformat() + 'Z',
        'likes': 0,
        'expected_category': 'spam'
    },
    {
        'comment_id': 'Uge_F6G7H8I9',
        'video_id': 'defGHI456789',
        'author': 'David Park',
        'text': 'This is brilliant work! Absolutely fantastic. Thanks for sharing!',
        'timestamp': (datetime.now() - timedelta(days=1, hours=3)).isoformat() + 'Z',
        'likes': 15,
        'expected_category': 'praise'
    },
    {
        'comment_id': 'Ugf_G7H8I9J0',
        'video_id': 'jklMNO789012',
        'author': 'Lisa Martinez',
        'text': 'Can you provide more details on the tools you mentioned? Where can we find them?',
        'timestamp': (datetime.now() - timedelta(days=1, hours=6)).isoformat() + 'Z',
        'likes': 5,
        'expected_category': 'questions'
    },
    {
        'comment_id': 'Ugg_H8I9J0K1',
        'video_id': 'jklMNO789012',
        'author': 'James Thompson',
        'text': 'We have a collaboration opportunity for you. Visit my site: [link]',
        'timestamp': (datetime.now() - timedelta(days=2)).isoformat() + 'Z',
        'likes': 0,
        'expected_category': 'sales'
    },
    {
        'comment_id': 'Ugh_I9J0K1L2',
        'video_id': 'pqrSTU012345',
        'author': 'Nina Petrov',
        'text': 'Wonderful! This is exactly what I was looking for. Excellent quality!',
        'timestamp': (datetime.now() - timedelta(days=2, hours=4)).isoformat() + 'Z',
        'likes': 22,
        'expected_category': 'praise'
    },
    {
        'comment_id': 'Ugi_J0K1L2M3',
        'video_id': 'pqrSTU012345',
        'author': 'Tom Brown',
        'text': 'What timeline should I expect? How long does it typically take?',
        'timestamp': (datetime.now() - timedelta(days=3)).isoformat() + 'Z',
        'likes': 4,
        'expected_category': 'questions'
    }
]

RESPONSE_TEMPLATES = {
    'questions': [
        "Thanks for asking! This is a common question. Here's what you need to know: [Provide specific answer based on your question]",
        "Great inquiry! I'm happy to help. [Address your specific question about tools/timeline/cost]",
        "Perfect question! Here are some resources that might help: [Include relevant links or detailed explanation]"
    ],
    'praise': [
        "Thank you so much! Your support means the world to me! 🙏",
        "Wow, I really appreciate that! Comments like this fuel my passion to keep creating. ❤️",
        "This made my day! Thank you for the kind words! 🌟"
    ]
}

def categorize_comment(text):
    """Categorize comment (simplified)."""
    text_lower = text.lower()
    
    # Spam detection
    if any(k in text_lower for k in ['bitcoin', 'crypto', 'mlm', 'make money fast', 'click here']):
        return 'spam'
    
    # Sales detection
    if any(k in text_lower for k in ['partnership', 'collaboration', 'brand', 'visit my', 'dm']):
        return 'sales'
    
    # Praise detection
    if any(k in text_lower for k in ['amazing', 'love', 'great', 'awesome', 'inspiring', 'thank you', 'excellent', 'wonderful', '❤', '🔥']):
        return 'praise'
    
    # Questions detection
    if any(k in text_lower for k in ['?', 'how', 'what', 'where', 'tools', 'timeline', 'cost']):
        return 'questions'
    
    return 'questions'

def main():
    """Run the demo."""
    print("\n" + "=" * 70)
    print("  YouTube Comment Monitor - SIMULATION/DEMO MODE")
    print("  (Showing how the system works with realistic mock data)")
    print("=" * 70 + "\n")
    
    log_file = '/Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl'
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    stats = {
        'total_processed': 0,
        'auto_responses_sent': 0,
        'flagged_for_review': 0,
        'by_category': {
            'questions': 0,
            'praise': 0,
            'spam': 0,
            'sales': 0
        }
    }
    
    print("🎬 Processing mock comments from 'Concessa Obvius' channel...\n")
    
    for comment in MOCK_COMMENTS:
        category = categorize_comment(comment['text'])
        
        # Generate response for questions and praise
        if category in ['questions', 'praise']:
            response = RESPONSE_TEMPLATES[category][0]
            response_status = 'auto_responded'
            stats['auto_responses_sent'] += 1
        elif category == 'sales':
            response = None
            response_status = 'flagged'
            stats['flagged_for_review'] += 1
        else:  # spam
            response = None
            response_status = 'logged'
        
        # Log the comment
        record = {
            'timestamp': comment['timestamp'],
            'comment_id': comment['comment_id'],
            'commenter': comment['author'],
            'text': comment['text'],
            'category': category,
            'response_status': response_status,
            'response_sent': response is not None,
            'response_text': response,
            'likes': comment['likes']
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
        
        # Update stats
        stats['total_processed'] += 1
        stats['by_category'][category] += 1
        
        # Print summary
        print(f"📌 [{category.upper():8s}] @{comment['author']:15s}: {comment['text'][:55]:<55s}")
        if response:
            print(f"   ✅ Response: {response[:65]}...")
        elif category == 'sales':
            print(f"   🚩 FLAGGED FOR REVIEW - Possible partnership/collaboration offer")
        elif category == 'spam':
            print(f"   🔕 Filtered (spam)")
        print()
    
    # Generate report
    report = f"""
╔════════════════════════════════════════════════════════════╗
║          YouTube Comment Monitoring Report                 ║
║              "Concessa Obvius" Channel                      ║
║              (DEMO/SIMULATION MODE)                         ║
╚════════════════════════════════════════════════════════════╝

📊 SUMMARY STATISTICS
─────────────────────────────────────────────────────────────
Total Comments Processed:     {stats['total_processed']}
Auto-Responses Sent:          {stats['auto_responses_sent']}
Flagged for Manual Review:    {stats['flagged_for_review']}

📈 BREAKDOWN BY CATEGORY
─────────────────────────────────────────────────────────────
Questions:                    {stats['by_category']['questions']} ({stats['by_category']['questions'] * 100 // max(1, stats['total_processed']):>2d}%)
Praise:                       {stats['by_category']['praise']} ({stats['by_category']['praise'] * 100 // max(1, stats['total_processed']):>2d}%)
Spam:                         {stats['by_category']['spam']} ({stats['by_category']['spam'] * 100 // max(1, stats['total_processed']):>2d}%)
Sales/Partnerships:           {stats['by_category']['sales']} ({stats['by_category']['sales'] * 100 // max(1, stats['total_processed']):>2d}%)

📝 LOG FILE LOCATION
─────────────────────────────────────────────────────────────
{log_file}

🔍 NEXT STEPS
─────────────────────────────────────────────────────────────
1. Review flagged sales offers in the log file
2. Set up YouTube API key (see YOUTUBE_SETUP.md)
3. Run live monitoring:
   export YOUTUBE_API_KEY='your-key'
   python3 .cache/youtube_monitor.py

⏰ COMPLETION TIME (UTC)
─────────────────────────────────────────────────────────────
{datetime.utcnow().isoformat()}Z

═════════════════════════════════════════════════════════════
"""
    
    print(report)
    print(f"✅ Demo complete! Log file saved: {log_file}")
    print(f"\n📋 See {log_file} for full comment details in JSONL format")

if __name__ == '__main__':
    main()
