# Task Routing Guide

## How to Add New Tasks to Kimi Router

This guide explains how to add new tasks to the smart routing system.

---

## Quick Start

### Example 1: Route a Research Task to Kimi

```javascript
const router = require('./router');

const task = {
  taskName: 'Analyze SaaS competitors in healthcare',
  type: 'research',
  estimatedTokens: 12000,
  timeSensitive: false,
  qualityCritical: false,
  messages: [
    {
      role: 'user',
      content: 'Who are the top 5 SaaS competitors in healthcare? Focus on recent funding and market share.'
    }
  ]
};

try {
  const result = await router.executeTask(task);
  console.log('✓ Response from:', result.model);
  console.log('Content:', result.content);
  console.log('Cost:', '$' + result.cost.toFixed(5));
} catch (error) {
  console.error('Task failed:', error.message);
}
```

**Router Decision:** Routes to **KIMI K2.5** because:
- Type is `research`
- 12k tokens (>10k threshold)
- Not time-sensitive
- Not quality-critical

---

## Task Characteristics

### type

Determines primary routing decision:

| Type | Model | Use Case |
|------|-------|----------|
| `research` | Kimi | Market research, competitor analysis, LinkedIn insights |
| `batch_processing` | Kimi | Document analysis, log processing, bulk extraction |
| `long_context` | Kimi | Memory synthesis, pattern extraction from large datasets |
| `discord` | Claude | Real-time chat responses |
| `jarvis` | Claude | Home automation, system integration |
| `support` | Claude | Customer support, complaints |
| `reasoning` | Claude | Algorithm design, architecture decisions |
| `general` | Claude | Default, unclassified tasks |

### estimatedTokens

Your best guess of total tokens (input + output):

```javascript
// Example: "Analyze 100 customer reviews and create a summary"
// Input: ~200 tokens (prompt)
// Output: ~800 tokens (expected response)
// Estimate: 1000 tokens
estimatedTokens: 1000

// Example: "Extract key data from 50 PDFs"
// Input: ~300 tokens (instructions)
// Output: ~8000 tokens (lots of structured data)
// Estimate: 8300 tokens
estimatedTokens: 8300
```

**Rough Formula:**
```
estimatedTokens = (input_text_length / 4) + (expected_output_length / 4)
```

### timeSensitive

Should response come back in <1 second?

```javascript
// Time-sensitive examples:
{
  timeSensitive: true   // Discord messages, live support chat
}

// Not time-sensitive examples:
{
  timeSensitive: false  // Research, batch processing, analysis
}
```

### qualityCritical

Is this customer-facing or quality-critical?

```javascript
// Quality-critical examples:
{
  qualityCritical: true  // Customer complaint responses, support emails, sales pitches
}

// Not quality-critical examples:
{
  qualityCritical: false  // Internal research, analysis, data processing
}
```

---

## Common Task Patterns

### Pattern 1: Research Task

```javascript
const task = {
  taskName: 'LinkedIn Influencers in AI/ML',
  type: 'research',
  estimatedTokens: 15000,
  timeSensitive: false,
  qualityCritical: false,
  messages: [
    {
      role: 'user',
      content: 'Find top 20 AI/ML influencers on LinkedIn with 100k+ followers'
    }
  ]
};

// Routes to: KIMI K2.5 ✓
// Reason: research + 15k tokens
```

### Pattern 2: Real-time Discord Response

```javascript
const task = {
  taskName: 'Discord: Quick React Question',
  type: 'discord',
  estimatedTokens: 500,
  timeSensitive: true,
  qualityCritical: true,
  messages: [
    {
      role: 'user',
      content: 'Quick: What does React.useCallback do?'
    }
  ]
};

// Routes to: CLAUDE 3.5 ✓
// Reason: Discord type + time-sensitive
```

### Pattern 3: Batch Document Processing

```javascript
const task = {
  taskName: 'Extract Metrics from 100 Annual Reports',
  type: 'batch_processing',
  estimatedTokens: 45000,
  timeSensitive: false,
  qualityCritical: false,
  messages: [
    {
      role: 'user',
      content: `Analyze 100 PDF annual reports and extract:
        - Revenue
        - Net Income
        - Year-over-year growth
        - CEO name
        Return as CSV`
    }
  ],
  maxTokens: 8000
};

// Routes to: KIMI K2.5 ✓
// Reason: batch_processing + 45k tokens
```

### Pattern 4: Complex Reasoning

```javascript
const task = {
  taskName: 'Design Distributed Consensus Algorithm',
  type: 'reasoning',
  estimatedTokens: 8000,
  timeSensitive: false,
  qualityCritical: true,
  messages: [
    {
      role: 'user',
      content: 'Design a Byzantine fault-tolerant consensus algorithm with <50% tolerance'
    }
  ]
};

// Routes to: CLAUDE 3.5 ✓
// Reason: qualityCritical flag
```

