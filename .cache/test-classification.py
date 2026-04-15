#!/usr/bin/env python3
"""
Simple classification test — test without needing API key.
"""

import re
from enum import Enum


class CommentCategory(Enum):
    QUESTIONS = "questions"
    PRAISE = "praise"
    SPAM = "spam"
    SALES = "sales"


def classify_comment(text: str) -> CommentCategory:
    """Classify a comment into one of four categories."""
    text_lower = text.lower()

    # SALES PATTERNS FIRST (take priority over questions)
    sales_keywords = [
        r"\bpartnership\b", r"\bcollaborate\b", r"\bsponsorship\b",
        r"\bwork with\b", r"\bbusiness opportunity\b", r"\bwhite label\b",
        r"\baffiliate\b", r"\brefer to business\b", r"\blet's partner\b",
        r"\binterested in working\b", r"\binterested.*working\b",
    ]

    for pattern in sales_keywords:
        if re.search(pattern, text_lower):
            return CommentCategory.SALES

    # SPAM PATTERNS
    spam_keywords = [
        r"\bcrypto\b", r"\bbitcoin\b", r"\bnft\b",
        r"\bmlm\b", r"\bmulti.?level\b", r"\bpromo",
        r"\bclick here\b", r"\blink in bio\b", r"\bcheck my profile\b",
        r"\bfollow me\b", r"\bsubscribe to my channel\b",
        r"\bvisit my site\b", r"\bporn\b", r"\bamazon link\b",
    ]

    for pattern in spam_keywords:
        if re.search(pattern, text_lower):
            return CommentCategory.SPAM

    # QUESTIONS patterns
    question_keywords = [
        r"\bhow\b", r"\bwhat\b", r"\bwhere\b", r"\bwhen\b", r"\bwhy\b",
        r"\bcan i\b", r"\bcould you\b", r"\bdo you\b",
        r"\bhow to\b", r"\btools\b", r"\bcost\b", r"\bprice\b",
        r"\btimeline\b", r"\bstart\b", r"\bbegin\b", r"\blean more\b",
        r"\bhelp\b", r"\bquestion\b", r"\b\?\s*$",
    ]

    for pattern in question_keywords:
        if re.search(pattern, text_lower):
            return CommentCategory.QUESTIONS

    # PRAISE patterns (default)
    praise_keywords = [
        r"\bamazing\b", r"\bawesome\b", r"\bgreat\b", r"\blove\b",
        r"\binspir", r"\bthanks\b", r"\bappreciate\b", r"\bbeautiful\b",
        r"\bincredible\b", r"\bfantastic\b", r"\bwonderful\b",
        r"\bthumbs up\b", r"\b👍\b", r"\b❤️?\b",
    ]

    for pattern in praise_keywords:
        if re.search(pattern, text_lower):
            return CommentCategory.PRAISE

    return CommentCategory.PRAISE


def run_tests():
    """Run classification tests."""
    print("\n" + "=" * 70)
    print("🧪 YOUTUBE COMMENT MONITOR — CLASSIFICATION TESTS")
    print("=" * 70)

    test_cases = [
        # QUESTIONS
        ("How do I get started with this?", CommentCategory.QUESTIONS),
        ("What tools do you recommend?", CommentCategory.QUESTIONS),
        ("Can I use this on Windows?", CommentCategory.QUESTIONS),
        ("What's the cost?", CommentCategory.QUESTIONS),
        ("How long does it take to learn?", CommentCategory.QUESTIONS),
        ("Help! I don't understand step 3", CommentCategory.QUESTIONS),
        ("Where can I learn more?", CommentCategory.QUESTIONS),
        ("When should I start?", CommentCategory.QUESTIONS),
        ("Why would I use this?", CommentCategory.QUESTIONS),
        
        # PRAISE
        ("This is amazing! Great content!", CommentCategory.PRAISE),
        ("Love this! Thanks for sharing", CommentCategory.PRAISE),
        ("Absolutely inspiring! ❤️", CommentCategory.PRAISE),
        ("Fantastic work! 👍", CommentCategory.PRAISE),
        ("Incredible tutorial!", CommentCategory.PRAISE),
        ("Thank you so much for this!", CommentCategory.PRAISE),
        ("Beautiful explanation!", CommentCategory.PRAISE),
        ("Awesome video!", CommentCategory.PRAISE),
        
        # SPAM
        ("Buy Bitcoin now! Click here", CommentCategory.SPAM),
        ("Join my MLM and get rich quick", CommentCategory.SPAM),
        ("Check my profile for crypto tips", CommentCategory.SPAM),
        ("NFT opportunity in my bio", CommentCategory.SPAM),
        ("Subscribe to my channel", CommentCategory.SPAM),
        ("Visit my site for more", CommentCategory.SPAM),
        ("Amazon link in my profile", CommentCategory.SPAM),
        
        # SALES
        ("Interested in a partnership with your channel", CommentCategory.SALES),
        ("Let's collaborate on some content", CommentCategory.SALES),
        ("We offer white label solutions", CommentCategory.SALES),
        ("Would you be interested in sponsorship?", CommentCategory.SALES),
        ("Join our affiliate program", CommentCategory.SALES),
        ("Work with us on a project", CommentCategory.SALES),
    ]

    passed = 0
    failed = 0

    for comment_text, expected_category in test_cases:
        result = classify_comment(comment_text)
        is_pass = result == expected_category
        status = "✅" if is_pass else "❌"
        
        if is_pass:
            passed += 1
        else:
            failed += 1
        
        display_text = (comment_text[:50] + "...") if len(comment_text) > 50 else comment_text
        print(f"{status} {expected_category.value:10s} | {display_text:53s} → {result.value}")

    # Summary
    print("\n" + "=" * 70)
    print(f"📊 RESULTS: {passed} ✅ passed, {failed} ❌ failed out of {len(test_cases)} tests")
    
    if failed == 0:
        print("🎉 All classification tests PASSED!")
    else:
        print(f"⚠️  {failed} tests FAILED")
    
    print("=" * 70 + "\n")

    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
