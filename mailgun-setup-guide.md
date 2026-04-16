# Mailgun Setup Guide (60 Seconds)

## What You're Getting
Email service. Free tier for testing + $0.50 per 1,000 emails after. Perfect for agent-sent notifications, alerts, and weekly reports.

## Sign Up (2 minutes)

1. **Go to:** https://www.mailgun.com
2. **Click "Sign Up"** (email recommended)
3. **Use email:** `abundancep@icloud.com`
4. **Create account:**
   - Name: `Abundance` or your name
   - Company: `Personal AI Agent`
   - Use case: `Transactional Email`
5. **Verify email** (check inbox)
6. **Create a sending domain** (or use sandbox domain for testing)

## Get Your Credentials

Once account loads, go to **Settings → API Keys**:

```
Key Name: Your-MG-Key-xxxxxxxx
API Base URL: https://api.mailgun.net/v3
```

### Send These to Agent (Encrypted Format)

```
CREDENTIALS_ENCRYPTED_v1:mailgun_api_key|mg-xxxxxxxx
CREDENTIALS_ENCRYPTED_v1:mailgun_domain|mail.yourdomain.com
```

### (Option A: Sandbox Domain - Immediate, No Domain Required)

If you don't have a business domain yet, use the **sandbox domain**:

1. Go to **Dashboard → Sending**
2. Copy sandbox domain: `sandbox-xxxxxx.mailgun.org`
3. Copy sandbox API key from same page
4. Send to agent:
```
CREDENTIALS_ENCRYPTED_v1:mailgun_api_key|mg-xxxxxxxx
CREDENTIALS_ENCRYPTED_v1:mailgun_domain|sandboxxxxxxx.mailgun.org
```

**Limitation:** Sandbox can only email addresses you authorize. Great for testing.

### (Option B: Custom Domain - Production)

1. Go to **Sending → Domains**
2. Click **Add New Domain**
3. Add your business domain (e.g., `mail.yourbusiness.com`)
4. Follow DNS verification steps (add MX + TXT records to your DNS provider)
5. Once verified, use that domain in credentials

**Advantage:** Can send to anyone. Costs apply after free tier.

## That's It!

Once agent receives your credentials, we'll:
- ✅ Send test email to verify setup
- ✅ Wire into alert system
- ✅ Activate weekly summary emails
- ✅ Track bounces + unsubscribes

**Timeline:** Signup (2 min) → Sandbox verification (1 min) → Send credentials (1 min) → Emails live (< 5 min)

## Pricing

- **Free tier:** 5,000 emails/month (enough for agent alerts + weekly reports)
- **After free:** $0.50 per 1,000 emails (~$50/month for 100k emails)

---

**Recommended:** Start with sandbox domain. Once business domain is ready (Day 1 legal setup), upgrade to custom domain for production.