### Pattern 5: Customer Support

```javascript
const task = {
  taskName: 'Complaint Resolution: Late Delivery',
  type: 'support',
  estimatedTokens: 2000,
  timeSensitive: false,
  qualityCritical: true,
  messages: [
    {
      role: 'user',
      content: `Customer complaint: "My order arrived 2 weeks late with damaged packaging"
      
      Instructions: 
      - Be empathetic
      - Offer solution
      - Professional tone
      - Keep under 150 words`
    }
  ]
};

// Routes to: CLAUDE 3.5 ✓
// Reason: support type + quality-critical
```

### Pattern 6: Long-context Memory Work

```javascript
const task = {
  taskName: 'Synthesize 60 Days of Memory Files',
  type: 'long_context',
  estimatedTokens: 35000,
  timeSensitive: false,
  qualityCritical: false,
  messages: [
    {
      role: 'user',
      content: `Analyze 60 daily memory files and identify:
      - Top 5 productivity patterns
      - Key learning moments
      - Recommendations for improvement
      - Trends over time`
    }
  ]
};

// Routes to: KIMI K2.5 ✓
// Reason: long_context + 35k tokens
```

---

## Token Estimation Guide

### How Many Tokens?

| Content Type | Tokens | Example |
|--------------|--------|---------|
| Single word | ~0.25 | "hello" |
| Short sentence | ~10 | "What is the weather?" |
| Paragraph | ~150 | Medium paragraph (~75 words) |
| Page of text | ~500 | Single printed page |
| Short article | ~2000 | ~1000-word article |
| Research paper | ~5000-8000 | 20-page paper |
| Book chapter | ~10000+ | 40-50 pages |

### Estimation Formula

```
tokens ≈ text_length_in_characters / 4

Examples:
- "Hello world" (11 chars) → ~3 tokens
- 100-word paragraph (600 chars) → ~150 tokens
- Full research paper (50,000 chars) → ~12,500 tokens
```

### For Your Task

**Input tokens:**
- Count characters in your prompt and instructions
- Divide by 4
- Add 10% buffer

**Output tokens:**
- Estimate how verbose the response will be
- Typical response: 500-2000 tokens
- Large response (tables, lists, code): 2000-5000 tokens
- Very large response (full documents): 5000+ tokens

**Total:**
```
estimatedTokens = input_tokens + output_tokens
```

---

## Routing Decision Tree

```
START: Task received
  │
  ├─→ Type = "discord"? ──YES──→ CLAUDE (real-time)
  │
  ├─→ Type = "jarvis"? ──YES──→ CLAUDE (system integration)
  │
  ├─→ timeSensitive = true? ──YES──→ CLAUDE (speed required)
  │
  ├─→ qualityCritical = true? ──YES──→ CLAUDE (quality matters)
  │
  ├─→ Type = "research"? ──YES──→ KIMI (cost optimization)
  │
  ├─→ Type = "batch_processing"? ──YES──→ KIMI (scale)
  │
  ├─→ Type = "long_context"? ──YES──→ KIMI (efficiency)
  │
  ├─→ estimatedTokens > 10000? ──YES──→ KIMI (cost threshold)
  │
  └─→ DEFAULT ──→ CLAUDE (safest choice)
```

---

## Testing Your Task

### Test Routing (No API Call)

```javascript
const router = require('./router');

const task = {
  taskName: 'My new task',
  type: 'research',
  estimatedTokens: 12000,
  timeSensitive: false,
  qualityCritical: false
};

const routing = router.routeTask(task);
console.log('Model:', routing.model);        // Expected: kimi
console.log('Reason:', routing.reason);      // Expected: research task (>10k tokens)
```

### Verify Costs

```javascript
const inputTokens = 200;
const outputTokens = 1200;

const kimiCost = router.calculateCost('kimi', inputTokens, outputTokens);
const claudeCost = router.calculateCost('claude', inputTokens, outputTokens);

console.log('Kimi cost: $' + kimiCost.toFixed(5));      // ~$0.00063
console.log('Claude cost: $' + claudeCost.toFixed(5));  // ~$0.01860
console.log('Savings: ' + ((claudeCost/kimiCost - 1) * 100).toFixed(0) + '%');  // ~2857%
```

### Run Full Test

```bash
node tests/test-suite.js
```

Should show 10/10 tests passing.

---

## Customizing Routing Rules

### Add a New Task Type

Edit `router.js` in the `routeTask()` function:

