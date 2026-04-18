# JARVIS Integration Guide - How the Layers Work Together

This guide explains how the Kimi Router, Chief of Staff, and Service Automation layers integrate with JARVIS.

## Architecture Overview

### The Flow

```
User Input (Voice)
    ↓
Web Speech API (unchanged)
    ↓
Integration Adapter
    ├→ Route task (Kimi vs Claude)
    ├→ Extract memories from Chief of Staff
    ├→ Detect service automation triggers
    └→ Build enhanced system prompt
    ↓
LLM Selection
    ├→ Kimi K2.5 (70% of tasks)
    ├→ Claude Haiku (30% of tasks)
    └→ Call appropriate API
    ↓
Response Processing
    ├→ Log memory if important
    ├→ Update service pipeline if needed
    └→ Track cost
    ↓
TTS + Orb Animation (unchanged)
```

## Layer 1: Kimi Router (Cost Optimization)

### Purpose
Smart task classification that routes to Kimi K2.5 (cheap, good for research) or Claude (fast, good for real-time).

### How It Works

1. **Task Classification** - Analyzes input to determine category:
   - **Research** → Kimi (95% confidence)
   - **Batch Processing** → Kimi (90% confidence)
   - **Long Context** → Kimi (85% confidence)
   - **Real-Time** → Claude (95% confidence)
   - **Critical/Legal** → Claude (99% confidence)
   - **Creative** → Claude (80% confidence)
   - **Code** → Claude (85% confidence)
   - **Planning** → Kimi (75% confidence)

2. **Cost Estimation** - Predicts token usage and cost:
   ```python
   # Example: "Search for AI trends"
   - Estimated input: ~200 tokens
   - Estimated output: ~150 tokens
   - Cost if Kimi: $0.00032
   - Cost if Claude: $0.00450
   - Savings: 93%
   ```

3. **Budget Management** - Prevents overspending:
   - Daily budget limit (default $50)
   - Alerts at 75% and 90% spent
   - Forces non-critical tasks to Kimi if over budget

4. **Distribution Target** - Maintains 70/30 split:
   - Aims for 70% of tasks to Kimi
   - 30% to Claude for critical/real-time work
   - Adjusts classification confidence to maintain ratio

### Integration Points

```python
# In your JARVIS server.py:
from integration_adapter import get_adapter

adapter = get_adapter()
routing = adapter.process_user_input(user_input)

# Use routing decision
if routing['routing'].router == LLMRouter.KIMI:
    llm_response = call_openrouter_kimi(user_input, model="kimi-k2-5")
else:
    llm_response = call_anthropic_claude(user_input)
    
# Cost automatically tracked
```

### Accessing Router Data

```python
from kimi_router import get_router

router = get_router()

# Get today's metrics
metrics = router.get_today_metrics()
print(f"Tasks: {metrics.total_tasks}")
print(f"Kimi: {metrics.kimi_tasks} ({metrics.kimi_percentage:.0%})")
print(f"Cost: ${metrics.total_cost:.2f}")
print(f"Savings: ${metrics.savings_vs_all_claude:.2f}")

# Get routing history
history = router.get_routing_history(limit=20)
for decision in history:
    print(f"{decision['task_id']}: {decision['router']} ({decision['category']})")

# Get cost breakdown
costs = router.get_cost_breakdown()
print(f"Budget remaining: ${costs['budget_remaining']:.2f}")
```

## Layer 2: Chief of Staff (Memory & Intelligence)

### Purpose
Persistent memory integrated with Obsidian vault. Learns patterns, tracks decisions, and provides context for future interactions.

### How It Works

1. **Memory Types**:
   - **Facts** - Information about user (location, name, preferences)
   - **Preferences** - How user likes things done
   - **Decisions** - Important choices made
   - **Lessons** - Patterns learned
   - **Goals** - User's objectives

2. **Storage**:
   - Obsidian vault (human-readable)
   - SQLite FTS5 database (searchable)
   - Full-text search on all memories

3. **Pattern Extraction**:
   - Analyzes repeated decisions
   - Identifies preferences
   - Tracks outcome patterns

### Integration Points

