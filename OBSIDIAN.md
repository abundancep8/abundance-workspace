# OBSIDIAN.md — Second Brain Configuration

*How to set up Obsidian vault + sync with this workspace.*

---

## Vault Structure (Obsidian)

```
My Second Brain/
├── 00 System/
│   ├── SOUL.md → (symlink from workspace)
│   ├── OBSIDIAN.md (this file)
│   └── README.md
├── 10 Decisions/
│   └── DECISIONS.md → (symlink from workspace)
├── 20 Patterns/
│   └── PATTERNS.md → (symlink from workspace)
├── 30 Memory/
│   ├── MEMORY.md → (symlink from workspace)
│   ├── Daily Logs/ → (symlink to memory/YYYY-MM-DD.md files)
│   └── Projects/
│       └── Service Business/
├── 40 Projects/
│   ├── Service Business System/
│   │   ├── README.md → (symlink from SERVICE_BUSINESS_SYSTEM/)
│   │   └── Notes/
│   └── YouTube Monitoring/
└── 50 Assets/
    └── (images, PDFs, references)
```

---

## Setup Instructions

### 1. Create Vault

```bash
# Open Obsidian
# Create new vault: "My Second Brain"
# Location: ~/Obsidian Vaults/My Second Brain
```

### 2. Set Up Symlinks (Automatic Sync)

```bash
cd ~/Obsidian\ Vaults/My\ Second\ Brain/

# System
ln -s ~/.openclaw/workspace/SOUL.md "00 System/SOUL.md"
ln -s ~/.openclaw/workspace/OBSIDIAN.md "00 System/OBSIDIAN.md"

# Decisions & Patterns
ln -s ~/.openclaw/workspace/DECISIONS.md "10 Decisions/DECISIONS.md"
ln -s ~/.openclaw/workspace/PATTERNS.md "20 Patterns/PATTERNS.md"

# Memory
ln -s ~/.openclaw/workspace/MEMORY.md "30 Memory/MEMORY.md"
ln -s ~/.openclaw/workspace/memory "30 Memory/Daily Logs"

# Projects
ln -s ~/.openclaw/workspace/SERVICE_BUSINESS_SYSTEM "40 Projects/Service Business System"
```

### 3. Configure Obsidian Settings

**Settings → Core plugins:**
- ✅ File explorer
- ✅ Search
- ✅ Graph view
- ✅ Backlinks
- ✅ Tag pane
- ✅ Daily notes

**Settings → Community plugins (recommended):**
- `Dataview` — Query markdown metadata
- `Obsidian Git` — Auto-commit vault changes
- `Calendar` — Navigate daily logs
- `Map of Content` — Create index pages

### 4. Enable Backlinks Panel

**Settings → Appearance:**
- Enable "Strict line breaks" (for markdown compatibility)
- Set font size to readable level
- Enable dark mode (default)

---

## Wiki-Style Linking Pattern

### In DECISIONS.md (Example):

```markdown
## Service Business Strategy (2026-04-13)

**Status:** ✅ Committed  

**Related:** [[SERVICE_BUSINESS_SYSTEM/README.md|Service Business System]]
```

### In PATTERNS.md (Example):

```markdown
### Pattern: Boil the Ocean Delivery

**Source:** [[SOUL.md#Boil the Ocean|SOUL.md - Boil the Ocean Principle]]
```

### In Daily Logs (memory/YYYY-MM-DD.md):

```markdown
## Service Business System Build

**Decision tracked:** [[DECISIONS.md#Service Business Strategy|Service Business Strategy]]  
**Pattern identified:** [[PATTERNS.md#Pattern: Building While Waiting|Building While Waiting]]  
**Principle applied:** [[SOUL.md#Boil the Ocean|Boil the Ocean]]
```

---

## Bi-Directional Linking in Action

**When you open SOUL.md:**
- Right panel shows all files linking to it (decisions, patterns, daily logs)
- Graph view shows relationships visually

**When you open DECISIONS.md:**
- Backlinks panel shows which daily logs mentioned these decisions
- You can trace decision → pattern → outcome

**When you open PATTERNS.md:**
- See which decisions led to each pattern
- Track which projects use each pattern

---

## Graphify Integration (Token Optimization)

### Optimization Points:

**1. Query Deduplication**
When searching across DECISIONS.md + PATTERNS.md + MEMORY.md:
- Cache frequent queries ("What patterns work for X?")
- Reuse decision summaries across related decisions
- Link to common principles instead of repeating them

