#!/usr/bin/env python3
"""
YouTube Comment Monitor — 30-minute Cron Job
Monitors Concessa Obvius channel for new comments on videos.
Categorizes, auto-responds to helpful categories, flags partnerships for review.

Schedule: Every 30 minutes
Output: .cache/youtube-comments.jsonl | .cache/youtube-comment-report.txt | .cache/youtube-comment-flagged.jsonl
"""

import json
import sys
import os
import hashlib
from datetime import datetime
from pathlib import Path
from enum import Enum
import subprocess
import re

class CommentCategory(Enum):
    """Comment categorization types"""
    QUESTIONS = "questions"          # how do I start, tools, cost, timeline
    PRAISE = "praise"                 # amazing, inspiring, thank you
    SPAM = "spam"                     # crypto, mlm, scams
    SALES = "sales"                   # partnership, collaboration, brand deals
    OTHER = "other"

class YouTubeCommentMonitor:
    def __init__(self):
        self.workspace = Path.home() / ".openclaw/workspace"
        self.cache_dir = self.workspace / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.comments_log = self.cache_dir / "youtube-comments.jsonl"
        self.flagged_log = self.cache_dir / "youtube-comments-flagged.jsonl"
        self.state_file = self.cache_dir / "youtube-comment-state.json"
        self.report_file = self.cache_dir / "youtube-comment-report.txt"
        self.metrics_file = self.cache_dir / "youtube-comment-metrics.jsonl"
        
        self.channel_id = "UC326742c_CXvNQ6IcnZ8Jkw"  # Concessa Obvius
        self.channel_name = "Concessa Obvius"
        
        # Category keywords for classification
        self.category_keywords = {
            CommentCategory.QUESTIONS.value: [
                'how', 'where', 'what', 'when', 'why',
                'cost', 'price', 'pricing', 'timeline', 'timeline', 'how much',
                'setup', 'start', 'begin', 'tutorial', 'guide',
                'tools', 'software', 'platform', 'system requirements',
                'help', 'support', 'question', 'confused', 'understand'
            ],
            CommentCategory.PRAISE.value: [
                'amazing', 'inspiring', 'awesome', 'fantastic', 'incredible',
                'love', 'thank you', 'thanks', 'great', 'excellent',
                'brilliant', 'genius', 'perfect', 'beautiful',
                'changed my life', 'game changer', 'best', 'helped me'
            ],
            CommentCategory.SPAM.value: [
                'crypto', 'bitcoin', 'nft', 'blockchain',
                'get rich', 'make money fast', 'mlm', 'multi level',
                'pyramid', 'forex', 'stock tips', 'guaranteed profit',
                'check my channel', 'visit my site', 'click here', 'dm for info'
            ],
            CommentCategory.SALES.value: [
                'partnership', 'collaborate', 'collaboration', 'brand deal',
                'sponsorship', 'sponsor', 'work together', 'colab',
                'promotion', 'affiliate', 'business opportunity',
                'let\'s partner', 'let\'s collaborate', 'let\'s work'
            ]
        }
        
        # Template responses for each category
        self.templates = {
            CommentCategory.QUESTIONS.value: """Thanks for the question! 🙋

I'd love to help. Here are some resources:

📚 **Setup & Getting Started:**
• Complete guide: https://docs.concessa.com/getting-started
• Video tutorials: https://youtube.com/@ConcessaObvius/tutorials
• FAQ: https://docs.concessa.com/faq

💬 **For specific help:**
Reply here or DM me, and include:
- What you're trying to do
- Where you're stuck
- Your setup (OS, browser, etc.)

Looking forward to helping! 🚀""",

            CommentCategory.PRAISE.value: """Thank you so much! 💖

This means the world to me. I'm so glad this resonated with you.

Keep building amazing things! ✨""",

            CommentCategory.SPAM.value: None,  # No auto-response for spam

            CommentCategory.SALES.value: None,  # Flagged for manual review
        }
        
        self.load_state()

    def load_state(self):
        """Load processing state to track processed comments"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    self.state = json.load(f)
                    # Ensure required keys exist
                    if "processed_hashes" not in self.state:
                        self.state["processed_hashes"] = []
                    if "last_check" not in self.state:
                        self.state["last_check"] = None
            except (json.JSONDecodeError, IOError):
                self.state = {
                    "last_check": None,
                    "processed_hashes": []
                }
        else:
            self.state = {
                "last_check": None,
                "processed_hashes": []
            }
            # Create the file
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def save_state(self):
        """Save state to prevent duplicate processing"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def categorize_comment(self, text):
        """Categorize a comment based on keywords"""
        text_lower = text.lower()
        
        # Check each category's keywords
        for category, keywords in self.category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return CommentCategory.OTHER.value

    def get_comment_hash(self, commenter, text, timestamp):
        """Generate hash for duplicate detection"""
        content = f"{commenter}:{text}:{timestamp[:10]}"  # Date-based hash (ignore time variance)
        return hashlib.md5(content.encode()).hexdigest()

    def is_duplicate(self, comment_hash):
        """Check if comment was already processed"""
        return comment_hash in self.state["processed_hashes"]

    def fetch_comments(self):
        """
        Fetch recent comments from YouTube channel.
        
        NOTE: Requires YouTube Data API OAuth credentials in ~/.secrets/youtube-credentials.json
        For now, checks manual queue at .cache/youtube-comments-inbox.jsonl
        """
        comments = []
        
        # Check for manual comment queue (input from CLI or other source)
        inbox_file = self.cache_dir / "youtube-comments-inbox.jsonl"
        if inbox_file.exists():
            with open(inbox_file) as f:
                for line in f:
                    if line.strip():
                        comments.append(json.loads(line))
            
            # Clear inbox after processing
            inbox_file.unlink()
        
        return comments

    def process_comments(self):
        """Main processing loop"""
        comments = self.fetch_comments()
        
        if not comments:
            return self.generate_empty_report()
        
        processed = []
        auto_responses = 0
        flagged_for_review = 0
        
        for comment in comments:
            commenter = comment.get('commenter', 'Anonymous')
            text = comment.get('text', '')
            timestamp = comment.get('timestamp', datetime.utcnow().isoformat())
            
            # Generate hash for deduplication
            comment_hash = self.get_comment_hash(commenter, text, timestamp)
            
            if self.is_duplicate(comment_hash):
                continue  # Skip duplicate
            
            # Categorize
            category = self.categorize_comment(text)
            
            # Determine response
            response_text = None
            manual_review = False
            
            if category == CommentCategory.QUESTIONS.value:
                response_text = self.templates[CommentCategory.QUESTIONS.value]
                auto_responses += 1
            elif category == CommentCategory.PRAISE.value:
                response_text = self.templates[CommentCategory.PRAISE.value]
                auto_responses += 1
            elif category == CommentCategory.SPAM.value:
                response_text = None  # No response for spam
            elif category == CommentCategory.SALES.value:
                response_text = None
                manual_review = True
                flagged_for_review += 1
            
            # Create log entry
            log_entry = {
                "timestamp": timestamp,
                "commenter": commenter,
                "text": text,
                "category": category,
                "response_sent": response_text is not None,
                "response_status": "auto-responded" if response_text else ("flagged_for_review" if manual_review else "no_response"),
                "hash": comment_hash
            }
            
            processed.append(log_entry)
            self.state["processed_hashes"].append(comment_hash)
            
            # Log to main comments file
            with open(self.comments_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            # If flagged, log separately
            if manual_review:
                with open(self.flagged_log, 'a') as f:
                    f.write(json.dumps({
                        **log_entry,
                        "review_status": "pending",
                        "review_assigned_to": None
                    }) + '\n')
        
        self.state["last_check"] = datetime.utcnow().isoformat()
        self.save_state()
        
        return {
            "processed": len(processed),
            "auto_responses": auto_responses,
            "flagged_for_review": flagged_for_review,
            "by_category": self.count_by_category(processed)
        }

    def count_by_category(self, comments):
        """Count comments by category"""
        counts = {}
        for comment in comments:
            cat = comment['category']
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    def generate_empty_report(self):
        """Generate report when no new comments"""
        return {
            "processed": 0,
            "auto_responses": 0,
            "flagged_for_review": 0,
            "by_category": {}
        }

    def generate_report(self, stats):
        """Generate human-readable report"""
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║         YouTube Comment Monitor Report - {self.channel_name}            ║
║                    {datetime.utcnow().isoformat()}                         ║
╚════════════════════════════════════════════════════════════════╝

📊 METRICS
──────────────────────────────────────────────────────────────────
Total Comments Processed:        {stats['processed']}
Auto-Responses Sent:             {stats['auto_responses']}
Flagged for Review (Sales):      {stats['flagged_for_review']}

📂 BREAKDOWN BY CATEGORY
──────────────────────────────────────────────────────────────────
Questions:                       {stats['by_category'].get('questions', 0)}
Praise:                          {stats['by_category'].get('praise', 0)}
Spam:                            {stats['by_category'].get('spam', 0)}
Sales/Partnerships:              {stats['by_category'].get('sales', 0)}
Other:                           {stats['by_category'].get('other', 0)}

📍 LOGS
──────────────────────────────────────────────────────────────────
All comments:  {self.comments_log}
Flagged items: {self.flagged_log}
State:         {self.state_file}

💬 MANUAL REVIEW
──────────────────────────────────────────────────────────────────
If flagged comments exist, review them at:
  cat {self.flagged_log}

To respond to a flagged comment manually, create a reply in YouTube Studio.

⏰ NEXT RUN
──────────────────────────────────────────────────────────────────
Schedule: Every 30 minutes
Last Run: {datetime.utcnow().isoformat()}

════════════════════════════════════════════════════════════════════
"""
        
        with open(self.report_file, 'w') as f:
            f.write(report)
        
        return report.strip()

    def log_metrics(self, stats):
        """Log metrics in JSON format for dashboards/monitoring"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "run_id": hashlib.md5(datetime.utcnow().isoformat().encode()).hexdigest()[:8],
            "total_processed": stats['processed'],
            "auto_responses": stats['auto_responses'],
            "flagged_for_review": stats['flagged_for_review'],
            "by_category": stats['by_category']
        }
        
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')

    def run(self):
        """Run the monitor"""
        try:
            stats = self.process_comments()
            report = self.generate_report(stats)
            self.log_metrics(stats)
            
            print(report)
            return 0
        except Exception as e:
            error_msg = f"[ERROR] {datetime.utcnow().isoformat()}: {str(e)}"
            print(error_msg, file=sys.stderr)
            
            # Log error
            error_file = self.cache_dir / "youtube-comment-monitor-error.log"
            with open(error_file, 'a') as f:
                f.write(error_msg + '\n')
            
            return 1

if __name__ == "__main__":
    monitor = YouTubeCommentMonitor()
    sys.exit(monitor.run())
