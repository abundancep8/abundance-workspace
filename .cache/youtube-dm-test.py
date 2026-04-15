#!/usr/bin/env python3
"""
Test script for YouTube DM Monitor
Tests categorization logic with sample DMs
"""

import json
import re
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


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
    """Test version without Google API dependencies"""
    
    LOG_FILE = Path('.cache/youtube-dms.jsonl')
    STATE_FILE = Path('.cache/youtube-dm-state.json')
    
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
            r'features.*comparison', r'demo', r'interested in'
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
    
    def log_dm(self, dm: DM):
        """Log DM to JSONL file"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(asdict(dm)) + '\n')


# Sample DMs for testing
SAMPLE_DMS = [
    {
        'id': 'dm_001',
        'sender': 'Alice Johnson',
        'sender_id': 'user_alice',
        'text': 'Hi! How do I set up the product? I\'m a bit confused about the installation process.'
    },
    {
        'id': 'dm_002',
        'sender': 'Bob Smith',
        'sender_id': 'user_bob',
        'text': 'Can you add me to your email newsletter? I want to get updates on new features.'
    },
    {
        'id': 'dm_003',
        'sender': 'Carol White',
        'sender_id': 'user_carol',
        'text': 'What\'s your pricing? I\'m interested in buying for my business.'
    },
    {
        'id': 'dm_004',
        'sender': 'Diana Prince',
        'sender_id': 'user_diana',
        'text': 'Hey! I run a tech blog with 50k followers. Would you be interested in a collaboration or sponsorship?'
    },
    {
        'id': 'dm_005',
        'sender': 'Eve Wilson',
        'sender_id': 'user_eve',
        'text': 'Tutorial help - I can\'t install on Windows. Getting error 404. Help?'
    },
    {
        'id': 'dm_006',
        'sender': 'Frank Thomas',
        'sender_id': 'user_frank',
        'text': 'I\'m a YouTube affiliate. Can we discuss an affiliate partnership program?'
    },
    {
        'id': 'dm_007',
        'sender': 'Grace Lee',
        'sender_id': 'user_grace',
        'text': 'Which product would you recommend for a small team of 5 people?'
    },
    {
        'id': 'dm_008',
        'sender': 'Henry Brown',
        'sender_id': 'user_henry',
        'text': 'How much does the premium plan cost per month?'
    },
]


def test_categorization():
    """Test DM categorization"""
    monitor = YouTubeDMMonitor()
    
    print("=" * 70)
    print("YouTube DM Monitor - Categorization Test")
    print("=" * 70)
    print()
    
    results = {
        'setup_help': [],
        'newsletter': [],
        'product_inquiry': [],
        'partnership': [],
    }
    
    for dm in SAMPLE_DMS:
        category_name, template_key = monitor.categorize_dm(dm['text'])
        response = monitor.RESPONSES[template_key]
        
        print(f"📨 {dm['sender']}")
        print(f"   Message: {dm['text']}")
        print(f"   Category: {category_name}")
        print(f"   Response: {response[:60]}...")
        print()
        
        results[template_key].append({
            'sender': dm['sender'],
            'text': dm['text'],
            'category': category_name
        })
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total DMs tested: {len(SAMPLE_DMS)}")
    print()
    print("Breakdown:")
    for key, items in results.items():
        category_name = key.replace('_', ' ').title()
        print(f"  {category_name}: {len(items)}")
    
    print()
    print("=" * 70)
    print()
    
    # Detailed breakdown
    for key, items in results.items():
        if items:
            category_name = key.replace('_', ' ').title()
            print(f"{category_name}:")
            for item in items:
                print(f"  • {item['sender']}")
            print()


def test_logging():
    """Test DM logging"""
    monitor = YouTubeDMMonitor()
    
    # Create a sample DM and log it
    dm = DM(
        timestamp=datetime.now().isoformat(),
        sender='Test User',
        sender_id='test_123',
        text='Test message',
        category='Product inquiry',
        response_sent=True,
        response_template='Thanks for your interest!',
        dm_id='test_dm_001'
    )
    
    monitor.log_dm(dm)
    
    # Read it back
    if monitor.log_file.exists():
        print("✓ DM logged successfully to", monitor.log_file)
        print()
        print("Log file contents:")
        with open(monitor.log_file, 'r') as f:
            content = f.read()
            if content:
                log_entry = json.loads(content.strip().split('\n')[-1])
                print(json.dumps(log_entry, indent=2))


if __name__ == '__main__':
    print()
    test_categorization()
    print("Testing logging...")
    test_logging()
