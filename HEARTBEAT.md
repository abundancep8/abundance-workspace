# HEARTBEAT.md — Daily Pulse Checks

Run 2-4x per day. Check these items in rotation. When nothing needs attention, respond `HEARTBEAT_OK`.

## Daily Checks (Every Session)

- [ ] **System Status:** Read `SYSTEMS_STATUS.md`. Are any systems blocked? Need unblocking?
  - Quick check: Look at 🟡 DEPLOYED BUT INCOMPLETE and 🔴 BLOCKED sections
  - Action if yes: Note which systems need attention in today's memory file
  - Action if no: Reply HEARTBEAT_OK
  
## Rotating Checks (Pick 1-2 per heartbeat, vary daily)

- [ ] **Email & Messages:** Any urgent unread messages or notifications?
- [ ] **Calendar:** Upcoming events in next 24-48 hours?
- [ ] **GitHub:** Any PR reviews or deployments pending?
- [ ] **Token Budget:** Check `~/.cache/token-ledger.json` — are we under daily budget?

---

**Rule:** Don't check all 5 items every time. Vary them across the day. Batch similar checks together.

**When to alert (do NOT reply HEARTBEAT_OK):**
- System blocker that can be unblocked in <30 min
- Urgent email or calendar event
- Token budget exceeded
- Deployment needed
- Any actionable task

**When to stay quiet (reply HEARTBEAT_OK):**
- All systems running smoothly
- Nothing new since last check
- It's late night (23:00-08:00) unless urgent
- Human is clearly busy