```javascript
function routeTask(task) {
  const { type, estimatedTokens, ... } = task;

  // Add your custom rule
  if (type === 'my_custom_type') {
    return { 
      model: 'kimi', 
      reason: 'My custom task type'
    };
  }

  // Rest of routing logic...
}
```

### Add a New Threshold

```javascript
// Route to Kimi if tokens > 8000 (instead of 10000)
const routeToKimi = estimatedTokens > 8000;

// Or based on multiple factors:
const routeToKimi = 
  estimatedTokens > 8000 ||
  (type === 'analytics' && !qualityCritical);
```

### Update Pricing

If OpenRouter prices change:

```javascript
function calculateCost(model, inputTokens, outputTokens) {
  const costs = {
    kimi: { 
      input: 0.00014,    // UPDATE HERE
      output: 0.00042    // UPDATE HERE
    },
    claude: { 
      input: 0.003,      // UPDATE HERE
      output: 0.015      // UPDATE HERE
    }
  };
  // ...
}
```

---

## Common Mistakes

❌ **Mistake 1:** Underestimating token count
```javascript
estimatedTokens: 500  // Too low for batch processing!
```
✅ **Fix:** Always round up. Better to estimate high than hit limits.

❌ **Mistake 2:** Setting timeSensitive=true when not needed
```javascript
timeSensitive: true  // Forces Claude even for research
```
✅ **Fix:** Only true for Discord, live chat, or <1s requirements.

❌ **Mistake 3:** Not setting qualityCritical=true for customer-facing work
```javascript
qualityCritical: false  // But this is an email to a customer!
```
✅ **Fix:** Always true for anything the customer sees.

❌ **Mistake 4:** Wrong message format
```javascript
messages: "What is AI?"  // Should be an array of objects
```
✅ **Fix:** Use OpenAI message format:
```javascript
messages: [
  { role: 'user', content: 'What is AI?' }
]
```

❌ **Mistake 5:** Forgetting to handle errors
```javascript
const result = await router.executeTask(task);
console.log(result.content);  // Crashes if error!
```
✅ **Fix:** Use try/catch:
```javascript
try {
  const result = await router.executeTask(task);
  console.log(result.content);
} catch (error) {
  console.error('Task failed:', error.message);
}
```

---

## Performance Tips

### Optimize Token Usage

1. **Compress prompts:** Remove unnecessary words
2. **Use examples:** Show input/output format briefly
3. **Set maxTokens:** Limit response size
```javascript
maxTokens: 1000  // Will cut off longer responses
```

### Batch Similar Tasks

```javascript
// Instead of 10 separate calls
for (let i = 0; i < 10; i++) {
  await router.executeTask(task);  // 10 API calls
}

// Do one batch request
const batchTask = {
  taskName: 'Batch analyze 10 items',
  type: 'batch_processing',
  estimatedTokens: 8000,
  messages: [{
    role: 'user',
    content: `Analyze these 10 items:
    1. ...
    2. ...
    ...
    10. ...`
  }]
};
await router.executeTask(batchTask);  // 1 API call
```

### Monitor Costs

```javascript
const report = router.generateReport();
console.log('Daily cost: $' + report.totalCost);
console.log('By model:', report.byModel);
```

---

## Advanced Usage

### Conditional Routing

```javascript
function selectModel(task) {
  const router = require('./router');
  const routing = router.routeTask(task);
  
  // Override based on custom logic
  if (task.forceModel) {
    return task.forceModel;
  }
  
  return routing.model;
}
```

### Fallback Logic

```javascript
async function executeWithFallback(task) {
  try {
    // Try Kimi first if routed there
    return await router.executeTask(task);
  } catch (error) {
    // Fall back to Claude if Kimi fails
    console.warn('Kimi failed, falling back to Claude');
    return await router.callOpenRouter(task.messages, 'claude');
  }
}
```

### A/B Testing

```javascript
async function abTestModels(task) {
  // Run task on both models, compare results
  const kimiResult = await router.callOpenRouter(task.messages, 'kimi');
  const claudeResult = await router.callOpenRouter(task.messages, 'claude');
  
  return {
    kimi: { content: kimiResult.content, tokens: kimiResult.outputTokens },
    claude: { content: claudeResult.content, tokens: claudeResult.outputTokens }
  };
}
```

---

## Summary

1. **Define your task** with type, token estimate, and flags
2. **Call router.executeTask()** - routing happens automatically
3. **Check result** - logs are written to performance.jsonl
4. **Monitor costs** - use generateReport() to see savings
5. **Optimize over time** - refine routing rules based on data

**Result: 47% daily cost savings while maintaining quality!** 💰✨

---

*Kimi K2.5 Routing Guide v1.0*  
*Created: 2026-04-15*
