# Live Neural Engine - Active Reasoning Brain

A real-time thinking system that maintains active state, fires pattern matches dynamically, retrieves knowledge on-demand, reasons through problems, and persists insights back to your Obsidian vault.

## 🧠 What Is This?

The Neural Engine is **not a chatbot**. It's a thinking system that:

- **Maintains real-time state** of what's currently being processed
- **Fires patterns dynamically** when they match incoming input
- **Retrieves context from Obsidian** based on fired patterns
- **Reasons deeply** using Claude's extended thinking
- **Logs insights back to Obsidian** for future reference
- **Scales with recursive thinking** for harder problems
- **Integrates with JARVIS** for conversational thinking

### Core Architecture

```
Input
  ↓
[Neural State Manager] — Active memory (what's in focus)
  ↓
[Pattern Matcher] — Fire patterns matching the input
  ↓
[Obsidian Retriever] — Pull relevant knowledge from vault
  ↓
[Reasoning Loop] — Think deeply with Claude
  ↓
[Obsidian Writer] — Store insights back to vault
  ↓
Output + Summary
```

## 🚀 Quick Start

### Installation

```bash
cd ~/path/to/neural-engine
npm install @anthropic-ai/sdk
```

### Run the Demo

```bash
# Run demo with default queries
node demo.js

# Run with custom query
node demo.js "What should I focus on today?"
```

### Run Tests

```bash
node test-neural-engine.js
```

## 📦 Core Components

### 1. **Neural State Manager** (`neural-state.js`)

Maintains what's currently "in focus" for the AI.

**Key Methods:**
- `addContext(item, weight)` — Add to active context
- `firePattern(name, confidence, context)` — Fire a pattern
- `addQuery(query)` — Track active reasoning query
- `logInsight(insight)` — Log discovered insight
- `pushReasoning(reasoning)` — Push to thinking stack
- `export()` — Get current state for visualization

**Data Structure:**
```json
{
  "activeContext": [{"content": "...", "weight": 0.9, "addedAt": 1234}],
  "firedPatterns": [{"pattern": "learning-pattern", "confidence": 0.85, "firedAt": 1234}],
  "activeQueries": [{"query": "...", "status": "processing"}],
  "recentInsights": [{"insight": "...", "discoveredAt": 1234}],
  "thinkingDepth": 1,
  "recursionStack": []
}
```

### 2. **Pattern Matcher** (`pattern-matcher.js`)

Identifies relevant patterns when new input arrives.

**Core Patterns:**
- `decision-pattern` — Decision-making contexts
- `learning-pattern` — Learning & discovery
- `problem-solving` — Debugging & fixes
- `creativity-pattern` — Creative ideation
- `connection-pattern` — Synthesis & linking
- `optimization-pattern` — Improvement & efficiency

**Key Methods:**
- `firePatterns(input, threshold)` — Fire patterns for input
- `scoreTextAgainstPattern(text, pattern)` — Score match confidence
- `addPattern(name, keywords, relevance, domain)` — Add custom patterns
- `combinePatterns(firedPatterns)` — Combine multiple patterns for context

**Pattern Object:**
```javascript
{
  pattern: "learning-pattern",
  confidence: 0.85,      // 0-1
  domain: "learning",
  timestamp: 1234567890
}
```

### 3. **Obsidian Retriever** (`obsidian-retriever.js`)

Queries Obsidian vault when patterns fire.

**Key Methods:**
- `indexVault()` — Index all markdown files
- `retrieveForPattern(pattern, limit)` — Get context for pattern
- `retrieveByDomain(domain, limit)` — Get domain-specific knowledge
- `readFile(filePath)` — Read full file content

**Vault Structure Used:**
```
My Second Brain/
  ├─ 00 System/
  ├─ 10 Decisions/
  ├─ 20 Patterns/      ← Pattern index stored here
  ├─ 30 Memory/        ← Neural outputs stored here
  ├─ 40 Projects/
  └─ 50 Assets/
```

### 4. **Reasoning Loop** (`reasoning-loop.js`)

Executes dynamic reasoning with Claude's extended thinking.

**Key Methods:**
- `reason(problem, context, patterns)` — Main reasoning pipeline
- `reasonRecursive(problem, prevResult, depth)` — Deeper thinking
- `parseInsights(thinking, response)` — Extract insights
- `evaluateReasoning(result)` — Score reasoning quality

**Reasoning Result:**
```javascript
{
  problem: "...",
  thinking: "Internal reasoning...",
  response: "Final answer...",
  insights: ["insight1", "insight2"],
  quality: {
    hasThinking: true,
    hasInsights: true,
    score: 0.95
  }
}
```

