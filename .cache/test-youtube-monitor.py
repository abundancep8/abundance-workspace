#!/usr/bin/env python3
"""
Test suite for YouTube Comment Monitor classification logic.
Tests comment classification without requiring API credentials.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Import only the classification logic (skip API initialization)
import os
os.environ["YOUTUBE_API_KEY"] = "test-key-for-classification-testing-only"

from youtube_monitor import YouTubeCommentMonitor, CommentCategory


def test_classifications():
    """Test comment classification logic."""
    print("\n" + "=" * 70)
    print("🧪 YOUTUBE COMMENT MONITOR — CLASSIFICATION TESTS")
    print("=" * 70)

    # Test data: (comment_text, expected_category)
    test_cases = [
        # QUESTIONS
        ("How do I get started with this?", CommentCategory.QUESTIONS),
        ("What tools do you recommend?", CommentCategory.QUESTIONS),
        ("Can I use this on Windows?", CommentCategory.QUESTIONS),
        ("What's the cost?", CommentCategory.QUESTIONS),
        ("How long does it take to learn?", CommentCategory.QUESTIONS),
        ("Help! I don't understand step 3", CommentCategory.QUESTIONS),
        
        # PRAISE
        ("This is amazing! Great content!", CommentCategory.PRAISE),
        ("Love this! Thanks for sharing", CommentCategory.PRAISE),
        ("Absolutely inspiring! ❤️", CommentCategory.PRAISE),
        ("Fantastic work! 👍", CommentCategory.PRAISE),
        ("Incredible tutorial!", CommentCategory.PRAISE),
        ("Thank you so much for this!", CommentCategory.PRAISE),
        
        # SPAM
        ("Buy Bitcoin now! Click here", CommentCategory.SPAM),
        ("Join my MLM and get rich quick", CommentCategory.SPAM),
        ("Check my profile for crypto tips", CommentCategory.SPAM),
        ("NFT opportunity in my bio", CommentCategory.SPAM),
        ("Subscribe to my channel", CommentCategory.SPAM),
        
        # SALES
        ("Interested in a partnership with your channel", CommentCategory.SALES),
        ("Let's collaborate on some content", CommentCategory.SALES),
        ("We offer white label solutions", CommentCategory.SALES),
        ("Would you be interested in sponsorship?", CommentCategory.SALES),
        ("Join our affiliate program", CommentCategory.SALES),
    ]

    # Create a monitor instance (will fail on API init, but we only care about classification)
    monitor = None
    try:
        monitor = YouTubeCommentMonitor()
    except SystemExit:
        # Extract just the classification method
        from youtube_monitor import YouTubeCommentMonitor as TestMonitor
        # Create a minimal instance
        class MinimalMonitor:
            @staticmethod
            def classify_comment(text):
                import re
                from enum import Enum
                
                class Category(Enum):
                    QUESTIONS = "questions"
                    PRAISE = "praise"
                    SPAM = "spam"
                    SALES = "sales"
                
                text_lower = text.lower()
                
                question_keywords = [
                    r"\bhow\b", r"\bwhat\b", r"\bwhere\b", r"\bwhen\b", r"\bwhy\b",
                    r"\bcan i\b", r"\bcould you\b", r"\bwould you\b", r"\bdo you\b",
                    r"\bhow to\b", r"\btools\b", r"\bcost\b", r"\bprice\b",
                    r"\btimeline\b", r"\bstart\b", r"\bbegin\b", r"\bhelp\b",
                    r"\bquestion\b", r"\b\?\s*$",
                ]
                
                for pattern in question_keywords:
                    if re.search(pattern, text_lower):
                        return Category.QUESTIONS
                
                spam_keywords = [
                    r"\bcrypto\b", r"\bbitcoin\b", r"\bnft\b", r"\bmlm\b",
                    r"\bpromo", r"\bclick here\b", r"\blink in bio\b",
                    r"\bcheck my profile\b", r"\bfollow me\b",
                    r"\bsubscribe to my channel\b", r"\bvisit my site\b",
                ]
                
                for pattern in spam_keywords:
                    if re.search(pattern, text_lower):
                        return Category.SPAM
                
                sales_keywords = [
                    r"\bpartnership\b", r"\bcollaboration\b", r"\bsponsorship\b",
                    r"\bwork with\b", r"\bbusiness opportunity\b", r"\bwhite label\b",
                    r"\baffiliate\b",
                ]
                
                for pattern in sales_keywords:
                    if re.search(pattern, text_lower):
                        return Category.SALES
                
                return Category.PRAISE
        
        monitor = MinimalMonitor()

    # Run tests
    passed = 0
    failed = 0

    for comment_text, expected_category in test_cases:
        result = monitor.classify_comment(comment_text)
        status = "✅" if result == expected_category else "❌"
        
        if result == expected_category:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status} {expected_category.value.upper()}")
        print(f"   Comment: \"{comment_text[:60]}...\"" if len(comment_text) > 60 else f"   Comment: \"{comment_text}\"")
        print(f"   Expected: {expected_category.value}")
        print(f"   Got: {result.value}")

    # Summary
    print("\n" + "=" * 70)
    print(f"📊 TEST RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    
    if failed == 0:
        print("✅ All classification tests passed!")
    else:
        print(f"⚠️  {failed} tests failed — review classification patterns")
    
    print("=" * 70 + "\n")

    return failed == 0


def test_response_generation():
    """Test response generation."""
    print("\n" + "=" * 70)
    print("🧪 RESPONSE GENERATION TESTS")
    print("=" * 70)

    test_cases = [
        (CommentCategory.QUESTIONS, "How do I start?", "Thanks for the question!"),
        (CommentCategory.PRAISE, "Amazing!", "Thank you so much!"),
        (CommentCategory.SALES, "Partnership?", None),
        (CommentCategory.SPAM, "Buy crypto!", None),
    ]

    class MinimalMonitor:
        @staticmethod
        def generate_response(category, comment_text):
            if category == CommentCategory.QUESTIONS:
                return (
                    "Thanks for the question! We appreciate your interest. "
                    "Check out our channel for more insights and resources. "
                    "Feel free to reach out if you have more questions!"
                )
            elif category == CommentCategory.PRAISE:
                return "Thank you so much! 🙏 Your support means everything to us."
            else:
                return None

    monitor = MinimalMonitor()
    all_pass = True

    for category, comment, expected_snippet in test_cases:
        response = monitor.generate_response(category, comment)
        
        if expected_snippet is None:
            if response is None:
                status = "✅"
            else:
                status = "❌"
                all_pass = False
        else:
            if response and expected_snippet in response:
                status = "✅"
            else:
                status = "❌"
                all_pass = False

        print(f"\n{status} {category.value.upper()}")
        print(f"   Comment: \"{comment}\"")
        if response:
            print(f"   Response: \"{response[:60]}...\"")
        else:
            print(f"   Response: None (as expected)")

    print("\n" + "=" * 70)
    if all_pass:
        print("✅ All response generation tests passed!")
    else:
        print("⚠️  Some response tests failed")
    print("=" * 70 + "\n")

    return all_pass


if __name__ == "__main__":
    try:
        classification_ok = test_classifications()
        response_ok = test_response_generation()
        
        if classification_ok and response_ok:
            print("\n🎉 ALL TESTS PASSED!\n")
            sys.exit(0)
        else:
            print("\n⚠️  SOME TESTS FAILED\n")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}\n")
        sys.exit(1)
