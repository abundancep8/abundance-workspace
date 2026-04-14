# Cron Job Authentication Pattern

## Credentials Location
All secrets are in `.secrets/` directory (git-ignored):
- `youtube-credentials.json` — OAuth 2.0 credentials (set up 4x by user)
- `youtube-token.json` — Active refresh token
- `.x-tokens.env` — X API tokens

## How to Wire YouTube Auth to Cron Jobs

### Option A: Source .env in Cron Script (Recommended)
```bash
#!/bin/bash

# Load secrets from workspace root
export YOUTUBE_CREDENTIALS_PATH="/Users/abundance/.openclaw/workspace/.secrets/youtube-credentials.json"
export YOUTUBE_TOKEN_PATH="/Users/abundance/.openclaw/workspace/.secrets/youtube-token.json"

# Your cron logic here
python3 /path/to/youtube-monitor.py
```

### Option B: Direct Path Reference in Python
```python
import json
import os

WORKSPACE_ROOT = "/Users/abundance/.openclaw/workspace"
CREDS_PATH = f"{WORKSPACE_ROOT}/.secrets/youtube-credentials.json"
TOKEN_PATH = f"{WORKSPACE_ROOT}/.secrets/youtube-token.json"

with open(CREDS_PATH) as f:
    credentials = json.load(f)
```

### Option C: Environment Variable (if using cron with .env file)
In `.openclaw/config` or your cron scheduler:
```
YOUTUBE_CREDENTIALS_PATH=/Users/abundance/.openclaw/workspace/.secrets/youtube-credentials.json
YOUTUBE_TOKEN_PATH=/Users/abundance/.openclaw/workspace/.secrets/youtube-token.json
```

## Cron Job Examples

### YouTube DM Monitor
```bash
#!/bin/bash
export YOUTUBE_CREDENTIALS_PATH="/Users/abundance/.openclaw/workspace/.secrets/youtube-credentials.json"
python3 /Users/abundance/.openclaw/workspace/scripts/youtube-dm-monitor.py
```

### YouTube Comment Monitor
```bash
#!/bin/bash
export YOUTUBE_TOKEN_PATH="/Users/abundance/.openclaw/workspace/.secrets/youtube-token.json"
python3 /Users/abundance/.openclaw/workspace/scripts/youtube-comment-monitor.py
```

## Verification Checklist
- [ ] `.secrets/youtube-credentials.json` exists and is readable
- [ ] `.secrets/youtube-token.json` exists (refresh token)
- [ ] Cron script sets `YOUTUBE_CREDENTIALS_PATH` before calling Python
- [ ] Python script reads from environment variable (not hardcoded path)
- [ ] Test cron script manually before scheduling: `bash /path/to/script.sh`
- [ ] Verify token refresh works (YouTube API will auto-update token.json)

## Why This Matters
- **Credentials already exist:** No need to ask user to set up again
- **Unblocks:** YouTube DM monitor, YouTube comment monitor, and any other YouTube workflows
- **Pattern:** Apply same approach to X API, Blotato API, and other services in `.secrets/`