```python
# In your JARVIS server.py:
from integration_adapter import get_adapter

adapter = get_adapter()

# Extract memories relevant to current task
result = adapter.process_user_input(user_input)
chief_context = result['chief_context']

# Include memories in system prompt
system_prompt += f"\n## Relevant memories:\n{chief_context}"

# Remember important information
adapter.handle_memory_action(
    action="remember",
    content="User prefers React over Vue",
    category="preference",
    tags=["technology", "frontend"]
)

# Log important decisions
adapter.handle_memory_action(
    action="log_decision",
    content="Chose Kimi for cost optimization",
    context="Architecture decision",
    rationale="10x cheaper for research tasks"
)
```

### Obsidian Integration

The system automatically creates and maintains these directories in your vault:

```
Obsidian Vault/
├── JARVIS_MEMORIES/
│   ├── mem_20240101_120000.md  (individual memories)
│   └── mem_20240101_140000.md
├── JARVIS_DECISIONS/
│   ├── dec_20240101_100000.md  (individual decisions)
│   └── dec_20240101_150000.md
├── JARVIS_MEMORIES.md           (index)
└── JARVIS_DECISIONS.md          (index)
```

### Accessing Chief of Staff

```python
from chief_of_staff import get_chief

chief = get_chief(vault_path="~/Obsidian")

# Search memories
memories = chief.search_memories("React", category="preference")
for mem in memories:
    print(f"{mem.category}: {mem.content}")

# Search decisions
decisions = chief.search_decisions("architecture")
for dec in decisions:
    print(f"{dec.decision}: {dec.rationale}")

# Get recent memories
recent = chief.get_recent_memories(limit=10)

# Extract patterns
patterns = chief.extract_patterns()

# Health check
health = chief.health_check()
print(f"Vault accessible: {health['vault_accessible']}")
print(f"Memories: {health['memory_count']}")
```

## Layer 3: Service Automation (Lead/Deal Management)

### Purpose
Automate service business workflows: lead generation, sales pipeline, proposal generation, and meeting scheduling.

### How It Works

1. **Lead Management**:
   - Add leads with source tracking
   - Score fit (0.0-1.0)
   - Tag for segmentation
   - Track contact history

2. **Deal Pipeline**:
   - Prospect → Qualified → Engaged → Proposed → Negotiating → Closed
   - Track deal value
   - Monitor email/meeting count
   - Calculate pipeline health

3. **Automation Workflows**:
   - Lead qualification process
   - Deal progression checklist
   - Email outreach sequences
   - Proposal generation

### Integration Points

```python
# In your JARVIS voice responses:
from integration_adapter import get_adapter

adapter = get_adapter()
service_actions = result['service_actions']

# Detect when to trigger service actions
if "prompt_for_lead_details" in service_actions:
    # JARVIS says: "I'd be happy to add that lead. What's their email?"
    # User provides details
    # Then:
    params = parse_user_input_for_lead()
    result = adapter.handle_service_action("add_lead", params)
    # JARVIS says: f"Added {result['message']}"

if "show_pipeline_summary" in service_actions:
    pipeline = adapter.handle_service_action("get_pipeline", {})['pipeline']
    # JARVIS says: f"You have ${pipeline['total_pipeline']:,.0f} in pipeline"

if "prompt_for_deal_action" in service_actions:
    # Let JARVIS guide deal creation/update
    pass
```

### Service Workflows

The system supports these workflows:

**1. Lead Qualification**
```
1. Add lead to database
2. Research company (Kimi router)
3. Score fit (0.0-1.0)
4. Create deal if qualified (fit_score > 0.6)
```

**2. Deal Progression**
```
Prospect → Qualified → Engaged → Proposed → Negotiating → Closed Won/Lost
  ↓          ↓          ↓         ↓          ↓
 Email   Discovery  Requirements Proposal   Objection
 intro    call      gathering    review     handling
```

**3. Email Outreach Sequence**
```
Day 0: Introduction email
Day 3: Value proposition follow-up
Day 7: Case study / social proof
Day 10: Soft close / last touch
```

**4. Proposal Generation**
```
Template selection → Fill with deal data → Review → Send
Available templates: default, web, consulting, custom
```

### Accessing Service Automation

