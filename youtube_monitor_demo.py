#!/usr/bin/env python3
"""
YouTube Comment Monitor Demo
Simulates the comment monitoring system with sample data (no API key required)
Shows what the system outputs when it processes comments
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

CACHE_DIR = Path(".cache")
COMMENTS_LOG = CACHE_DIR / "youtube-comments-demo.jsonl"
PROCESSED_FILE = CACHE_DIR / "youtube-processed-demo.json"
ERRORS_LOG = CACHE_DIR / "youtube-errors-demo.log"

# Sample comments for demonstration
SAMPLE_COMMENTS = [
    {
        "id": "Ugx_JhF3kL_FvN8K",
        "commenter": "Sarah Mitchell",
        "text": "How do I get started with this? What's the timeline?",
        "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z",
        "category": 1  # Questions
    },
    {
        "id": "Ugz_PqR7sL_MvN2K",
        "commenter": "Alex Johnson",
        "text": "This is absolutely amazing! Love your approach! 🙌",
        "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat() + "Z",
        "category": 2  # Praise
    },
    {
        "id": "Ugx_KlM3nO_PvN5K",
        "commenter": "CryptoBro2000",
        "text": "Get rich quick with Bitcoin! DM for details. GUARANTEED returns! 🚀",
        "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat() + "Z",
        "category": 3  # Spam
    },
    {
        "id": "Ugz_WxY9zL_FvN8K",
        "commenter": "Emma Davis",
        "text": "What tools do you recommend for beginners? Cost effective options?",
        "timestamp": (datetime.utcnow() - timedelta(minutes=20)).isoformat() + "Z",
        "category": 1  # Questions
    },
    {
        "id": "Ugx_AbC1dE_FvN3K",
        "commenter": "Michael Chen",
        "text": "Inspiring content! Really appreciate what you're doing. Keep it up!",
        "timestamp": (datetime.utcnow() - timedelta(minutes=25)).isoformat() + "Z",
        "category": 2  # Praise
    },
    {
        "id": "Ugz_FgH5iJ_PvN6K",
        "commenter": "Business Inquiry Team",
        "text": "Hey! We'd love to collaborate on a partnership. Let's work together!",
        "timestamp": (datetime.utcnow() - timedelta(minutes=28)).isoformat() + "Z",
        "category": 4  # Sales
    }
]

CATEGORIES = {
    1: "Questions",
    2: "Praise",
    3: "Spam",
    4: "Sales"
}

TEMPLATES = {
    1: "Thanks for the question! Check our FAQ at https://concessa.obvius.io/faq or reply with specifics.",
    2: "Thank you so much! Really appreciate the support 🙏"
}


def main():
    print(f"🎬 YouTube Comment Monitor DEMO (No API Key Required)")
    print(f"Started: {datetime.now().isoformat()}\n")
    
    CACHE_DIR.mkdir(exist_ok=True)
    
    stats = {
        "total_processed": 0,
        "by_category": {1: 0, 2: 0, 3: 0, 4: 0},
        "auto_responded": {1: 0, 2: 0},
        "flagged_for_review": 0,
        "spam_filtered": 0,
    }
    
    print("📝 Processing sample comments...\n")
    
    for comment in SAMPLE_COMMENTS:
        category = comment["category"]
        stats["by_category"][category] += 1
        stats["total_processed"] += 1
        
        # Determine response status
        response_status = "skipped"
        
        if category == 1 or category == 2:
            response_status = "sent"
            stats["auto_responded"][category] += 1
            print(f"  ✅ [{CATEGORIES[category]}] {comment['commenter']}")
            print(f"     Message: {comment['text'][:60]}...")
            print(f"     → Response sent: {TEMPLATES[category]}\n")
        elif category == 4:
            response_status = "flagged"
            stats["flagged_for_review"] += 1
            print(f"  🚨 [{CATEGORIES[category]}] {comment['commenter']}")
            print(f"     Message: {comment['text'][:60]}...")
            print(f"     → FLAGGED FOR MANUAL REVIEW\n")
        elif category == 3:
            response_status = "skipped"
            stats["spam_filtered"] += 1
            print(f"  ❌ [{CATEGORIES[category]}] {comment['commenter']}")
            print(f"     Message: {comment['text'][:60]}...")
            print(f"     → SPAM FILTERED\n")
        
        # Log comment
        log_entry = {
            "timestamp": comment["timestamp"],
            "comment_id": comment["id"],
            "commenter": comment["commenter"],
            "text": comment["text"],
            "category": category,
            "response_status": response_status
        }
        
        with open(COMMENTS_LOG, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    # Save processed comments
    with open(PROCESSED_FILE, "w") as f:
        json.dump({"comment_ids": [c["id"] for c in SAMPLE_COMMENTS]}, f, indent=2)
    
    print("✅ Demo processing complete.\n")
    print_report(stats)


def print_report(stats: dict):
    """Generate and print report"""
    report = f"""
╔════════════════════════════════════════════════════════════════════╗
║          YouTube Comment Monitor Report (DEMO)                     ║
║          Channel: Concessa Obvius                                  ║
║          {datetime.now().isoformat()}{' ' * (32 - len(datetime.now().isoformat()))}║
╚════════════════════════════════════════════════════════════════════╝

📊 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Comments Processed:      {stats.get('total_processed', 0)}

📂 CATEGORIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Questions (1):               {stats.get('by_category', {}).get(1, 0)}
  Praise (2):                  {stats.get('by_category', {}).get(2, 0)}
  Spam (3):                    {stats.get('by_category', {}).get(3, 0)}
  Sales Inquiries (4):         {stats.get('by_category', {}).get(4, 0)}

🤖 AUTO-RESPONSES SENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Sent to Questions:           {stats.get('auto_responded', {}).get(1, 0)}
  Sent to Praise:              {stats.get('auto_responded', {}).get(2, 0)}
  Total Auto-Responses:        {sum(stats.get('auto_responded', {}).values())}

🚨 MANUAL REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Flagged for Review:          {stats.get('flagged_for_review', 0)}

⚠️  FILTERING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Spam Filtered:               {stats.get('spam_filtered', 0)}

📁 OUTPUT FILES (Demo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Comments Log:                {COMMENTS_LOG}
  Processed Log:               {PROCESSED_FILE}
  Errors Log:                  {ERRORS_LOG}

💡 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Get YouTube API key from Google Cloud Console
  2. Set environment variable: export YOUTUBE_API_KEY="your-key"
  3. Run: python3 youtube_monitor.py
  4. Set up cron job for automated monitoring

📖 Documentation: YOUTUBE_MONITOR_README.md

────────────────────────────────────────────────────────────────────
Demo report generated: {datetime.now().isoformat()}
    """
    
    print(report)
    
    # Save report to file
    with open(CACHE_DIR / f"youtube-report-demo-{datetime.now().isoformat().replace(':', '-')}.txt", "w") as f:
        f.write(report)
    
    print(f"\n✅ Check .cache/ directory for output files\n")


if __name__ == "__main__":
    main()
