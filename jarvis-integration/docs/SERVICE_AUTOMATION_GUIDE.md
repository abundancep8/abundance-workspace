# Service Automation Guide - Lead Gen + Sales Pipeline

Complete guide to using JARVIS service automation for lead management, deal progression, and sales workflows.

## Overview

The service automation layer helps service business owners:
- Add and qualify leads
- Track deals through pipeline
- Generate proposals from templates
- Log outreach and meetings
- Forecast revenue
- Identify at-risk deals

## Core Concepts

### Lead

A prospect or potential customer with:
- Contact info (name, email, company, title)
- Source tracking (LinkedIn, email, referral, etc.)
- Fit score (0.0-1.0 confidence)
- Tags for segmentation
- Custom fields for flexibility

### Deal

A sales opportunity with:
- Linked lead
- Deal value ($)
- Stage (Prospect → Closed Won/Lost)
- Expected close date
- Contact history (emails, meetings)
- Probability of close

### Proposal

A document generated from a template:
- Deal-specific pricing
- Scope of work
- Timeline
- Investment amount
- Next steps

## Workflows

### 1. Lead Qualification Workflow

**Goal**: Convert a new lead into a qualified prospect with a deal

**Steps**:

1. **Identify Lead**
   ```
   User: "Add John Smith from Acme Corp to my pipeline"
   JARVIS: "What's John's title and email?"
   User: "VP of Sales, john@acme.com"
   ```

2. **Add to System**
   ```python
   lead = automation.add_lead(
       name="John Smith",
       email="john@acme.com",
       company="Acme Corp",
       title="VP of Sales",
       source=LeadSource.OUTREACH,
       fit_score=0.0  # Will be scored next
   )
   ```

3. **Research & Score**
   ```
   JARVIS: "Let me research Acme Corp... (uses Kimi router)"
   
   Analysis:
   - Company size: 200-500 people ✓
   - Industry: Tech SaaS ✓
   - Budget profile: Seems likely ✓
   - Competitive products: Some ✗
   
   Fit Score: 0.75/1.0
   ```

4. **Create Deal (if qualified)**
   ```python
   # Qualified = fit_score > 0.6
   if lead.fit_score > 0.6:
       deal = automation.create_deal(
           lead_id=lead.id,
           value=50000,  # Estimated
           expected_close=datetime.now() + timedelta(days=30)
       )
   ```

5. **First Contact**
   ```
   JARVIS: "Ready to reach out? I can send an introduction."
   User: "Yes, keep it brief and relevant"
   JARVIS: [Drafts personalized email]
   JARVIS: "Sent introduction to John"
   ```

### 2. Deal Progression Workflow

**Goal**: Move deal from Prospect through Close

**Pipeline Stages**:

```
PROSPECT
  ↓ (Introduction sent)
QUALIFIED  
  ↓ (Discovery call scheduled)
ENGAGED
  ↓ (Requirements documented)
PROPOSED
  ↓ (Proposal sent, reviewing)
NEGOTIATING
  ↓ (Terms discussed)
CLOSED_WON / CLOSED_LOST
```

**Step-by-step**:

```
Day 0: Prospect Stage
  JARVIS: "Sent introduction email to John"
  automation.log_email(lead.id, "Quick intro - [Company]")

Day 3: Qualified Stage
  User: "John responded, seems interested"
  automation.update_deal_stage(
      deal.id, 
      DealStage.QUALIFIED,
      notes="Positive initial response"
  )

Day 5: Engaged Stage
  JARVIS: "Ready to schedule discovery call?"
  automation.schedule_meeting(
      deal.id,
      scheduled_date=datetime(2024, 1, 15, 14, 0),
      duration_minutes=30,
      meeting_type="discovery_call"
  )

Day 6: Proposal Stage
  User: "Let's send a proposal"
  proposal = automation.generate_proposal(deal.id, template="default")
  JARVIS: "Generated proposal for $50K. Review?"
  [Show preview]
  automation.update_deal_stage(deal.id, DealStage.PROPOSED)

Day 10: Negotiating
  User: "John wants 20% discount"
  automation.update_deal_stage(
      deal.id,
      DealStage.NEGOTIATING,
      notes="Negotiating price. Offered 10% discount"
  )

Day 15: Closed Won!
  User: "John signed! Deal closed"
  automation.update_deal_stage(deal.id, DealStage.CLOSED_WON)
  # Revenue logged, pipeline updated
```

### 3. Email Outreach Sequence

**Goal**: Nurture leads through a structured email sequence

**Default Sequence**:

