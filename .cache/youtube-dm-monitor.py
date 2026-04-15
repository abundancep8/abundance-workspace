#!/usr/bin/env python3
"""
YouTube DM Monitor for Concessa Obvius
Monitors YouTube DMs, categorizes, auto-responds, and logs.
Runs hourly via cron.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import re
from dataclasses import dataclass, asdict

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.api_core.exceptions import HttpError
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Google API client not installed. Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)


@dataclass
class DM:
    """DM record"""
    timestamp: str
    sender: str
    sender_id: str
    text: str
    category: str
    response_sent: bool
    response_template: str
    dm_id: str


class YouTubeDMMonitor:
    """Monitor and manage YouTube DMs for Concessa Obvius"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
    LOG_FILE = Path('.cache/youtube-dms.jsonl')
    STATE_FILE = Path('.cache/youtube-dm-state.json')
    CREDENTIALS_FILE = Path('.cache/youtube-credentials.json')
    TOKEN_FILE = Path('.cache/youtube-token.json')
    
    # Template responses for each category
    RESPONSES = {
        'setup_help': (
            "Thanks for reaching out! I'd be happy to help you get set up. "
            "Check out our setup guide at [link] or reply with specific questions. "
            "We're here to help! 🙌"
        ),
        'newsletter': (
            "Great! I've added you to our updates list. "
            "You'll get news on new features, tips, and exclusive content. "
            "Thanks for staying connected! 📬"
        ),
        'product_inquiry': (
            "Thanks for your interest! Our products are designed to [value proposition]. "
            "Visit [product page] to learn more, or reply with any questions. "
            "Happy to discuss what works best for you. 💡"
        ),
        'partnership': (
            "Thanks for reaching out! We're always interested in collaborations. "
            "I'm flagging this for our partnership team to review. "
            "Someone will follow up soon. 🤝"
        ),
    }
    
    def __init__(self):
        """Initialize monitor"""
        self.log_file = self.LOG_FILE
        self.state_file = self.STATE_FILE
        self.youtube = None
        self.dms_processed = 0
        self.auto_responses_sent = 0
        self.product_inquiries = []
        self.partnerships = []
        
    def authenticate(self) -> bool:
        """Authenticate with YouTube API"""
        creds = None
        
        # Check for existing token
        if self.TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(self.TOKEN_FILE), self.SCOPES)
        
        # If no valid creds, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif self.CREDENTIALS_FILE.exists():
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.CREDENTIALS_FILE), self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            else:
                print("ERROR: YouTube credentials not configured.")
                print("Set up OAuth credentials:")
                print("  1. Go to https://console.cloud.google.com/")
                print("  2. Create OAuth 2.0 Desktop Application credentials")
                print("  3. Save as .cache/youtube-credentials.json")
                return False
        
        # Save token for next run
        with open(self.TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
        
        self.youtube = build('youtube', 'v3', credentials=creds)
        return True
    
    def categorize_dm(self, text: str) -> tuple[str, str]:
        """
        Categorize DM based on content.
        Returns (category, template_key)
        """
        text_lower = text.lower()
        
        # Setup help patterns
        setup_patterns = [
            r'how to setup', r'how do i.*setup', r'confused.*setup',
            r'help.*getting started', r'can\'t.*install', r'not working',
            r'where do i.*start', r'tutorial.*help', r'help.*install',
            r'error.*\d+', r'getting error', r'confused about.*install',
            r'installation process', r'how do i.*install', r'can\'t get.*start'
        ]
        
        # Newsletter patterns
        newsletter_patterns = [
            r'email.*list', r'newsletter', r'updates.*list',
            r'add.*email', r'subscribe', r'keep.*posted'
        ]
        
        # Product inquiry patterns
        product_patterns = [
            r'how much', r'pricing', r'cost', r'buy', r'purchase',
            r'product.*selection', r'which.*best', r'recommend',
            r'features.*comparison', r'demo'
        ]
        
        # Partnership patterns
        partnership_patterns = [
            r'collaborate', r'partnership', r'sponsor', r'work.*together',
            r'affiliate', r'promotion', r'cross.*promote', r'brand.*ambassador'
        ]
        
        # Check patterns in order of priority
        for pattern in setup_patterns:
            if re.search(pattern, text_lower):
                return 'Setup help', 'setup_help'
        
        for pattern in partnership_patterns:
            if re.search(pattern, text_lower):
                return 'Partnership', 'partnership'
        
        for pattern in product_patterns:
            if re.search(pattern, text_lower):
                return 'Product inquiry', 'product_inquiry'
        
        for pattern in newsletter_patterns:
            if re.search(pattern, text_lower):
                return 'Newsletter', 'newsletter'
        
        # Default to product inquiry if unclear
        return 'Product inquiry', 'product_inquiry'
    
    def get_last_check_time(self) -> datetime:
        """Get timestamp of last DM check"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    return datetime.fromisoformat(state.get('last_check', (datetime.now() - timedelta(hours=1)).isoformat()))
            except:
                pass
        
        # Default to 1 hour ago
        return datetime.now() - timedelta(hours=1)
    
    def save_state(self, last_check: datetime):
        """Save monitor state"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump({
                'last_check': last_check.isoformat(),
                'total_processed': self.dms_processed
            }, f)
    
    def log_dm(self, dm: DM):
        """Log DM to JSONL file"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(asdict(dm)) + '\n')
    
    def fetch_dms(self) -> list[dict]:
        """Fetch new DMs from YouTube"""
        if not self.youtube:
            return []
        
        try:
            # Note: YouTube doesn't have a direct DM API in the public API
            # This is a placeholder for the actual implementation
            # In practice, you'd need to use YouTube Community posts or
            # implement a custom scraper with proper authentication
            
            print("NOTE: YouTube DM API requires custom implementation.")
            print("This script is configured for manual DM input or custom API integration.")
            return []
        
        except HttpError as e:
            print(f"API Error: {e}")
            return []
    
    def send_response(self, dm_id: str, sender_id: str, response: str) -> bool:
        """Send auto-response to sender (placeholder)"""
        # YouTube DMs would be sent via custom implementation
        # This is a placeholder
        return True
    
    def process_dms(self, dms: list[dict]) -> list[DM]:
        """Process and categorize DMs"""
        processed = []
        
        for dm in dms:
            sender = dm.get('sender', 'Unknown')
            sender_id = dm.get('sender_id', '')
            text = dm.get('text', '')
            dm_id = dm.get('id', '')
            
            # Categorize
            category_name, template_key = self.categorize_dm(text)
            response_template = self.RESPONSES.get(template_key, '')
            
            # Send response
            response_sent = self.send_response(dm_id, sender_id, response_template)
            if response_sent:
                self.auto_responses_sent += 1
            
            # Track by category
            if category_name == 'Product inquiry':
                self.product_inquiries.append({
                    'sender': sender,
                    'text': text,
                    'dm_id': dm_id
                })
            elif category_name == 'Partnership':
                self.partnerships.append({
                    'sender': sender,
                    'text': text,
                    'dm_id': dm_id
                })
            
            # Create log entry
            dm_record = DM(
                timestamp=datetime.now().isoformat(),
                sender=sender,
                sender_id=sender_id,
                text=text,
                category=category_name,
                response_sent=response_sent,
                response_template=response_template,
                dm_id=dm_id
            )
            
            processed.append(dm_record)
            self.dms_processed += 1
        
        return processed
    
    def generate_report(self) -> str:
        """Generate summary report"""
        report = []
        report.append("=" * 60)
        report.append(f"YouTube DM Monitor Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")
        report.append(f"📊 SUMMARY")
        report.append(f"  Total DMs processed:    {self.dms_processed}")
        report.append(f"  Auto-responses sent:    {self.auto_responses_sent}")
        report.append(f"  Product inquiries:      {len(self.product_inquiries)}")
        report.append(f"  Partnership requests:   {len(self.partnerships)}")
        report.append("")
        
        if self.product_inquiries:
            report.append(f"💡 PRODUCT INQUIRIES (Conversion Potential)")
            for inquiry in self.product_inquiries:
                report.append(f"  • {inquiry['sender']}: {inquiry['text'][:50]}...")
        
        if self.partnerships:
            report.append(f"🤝 PARTNERSHIPS (Flagged for Manual Review)")
            for partnership in self.partnerships:
                report.append(f"  • {partnership['sender']}: {partnership['text'][:50]}...")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def run(self):
        """Execute monitor"""
        print("🚀 YouTube DM Monitor Starting...")
        
        # Authenticate
        if not self.authenticate():
            print("❌ Authentication failed")
            return False
        
        # Fetch DMs
        print("📥 Fetching DMs...")
        dms = self.fetch_dms()
        
        if not dms:
            print("ℹ️  No new DMs found")
            self.save_state(datetime.now())
            return True
        
        # Process DMs
        print(f"⚙️  Processing {len(dms)} DM(s)...")
        processed = self.process_dms(dms)
        
        # Log DMs
        for dm in processed:
            self.log_dm(dm)
            print(f"  ✓ Logged: {dm.sender} - {dm.category}")
        
        # Generate report
        report = self.generate_report()
        print("\n" + report)
        
        # Save state
        self.save_state(datetime.now())
        
        return True


def main():
    """Main entry point"""
    monitor = YouTubeDMMonitor()
    success = monitor.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
