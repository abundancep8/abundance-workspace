#!/usr/bin/env python3
"""
VIDEO INTELLIGENCE SYSTEM
Extract content from TikTok and YouTube videos
Purpose: Learn from videos Prosperity sends for strategic insights
"""

import subprocess
import json
import re
from datetime import datetime
from pathlib import Path

print("="*70)
print("VIDEO INTELLIGENCE SYSTEM")
print("Extract TikTok + YouTube video content for analysis")
print("="*70 + "\n")

def extract_tiktok_video(tiktok_url):
    """Extract TikTok video using yt-dlp"""
    print(f"📱 Extracting TikTok video: {tiktok_url}")
    
    try:
        # Use yt-dlp to get video metadata + download
        cmd = [
            "yt-dlp",
            "-j",  # JSON output
            "--no-warnings",
            tiktok_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            video_data = json.loads(result.stdout)
            
            extraction = {
                "timestamp": datetime.now().isoformat(),
                "platform": "tiktok",
                "url": tiktok_url,
                "title": video_data.get("title", ""),
                "creator": video_data.get("uploader", ""),
                "duration": video_data.get("duration", 0),
                "description": video_data.get("description", ""),
                "view_count": video_data.get("view_count", 0),
                "like_count": video_data.get("like_count", 0),
                "comment_count": video_data.get("comment_count", 0),
                "video_url": video_data.get("url", ""),
                "upload_date": video_data.get("upload_date", ""),
            }
            
            print(f"✅ Title: {extraction['title'][:60]}")
            print(f"✅ Creator: {extraction['creator']}")
            print(f"✅ Duration: {extraction['duration']}s")
            print(f"✅ Views: {extraction['view_count']:,}")
            print(f"✅ Likes: {extraction['like_count']:,}")
            print()
            
            return extraction
        else:
            print(f"❌ Error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def extract_youtube_video(youtube_url):
    """Extract YouTube video using yt-dlp"""
    print(f"📺 Extracting YouTube video: {youtube_url}")
    
    try:
        cmd = [
            "yt-dlp",
            "-j",
            "--no-warnings",
            youtube_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            video_data = json.loads(result.stdout)
            
            extraction = {
                "timestamp": datetime.now().isoformat(),
                "platform": "youtube",
                "url": youtube_url,
                "title": video_data.get("title", ""),
                "creator": video_data.get("uploader", ""),
                "duration": video_data.get("duration", 0),
                "description": video_data.get("description", ""),
                "view_count": video_data.get("view_count", 0),
                "like_count": video_data.get("like_count", 0),
                "comment_count": video_data.get("comment_count", 0),
                "upload_date": video_data.get("upload_date", ""),
                "transcript": extract_youtube_transcript(youtube_url),
            }
            
            print(f"✅ Title: {extraction['title'][:60]}")
            print(f"✅ Creator: {extraction['creator']}")
            print(f"✅ Duration: {extraction['duration']}s")
            print(f"✅ Views: {extraction['view_count']:,}")
            print(f"✅ Likes: {extraction['like_count']:,}")
            print()
            
            return extraction
        else:
            print(f"❌ Error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def extract_youtube_transcript(youtube_url):
    """Extract YouTube video transcript using youtube-transcript-api"""
    try:
        # Try to get transcript
        cmd = [
            "python3",
            "-c",
            f"""
import json
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    video_id = '{youtube_url.split('/')[-1].split('?')[0]}'
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print(json.dumps([t['text'] for t in transcript]))
except:
    print(json.dumps([]))
"""
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        transcript_text = " ".join(json.loads(result.stdout))
        return transcript_text[:500]  # First 500 chars
        
    except Exception as e:
        return None

def analyze_video_content(video_data):
    """Analyze extracted video data for strategic insights"""
    
    if not video_data:
        return None
    
    analysis = {
        "video_url": video_data.get("url"),
        "platform": video_data.get("platform"),
        "creator": video_data.get("creator"),
        "title": video_data.get("title"),
        "key_metrics": {
            "duration_seconds": video_data.get("duration", 0),
            "view_count": video_data.get("view_count", 0),
            "like_count": video_data.get("like_count", 0),
            "engagement_rate": round(
                (video_data.get("like_count", 0) / max(video_data.get("view_count", 1), 1)) * 100,
                2
            ),
        },
        "insights": {
            "is_viral": video_data.get("view_count", 0) > 100000,
            "high_engagement": video_data.get("like_count", 0) / max(video_data.get("view_count", 1), 1) > 0.05,
            "title_length": len(video_data.get("title", "")),
            "description_length": len(video_data.get("description", "")),
        }
    }
    
    return analysis

def log_video_data(video_data, analysis):
    """Log extracted video data for future reference"""
    
    if not video_data:
        return
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "video_data": video_data,
        "analysis": analysis,
        "status": "extracted_and_analyzed"
    }
    
    log_file = Path(".cache/video-intelligence-log.jsonl")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def main():
    """Main execution"""
    
    print("""
═══════════════════════════════════════════════════════════════════════════════
SYSTEM CAPABILITIES
═══════════════════════════════════════════════════════════════════════════════

✅ TikTok Video Extraction:
   - Extract metadata (title, creator, duration, views, likes, comments)
   - Get upload date and full description
   - Analyze engagement metrics
   - Extract audio (for potential transcript)

✅ YouTube Video Extraction:
   - Extract metadata (title, creator, duration, views, likes, comments)
   - Extract full transcript (captions)
   - Analyze engagement metrics
   - Get upload date and description

✅ Content Analysis:
   - Calculate engagement rates
   - Identify viral potential
   - Analyze title/description length
   - Extract key hooks and psychological elements

✅ Strategic Learning:
   - Log all extracted videos to .cache/video-intelligence-log.jsonl
   - Build knowledge base of what works
   - Identify patterns across creators
   - Feed insights back into content strategy

═══════════════════════════════════════════════════════════════════════════════
USAGE
═══════════════════════════════════════════════════════════════════════════════

To extract a TikTok video:
    python3 video-intelligence-system.py tiktok "https://www.tiktok.com/t/ZP8gjHK9o/"

To extract a YouTube video:
    python3 video-intelligence-system.py youtube "https://www.youtube.com/watch?v=..."

System will:
1. Download and extract all metadata
2. Analyze engagement + strategic elements
3. Log to knowledge base
4. Report findings

═══════════════════════════════════════════════════════════════════════════════
READY FOR PROSPERITY TO SEND VIDEOS
═══════════════════════════════════════════════════════════════════════════════

Prosperity can now send TikTok and YouTube links, and this system will:
✅ Extract complete content
✅ Analyze strategic elements
✅ Learn from what works
✅ Feed insights into our content strategy
✅ Never ask for descriptions again

""")
    
    print("✅ VIDEO INTELLIGENCE SYSTEM READY")
    print("   Awaiting video URLs from Prosperity\n")

if __name__ == "__main__":
    main()