```
Day 0: Introduction
Subject: Quick thought on [Company Name]
Body: Personalized intro + why you're reaching out

Day 3: Value Proposition
Subject: How [Company] could achieve [X]% improvement
Body: Specific benefit statement + case study reference

Day 7: Social Proof
Subject: Case study - [Similar Company] achieved [Result]
Body: Concrete example + how it could apply to them

Day 10: Soft Close
Subject: Last touch - [Your Name]
Body: Low-pressure final attempt, offer to help
```

**Using with JARVIS**:

```
User: "Send John the email sequence"
JARVIS: "Which template? (introduction, value, social_proof, close)"
User: "Start with introduction"
JARVIS: [Drafts] "Sound good?" [Shows preview]
User: "Perfect, send it"
automation.log_email(lead.id, "Introduction email sent")
```

### 4. Proposal Generation Workflow

**Goal**: Create customized proposals from templates

**Process**:

1. **Trigger**
   ```
   User: "Generate proposal for John's deal"
   ```

2. **Select Template**
   - `default` - General services
   - `web` - Web development
   - `consulting` - Strategic consulting
   - `custom` - Build from scratch

3. **Auto-fill**
   ```python
   proposal = automation.generate_proposal(
       deal_id=deal.id,
       template="web"
   )
   
   # Automatically includes:
   # - Client name (John Smith, Acme Corp)
   # - Project value ($50,000)
   # - Your company details
   # - Scope of work
   # - Timeline
   # - Payment terms
   ```

4. **Review & Customize**
   ```
   JARVIS: "Generated proposal. Want to customize?"
   User: "Add custom scope item: API integration"
   [Edit proposal content]
   ```

5. **Send**
   ```
   User: "Looks good, send it"
   [Email proposal to john@acme.com]
   automation.log_email(lead.id, "Proposal sent - Web project")
   automation.update_deal_stage(deal.id, DealStage.PROPOSED)
   ```

## Pipeline Management

### View Pipeline Summary

```
User: "What's my sales pipeline look like?"

JARVIS returns:
- Total Pipeline Value: $425,000
- Deal Count by Stage:
  - Prospect: 3 deals ($75K)
  - Qualified: 2 deals ($100K)
  - Engaged: 4 deals ($150K)
  - Proposed: 2 deals ($75K)
  - Negotiating: 1 deal ($25K)
- Upcoming Meetings: 5 this week
- Email Sent: 12 this week
- High-Priority Deals: [list of at-risk deals]
```

### Identify At-Risk Deals

Deals need attention if:
- No contact in 7 days (stale)
- Expected close date < 5 days (urgent)
- Stuck in Engaged > 14 days (stalled)

```python
priority = automation.get_high_priority_deals(limit=5)
# JARVIS: "You have 3 deals needing attention:
#   1. John at Acme - $50K due in 3 days
#   2. Jane at TechCorp - No contact in 10 days
#   3. Bob at StartupInc - Stuck in proposal review"
```

### Deal Analytics

```
automation.get_pipeline_summary()
Returns:
- total_pipeline: Total value across all open deals
- stage_breakdown: Deals and value by stage
- leads_by_source: Which sources bring best deals
- upcoming_meetings: Calendar view
```

## Integrating with Voice

### Common Voice Commands

```
"Add a new lead"
→ JARVIS: "What's their name?"

"Create a deal for John"
→ JARVIS: "What's the deal size?"

"Move John to qualified"
→ automation.update_deal_stage(deal.id, DealStage.QUALIFIED)

"Show my pipeline"
→ JARVIS: [Reads pipeline summary]

"Generate proposal for John"
→ Triggers proposal generation flow

"Schedule meeting with Jane"
→ automation.schedule_meeting(...)

"Log email sent to Bob"
→ automation.log_email(lead.id, "Follow-up")

"Who needs follow-up?"
→ JARVIS: [Lists stale deals]
```

### Embedding in JARVIS Responses

When service actions are detected:

```python
result = adapter.process_user_input(user_input)

if "prompt_for_lead_details" in result['service_actions']:
    # User mentioned adding a lead
    # JARVIS should guide them through the process
    JARVIS: "I'd be happy to add a new lead. What's their name?"
    
if "show_pipeline_summary" in result['service_actions']:
    # User asked about pipeline
    pipeline = automation.get_pipeline_summary()
    JARVIS: f"You have ${pipeline['total_pipeline']:,.0f} in pipeline across {pipeline['total_leads']} leads"
```

## Best Practices

### 1. Score Leads Immediately
```python
# Don't leave fit_score at 0
# Research quickly and score 0.0-1.0
lead = automation.add_lead(..., fit_score=0.75)
# 0.0-0.3: Poor fit, not pursuing
# 0.3-0.6: Possible fit, needs more info
# 0.6-0.8: Good fit, create deal
# 0.8-1.0: Excellent fit, high priority
```

