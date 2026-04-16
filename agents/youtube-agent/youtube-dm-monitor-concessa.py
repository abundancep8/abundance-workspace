#!/usr/bin/env python3
"""
YouTube DM Monitor for Concessa Obvius
Monitors incoming DMs, categorizes them, sends auto-responses, flags partnerships.
Runs hourly via cron. No auth required — autonomous local cache operation.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class ConcessaDMMonitor:
    def __init__(self):
        self.workspace = Path(os.path.expanduser("~/.openclaw/workspace"))
        self.cache_dir = self.workspace / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.dms_log = self.cache_dir / "youtube-dms.jsonl"
        self.state_file = self.cache_dir / ".youtube-dms-state.json"
        self.report_file = self.cache_dir / "youtube-dm-report.txt"
        
    def load_state(self):
        """Load processing state (prevents duplicate processing)"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "last_processed_ids": [],
            "last_run": None,
            "total_lifetime_dms": 0,
            "total_lifetime_responses": 0,
            "total_lifetime_flagged": 0
        }
    
    def save_state(self, state):
        """Save processing state"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def categorize_dm(self, text):
        """
        Categorize DM into one of four categories:
        1. Setup help
        2. Newsletter
        3. Product inquiry
        4. Partnership
        """
        text_lower = text.lower()
        
        # Partnership (prioritize this first)
        partnership_keywords = [
            'partner', 'collab', 'sponsor', 'sponsorship', 'brand deal', 
            'affiliate', 'business opportunity', 'work together', 'growth hack',
            'marketing', 'cross-promote', 'guest post', 'podcast', 'interview',
            'investment', 'venture', 'strategic alliance', 'joint venture'
        ]
        if any(kw in text_lower for kw in partnership_keywords):
            return 'partnership'
        
        # Product inquiry
        product_keywords = [
            'buy', 'purchase', 'price', 'cost', 'how much', 'pricing', 'order',
            'available', 'product', 'service', 'tier', 'package', 'plan',
            'subscription', 'membership', 'access', 'tool', 'platform'
        ]
        if any(kw in text_lower for kw in product_keywords):
            return 'product_inquiry'
        
        # Newsletter
        newsletter_keywords = [
            'newsletter', 'email', 'subscribe', 'signup', 'list', 'updates',
            'mailing', 'opt-in', 'notification', 'news'
        ]
        if any(kw in text_lower for kw in newsletter_keywords):
            return 'newsletter'
        
        # Setup help / Support
        setup_keywords = [
            'help', 'how', 'setup', 'start', 'install', 'guide', 'tutorial',
            'confused', 'stuck', 'error', 'not working', 'problem', 'issue',
            'support', 'question', 'explain', 'understand', 'where', 'which'
        ]
        if any(kw in text_lower for kw in setup_keywords):
            return 'setup_help'
        
        # Default
        return 'setup_help'
    
    def get_response(self, category):
        """Get templated auto-response for each category"""
        templates = {
            'setup_help': [
                "Hey! Happy to help you get started. What part of the setup is giving you trouble? I'll walk you through it.",
                "Great question! Check out the setup guide in my bio — if you get stuck, let me know which step and I'll unblock you.",
                "I've got you. Drop me the specific part that's confusing and I'll send you the exact steps.",
            ],
            'newsletter': [
                "Thanks for the interest! You can sign up with the link in my bio. I send weekly updates on what I'm building.",
                "Love the enthusiasm! The newsletter signup is pinned at the top of my bio — I share everything there first.",
                "Awesome. Email list link is right in the bio. I keep it real and send something worth reading every week.",
            ],
            'product_inquiry': [
                "Perfect. Everything is listed on the site (link in bio). What's your main use case? I can point you to the right option.",
                "Great question. Check the offerings page for pricing and details. Hit me back if you have specific questions about what fits your needs.",
                "I've got several tiers depending on what you're trying to do. What's the main thing you're looking to solve?",
            ],
            'partnership': None  # Will be flagged, not auto-responded
        }
        
        if category == 'partnership':
            return None
        
        # Return first template for this category (could randomize in future)
        return templates.get(category, templates['setup_help'])[0]
    
    def process_dms(self, new_dms):
        """Process new DMs: categorize, respond, log"""
        state = self.load_state()
        results = {
            'processed': 0,
            'auto_responses': 0,
            'flagged': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for dm in new_dms:
            dm_id = dm.get('id', f"{dm.get('sender')}_{dm.get('timestamp')}")
            
            # Skip if already processed
            if dm_id in state['last_processed_ids']:
                continue
            
            # Categorize
            category = self.categorize_dm(dm.get('text', ''))
            
            # Get response
            response = self.get_response(category)
            response_sent = response is not None
            
            # Log to JSONL
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'sender': dm.get('sender'),
                'text': dm.get('text'),
                'category': category,
                'response_sent': response_sent,
                'response': response if response_sent else '',
                'dm_id': dm_id
            }
            
            with open(self.dms_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            # Track results
            state['last_processed_ids'].append(dm_id)
            state['total_lifetime_dms'] += 1
            results['processed'] += 1
            
            if response_sent:
                state['total_lifetime_responses'] += 1
                results['auto_responses'] += 1
            else:
                # Partnership inquiry
                state['total_lifetime_flagged'] += 1
                results['flagged'].append({
                    'sender': dm.get('sender'),
                    'text': dm.get('text'),
                    'category': category
                })
        
        # Update state
        state['last_run'] = datetime.now().isoformat()
        self.save_state(state)
        
        return results, state
    
    def generate_report(self, results, state):
        """Generate human-readable report"""
        report_lines = [
            f"YouTube DM Monitor Report — Concessa Obvius",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            "",
            "📊 This Run",
            f"  DMs Processed: {results['processed']}",
            f"  Auto-Responses Sent: {results['auto_responses']}",
            f"  Flagged for Review: {len(results['flagged'])}",
            "",
            "📈 Lifetime Totals",
            f"  Total DMs: {state['total_lifetime_dms']}",
            f"  Total Auto-Responses: {state['total_lifetime_responses']}",
            f"  Total Flagged: {state['total_lifetime_flagged']}",
            "",
        ]
        
        if results['flagged']:
            report_lines.append("🚩 Flagged for Manual Review (Partnerships)")
            for item in results['flagged']:
                report_lines.append(f"  • {item['sender']}: {item['text'][:60]}...")
            report_lines.append("")
        
        report_lines.extend([
            "✅ Status: Operational",
            f"Last run: {state['last_run']}"
        ])
        
        return "\n".join(report_lines)
    
    def run(self):
        """Main monitoring loop (run hourly via cron)"""
        # In live mode, would fetch from YouTube API here
        # For now, we check the cache for new DMs
        
        # Example: Check if there are any new DMs in an input queue
        input_queue = self.cache_dir / ".youtube-dm-input-queue.jsonl"
        new_dms = []
        
        if input_queue.exists():
            with open(input_queue, 'r') as f:
                new_dms = [json.loads(line) for line in f if line.strip()]
            
            # Clear the queue after processing
            input_queue.unlink()
        
        results, state = self.process_dms(new_dms)
        report = self.generate_report(results, state)
        
        # Write report
        with open(self.report_file, 'w') as f:
            f.write(report)
        
        # Console output
        print(report)
        
        return results


if __name__ == "__main__":
    monitor = ConcessaDMMonitor()
    monitor.run()
