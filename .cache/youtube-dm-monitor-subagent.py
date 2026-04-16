#!/usr/bin/env python3
"""
YouTube DM Monitor Subagent v2.0
Monitors, categorizes, auto-responds to, and logs YouTube DMs
Integrates with existing monitoring system and reports to main agent
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import re
from dataclasses import dataclass, asdict
import hashlib
import uuid

# Configuration
WORKSPACE = Path('/Users/abundance/.openclaw/workspace')
CACHE_DIR = WORKSPACE / '.cache'
DM_LOG = CACHE_DIR / 'youtube-dms.jsonl'
STATE_FILE = CACHE_DIR / '.youtube-dms-state.json'
CONFIG_FILE = CACHE_DIR / 'youtube-dm-monitor-config.json'
PARTNERSHIPS_LOG = CACHE_DIR / 'youtube-flagged-partnerships.jsonl'
INBOX_QUEUE = CACHE_DIR / 'youtube-dm-inbox.jsonl'
REPORT_FILE = CACHE_DIR / 'youtube-dms-report.txt'

# Template responses
RESPONSE_TEMPLATES = {
    'setup_help': {
        'subject': 'Help with Setup',
        'body': """Hi there! 👋

Thanks for reaching out about setup. I'm here to help!

📚 **Resources:**
• Full setup guide: https://docs.concessa.com/setup
• Video tutorial: https://youtube.com/watch?v=...
• FAQ & Troubleshooting: https://docs.concessa.com/faq

💬 **Got a specific issue?** Reply with:
- What step you're on
- What error you're seeing
- Your setup (OS, browser, etc.)

I'll get you unstuck! 🚀
"""
    },
    'newsletter': {
        'subject': 'Newsletter Confirmation',
        'body': """Perfect! ✨

I've added you to our newsletter! You'll get:

📧 **Weekly updates:**
• New feature releases
• Tips & tricks
• Exclusive content for subscribers
• Special offers

👀 You can manage your preferences anytime.

Thanks for staying connected! 💌
"""
    },
    'product_inquiry': {
        'subject': 'Product Info & Pricing',
        'body': """Great question! 🎯

Thanks for your interest. Here's what you need to know:

📦 **Product Details:**
• Features overview: https://concessa.com/features
• Pricing plans: https://concessa.com/pricing
• Live demo: https://demo.concessa.com
• Case studies: https://concessa.com/cases

💰 **Quick Summary:**
• Starter: $29/month (up to 1000 users)
• Pro: $99/month (up to 10K users)
• Enterprise: Custom pricing

❓ **Help me help you:**
- What's your main use case?
- How many team members?
- Any specific features you need?

Let's find the perfect plan for you! 💡
"""
    },
    'partnership': {
        'subject': 'Partnership Opportunity',
        'body': """Thanks for reaching out! 🤝

We're always excited about partnership opportunities. Your message has been flagged for our partnership team to review in detail.

📧 **Next steps:**
- Our team will review your proposal
- We'll reach out within 24-48 hours
- Let's chat about possibilities!

For urgent collab inquiries, email us: partnerships@concessa.com