### 5. **Obsidian Writer** (`obsidian-writer.js`)

Persists reasoning results back to Obsidian.

**Key Methods:**
- `saveReasoning(result)` — Save full reasoning to note
- `saveInsight(insight, source)` — Save individual insight
- `updatePatternIndex(patterns)` — Update pattern registry
- `saveDailyReport(sessionData)` — Generate session report

**Saves To:**
- `neural-reasoning-[timestamp].md` — Full reasoning logs
- `neural-report-[date].md` — Daily summaries
- `_NEURAL_INDEX.md` — Pattern registry

### 6. **Neural Engine Main** (`neural-engine-main.js`)

Orchestrator that coordinates all components.

**Key Methods:**
- `think(input)` — Core pipeline: patterns → retrieval → reasoning → persistence
- `getState()` — Export current neural state
- `visualizeNeurons()` — ASCII visualization of firing patterns
- `generateReport()` — Session metrics
- `saveDailyReport()` — Persist to Obsidian

**Pipeline Flow:**
```
1. Add input to active context
2. Fire patterns
3. Retrieve context from Obsidian
4. Reason about input
5. Log insights to neural state
6. Consider recursive reasoning if high quality
7. Save results to Obsidian
8. Return summary
```

### 7. **JARVIS Connector** (`jarvis-neural-connector.js`)

Bridges the neural engine to conversational interfaces.

**Key Methods:**
- `processQuery(userMessage, context)` — Run message through neural engine
- `formatDiscordResponse(result)` — Format for Discord/messaging
- `visualizeBrain()` — Show firing patterns
- `getNeuralState()` — Get diagnostic state
- `saveDailyReport()` — Persist session

**Discord Response Format:**
```
**Answer**: [Primary insight]

**Active Patterns**: `pattern1`, `pattern2`

**Insights**:
• Insight 1
• Insight 2

**Reasoning Quality**: [████████░░░░░░░░░░░░] 80%
```

## 📊 Usage Examples

### Example 1: Simple Query

```javascript
const NeuralEngine = require('./neural-engine-main');

const engine = new NeuralEngine();
const result = await engine.think("How can I improve my decision-making?");

console.log(result.firedPatterns);  // [{pattern: "decision-pattern", ...}]
console.log(result.insights);        // ["Insight 1", "Insight 2", ...]
console.log(result.quality);         // {hasThinking: true, score: 0.95}
```

### Example 2: JARVIS Integration

```javascript
const JARVISNeuralConnector = require('./jarvis-neural-connector');

const jarvis = new JARVISNeuralConnector();
const response = await jarvis.processQuery("What should I focus on?");

const formatted = jarvis.formatDiscordResponse(response);
// Send to Discord
```

### Example 3: Access Neural State

```javascript
const engine = new NeuralEngine();
await engine.think("Test query");

const state = engine.getState();
console.log(state.topPatterns);      // Top 5 fired patterns
console.log(state.thinkingDepth);    // Recursion depth
console.log(state.neuralState);      // Full neural state
```

### Example 4: Custom Patterns

```javascript
const matcher = require('./pattern-matcher');
const pm = new matcher.PatternMatcher();

pm.addPattern(
  'customer-pattern',
  ['customer', 'client', 'user', 'buyer'],
  0.9,
  'sales'
);

const fired = pm.firePatterns("We got a new customer inquiry!");
// → [{pattern: "customer-pattern", confidence: 0.95, domain: "sales"}]
```

## 🧠 How It Thinks

The neural engine executes a thinking pipeline:

### Step 1: Pattern Matching
Input is scored against known patterns. High-confidence patterns are "fired" (activated in neural state).

### Step 2: Knowledge Retrieval
Fired patterns trigger domain-specific retrieval from your Obsidian vault. Only relevant context is loaded.

### Step 3: Deep Reasoning
The pattern + context is sent to Claude with extended thinking enabled. The AI thinks through the problem step-by-step.

### Step 4: Insight Extraction
Claude's thinking output is parsed to extract key insights and learnings.

### Step 5: Persistence
Results are saved back to Obsidian:
- Full reasoning logs
- Individual insights
- Pattern index updates
- Daily reports

### Step 6: Recursive Thinking (Optional)
If reasoning quality is high and many insights were found, the engine may trigger a second reasoning pass for deeper analysis.

## 📈 Performance & Monitoring

### Visualization

```javascript
const engine = new NeuralEngine();
await engine.think("Example");

console.log(engine.visualizeNeurons());
```