```python
from service_automation import get_automation, LeadSource, DealStage
from datetime import datetime, timedelta

automation = get_automation()

# Add a lead
lead = automation.add_lead(
    name="John Smith",
    email="john@acmecorp.com",
    company="Acme Corp",
    title="VP Sales",
    source=LeadSource.LINKEDIN,
    fit_score=0.85,
    tags=["enterprise", "tech"]
)

# Create a deal
deal = automation.create_deal(
    lead_id=lead.id,
    value=50000.0,
    expected_close=datetime.now() + timedelta(days=30)
)

# Progress through pipeline
automation.update_deal_stage(deal.id, DealStage.QUALIFIED, notes="Verified fit")
automation.update_deal_stage(deal.id, DealStage.ENGAGED)

# Generate proposal
proposal = automation.generate_proposal(deal.id, template="default")
automation.log_email(lead.id, "Proposal: {company_name}")

# Get pipeline summary
summary = automation.get_pipeline_summary()
print(f"Total pipeline: ${summary['total_pipeline']:,.2f}")
print(f"Leads by source:")
for source, count in summary['leads_by_source'].items():
    print(f"  {source}: {count}")

# Get high-priority deals
priority = automation.get_high_priority_deals(limit=5)
for deal in priority:
    print(f"{deal['lead_name']}: ${deal['value']} due {deal['expected_close']}")
```

## Putting It All Together

### Complete Example

```python
# User says: "Search for AI trends and add any interesting companies to my pipeline"

# 1. JARVIS processes input
from integration_adapter import get_adapter
adapter = get_adapter()
result = adapter.process_user_input(user_input)

# 2. Router decides: This is RESEARCH + SERVICE
routing = result['routing']
# routing.router = LLMRouter.KIMI (research task)
# service_actions = ['show_pipeline_summary']

# 3. Chief extracts relevant context
chief_context = result['chief_context']
# "Recent memories: User focuses on B2B SaaS companies, prefers products over services"

# 4. Build system prompt with all context
system_prompt += chief_context
system_prompt += "You're about to research for the user and potentially add to their pipeline"

# 5. Call Kimi for research (because routing says so)
research_response = call_openrouter_kimi(
    user_input,
    model="kimi-k2-5",
    system_prompt=system_prompt
)

# 6. JARVIS responds with findings
# "I found 3 companies: XYZ, ABC, DEF. Should I add any to your pipeline?"

# 7. User says "Yes, add XYZ and ABC"
# 8. JARVIS triggers service automation
params = {
    "name": "XYZ Corp",
    "email": "contact@xyz.com",
    "company": "XYZ Corp",
    "title": "CEO",
    "source": "OUTREACH",
    "fit_score": 0.9
}
lead_result = adapter.handle_service_action("add_lead", params)
# JARVIS: "Added XYZ Corp. Want to create a deal?"

# 9. All actions logged:
# - Research routed to Kimi (cost: $0.0003)
# - Decision logged in Chief (added 2 leads)
# - Leads added to pipeline
# - Cost tracked
```

## Performance Considerations

### Response Time
- **Router classification**: <10ms
- **Memory lookup**: <50ms
- **Kimi call**: 2-5 seconds
- **Claude call**: 1-3 seconds
- **Database writes**: <100ms

### Cost Optimization
- Research tasks: ~93% savings with Kimi
- Real-time chat: 0% extra cost (same speed with Claude)
- Batch processing: ~90% savings with Kimi
- Critical decisions: 0% extra cost (Claude for safety)

## Troubleshooting Integration

### Router not routing to Kimi
Check: Is the task classification confidence too low? Is budget exceeded?
```python
decision = router.route(task_id, input)
print(f"Confidence: {decision.confidence}")
print(f"Budget: ${router.budget_spent_today} / ${router.budget_limit}")
```

### Obsidian not saving memories
Check: Vault path is correct and directory writable
```python
chief = get_chief()
health = chief.health_check()
print(f"Vault accessible: {health['vault_accessible']}")
```

### Service automation not triggering
Check: User input contains service action keywords
```python
result = adapter.process_user_input(user_input)
print(f"Service actions: {result['service_actions']}")
```

---

**Summary**: The three layers work together seamlessly - router decides HOW to respond efficiently, Chief of Staff remembers context, and Service Automation executes business workflows - all while keeping JARVIS working perfectly.
