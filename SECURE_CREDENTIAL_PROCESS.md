# Secure Credential Input - No Passwords in Chat

## How to Share Passwords Securely (EVERY TIME)

### Step 1: Open Terminal
```
Open your Mac terminal (Cmd + Space, type "terminal", press Enter)
```

### Step 2: Navigate to Workspace
```bash
cd /Users/abundance/.openclaw/workspace
```

### Step 3: Run the Secure Input Script
```bash
python3 secure-credential-input.py
```

### Step 4: Follow the Prompts (In Terminal, NOT in Discord)
- Service name: `blotato`
- Email: `abundancep@icloud.com`
- Password: (type it - will NOT show on screen) ← This is secure
- Confirm password: (type again - will NOT show)

### Step 5: Script Encrypts & Stores Locally
✅ Password is encrypted immediately
✅ Stored in `.secrets/blotato-credentials.json`
✅ Never appears in chat, logs, or history
✅ Only you can decrypt it (local machine key)

### Step 6: Tell Me in Discord
Just say: **"Password entered securely in terminal"**

I'll then:
1. Load the credential from encrypted storage
2. Use it for browser automation
3. Generate video
4. Upload to YouTube

---

## Example Terminal Session

```
$ python3 secure-credential-input.py

╔════════════════════════════════════════════════════════════════╗
║         SECURE CREDENTIAL STORAGE                              ║
╚════════════════════════════════════════════════════════════════╝

What service? (e.g., 'blotato', 'youtube', 'gumroad'): blotato
Username/Email for blotato: abundancep@icloud.com

📝 Enter password for blotato
   (Your password will NOT be visible as you type)
   (It will be encrypted and stored securely)

Password for abundancep@icloud.com: [you type, nothing shows]
Re-enter password: [you type, nothing shows]

============================================================
✅ COMPLETE: BLOTATO credentials stored
============================================================

To use these credentials:
  creds = load_credential_securely('blotato')
```

---

## Key Points

1. **Password is NEVER typed in Discord** — Only in terminal
2. **Password is encrypted immediately** — Not stored in plain text
3. **Local encryption only** — Key stays on your machine
4. **Reusable for all services** — Same script for YouTube, Gumroad, Stripe, etc.
5. **I can load it securely** — Decrypt and use without ever seeing it displayed

---

## For Every Sensitive Credential Going Forward

Use this exact process:
1. Run `python3 secure-credential-input.py`
2. Enter service name + credentials (in terminal)
3. Tell me in Discord: "Credential entered securely"
4. I load and use it

**No passwords in chat. Ever.**

---

## If You Need to Change a Credential

Just run the script again with the same service name. It overwrites the encrypted file.

```bash
python3 secure-credential-input.py
→ Service: blotato
→ New password...
✅ Updated
```

---

## Where Your Credentials Are Stored

```
.secrets/
├── blotato-credentials.json      (encrypted password + username)
├── blotato-key.bin               (encryption key)
├── youtube-credentials.json      (if added)
├── youtube-key.bin
└── [other services...]
```

All files are `chmod 600` (owner read/write only).
