#!/usr/bin/env python3
"""
Test Suite for YouTube Comment Monitor
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from categorizer import CommentCategorizer
from logger import CommentLogger


def test_categorization():
    """Test comment categorization."""
    print("\n📋 Testing Comment Categorization...")
    
    categorizer = CommentCategorizer()
    
    test_cases = [
        # Questions
        ("How do I get started?", "1_questions"),
        ("What's the cost?", "1_questions"),
        ("how can i use this tool", "1_questions"),
        ("What is this?", "1_questions"),
        
        # Praise
        ("This is amazing!", "2_praise"),
        ("Love this so much ❤️", "2_praise"),
        ("Brilliant work!", "2_praise"),
        ("Thank you for this!", "2_praise"),
        ("Incredibly helpful", "2_praise"),
        
        # Spam
        ("Buy Bitcoin now!", "3_spam"),
        ("Join my MLM opportunity", "3_spam"),
        ("Click here for free crypto", "3_spam"),
        ("Earn money fast from home", "3_spam"),
        
        # Sales
        ("Let's collaborate!", "4_sales"),
        ("Partnership opportunity", "4_sales"),
        ("Interested in working together", "4_sales"),
        ("Can we partner?", "4_sales"),
    ]
    
    passed = 0
    failed = 0
    
    for text, expected in test_cases:
        result = categorizer.categorize(text)
        status = "✅" if result == expected else "❌"
        
        print(f"{status} '{text}' -> {result} (expected: {expected})")
        
        if result == expected:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_logging(cache_dir: Path = None):
    """Test JSONL logging."""
    print("\n📝 Testing Comment Logging...")
    
    if cache_dir is None:
        cache_dir = Path(__file__).parent / "test_cache"
        cache_dir.mkdir(exist_ok=True)
    
    logger = CommentLogger(cache_dir)
    
    # Create test comments
    test_comments = [
        {
            'timestamp': '2026-04-17T10:00:00Z',
            'commenter_name': 'Alice',
            'commenter_id': 'UC1234',
            'comment_text': 'Great video!',
            'video_id': 'vid001',
            'category': '2_praise',
            'response_status': 'sent',
            'response_text': 'Thanks Alice!',
        },
        {
            'timestamp': '2026-04-17T10:05:00Z',
            'commenter_name': 'Bob',
            'commenter_id': 'UC5678',
            'comment_text': 'How do I use this?',
            'video_id': 'vid001',
            'category': '1_questions',
            'response_status': 'sent',
            'response_text': 'Here are the docs...',
        },
    ]
    
    # Log comments
    logged = logger.log_batch(test_comments)
    print(f"✅ Logged {logged} comments")
    
    # Read comments back
    comments = logger.read_comments(limit=10)
    print(f"✅ Read {len(comments)} comments from file")
    
    # Generate report
    report = logger.generate_report()
    print(f"✅ Generated report:")
    print(f"   - Total: {report['total_comments']}")
    print(f"   - Questions: {report['by_category']['1_questions']}")
    print(f"   - Praise: {report['by_category']['2_praise']}")
    print(f"   - Sent: {report['by_status']['sent']}")
    
    return logged == len(test_comments) and len(comments) > 0


def test_response_templates():
    """Test response templates."""
    print("\n📧 Testing Response Templates...")
    
    categorizer = CommentCategorizer()
    
    # Test default templates
    templates = {
        '1_questions': categorizer.get_response_template('1_questions'),
        '2_praise': categorizer.get_response_template('2_praise'),
    }
    
    for category, template in templates.items():
        if template:
            print(f"✅ {category}:")
            print(f"   {template[:50]}...")
        else:
            print(f"❌ No template for {category}")
    
    return all(templates.values())


def test_with_config():
    """Test with actual config file."""
    print("\n⚙️  Testing with Real Config...")
    
    config_path = Path.home() / '.openclaw' / 'workspace' / '.cache' / 'youtube-monitor-config.json'
    
    if not config_path.exists():
        print(f"⚠️  Config not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        categorizer = CommentCategorizer(config)
        print(f"✅ Loaded config for {config['channel']['name']}")
        
        # Test with config keywords
        test_text = "How do I start?"
        result = categorizer.categorize(test_text)
        print(f"✅ Categorized test with config: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("YouTube Comment Monitor - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Categorization", test_categorization()))
    results.append(("Logging", test_logging()))
    results.append(("Templates", test_response_templates()))
    results.append(("Config", test_with_config()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
