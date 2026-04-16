# OpenRouter Kimi K2.5 Configuration

**Status:** ✅ ACTIVE
**Date Configured:** 2026-04-15 20:06 PDT
**API Key:** Stored securely in `.secrets/` (git-ignored)

## Integration Details

**Provider:** OpenRouter
**Model:** kimi-k2-5
**Endpoint:** https://openrouter.ai/api/v1/chat/completions

## Routing Rules

**Use Kimi K2.5 for:**
- Research tasks (LinkedIn, competitor analysis)
- Batch processing (large document analysis)
- Long-context work (memory synthesis, pattern extraction)
- Cost-sensitive operations (>10k tokens)

**Use Claude for:**
- Real-time interactions (Discord, JARVIS)
- Complex reasoning (strategy, decision-making)
- Time-sensitive tasks (need low latency)
- Quality-critical work (customer-facing responses)

## Expected Savings

- **Per-token cost:** 46% reduction vs Claude
- **Daily projection:** $0.30 → $0.16 (est. 47% daily reduction)
- **Monthly projection:** $9.00 → $4.80 (est. $4.20/month saved)

## Integration Status

- [x] API key secured
- [ ] Router logic implemented
- [ ] Test with real request
- [ ] Monitor performance
- [ ] Optimize token routing

---

**Next Steps:** Wire OpenRouter routing logic into cron jobs + Claude-Mem integration
