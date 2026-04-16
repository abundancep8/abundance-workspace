# Supabase Setup Guide (60 Seconds)

## What You're Getting
PostgreSQL database (500MB free tier) + REST API + real-time subscriptions. Enough for agent memory, task logs, and learning cycles.

## Sign Up (2 minutes)

1. **Go to:** https://supabase.com
2. **Click "Sign Up"** (GitHub or email)
3. **Use email:** `abundancep@icloud.com`
4. **Verify email** (check inbox, click link)
5. **Create a project:**
   - Project name: `openclaw-agent`
   - Region: `us-west-1` (closest to you)
   - Database password: Generate and save securely
6. **Wait 30 seconds** for database to initialize

## Get Your Credentials

Once project loads, go to **Settings → Database → Connection String**:

```
postgresql://[user]:[password]@[host]/postgres
```

### Send This to Agent (Encrypted Format)
```
CREDENTIALS_ENCRYPTED_v1:supabase_connection_string|postgresql://user:password@db.supabase.co:5432/postgres
```

## Optional: Expose via Supabase Edge Functions

If you want the dashboard to fetch data from the web:

1. Go to **SQL Editor** → **New Query**
2. Run the schema SQL (provided separately)
3. Go to **Authentication → Policies**
4. Enable Row Level Security (RLS) on `task_log` table if you want public access

## That's It!

Once agent receives your connection string, we'll:
- ✅ Create tables automatically
- ✅ Wire up real-time sync
- ✅ Build live dashboard
- ✅ Start logging task metrics

**Timeline:** Signup (2 min) → Send credentials (1 min) → Integration live (< 5 min after credentials)