**Example (Before):**
```markdown
Pattern A: ...description... (100 tokens)
Pattern B: ...similar description... (100 tokens)
Pattern C: ...similar description... (100 tokens)
Total: 300 tokens
```

**After (Graphify):**
```markdown
Pattern A: ...description... (100 tokens)
Pattern B: See [[Common Pattern Template|template]], apply to X (20 tokens)
Pattern C: See [[Common Pattern Template|template]], apply to Y (20 tokens)
Total: 140 tokens (53% savings)
```

**2. Prompt Caching for Synthesis**
Weekly synthesis cron job (generates patterns from daily logs):
- Cache: "Here are 7 daily logs from this week"
- Reuse: "Extract patterns following this template"
- Cost: ~50 tokens (vs. 500+ without cache)

**3. Knowledge Graph Reuse**
When writing new decisions/patterns:
- Query existing graph: "Show me similar decisions"
- Cache results: "These 3 similar patterns exist"
- Reference: "See [[Pattern X]] instead of repeating"

---

## Weekly Synthesis Workflow (Automated)

### Every Sunday @ 8 AM:

1. **Cron job runs:** Read memory/YYYY-MM-*.md (past 7 days)
2. **Extract patterns:** Identify recurring themes
3. **Update PATTERNS.md:** Add new patterns + observations
4. **Generate links:** Auto-add [[wiki-style]] references
5. **Notify:** "3 new patterns found, 2 decisions updated"
6. **Sync to Obsidian:** Symlinks auto-update (Obsidian reloads)

### Manual Review (5 min):
- Open PATTERNS.md in Obsidian
- Review new patterns (already linked)
- Adjust if needed
- Done

---

## Obsidian Query Examples

### Find all decisions about service business:

```
tag:#service-business
OR
link:SERVICE_BUSINESS_SYSTEM
```

### Find all patterns from past 7 days:

```
file:30\ Memory/Daily\ Logs
backlink:PATTERNS.md
```

### Find all references to a specific principle:

```
link:SOUL.md#Boil\ the\ Ocean
```

### Graph view (visual relationships):

Open graph view → search "Boil the Ocean" → see all connected decisions/patterns/projects

---

## File Format Rules (For Graphify Optimization)

**Keep consistent to maximize deduplication:**

### Decisions:
```markdown
## [Title] ([Date])

**Decision:** [Choice made]
**Rationale:** [Why]
**Status:** [Active/Paused/Complete]
**Related:** [[Link 1|Label]], [[Link 2|Label]]
```

### Patterns:
```markdown
### Pattern: [Name]

**Observed:** [What happened]
**Insight:** [Why it matters]
**Applies to:** [Where to use]
**Reuse:** [How to apply elsewhere]
**Source:** [[Link|Label]]
```

### Daily Logs:
```markdown
## [Topic]

**Context:** [What's happening]
**Decision tracked:** [[DECISIONS.md#Anchor|Link]]
**Pattern identified:** [[PATTERNS.md#Anchor|Link]]
**Principle applied:** [[SOUL.md#Anchor|Link]]
```

---

## Token Budget for Knowledge System

**Current state (no Obsidian yet):**
- Daily logs: ~100 tokens/day
- Weekly synthesis: ~200 tokens/week
- Monthly curation: ~300 tokens/month
- **Total:** ~$0.003/month

**After Obsidian + Graphify:**
- Daily logs: ~50 tokens/day (50% reduction via caching)
- Weekly synthesis: ~50 tokens/week (75% reduction via prompt reuse)
- Monthly curation: ~50 tokens/month (83% reduction via knowledge graph)
- **Total:** ~$0.0008/month

**Savings:** 70% token reduction on knowledge work (validates Graphify claims)

---

## Backups & Sync

**Obsidian vault is local** (~/Obsidian Vaults/):
- Symlinks keep it in sync with workspace
- Git backup of workspace covers both

**To backup vault manually:**
```bash
cd ~/Obsidian\ Vaults/My\ Second\ Brain/
git init
git add .
git commit -m "vault backup $(date)"
```

---

## Next Steps

1. ✅ Create DECISIONS.md (done)
2. ✅ Create PATTERNS.md (done)
3. ⏳ Create Obsidian vault structure (manual, 5 min)
4. ⏳ Set up symlinks (automatic, 2 min)
5. ⏳ Configure Obsidian plugins (manual, 10 min)
6. ⏳ Create weekly synthesis cron job (automated)

**Total setup time:** ~15 minutes (one-time)  
**Ongoing effort:** 0 minutes (fully automated)

---

*Last Updated: 2026-04-13 20:20 PDT*
