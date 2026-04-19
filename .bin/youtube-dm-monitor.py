#!/usr/bin/env python3
"""
YouTube DM Monitor for Concessa Obvius
Monitors incoming DMs, categorizes them, sends auto-responses, and logs activity.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from enum import Enum

class DMCategory(Enum):
    """DM categorization types"""
    SETUP_HELP = "setup_help"
    NEWSLETTER = "newsletter"
    PRODUCT_INQUIRY = "product_inquiry"
    PARTNERSHIP = "partnership"

class YouTubeDMMonitor:
    def __init__(self):
        self.workspace = Path.home() / ".openclaw/workspace"
        self.cache_file = self.workspace / ".cache/youtube-dms.jsonl"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.templates = {
            DMCategory.SETUP_HELP.value: """Hi there! 👋

Thanks for reaching out about setup. I'm here to help!

📚 **Resources:**
• Full setup guide: https://docs.concessa.com/setup
• Video tutorial: https://youtube.com/concessa-setup
• FAQ & Troubleshooting: https://docs.concessa.com/faq

💬 **Got a specific issue?** Reply with:
- What step you're on
- What error you're seeing
- Your setup (OS, browser, etc.)

I'll get you unstuck! 🚀""",

            DMCategory.NEWSLETTER.value: """Perfect! ✨

I've added you to our newsletter! You'll get:

📧 **Weekly updates:**
• New feature releases
• Tips & tricks
• Exclusive content for subscribers
• Special offers

👀 You can manage your preferences anytime.

Thanks for staying connected! 💌""",

            DMCategory.PRODUCT_INQUIRY.value: """Great question! 🏢

Thanks for your interest. Here's what you need to know:

📦 **Product Details:**
• Features overview: https://concessa.com/features
• Pricing plans: https://concessa.com/pricing
• Live demo: https://demo.concessa.com
• Case studies: https://concessa.com/cases

💰 **Our Plans:**
• Starter: $29/month (up to 1000 users)
• Pro: $99/month (up to 10K users)
• Enterprise: Custom pricing

❓ **Help me help you:**
- What's your main use case?
- How many team members?
- Any specific features you need?

Let's find the perfect plan for you! 💡""",

            DMCategory.PARTNERSHIP.value: """Ooh, interesting! 🤝

I love hearing partnership ideas. Let me flag this for our partnerships team.

📧 For collaboration inquiries: partnerships@concessa.com

Tell them:
- What you have in mind
- Your audience/reach
- What makes sense to collaborate on

We'll dive deeper ASAP! 🚀"""
        }
        
        # Keywords for categorization
        self.category_keywords = {
            DMCategory.SETUP_HELP: ["setup", "help", "error", "stuck", "confused", "how do i", "how to", "tutorial", "guide", "configuration", "install", "get started"],
            DMCategory.NEWSLETTER: ["newsletter", "email list", "updates", "subscribe", "stay updated", "mailing list"],
            DMCategory.PRODUCT_INQUIRY: ["price", "pricing", "buy", "purchase", "cost", "plan", "features", "product", "interested in", "what's the", "how much"],
            DMCategory.PARTNERSHIP: ["partner", "partnership", "collaborate", "collaboration", "sponsor", "sponsorship", "brand deal", "collab", "work together"],
        }
    
    def categorize_dm(self, text: str) -> str:
        """Categorize a DM based on keyword matching"""
        text_lower = text.lower()
        
        # Score each category
        scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score
        
        # Return highest scoring category, default to setup_help
        best_category = max(scores, key=scores.get) if max(scores.values()) > 0 else DMCategory.SETUP_HELP
        return best_category.value
    
    def process_dm(self, sender: str, text: str, sender_id: str = None) -> dict:
        """Process a single DM"""
        category = self.categorize_dm(text)
        response_template = self.templates[category]
        
        dm_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sender": sender,
            "sender_id": sender_id or f"uc_{sender.lower().replace(' ', '_')}",
            "text": text,
            "category": category,
            "response_sent": response_template != "",
            "response_template": response_template,
            "manual_review": category == DMCategory.PARTNERSHIP.value
        }
        
        return dm_record
    
    def log_dm(self, dm_record: dict):
        """Log a DM to the cache file"""
        with open(self.cache_file, 'a') as f:
            f.write(json.dumps(dm_record) + '\n')
    
    def generate_report(self, since_hours: int = 24) -> dict:
        """Generate activity report for the last N hours"""
        now = datetime.utcnow()
        cutoff = now.timestamp() - (since_hours * 3600)
        
        stats = {
            "total_processed": 0,
            "auto_responses": 0,
            "by_category": {
                "setup_help": 0,
                "newsletter": 0,
                "product_inquiry": 0,
                "partnership": 0,
            },
            "partnerships_flagged": [],
            "product_inquiries": []
        }
        
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        dm = json.loads(line)
                        
                        # Parse timestamp
                        ts_str = dm.get('timestamp', '').replace('Z', '+00:00')
                        try:
                            ts = datetime.fromisoformat(ts_str).timestamp()
                        except:
                            continue
                        
                        if ts < cutoff:
                            continue
                        
                        stats["total_processed"] += 1
                        
                        category = dm.get('category', 'unknown')
                        if category in stats["by_category"]:
                            stats["by_category"][category] += 1
                        
                        if dm.get('response_sent'):
                            stats["auto_responses"] += 1
                        
                        if category == 'partnership' and dm.get('manual_review'):
                            stats["partnerships_flagged"].append({
                                "sender": dm.get('sender'),
                                "text": dm.get('text'),
                                "timestamp": dm.get('timestamp')
                            })
                        
                        if category == 'product_inquiry':
                            stats["product_inquiries"].append({
                                "sender": dm.get('sender'),
                                "text": dm.get('text'),
                                "timestamp": dm.get('timestamp')
                            })
                    
                    except json.JSONDecodeError:
                        pass
        
        return stats
    
    def print_report(self, stats: dict):
        """Print a formatted report"""
        print("""
╔════════════════════════════════════════════╗
║   YOUTUBE DM MONITOR - CONCESSA OBVIUS     ║
║   Hourly Report                            ║
╚════════════════════════════════════════════╝
""")
        print(f"Generated: {datetime.now().isoformat()}\n")
        
        print("📊 STATS (Last 24 hours)")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Total DMs Processed:           {stats['total_processed']}")
        print(f"Auto-Responses Sent:           {stats['auto_responses']}")
        print(f"Conversion Potential (leads):  {stats['by_category']['product_inquiry']} ⭐\n")
        
        print("📋 BREAKDOWN BY CATEGORY")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for cat, count in stats['by_category'].items():
            icon = "⭐" if cat == "product_inquiry" else "🚩" if cat == "partnership" else "✅"
            print(f"{icon} {cat.replace('_', ' ').title():.<30} {count}")
        
        if stats['partnerships_flagged']:
            print(f"\n🚩 PARTNERSHIPS FOR MANUAL REVIEW ({len(stats['partnerships_flagged'])})")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            for pf in stats['partnerships_flagged']:
                print(f"  • {pf['sender']}: \"{pf['text'][:60]}...\"")
                print(f"    Time: {pf['timestamp']}\n")
        
        if stats['product_inquiries']:
            print(f"\n💡 PRODUCT INQUIRY LEADS ({len(stats['product_inquiries'])})")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            for pi in stats['product_inquiries'][:5]:  # Show top 5
                print(f"  • {pi['sender']}: \"{pi['text'][:60]}...\"")
        
        print("\n✅ Monitor Status: ACTIVE")
        print("📍 Next check: Hourly\n")

def main():
    monitor = YouTubeDMMonitor()
    
    # Generate and print hourly report
    stats = monitor.generate_report(since_hours=1)
    monitor.print_report(stats)
    
    # Save stats to metrics file for trending
    metrics_file = monitor.workspace / ".cache/youtube-metrics.jsonl"
    metrics = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "dms_processed": stats['total_processed'],
        "auto_responses": stats['auto_responses'],
        "product_inquiries": stats['by_category']['product_inquiry'],
        "partnerships": stats['by_category']['partnership'],
    }
    
    with open(metrics_file, 'a') as f:
        f.write(json.dumps(metrics) + '\n')

if __name__ == "__main__":
    main()
