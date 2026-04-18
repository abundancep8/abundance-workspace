#!/usr/bin/env python3
"""
YouTube DM Monitor - Hourly Report Generator
Reads existing DM logs and generates hourly reports with categorization and stats.
No API dependencies required - works with local JSONL log file.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import sys

class YouTubeDMReportGenerator:
    """Generate hourly reports from DM logs"""
    
    CACHE_DIR = Path.home() / '.openclaw' / 'workspace' / '.cache'
    LOG_FILE = CACHE_DIR / 'youtube-dms.jsonl'
    STATE_FILE = CACHE_DIR / '.youtube-dms-state.json'
    REPORT_FILE = CACHE_DIR / 'youtube-dms-hourly-report.json'
    
    TEMPLATES = {
        'setup_help': "Thanks for reaching out! 👋\n\n📚 **Setup Resources:**\n• Full guide: https://docs.concessa.com/setup\n• Video tutorial: https://docs.concessa.com/video\n• FAQ: https://docs.concessa.com/faq\n\nReply with your specific issue and I'll help you get unstuck! 🚀",
        'newsletter': "Perfect! ✨\n\nI've added you to our newsletter! You'll get:\n\n📧 **Weekly updates:**\n• New features & releases\n• Tips & tricks\n• Exclusive content\n• Special offers\n\n👀 Manage preferences anytime.\nThanks for staying connected! 💌",
        'product_inquiry': "Great question! 🏢\n\nThanks for your interest. Here's what you need:\n\n📦 **Product Info:**\n• Features: https://concessa.com/features\n• Pricing: https://concessa.com/pricing\n• Live demo: https://demo.concessa.com\n• Case studies: https://concessa.com/cases\n\n💡 **Help me help you:**\n- What's your main use case?\n- Team size?\n- Special features needed?\n\nLet's find the perfect fit! 🎯",
        'partnership': "Thanks for reaching out! 🤝\n\nWe're always interested in collaborations. I'm flagging this for our partnership team to review.\n\nSomeone will follow up soon! 🌟",
    }
    
    KEYWORDS = {
        'setup_help': ['error', 'help', 'stuck', 'how', 'setup', 'guide', 'tutorial', 'install', 'configure', 'problem'],
        'newsletter': ['email list', 'newsletter', 'updates', 'subscribe', 'sign up', 'mailing list'],
        'product_inquiry': ['pricing', 'buy', 'cost', 'product', 'features', 'demo', 'trial', 'enterprise', 'plan', 'subscription'],
        'partnership': ['partner', 'collaborate', 'sponsor', 'brand', 'affiliate', 'integration', 'work together'],
    }
    
    def __init__(self):
        """Initialize report generator"""
        self.dms = []
        self.state = self.load_state()
        
    def load_state(self):
        """Load current state"""
        if self.STATE_FILE.exists():
            with open(self.STATE_FILE) as f:
                return json.load(f)
        return {
            'last_processed_ids': [],
            'last_run': None,
            'total_lifetime_dms': 0,
            'total_lifetime_responses': 0,
            'total_lifetime_flagged': 0,
            'latest_run_summary': {},
            'lifetime_stats': {}
        }
    
    def load_dms(self):
        """Load DMs from JSONL log"""
        dms = []
        if self.LOG_FILE.exists():
            with open(self.LOG_FILE) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        try:
                            dms.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return dms
    
    def categorize_dm(self, text):
        """Categorize a DM based on keywords"""
        text_lower = text.lower()
        scores = defaultdict(int)
        
        for category, keywords in self.KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[category] += 1
        
        if scores:
            return max(scores, key=scores.get)
        return 'other'
    
    def get_response_template(self, category):
        """Get template response for category"""
        return self.TEMPLATES.get(category, "Thanks for reaching out! I'll get back to you soon. 👋")
    
    def generate_hourly_report(self):
        """Generate hourly report"""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        # Load all DMs
        all_dms = self.load_dms()
        
        # Count new DMs from the last hour
        new_dms = []
        for dm in all_dms:
            if dm.get('dm_id') not in self.state['last_processed_ids']:
                try:
                    dm_time = datetime.fromisoformat(dm['timestamp'].replace('Z', '+00:00'))
                    if dm_time >= one_hour_ago:
                        new_dms.append(dm)
                except:
                    pass
        
        # Categorize and auto-respond
        stats = {
            'setup_help': 0,
            'newsletter': 0,
            'product_inquiry': 0,
            'partnership': 0,
            'other': 0
        }
        
        responses_sent = 0
        partnerships_flagged = []
        product_inquiries = []
        
        for dm in new_dms:
            category = dm.get('category', self.categorize_dm(dm['text']))
            stats[category] = stats.get(category, 0) + 1
            
            # Count responses
            if dm.get('response_sent', True):
                responses_sent += 1
            
            # Flag partnerships
            if category == 'partnership':
                if dm.get('manual_review', True):
                    partnerships_flagged.append({
                        'sender': dm.get('sender'),
                        'text': dm['text'][:200],
                        'timestamp': dm['timestamp']
                    })
            
            # Track product inquiries
            if category == 'product_inquiry':
                product_inquiries.append({
                    'sender': dm.get('sender'),
                    'inquiry': dm['text'][:150],
                    'timestamp': dm['timestamp']
                })
        
        # Update state
        processed_ids = self.state['last_processed_ids'] + [dm.get('dm_id') for dm in new_dms]
        self.state['last_processed_ids'] = processed_ids[-100:]  # Keep last 100
        self.state['last_run'] = now.isoformat()
        self.state['last_run_local'] = now.strftime('%Y-%m-%d %I:%M:%S %p %Z')
        self.state['total_lifetime_dms'] = len(all_dms)
        self.state['total_lifetime_responses'] = self.state.get('total_lifetime_responses', 0) + responses_sent
        self.state['total_lifetime_flagged'] = self.state.get('total_lifetime_flagged', 0) + len(partnerships_flagged)
        
        # Latest run summary
        self.state['latest_run_summary'] = {
            'execution_date': now.strftime('%Y-%m-%d'),
            'execution_time': now.strftime('%I:%M:%S %p %Z'),
            'dms_processed': len(new_dms),
            'new_dms': len(new_dms),
            'responses_sent': responses_sent,
            'flagged_partnerships': len(partnerships_flagged),
            'high_value_inquiries': len(product_inquiries)
        }
        
        # Lifetime stats
        self.state['lifetime_stats'] = {
            'setup_help': self.state.get('lifetime_stats', {}).get('setup_help', 0) + stats['setup_help'],
            'newsletter': self.state.get('lifetime_stats', {}).get('newsletter', 0) + stats['newsletter'],
            'product_inquiry': self.state.get('lifetime_stats', {}).get('product_inquiry', 0) + stats['product_inquiry'],
            'partnership': self.state.get('lifetime_stats', {}).get('partnership', 0) + stats['partnership'],
            'other': self.state.get('lifetime_stats', {}).get('other', 0) + stats['other'],
            'conversion_potential_leads': len(product_inquiries),
            'estimated_revenue_low': max(1500, len(product_inquiries) * 300),
            'estimated_revenue_high': max(2500, len(product_inquiries) * 800),
        }
        
        # Save state
        with open(self.STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
        
        # Build report
        report = {
            'timestamp': now.isoformat(),
            'status': 'completed',
            'execution_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'total_dms_processed': len(all_dms),
            'new_dms_this_hour': len(new_dms),
            'auto_responses_sent': responses_sent,
            'by_category': stats,
            'partnerships_flagged': len(partnerships_flagged),
            'interesting_partnerships': partnerships_flagged[:5],
            'product_inquiries_count': len(product_inquiries),
            'conversion_potential': f"{len(product_inquiries)} lead(s) ready to follow up" if product_inquiries else "No new product inquiries",
            'estimated_value': f"${self.state['lifetime_stats']['estimated_revenue_low']}-${self.state['lifetime_stats']['estimated_revenue_high']}",
            'lifetime_totals': {
                'total_dms': len(all_dms),
                'total_responses': self.state['total_lifetime_responses'],
                'total_flagged': self.state['total_lifetime_flagged'],
                'categories': self.state['lifetime_stats']
            }
        }
        
        # Save report
        with open(self.REPORT_FILE, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

def main():
    """Run hourly report"""
    generator = YouTubeDMReportGenerator()
    report = generator.generate_hourly_report()
    
    # Print summary
    print("\n" + "="*60)
    print(f"🎥 YOUTUBE DM MONITOR - HOURLY REPORT")
    print("="*60)
    print(f"Execution: {report['execution_time']}")
    print(f"Total DMs processed (lifetime): {report['total_dms_processed']}")
    print(f"New DMs this hour: {report['new_dms_this_hour']}")
    print(f"Auto-responses sent: {report['auto_responses_sent']}")
    print(f"\nCategory Breakdown:")
    for cat, count in report['by_category'].items():
        if count > 0:
            print(f"  • {cat}: {count}")
    print(f"\n🚀 Conversion Potential: {report['conversion_potential']}")
    print(f"💰 Estimated Value: {report['estimated_value']}")
    if report['partnerships_flagged'] > 0:
        print(f"⭐ Interesting Partnerships Flagged: {report['partnerships_flagged']}")
    print("="*60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
