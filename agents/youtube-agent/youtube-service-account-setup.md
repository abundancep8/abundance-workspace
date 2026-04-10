# YouTube API: Service Account Setup (No User Auth Required)

## Problem
OAuth user tokens expire and require browser-based re-auth.

## Solution
Use Google Service Account with long-lived credentials (no expiration).

## Steps
1. Go to Google Cloud Console
2. Create Service Account
3. Generate JSON key (never expires)
4. Grant channel access via YouTube account linking
5. Use service account key in all API calls

## Result
- Credentials never expire
- No user interaction needed
- Fully autonomous operation
- Comment monitoring works forever

## Implementation
Service account credentials stay in `.secrets/` encrypted.
YouTube API calls use service account, not user OAuth.
Autonomous and hands-free.
