# OpenClaw Token Budget — Daily Tracking

**Daily Budget:** $5.00 (Haiku model)
**Alert @ 75%:** $3.75
**Alert @ 100%:** $5.00

---

## Daily Log — 2026-04-09

| Time | Session | Input | Output | Cache Hit % | Est. Cost | Cumulative | Status |
|------|---------|-------|--------|-------------|-----------|------------|--------|
| 06:30 | cron:hourly-token-check | 37 | 1.4k | 63% | ~$0.006 | $0.006 | 🟢 OK |

**Calculation Basis (Claude Haiku):**
- Input: $0.80 / 1M tokens
- Output: $4.00 / 1M tokens
- Cache read (63% hit): 10% of input cost
- Estimated cost per check: ~$0.006

---

## Status

- **Current Spend:** $0.006
- **Budget Remaining:** $4.994
- **% of Daily Budget Used:** 0.12%
- **Status:** 🟢 GREEN — Well under budget

---

## Notes

- First hourly check of the day (6:30 AM)
- High cache hit rate (63%) indicates efficient reuse of prompt context
- Cron job token usage is minimal; most spending will come from manual sessions
