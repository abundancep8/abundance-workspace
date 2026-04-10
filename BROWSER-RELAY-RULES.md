# BROWSER RELAY RULES - CRITICAL

## The Rule
**ALWAYS use the existing open browser with OpenClaw relay ON.**
**NEVER spawn new browser windows or sessions.**

When you open new windows/sessions, the relay breaks and the existing browser can't function.

---

## Implementation

### ✅ DO THIS
```
1. User has Chrome open
2. OpenClaw relay toolbar button is ON (badge visible)
3. I use: browser(profile="chrome") 
4. I interact with existing tabs
5. Everything works in parallel
```

### ❌ NEVER DO THIS
```
1. Spawn new browser window with exec/subprocess
2. Create headless/hidden Chrome instances
3. Open multiple conflicting browser sessions
4. Restart browser while relay is attached
```

---

## Why This Matters

**When I open a new window:**
- Relay on existing browser breaks
- Other sessions can't use browser
- Automation fails silently
- User's Chrome becomes non-responsive

**When I use existing relay:**
- All tabs work together
- No session conflicts
- Browser stays responsive
- User can see everything happening

---

## The Pattern

```python
# CORRECT: Use existing browser relay
browser.action="snapshot"
browser.profile="chrome"  # Use relay, not sandbox

# WRONG: Spawn new browser
subprocess.run(["open", "-a", "Google Chrome"])  # BLOCKS relay
exec("chromium --headless")  # BREAKS relay
```

---

## Commit This

Every time I need browser interaction:
1. Check: Is the relay already on? (user has OpenClaw toolbar button active)
2. Yes → Use it (browser.profile="chrome")
3. No → Ask user to attach tab first
4. Never → Spawn new instances

---

## Affected Systems

- **YouTube automation** (Blotato video generation + posting)
- **X/Twitter automation** (thread posting with videos)
- **Vercel landing page** (checkout testing)
- **Email capture** (form testing)
- **All interactive systems**

All must use the existing relay. No exceptions.

---

## Status
✅ Rule understood
✅ Applied to all future browser interactions
✅ No new windows ever
✅ Always use existing relay