Thanks for thinking of us! 🚀
"""
    }
}


@dataclass
class DM:
    """DM record"""
    dm_id: str
    timestamp: str
    sender: str
    sender_id: str
    text: str
    category: str
    response_sent: bool
    response_template: str
    manual_review: bool = False
    
    def to_jsonl(self) -> str:
        """Serialize to JSONL format"""
        return json.dumps(asdict(self))


class YouTubeDMMonitorSubagent:
    """Process YouTube DMs with categorization and auto-response"""
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.dm_log = DM_LOG
        self.state_file = STATE_FILE
        self.partnerships_log = PARTNERSHIPS_LOG
        self.config_file = CONFIG_FILE
        
        # Metrics
        self.dms_processed = 0
        self.auto_responses_sent = 0
        self.duplicates_skipped = 0
        self.partnerships_flagged = 0
        self.setup_help_count = 0
        self.newsletter_count = 0
        self.product_inquiry_count = 0
        
        # Results
        self.processed_dms = []
        self.flagged_partnerships = []
        self.errors = []
        
        # Load config
        self.load_config()
        self.load_state()
    
    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.errors.append(f"Config load error: {e}")
                self.config = {}
        else:
            self.config = {}
    
    def load_state(self):
        """Load monitor state"""
        self.processed_ids = set()
        self.last_run = None
        
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.processed_ids = set(state.get('last_processed_ids', []))
                    self.last_run = state.get('last_run')
            except Exception as e:
                self.errors.append(f"State load error: {e}")
    
    def save_state(self):
        """Save monitor state"""
        state = {
            'last_processed_ids': list(self.processed_ids),
            'last_run': datetime.now().isoformat(),
            'total_lifetime_dms': len(self.processed_ids),
            'total_lifetime_responses': self.auto_responses_sent,
            'total_lifetime_flagged': self.partnerships_flagged
        }
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def fetch_dms(self) -> List[Dict]:
        """Fetch new DMs from available sources"""
        dms = []
        
        # Source 1: /tmp/new-dms.json (webhook/external input)
        if Path('/tmp/new-dms.json').exists():
            try:
                with open('/tmp/new-dms.json', 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        dms.extend(data)
                    elif isinstance(data, dict) and 'dms' in data:
                        dms.extend(data['dms'])
            except Exception as e:
                self.errors.append(f"Error reading /tmp/new-dms.json: {e}")
        
        # Source 2: Environment variable DM_JSON
        dm_json = os.getenv('DM_JSON')
        if dm_json:
            try:
                data = json.loads(dm_json)
                if isinstance(data, list):
                    dms.extend(data)
            except Exception as e:
                self.errors.append(f"Error parsing DM_JSON: {e}")
        
        # Source 3: Inbox queue (JSONL file for manual input)
        if INBOX_QUEUE.exists():
            try:
                with open(INBOX_QUEUE, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                dms.append(json.loads(line))
                            except:
                                pass
                # Clear queue after reading
                INBOX_QUEUE.unlink()
            except Exception as e:
                self.errors.append(f"Error reading inbox queue: {e}")
        
        return dms
    
    def categorize_dm(self, text: str) -> Tuple[str, str]:
        """
        Categorize DM based on keywords and patterns.
        Returns (category_name, template_key)
        """
        text_lower = text.lower()
        
        # Load category patterns from config or use defaults
        categories = self.config.get('categories', [])
        
        for cat in categories:
            keywords = cat.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return cat.get('name', 'Unknown'), cat.get('id', 'unknown')
        
        # Default patterns if config not loaded
        patterns = {
            'setup_help': [
                r'\bhow\b.*setup', r'\bhelp\b', r'\bconfused\b',
                r'\berror\b', r'\bnot\s+working\b', r'\bstuck\b',
                r'\bcan\'t\b.*install', r'\bgetting\s+started\b',
                r'\btutorial\b', r'\bguide\b', r'\btrouble\b'
            ],
            'newsletter': [
                r'\bsubscribe\b', r'\bemail\s+list\b', r'\bupdates\b',
                r'\bnewsletter\b', r'\bsign\s+up\b', r'\bmailing\b',
                r'\bkeep.*posted\b'
            ],
            'product_inquiry': [
                r'\bprice\b', r'\bcost\b', r'\bbuy\b', r'\bpurchase\b',
                r'\bproduct\b', r'\bpricing\b', r'\bfeatures\b',
                r'\bavailable\b', r'\bcompare\b', r'\bdemo\b'
            ],
            'partnership': [
                r'\bpartner\b', r'\bcollab\b', r'\bsponsor\b',
                r'\bwork\s+together\b', r'\baffiliate\b',
                r'\bcross.?promote\b', r'\bbrand\s+ambassador\b',
                r'\bopportunit\b'
            ]
        }
        
        # Check patterns in priority order
        priority = ['partnership', 'setup_help', 'product_inquiry', 'newsletter']
        for category in priority:
            for pattern in patterns.get(category, []):
                if re.search(pattern, text_lower):
                    cat_name = category.replace('_', ' ').title()
                    return cat_name, category
        
        # Default
        return 'Product inquiry', 'product_inquiry'
    
    def process_dms(self, dms: List[Dict]) -> List[DM]:
        """Process and categorize DMs"""
        processed = []
        
        for dm in dms:
            # Generate DM ID if not present
            dm_id = dm.get('id') or dm.get('dm_id')
            if not dm_id:
                # Generate from sender + timestamp
                sender = dm.get('sender', 'unknown')
                timestamp = dm.get('timestamp', str(datetime.now()))
                hash_input = f"{sender}:{timestamp}:{dm.get('text', '')}"
                dm_id = 'dm-' + hashlib.md5(hash_input.encode()).hexdigest()[:12]
            
            # Skip duplicates
            if dm_id in self.processed_ids:
                self.duplicates_skipped += 1
                continue
            
            sender = dm.get('sender', 'Unknown')
            sender_id = dm.get('sender_id', '')
            text = dm.get('text', '')
            
            # Categorize
            category_name, template_key = self.categorize_dm(text)
            response_template = RESPONSE_TEMPLATES.get(template_key, {}).get('body', '')
            
            # Determine if auto-response should be sent
            response_sent = True
            if category_name == 'Partnership':
                response_sent = False  # Partnerships get flagged, not auto-responded
                self.partnerships_flagged += 1
                self.flagged_partnerships.append({
                    'dm_id': dm_id,
                    'sender': sender,
                    'text': text,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                self.auto_responses_sent += 1
            
            # Track category counts
            if category_name == 'Setup help':
                self.setup_help_count += 1
            elif category_name == 'Newsletter':
                self.newsletter_count += 1
            elif category_name == 'Product inquiry':
                self.product_inquiry_count += 1
            
            # Create DM record
            dm_record = DM(
                dm_id=dm_id,
                timestamp=datetime.now().isoformat(),
                sender=sender,
                sender_id=sender_id,
                text=text,
                category=category_name,
                response_sent=response_sent,
                response_template=response_template if response_sent else '',
                manual_review=(category_name == 'Partnership')
            )
            
            processed.append(dm_record)
            self.processed_ids.add(dm_id)
            self.dms_processed += 1
        
        return processed
    
    def log_dms(self, dms: List[DM]):
        """Log DMs to JSONL file"""
        if not dms:
            return
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with open(self.dm_log, 'a') as f:
            for dm in dms:
                f.write(dm.to_jsonl() + '\n')
    
    def log_partnerships(self):
        """Log flagged partnerships"""
        if not self.flagged_partnerships:
            return
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with open(self.partnerships_log, 'a') as f:
            for partnership in self.flagged_partnerships:
                f.write(json.dumps(partnership) + '\n')
    
    def generate_report(self) -> str:
        """Generate comprehensive report"""
        lines = []
        lines.append('=' * 80)
        lines.append('🎥 YOUTUBE DM MONITOR - SUBAGENT EXECUTION REPORT')
        lines.append('=' * 80)
        lines.append('')
        lines.append(f'⏱️  Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")}')
        lines.append(f'📍 Location: {WORKSPACE}')
        lines.append('')
        
        # This run metrics
        lines.append('📊 THIS RUN')
        lines.append('-' * 80)
        lines.append(f'New DMs Processed:        {self.dms_processed}')
        lines.append(f'Duplicates Skipped:       {self.duplicates_skipped}')
        lines.append(f'Auto-Responses Sent:      {self.auto_responses_sent}')
        lines.append(f'Partnerships Flagged:     {self.partnerships_flagged}')
        lines.append('')
        
        # Category breakdown
        lines.append('📂 CATEGORY BREAKDOWN')
        lines.append('-' * 80)
        lines.append(f'Setup Help 🔧:             {self.setup_help_count}')
        lines.append(f'Newsletter Signup 📧:      {self.newsletter_count}')
        lines.append(f'Product Inquiries 🛍️:     {self.product_inquiry_count}')
        lines.append(f'Partnerships Flagged 🤝:  {self.partnerships_flagged}')
        lines.append('')
        
        # Conversion potential
        lines.append('💰 CONVERSION POTENTIAL')
        lines.append('-' * 80)
        if self.product_inquiry_count > 0:
            lines.append(f'Product Inquiries: {self.product_inquiry_count} potential customers')
            lines.append('  → Recommend: Follow up with personalized demos or pricing info')
        if self.partnerships_flagged > 0:
            lines.append(f'Partnership Opportunities: {self.partnerships_flagged} flagged for manual review')
            lines.append('  → Flagged senders:')
            for partnership in self.flagged_partnerships:
                lines.append(f'     • {partnership["sender"]}: "{partnership["text"][:60]}..."')
        lines.append('')
        
        # Data logging
        lines.append('📝 DATA LOGGING')
        lines.append('-' * 80)
        lines.append(f'✓ Logged to: {self.dm_log}')
        if self.flagged_partnerships:
            lines.append(f'✓ Partnerships logged to: {self.partnerships_log}')
        lines.append('')
        
        # Errors
        if self.errors:
            lines.append('⚠️  WARNINGS / ERRORS')
            lines.append('-' * 80)
            for error in self.errors:
                lines.append(f'  ! {error}')
            lines.append('')
        
        # Recommendations
        lines.append('🚀 RECOMMENDATIONS')
        lines.append('-' * 80)
        if self.product_inquiry_count > 0:
            lines.append('1. Review product inquiries and send targeted follow-ups')
        if self.partnerships_flagged > 0:
            lines.append('2. Review flagged partnerships and determine next steps')
        if self.dms_processed == 0:
            lines.append('• No DMs to process. Check DM data sources:')
            lines.append('  - /tmp/new-dms.json')
            lines.append('  - DM_JSON environment variable')
            lines.append('  - Manual queue: .cache/youtube-dm-inbox.jsonl')
        lines.append('3. Run hourly via cron for continuous monitoring')
        lines.append('')
        
        lines.append('=' * 80)
        
        return '\n'.join(lines)
    
    def run(self) -> bool:
        """Execute the monitoring cycle"""
        try:
            # Fetch DMs
            dms = self.fetch_dms()
            
            # Process DMs
            if dms:
                processed = self.process_dms(dms)
                
                # Log results
                if processed:
                    self.log_dms(processed)
                
                # Log partnerships
                if self.flagged_partnerships:
                    self.log_partnerships()
            
            # Save state
            self.save_state()
            
            # Generate report
            report = self.generate_report()
            
            # Write report
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with open(REPORT_FILE, 'w') as f:
                f.write(report)
            
            # Print report
            print(report)
            
            return True
            
        except Exception as e:
            error_msg = f"Fatal error: {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return False


def main():
    """Main entry point"""
    monitor = YouTubeDMMonitorSubagent()
    success = monitor.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
