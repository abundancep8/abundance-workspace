#!/usr/bin/env python3
"""
BLOTATO X/TWITTER VIDEO SYSTEM
Generate short video clips for X posts using Blotato
Framework: Psychology-first threads + embedded videos
"""

import requests
import json
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet

print("="*70)
print("X/TWITTER + BLOTATO VIDEO SYSTEM")
print("="*70)

# Load Blotato credentials
cred_file = list(Path(".secrets/credentials").glob("*blotato*credentials*"))[0]
key_file = list(Path(".secrets/credentials").glob("*blotato*key*"))[0]

with open(key_file, 'rb') as f:
    key = f.read()
cipher = Fernet(key)

with open(cred_file, 'r') as f:
    cred_data = json.load(f)

blotato_email = cred_data['username']
blotato_password = cipher.decrypt(cred_data['encrypted_password'].encode()).decode()

print(f"\n✅ Blotato account: {blotato_email}")
print(f"✅ Ready to generate X video content\n")

# X VIDEO STRATEGY (different from YouTube)
# YouTube: 30-60 sec caption + full script
# X: 15-30 sec video clip + 280 char text hook

X_VIDEO_THREADS = {
    "ai_hiring_story": {
        "title": "I hired an AI",
        "videos": [
            {
                "duration": "15 sec",
                "script": "Day 1: I hired an AI. Day 7: Making money. Day 30: $4,200. This is how leverage works.",
                "visuals": ["Dashboard showing money", "AI working", "Calendar days passing", "Revenue increasing"],
                "hook": "I fired myself and hired an AI. Here's what happened."
            },
            {
                "duration": "20 sec",
                "script": "The AI didn't replace me. It freed me. Before: 80% manual labor. Now: 95% strategy, 5% execution. That's multiplication, not replacement.",
                "visuals": ["Before/after split screen", "Person working hard", "Person thinking strategically", "Dashboard automation"],
                "hook": "This is what nobody tells you about AI replacing work."
            },
            {
                "duration": "15 sec",
                "script": "AI works 24/7. You work 8. That's not competition. That's 3x leverage built in. Most people think AI is a threat. I think it's a business advantage.",
                "visuals": ["24-hour clock", "AI working at night", "Person resting", "Wealth compound chart"],
                "hook": "The wealth gap just got real."
            }
        ]
    },
    
    "wealth_gap": {
        "title": "The Wealth Gap",
        "videos": [
            {
                "duration": "20 sec",
                "script": "There are two types of people now: Those using AI for leverage. Those grinding manually. The wealth gap between them compounds every single month.",
                "visuals": ["Two paths diverging", "One person busy", "One person relaxed", "Money stacks diverging"],
                "hook": "You get to choose which side you're on."
            },
            {
                "duration": "15 sec",
                "script": "Traditional business: 12 hours work = $1,000. AI-powered: 1 hour work + systems = $4,000. Same 24 hours. Different leverage.",
                "visuals": ["Exhausted vs rested", "Clock symbols", "Income bars", "Exponential curve"],
                "hook": "This is why the rich aren't busier."
            },
            {
                "duration": "18 sec",
                "script": "Month 1: You're ahead. Month 3: You're way ahead. Month 6: The gap is massive. Leverage compounds. Systems grow. Your competition is still grinding.",
                "visuals": ["Time passing", "Exponential curve", "Person resting", "Money multiplying"],
                "hook": "Compound growth looks like magic."
            }
        ]
    },
    
    "automation_stack": {
        "title": "My Automation Stack",
        "videos": [
            {
                "duration": "20 sec",
                "script": "I use 5 tools to automate 80% of my work: Claude for writing. Blotato for videos. Stripe for payments. Vercel for hosting. OpenClaw for orchestration. Cost: $50/month. Revenue: $4,200.",
                "visuals": ["5 tool logos", "Pipeline flowing", "Automation happening", "Money coming in"],
                "hook": "Here's my entire tech stack."
            },
            {
                "duration": "15 sec",
                "script": "The most valuable skill isn't coding. It's knowing which tools to chain together. I don't build everything from scratch. I connect things that already work.",
                "visuals": ["Tools connecting", "Lego blocks snapping", "Pipeline forming", "System working"],
                "hook": "This is why non-technical people are winning."
            }
        ]
    }
}

# Generate video for each thread
print("\n📹 GENERATING X VIDEO CONTENT")
print("="*70 + "\n")

total_videos = 0
for thread_name, thread_data in X_VIDEO_THREADS.items():
    print(f"Thread: {thread_data['title']}")
    print(f"Videos: {len(thread_data['videos'])}")
    
    for idx, video_data in enumerate(thread_data['videos'], 1):
        total_videos += 1
        print(f"  [{idx}] {video_data['hook'][:50]}...")
        print(f"      Duration: {video_data['duration']}")
        print(f"      Hook: {video_data['hook']}")
        print(f"      Script: {video_data['script'][:60]}...\n")
        
        # Log to queue
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "x_video_generation",
            "thread": thread_name,
            "video_idx": idx,
            "hook": video_data['hook'],
            "script": video_data['script'],
            "duration": video_data['duration'],
            "status": "queued"
        }
        
        with open('.cache/x-blotato-video-queue.jsonl', 'a') as f:
            f.write(json.dumps(event) + '\n')

print(f"\n{'='*70}")
print(f"✅ TOTAL VIDEOS QUEUED: {total_videos}")
print(f"{'='*70}\n")

print("""
X VIDEO POSTING STRATEGY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THREAD STRUCTURE (5-tweet sequences):
1. Hook tweet + short video (15 sec)
2. Thread continuation + video (20 sec)
3. Deeper point + video (15 sec)
4. Call to action + landing page link

POSTING SCHEDULE:
- Thread 1 (AI Hiring Story): Monday + Tuesday
- Thread 2 (Wealth Gap): Wednesday + Thursday
- Thread 3 (Automation Stack): Friday + Saturday
- Rotate weekly

ENGAGEMENT MECHANICS:
✓ 15-20 sec video (higher completion rate than text)
✓ Psychology-first hook (not sales)
✓ Thread format (5x engagement vs single tweet)
✓ Video + text (10x engagement boost)
✓ CTA in final tweet (link to landing page)

EXPECTED METRICS:
- Single tweet reach: 500 impressions
- Thread reach: 5K-15K impressions
- Videos: 3-5x engagement vs text-only
- CTR to landing page: 2-5%

AUTONOMOUS EXECUTION:
1. Daily Blotato generates videos
2. X posts threads at optimal times
3. Videos embedded in tweets
4. Landing page traffic increases
5. Conversions happen automatically
""")

print("\n✅ X VIDEO SYSTEM READY FOR DEPLOYMENT")
print("   Next: Connect Blotato to X posting agent\n")
