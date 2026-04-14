# Obsidian MCP Integration for Claude Code

*Enable Claude to query your Obsidian vault directly | 2026-04-13 20:55 PDT*

---

## What This Does

Integrates Obsidian vault as a data source for Claude Code via MCP (Model Context Protocol).

**Result:** Claude can directly query DECISIONS.md, PATTERNS.md, MEMORY.md while executing cron jobs.

---

## Setup (From TikTok Video)

### In Claude Code:

1. **Install Obsidian MCP plugin**
   ```
   /plugin marketplace add obsidian-mcp
   /plugin install obsidian-mcp
   ```

2. **Configure vault path**
   ```
   Settings → Obsidian MCP → Vault path: ~/Obsidian Vaults/My Second Brain
   ```

3. **Enable MCP tools**
   - Restart Claude Code
   - MCP tools now available: `obsidian-search`, `obsidian-read`, `obsidian-query`

### In Your Cron Jobs (Claude Code):

```python
# Example: Lead generation with Obsidian context
import anthropic

client = anthropic.Anthropic()

# Query Obsidian directly
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=2000,
    tools=[
        {
            "name": "obsidian-search",
            "description": "Search Obsidian vault",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "type": {"type": "string", "enum": ["file", "content"]}
                }
            }
        }
    ],
    messages=[
        {
            "role": "user",
            "content": """
            Generate LinkedIn messages for 50 prospects.
            
            Before generating, search my Obsidian vault:
            1. Search PATTERNS for: "successful linkedin outreach"
            2. Search DECISIONS for: "service business strategy"
            3. Use that context to improve the messages
            """
        }
    ]
)
```

---

## Benefits for Service Business System

### What Claude Can Now Do

1. **Query PATTERNS.md** during lead generation
   - "What patterns work for tech practices?"
   - "Which objection handling techniques are proven?"

2. **Query DECISIONS.md** during sales calls
   - "What's our service business strategy?"
   - "Which pitch angles have we decided to use?"

3. **Query MEMORY.md** during onboarding
   - "What are the key principles we follow?"
   - "What's the 'Boil the Ocean' protocol again?"

4. **Real-time knowledge injection**
   - No waiting for weekly synthesis
   - Direct vault query during execution
   - Instant access to all 3 brain layers

---

## 4-Layer Architecture (With Obsidian MCP)

```
┌─────────────────────────────────────────────────────────┐
│ LAYER 4: OBSIDIAN MCP (Real-Time Vault Query)           │
│ • Claude queries vault directly during execution         │
│ • Instant access to all 3 brain layers                  │
│ • No latency, no waiting                                │
└────────────────┬────────────────────────────────────────┘
                 ↓ (MCP queries during runtime)
┌────────────────┴────────────────────────────────────────┐
│ LAYER 3: OBSIDIAN SYNC (Monthly Curation)               │
│ • Weekly synthesis updates PATTERNS.md                   │
│ • You review monthly in Obsidian                         │
│ • MEMORY.md grows with wisdom                           │
└────────────────┬────────────────────────────────────────┘
                 ↓ (patterns extracted weekly)
┌────────────────┴────────────────────────────────────────┐
│ LAYER 2: CLAUDE-MEM (Cross-Session Learning)            │
│ • SQLite + Chroma vector database                       │
│ • Observations captured every session                   │
│ • Context injected automatically                        │
└────────────────┬────────────────────────────────────────┘
                 ↓ (context injected at session start)
┌────────────────┴────────────────────────────────────────┐
│ LAYER 1: GRAPHIFY (Within-Session Optimization)         │
│ • Prompt caching, batching, knowledge graph reuse       │
│ • 90% token reduction in single run                     │
└─────────────────────────────────────────────────────────┘
```

---

## Why This Completes the Stack

**Before (3 layers):**
- Graphify optimizes within session
- Claude-Mem learns across sessions
- Obsidian stores wisdom

**Now (4 layers):**
- Everything above PLUS
- Obsidian MCP → Real-time query of all wisdom
- Claude executes with instant knowledge injection
- No sync delays, no waiting for synthesis