Output:
```
╔════════════════════════════════════════╗
║       NEURAL ENGINE VISUALIZATION       ║
╚════════════════════════════════════════╝

⏱️  Uptime: 12.3s
📊 Queries: 3
🧠 Depth: 1

🔥 FIRING PATTERNS:
  learning-pattern              [██████████░░░░░░░░] 85%
  connection-pattern            [█████████░░░░░░░░░░] 75%
  problem-solving               [████████░░░░░░░░░░░] 80%
```

### State Export

```javascript
const state = engine.getState();
// {
//   engine: {uptime: 12300, queriesProcessed: 3},
//   neuralState: {...},
//   topPatterns: [...],
//   thinkingDepth: 1
// }
```

### Reports

```javascript
const report = engine.generateReport();
// {
//   session: {
//     duration: 12300,
//     queriesProcessed: 3,
//     averageTimePerQuery: 4100
//   },
//   patterns: [...],
//   insights: [...],
//   activeContext: 3,
//   recursionDepth: 1
// }
```

## 🔗 Obsidian Integration

The neural engine automatically:

1. **Reads from:** All `.md` files in your vault
2. **Writes to:** `30 Memory/` (reasoning logs & insights)
3. **Indexes:** `20 Patterns/_NEURAL_INDEX.md` (pattern registry)

### Generated Files

**Reasoning Logs:**
```
30 Memory/neural-reasoning-2024-04-16T13-45-23-456Z.md
```

**Daily Reports:**
```
30 Memory/neural-report-2024-04-16.md
```

**Insights:**
```
30 Memory/insight-how-to-improve-decisions-1234567890.md
```

### Frontmatter Format

All generated notes include metadata:
```yaml
---
type: neural-reasoning
created: 2024-04-16T13:45:23Z
problem: "How can I improve decisions?"
depth: 1
---
```

## 🧪 Testing

Run the test suite:

```bash
node test-neural-engine.js
```

Tests cover:
- Neural state manager (context, patterns, queries, insights)
- Pattern matcher (firing, scoring, custom patterns)
- Obsidian retriever (indexing, retrieval, domain lookup)
- Neural engine orchestration (initialization, export, visualization)

## 🎯 Key Features

✅ **Real-Time Active State** — Know what the brain is processing now
✅ **Dynamic Pattern Firing** — Patterns activate when relevant
✅ **On-Demand Knowledge** — Retrieves from Obsidian when needed
✅ **Deep Reasoning** — Uses Claude's extended thinking
✅ **Automatic Persistence** — Saves insights back to vault
✅ **Recursive Thinking** — Goes deeper for hard problems
✅ **Quality Scoring** — Evaluates reasoning confidence
✅ **Visualization** — See neurons firing in real-time
✅ **JARVIS Integration** — Use as conversational brain
✅ **Zero Hallucination** — All retrieved context is from your vault

## 🚀 Next Steps

1. **Deploy**: Copy neural-engine/ to your workspace
2. **Configure**: Point to your Obsidian vault path
3. **Integrate**: Use JARVISNeuralConnector in your chatbot/agent
4. **Monitor**: Watch the neural visualization and reports

## 📚 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT / JARVIS                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │  Neural State Manager  │ ← Active memory (in-focus)
         └──────────┬─────────────┘
                    │
                    ▼
         ┌────────────────────────┐
         │   Pattern Matcher      │ ← Which patterns fire?
         └──────────┬─────────────┘
                    │
                    ▼
         ┌────────────────────────┐
         │ Obsidian Retriever     │ ← Get relevant knowledge
         └──────────┬─────────────┘
                    │
                    ▼
         ┌────────────────────────┐
         │  Reasoning Loop        │ ← Think with Claude
         └──────────┬─────────────┘
                    │
                    ▼
         ┌────────────────────────┐
         │ Obsidian Writer        │ ← Save insights to vault
         └──────────┬─────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │  Summary + Visualization  │
        └──────────────────────────┘
```

## 🔧 Troubleshooting

**"Vault not found"**
- Check `vaultPath` in config
- Default: `~/Obsidian Vaults/My Second Brain`

**"No files indexed"**
- Ensure vault contains `.md` files
- Check file permissions

**"Reasoning times out"**
- Increase `maxThinkingTokens` (default: 3000)
- Reduce context items retrieved

**"Patterns not firing"**
- Check pattern keywords match your input
- Use `addPattern()` for custom patterns

## 📄 License

Built as part of OpenClaw AI architecture.

---

**Questions?** Check the test suite for usage examples, or review individual component docstrings.
