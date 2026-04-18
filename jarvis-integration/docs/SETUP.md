# JARVIS + Kimi K2.5 + Chief of Staff - Complete Setup Guide

This guide walks you through setting up the integrated JARVIS system with Kimi K2.5 cost routing, Chief of Staff memory intelligence, and service automation.

## Prerequisites

- **JARVIS installed** (from https://github.com/ethanplusai/jarvis)
- **Python 3.11+** with pip
- **Anthropic API key** (for Claude)
- **Kimi K2.5 access** (via OpenRouter or direct API)
- **Obsidian** with a vault (for Chief of Staff)
- **Mac** (JARVIS is macOS-only)

## Installation Steps

### 1. Set Up Integration Directory

```bash
# Clone the integration files into your JARVIS project
cd ~/path/to/jarvis
cp -r ~/Downloads/jarvis-integration . 

# Or if you're starting fresh:
git clone https://github.com/ethanplusai/jarvis.git
cd jarvis
mkdir jarvis-integration && cd jarvis-integration
# Place the integration files here
```

### 2. Install Dependencies

```bash
# Install required Python packages
pip install anthropic openai httpx

# Optional: If using OpenRouter for Kimi
pip install openrouter
```

### 3. Configure Environment

Create/update your `.env` file:

```env
# Original JARVIS keys
ANTHROPIC_API_KEY=your-anthropic-api-key
FISH_API_KEY=your-fish-audio-api-key
USER_NAME=sir

# New integration keys
KIMI_API_KEY=your-openrouter-key  # Or direct Kimi API key
OBSIDIAN_VAULT_PATH=~/Obsidian    # Path to your Obsidian vault
DAILY_BUDGET_LIMIT=50.0            # Daily budget in USD
```

### 4. Initialize Databases

```bash
cd jarvis-integration

# Create routing metrics database
python -c "from kimi_router import get_router; get_router()"

# Create Chief of Staff databases
python -c "from chief_of_staff import get_chief; get_chief('~/Obsidian')"

# Create service automation database
python -c "from service_automation import get_automation; get_automation()"
```

This will create three SQLite databases:
- `routing_metrics.db` - Routing decisions and cost tracking
- `chief_of_staff.db` - Memories and decisions
- `service_automation.db` - Leads, deals, proposals

### 5. Integrate with JARVIS Server

Update your `server.py` to import the adapter:

```python
# At the top of server.py, add:
from jarvis_integration.integration_adapter import get_adapter

# In your request handler, add:
adapter = get_adapter(
    vault_path=os.getenv("OBSIDIAN_VAULT_PATH", "~/Obsidian"),
    budget_limit=float(os.getenv("DAILY_BUDGET_LIMIT", "50.0"))
)

# Before processing user input:
integration_result = adapter.process_user_input(user_input, context)
routing_decision = integration_result['routing']

# Use the routing decision to select your LLM:
if routing_decision.router == LLMRouter.KIMI:
    # Call Kimi K2.5 via OpenRouter
    response = call_kimi_k2_5(user_input)
else:
    # Use existing Claude logic
    response = call_claude(user_input)
```

### 6. Set Up Frontend Dashboard

The frontend dashboard displays:
- Cost breakdown (Kimi vs Claude)
- Budget status and alerts
- Task history by model
- Service automation metrics
- Obsidian memory status

To add the dashboard to your frontend, update the UI to fetch:

```typescript
// In your frontend code
const dashboardData = await fetch('/api/integration/dashboard').then(r => r.json());

// Display routing metrics
const routing = dashboardData.routing;
console.log(`Kimi: ${routing.metrics.kimi_percentage}%`);
console.log(`Claude: ${routing.metrics.claude_percentage}%`);
console.log(`Budget: $${routing.cost.budget_spent}/${routing.cost.budget_limit}`);
```

## Verification Steps

### 1. Test Kimi Router

```bash
cd jarvis-integration
python kimi_router.py
```

Expected output: Task routing decisions with cost estimates

### 2. Test Chief of Staff

```bash
python chief_of_staff.py
```

Expected output: Memories stored in Obsidian vault + SQLite database

### 3. Test Service Automation

```bash
python service_automation.py
```

Expected output: Lead, deal, and proposal management working

### 4. Test Integration Adapter

```bash
python integration_adapter.py
```

Expected output: All layers working together

### 5. Run Full Test Suite

```bash
python -m pytest tests/test_integration.py -v
```

## Configuration Files

### `config/routing.json`
- Task classification rules
- Cost models for Kimi vs Claude
- Distribution targets (70/30)
- Budget management settings

### `config/service-workflows.json`
- Lead qualification workflow
- Deal progression stages
- Email outreach sequences
- Proposal templates
- Automation triggers

## Daily Operations

### Monitor Cost Breakdown
```bash
python -c "
from integration_adapter import get_adapter
adapter = get_adapter()
print(adapter.get_dashboard_data()['routing']['cost'])
"
```

### View Routing History
```bash
python -c "
from kimi_router import get_router
router = get_router()
print(router.get_routing_history(limit=10))
"
```

### Check Memory Status
```bash
python -c "
from chief_of_staff import get_chief
chief = get_chief('~/Obsidian')
print(chief.health_check())
"
```

### View Pipeline
```bash
python -c "
from service_automation import get_automation
automation = get_automation()
print(automation.get_pipeline_summary())
"
```

## Troubleshooting

### Issue: "Obsidian vault not found"
**Solution**: Update `.env` with correct `OBSIDIAN_VAULT_PATH`
```bash
echo "OBSIDIAN_VAULT_PATH=/Users/yourusername/Obsidian" >> .env
```

### Issue: "Kimi API key invalid"
**Solution**: Verify OpenRouter key or direct Kimi API key
```bash
python -c "
import os
key = os.getenv('KIMI_API_KEY')
print(f'Key found: {bool(key)}')
print(f'Key length: {len(key) if key else 0}')
"
```

### Issue: "Budget exceeded"
**Solution**: Check remaining budget and adjust daily limit
```bash
python -c "
from kimi_router import get_router
router = get_router()
metrics = router.get_cost_breakdown()
print(f\"Remaining: \${metrics['budget_remaining']:.2f}\")
"
```

### Issue: Databases not created
**Solution**: Manually initialize
```bash
python -c "
import sqlite3
conn = sqlite3.connect('routing_metrics.db')
conn.execute('CREATE TABLE IF NOT EXISTS routing_decisions (id TEXT PRIMARY KEY)')
conn.commit()
"
```

## Next Steps

1. **Start JARVIS server** with integration enabled
2. **Open Chrome** to http://localhost:5173
3. **View dashboard** to see routing metrics in real-time
4. **Speak to JARVIS** - tasks will automatically route to Kimi (70%) or Claude (30%)
5. **Check Obsidian** - memories and decisions logged automatically
6. **Review sales pipeline** - service automation available for lead/deal management

## Support

For issues or questions:
1. Check logs: `tail -f jarvis.log`
2. Run health check: `python integration_adapter.py`
3. Verify configuration: Check `.env` and config files
4. Test individual layers: Run `test_integration.py`

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         JARVIS Voice Interface              │
│  (Web Speech API + Three.js orb)            │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│     Integration Adapter (Orchestration)     │
└──────┬────────────┬────────────┬────────────┘
       │            │            │
       ▼            ▼            ▼
┌────────────┐ ┌──────────────┐ ┌──────────────┐
│   Kimi     │ │   Chief of   │ │   Service    │
│   Router   │ │   Staff      │ │  Automation  │
│ (70% cost) │ │ (Obsidian +  │ │ (Lead/Deal   │
│            │ │  Memory)     │ │  Management) │
└──────┬─────┘ └──────┬───────┘ └──────┬───────┘
       │              │                │
       ▼              ▼                ▼
    Kimi K2.5      Obsidian        Google Sheets
    (OpenRouter)   SQLite DBs       Mailgun
    Claude Haiku   FTS5 Search      Calendly
```

## Success Indicators

✅ Routing decisions logged and visible in dashboard
✅ Cost breakdown showing 70% Kimi / 30% Claude split
✅ Memories persisting in Obsidian vault
✅ Service automation workflows operational
✅ No original JARVIS features broken
✅ Dashboard displays real-time metrics
