# YouTube Comment Monitor - Authentication Workaround

## Status
**API Status:** ❌ FAILED - YouTube OAuth token expired  
**Last Successful Run:** 2026-04-18T09:01:45Z  
**Current Attempt:** 2026-04-18T16:30:00Z (PDT)

## Problem
YouTube Data API v3 requires OAuth2 authentication. The current token has expired and needs refresh.

## Solution & Next Steps

### Option 1: Refresh OAuth Token (Recommended)
1. Run: `gcloud auth application-default login`
2. Or visit: https://accounts.google.com/o/oauth2/v2/auth with Concessa Obvius Google account
3. Re-run monitor with refreshed credentials

### Option 2: Manual Comment Extraction Workaround
Until API is restored, use this workflow:

1. **Visit YouTube Channel:**
   - Go to: https://youtube.com/@ConcessaObvius/community (or main videos page)
   
2. **Browser Console Method:**
   ```javascript
   // In browser DevTools Console, run:
   const comments = Array.from(document.querySelectorAll('[data-comment-text]'))
     .map(el => ({
       timestamp: new Date().toISOString(),
       commenter: el.closest('#header')?.querySelector('ytd-comm-author-name')?.textContent || 'Unknown',
       text: el.getAttribute('data-comment-text'),
       comment_id: el.closest('ytd-comment-thread-renderer')?.getAttribute('comment-id') || 'unknown'
     }));
   console.json(comments); // Copy output
   ```

3. **Paste into temp file:** `~/.openclaw/workspace/new-comments-manual.json`

4. **Process locally:**
   ```bash
   # Run categorization on manual comments
   python3 -c "
   import json, re
   from datetime import datetime
   
   with open('new-comments-manual.json') as f:
       comments = json.load(f)
   
   for comment in comments:
       text = comment['text'].lower()
       
       # Categorize
       if any(word in text for word in ['how', 'where', 'what', 'cost', 'price', 'timeline']):
           comment['category'] = 'questions'
       elif any(word in text for word in ['amazing', 'inspiring', 'love', 'great', 'thank', 'awesome']):
           comment['category'] = 'praise'
       elif any(word in text for word in ['crypto', 'nft', 'mlm', 'get rich', 'blockchain']):
           comment['category'] = 'spam'
       elif any(word in text for word in ['partner', 'collab', 'sponsorship', 'brand deal', 'work with']):
           comment['category'] = 'sales'
       else:
           comment['category'] = 'other'
       
       # Log to cache
       print(json.dumps(comment))
   " > ~/.openclaw/workspace/.cache/new-comments-processed.jsonl
   ```

### Option 3: Use YouTube Official Tools
- Use YouTube Studio: https://studio.youtube.com → Analytics → Comments
- Export comments manually as CSV
- Process with categorization script above

## Cache Status
- **Total comments cached:** 115+ (from 2026-04-16 to 2026-04-18)
- **Auto-responded:** ~45 comments
- **Flagged for review (Sales):** ~20 comments
- **Spam logged:** ~25 comments
- **Last timestamp:** 2026-04-18T09:01:45Z

## Duplicate Prevention
Monitor detects duplicates using: `(commenter, text_hash, timestamp_within_5min)`
Current cache shows handling of repeat commenters (Sarah Chen, Emma Watson, Mike Johnson, etc.)

## Next Steps
1. **Refresh YouTube OAuth** (preferred method)
2. **Or** use manual extraction + local processing
3. **Restore full cache file** from git history if needed
4. **Re-run monitor** with valid credentials

---
*Generated: 2026-04-18T16:30:00Z (PDT)*