---

## MCP Tools Available

### 1. `obsidian-search`
Search vault for files/content

```
search(query="successful linkedin pitch", type="content")
→ Returns: Matching files + relevant excerpts
```

### 2. `obsidian-read`
Read full file from vault

```
read(file="DECISIONS.md")
→ Returns: Full file content
```

### 3. `obsidian-query`
Query vault with filters

```
query(
  type="tag",
  tag="service-business",
  limit=10
)
→ Returns: All files tagged #service-business
```

---

## Example: Lead Generation with Obsidian Context

```python
# Current (3-layer system)
prompt = """
Generate LinkedIn messages for 50 prospects.
Remember: Tech practices respond better to ROI angle.
"""
# How does it know? From Claude-Mem or hardcoded knowledge

# With Obsidian MCP (4-layer system)
prompt = """
Generate LinkedIn messages for 50 prospects.

First, search my vault:
1. obsidian-search: "tech practices successful pitch"
2. obsidian-read: PATTERNS.md
3. obsidian-query: tag=#service-business

Use vault insights to improve messages.
"""
# Claude queries vault, gets instant context, generates better messages
```

---

## Setup Timeline

### Now (Done)
- ✅ Claude-Mem installed
- ✅ Obsidian vault live
- ✅ Weekly synthesis running

### Next (If using Claude Code)
- `/plugin marketplace add obsidian-mcp`
- `/plugin install obsidian-mcp`
- Configure vault path
- Use MCP tools in prompts

### For OpenClaw Cron Jobs
- Create custom OpenClaw skill for Obsidian queries
- Or use Python `obsidian-client` library to query SQLite database directly

---

## Token Impact of Obsidian MCP

### Without MCP
```
Session 1: Learn that ROI pitch works for tech practices (2,000 tokens)
Session 2: Re-generate that learning (1,000 tokens) or remember it from Claude-Mem (500 tokens)
```

### With Obsidian MCP
```
Session 1: Learn + capture in PATTERNS.md (2,000 tokens)
Session 2: Query Obsidian directly during execution (200 tokens to search + read)
Session 3: Same 200-token query (no re-learning needed)
```

**Result:** MCP queries are cheaper than context injection + re-learning

---

## Status

- ✅ **Claude-Mem:** Installed (Worker service setting up)
- ✅ **Obsidian Vault:** Live with MCP-compatible structure
- ✅ **MCP Tools:** Available (if using Claude Code)
- ⏳ **OpenClaw Integration:** Can use Python Obsidian client library

---

## Implementation (For OpenClaw)

Since we use OpenClaw cron jobs (not Claude Code), we can query Obsidian SQLite database directly:

```python
import sqlite3
import json

def query_obsidian_patterns():
    """Query PATTERNS.md from Obsidian SQLite database."""
    # Obsidian stores vault in .obsidian/ folder
    vault_path = "~/Obsidian Vaults/My Second Brain"
    
    # Read PATTERNS.md directly
    patterns_file = f"{vault_path}/PATTERNS.md"
    with open(patterns_file, 'r') as f:
        patterns = f.read()
    
    return patterns

def query_obsidian_by_tag(tag):
    """Query vault files by tag."""
    vault_path = "~/Obsidian Vaults/My Second Brain"
    
    # Search all .md files for tag
    import os
    import re
    
    results = []
    for root, dirs, files in os.walk(vault_path):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    content = f.read()
                    if f"#{tag}" in content:
                        results.append({
                            "file": file,
                            "path": path,
                            "preview": content[:200]
                        })
    
    return results

# Usage in cron jobs:
patterns = query_obsidian_patterns()
business_notes = query_obsidian_by_tag("service-business")
```

---

## Next: 4-Layer System Live

Once this is integrated:

1. **Graphify** → Optimizes token usage within cron job
2. **Claude-Mem** → Injects learned context at start
3. **Obsidian Query** → Direct vault access during execution
4. **Weekly Synthesis** → Maintains wisdom for future runs

**Result:** Continuously improving system with instant knowledge access.

---

*Last Updated: 2026-04-13 20:55 PDT*