### 2. Tag Everything
```python
# Use tags for filtering and analysis
lead.tags = ["enterprise", "tech", "warm_intro"]
# Tags help with:
# - Filtering by industry/size
# - Identifying patterns
# - Custom reporting
```

### 3. Log All Contact
```python
# Every interaction should be logged
automation.log_email(lead.id, "Follow-up on proposal")
automation.schedule_meeting(deal.id, ...)
# This creates your activity history
```

### 4. Update Deal Regularly
```python
# Keep deal stages current
# Don't let deals sit in same stage > 10 days
# Move to next stage or close
automation.update_deal_stage(deal.id, new_stage, notes="reason")
```

### 5. Use Proposals Early
```python
# Don't wait until late to send proposal
# Generate and send earlier in process
# Helps with conversation and commitment
proposal = automation.generate_proposal(deal.id)
```

## Reports & Insights

### Pipeline Health Report
```
JARVIS: "Pipeline health check:"

✓ Total Pipeline: $425,000 (on target)
⚠ Stuck Deals: John at Acme (14 days in proposal)
✓ Meeting Momentum: 5 scheduled this week
⚠ Stale Leads: 2 prospects with no contact >7 days
✓ Proposal Close Rate: 40% (2 closed from 5 sent)

Action Items:
1. Follow up with Acme (14-day stale)
2. Schedule meeting with Jane (needs engagement)
3. Check in on negotiation with Bob
```

### Source Attribution
```
JARVIS: "Your best leads come from:"
1. LinkedIn: 5 leads, 60% qualified, avg deal $45K
2. Email: 4 leads, 50% qualified, avg deal $35K
3. Referrals: 3 leads, 100% qualified, avg deal $55K

Focus: More referrals (highest quality)
```

### Win Analysis
```
JARVIS: "Analysis of your closed deals:"

Total Closed: 8 deals, $380K revenue
Average Deal Size: $47.5K
Sales Cycle: 28 days avg
Success Rate: 33% (8 from 24)

Top Performing:
- Company Size: 100-500 employees
- Industry: B2B SaaS
- Source: Referrals & warm email
```

## Troubleshooting

### Leads not appearing in system
```python
# Check database
automation.get_pipeline_summary()
# If empty, try:
automation.health_check()  # Verify DB accessible
```

### Deal not updating stage
```python
# Verify deal exists and ID is correct
# Then update with verbose notes
automation.update_deal_stage(
    deal_id,
    new_stage,
    notes="Reason for update"
)
```

### Proposal not generating
```python
# Check:
# 1. Deal exists and is linked to lead
# 2. Template exists (default, web, consulting, custom)
# 3. Both deal and lead have required fields

automation.generate_proposal(deal.id, template="default")
```

### Pipeline shows old data
```python
# Service automation uses live SQLite
# Data updates in real-time
# If stale, check:
automation.health_check()  # Is DB accessible?
automation.get_pipeline_summary()  # Refresh
```

## Integration with Other Layers

### Kimi Router Integration
```
User: "Research this company's tech stack"
→ Router: Research task, use Kimi K2.5
→ Kimi researches (90% cheaper)
→ Results added to lead notes
→ Fit score updated based on findings
```

### Chief of Staff Integration
```
User: "Remember Acme Corp focuses on fintech"
→ Chief: Logs memory
→ Next time: "I know Acme focuses on fintech"
→ Helps with personalized outreach
```

## Advanced Usage

### Custom Fields
```python
lead = automation.add_lead(
    ...,
    custom_fields={
        "industry": "FinTech",
        "employee_count": 350,
        "tech_stack": "React, Node.js",
        "budget_range": "$40K-$60K",
        "decision_maker": "CTO + CFO"
    }
)
```

### Bulk Operations (future)
```python
# For now, add leads one at a time via voice
# Future: Support CSV import
# For now: Use JARVIS voice commands
```

### API Access
```python
from service_automation import get_automation
from datetime import datetime, timedelta

automation = get_automation()

# All operations available programmatically
leads = automation.get_all_leads()
deals = automation.get_all_deals()
summary = automation.get_pipeline_summary()
```

---

**Key Takeaway**: Service automation makes JARVIS into your personal sales assistant - handling lead tracking, pipeline management, and proposal generation while you focus on selling.

Use it for:
✓ Tracking all leads in one place
✓ Never losing track of deals
✓ Generating proposals faster
✓ Spotting at-risk deals early
✓ Understanding what works (win analysis)
✓ Forecasting revenue
