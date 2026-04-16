# Developer Reference - Integration API

Quick reference for integrating Supabase + Mailgun into your agent code.

---

## Import

```javascript
const {
  supabase,              // Supabase client
  logTask,               // Log a task execution
  saveMemory,            // Save a memory (decision, pattern, insight)
  getRecentTasks,        // Fetch recent tasks
  calculateMetrics,      // Get 24h metrics
  sendEmail,             // Send an email
  sendDailySummary,      // Send daily summary
  exportDashboardData    // Export all data as JSON
} = require('./supabase-integration');
```

---

## logTask()

Log a task execution to Supabase.

### Signature
```javascript
async logTask(task: {
  task_name: string,        // Name of the task
  model_used: string,       // Model name (claude-haiku, kimi-k2-5, etc.)
  tokens_used: number,      // Total tokens consumed
  cost: number,             // Cost in USD
  duration_ms: number,      // Duration in milliseconds
  status: string,           // 'success' | 'error' | 'timeout'
  error_message?: string,   // Error message if status is 'error'
  metadata?: object         // Custom metadata (JSON)
}): Promise<object>
```

### Example

```javascript
// Task succeeded
await logTask({
  task_name: 'send-email-campaign',
  model_used: 'claude-haiku',
  tokens_used: 2500,
  cost: 0.05,
  duration_ms: 3500,
  status: 'success'
});

// Task failed with error
await logTask({
  task_name: 'fetch-api',
  model_used: 'direct-api',
  tokens_used: 0,
  cost: 0.01,
  duration_ms: 1200,
  status: 'error',
  error_message: 'Connection timeout after 30s',
  metadata: { endpoint: '/api/users', retries: 3 }
});
```

### Returns
```javascript
{
  id: 123,
  task_name: 'send-email-campaign',
  model_used: 'claude-haiku',
  tokens_used: 2500,
  cost: 0.05,
  duration_ms: 3500,
  status: 'success',
  created_at: '2024-01-15T10:30:00Z'
}
```

---

## saveMemory()

Save an important decision, pattern, or insight.

### Signature
```javascript
async saveMemory(
  sessionId: string,        // Unique session ID
  memoryType: string,       // 'decision' | 'pattern' | 'insight' | 'error' | 'optimization'
  content: string,          // The memory content
  metadata?: object         // Custom metadata
): Promise<object>
```

### Example

```javascript
// Save a decision
await saveMemory(
  'session-abc123',
  'decision',
  'Use Kimi-K2.5 for batch email tasks instead of Claude due to 40% lower cost'
);

// Save a pattern
await saveMemory(
  'session-abc123',
  'pattern',
  'Tasks with >5000 tokens show 2x slowdown. Consider breaking into chunks.',
  { tokens_threshold: 5000 }
);

// Save an insight
await saveMemory(
  'session-abc123',
  'insight',
  'Success rate improves from 85% to 98% when adding input validation step'
);

// Save an error
await saveMemory(
  'session-abc123',
  'error',
  'API rate limit exceeded after 1000 requests/min. Add exponential backoff.',
  { limit: 1000, resetIn: 60000 }
);

// Save an optimization
await saveMemory(
  'session-abc123',
  'optimization',
  'Cache Claude responses for identical queries. Saves 30% tokens.',
  { savings_percent: 30 }
);
```

### Returns
```javascript
{
  id: 456,
  session_id: 'session-abc123',
  memory_type: 'decision',
  content: 'Use Kimi-K2.5 for batch...',
  metadata: { ... },
  created_at: '2024-01-15T10:30:00Z'
}
```

---

## getRecentTasks()

Fetch recent task logs.

### Signature
```javascript
async getRecentTasks(
  limit: number = 100,      // How many tasks to fetch
  model: string = null      // Optional filter by model
): Promise<Array>
```

### Example

```javascript
// Get last 50 tasks
const tasks = await getRecentTasks(50);

// Get last 100 Kimi tasks
const kimiTasks = await getRecentTasks(100, 'kimi-k2-5');

// Analyze
console.log(`Total cost: $${tasks.reduce((s, t) => s + t.cost, 0)}`);
console.log(`Success rate: ${(tasks.filter(t => t.status === 'success').length / tasks.length * 100).toFixed(1)}%`);
```

### Returns
```javascript
[
  {
    id: 1,
    task_name: 'send-email',
    model_used: 'claude-haiku',
    tokens_used: 2500,
    cost: 0.05,
    duration_ms: 3500,
    status: 'success',
    created_at: '2024-01-15T10:30:00Z'
  },
  // ... more tasks
]
```

---

## calculateMetrics()

Get 24-hour metrics.

### Signature
```javascript
async calculateMetrics(): Promise<{
  totalTasks: number,
  totalTokens: number,
  totalCost: number,
  successRate: number,          // 0-100
  avgDuration: number,          // milliseconds
  modelBreakdown: object        // { model_name: { count, tokens, cost } }
}>
```

### Example

```javascript
const metrics = await calculateMetrics();
console.log(metrics);
// {
//   totalTasks: 42,
//   totalTokens: 105000,
//   totalCost: 2.10,
//   successRate: 95.24,
//   avgDuration: 2840,
//   modelBreakdown: {
//     'claude-haiku': { count: 21, tokens: 52500, cost: 1.05 },
//     'kimi-k2-5': { count: 21, tokens: 52500, cost: 0.63 }
//   }
// }

// Use in alerts
if (metrics.totalCost > 10) {
  console.warn(`⚠️ Cost exceeded $10! Current: $${metrics.totalCost}`);
}

// Calculate efficiency (tokens per dollar)
const kimiEfficiency = metrics.modelBreakdown['kimi-k2-5'].tokens / 
                       metrics.modelBreakdown['kimi-k2-5'].cost;
console.log(`Kimi efficiency: ${kimiEfficiency} tokens/$`);
```

### Returns
```javascript
{
  totalTasks: 42,
  totalTokens: 105000,
  totalCost: 2.10,
  successRate: 95.24,
  avgDuration: 2840,
  modelBreakdown: {
    'claude-haiku': { count: 21, tokens: 52500, cost: 1.05 },
    'kimi-k2-5': { count: 21, tokens: 52500, cost: 0.63 }
  }
}
```

---

## sendEmail()

Send an email via Mailgun.

### Signature
```javascript
async sendEmail(email: {
  to: string,               // Recipient email
  subject: string,          // Email subject
  html: string,             // HTML body
  text?: string,            // Optional plain text body
  from?: string             // Optional from address
}): Promise<object | null>
```

### Example

```javascript
// Basic email
await sendEmail({
  to: 'user@example.com',
  subject: 'Task Complete',
  html: '<h1>Your task is done!</h1>'
});

// With plain text fallback
await sendEmail({
  to: 'user@example.com',
  subject: 'Daily Report',
  html: '<h1>Daily Summary</h1><p>42 tasks completed</p>',
  text: 'Daily Summary: 42 tasks completed'
});

// Custom from address
await sendEmail({
  to: 'user@example.com',
  subject: 'Important Alert',
  html: '<h1>⚠️ Cost Alert</h1>',
  from: 'alerts@yourdomain.com'
});
```

### Returns
```javascript
{
  message: '...',
  id: '<...'
}

// Or null if error (check console logs)
```

---

## sendDailySummary()

Send a daily performance summary email.

### Signature
```javascript
async sendDailySummary(
  toEmail: string           // Recipient email
): Promise<object | null>
```

### Example

```javascript
// Send daily summary
await sendDailySummary('abundancep@icloud.com');

// Use in cron (8 AM daily)
// 0 8 * * * node -e "require('./supabase-integration').sendDailySummary('user@example.com')"
```

### Returns
```javascript
{
  message: '...',
  id: '<20240115103000.xyz@sandboxabc.mailgun.org>'
}
```

---

## exportDashboardData()

Export all dashboard data as JSON.

### Signature
```javascript
async exportDashboardData(): Promise<{
  metrics: object,
  recentTasks: Array,
  exportedAt: string
}>
```

### Example

```javascript
const data = await exportDashboardData();
console.log(JSON.stringify(data, null, 2));

// Save to file
const fs = require('fs');
fs.writeFileSync('dashboard-export.json', JSON.stringify(data, null, 2));

// Upload to analysis tool
await uploadToAnalysisTool(data);
```

### Returns
```javascript
{
  metrics: {
    totalTasks: 150,
    totalTokens: 375000,
    totalCost: 7.50,
    successRate: 97.33,
    avgDuration: 2840,
    modelBreakdown: { ... }
  },
  recentTasks: [
    { id: 1, task_name: '...', ... },
    // ... up to 1000 recent tasks
  ],
  exportedAt: '2024-01-15T22:35:00Z'
}
```

---

## Supabase Client

Direct access to Supabase for custom queries.

### Signature
```javascript
const { supabase } = require('./supabase-integration');

// Query any table
const { data, error } = await supabase
  .from('task_log')
  .select('*')
  .eq('status', 'error')
  .order('created_at', { ascending: false })
  .limit(10);

// Insert data
const { data, error } = await supabase
  .from('task_log')
  .insert([{ task_name: '...', ... }])
  .select();

// Update
const { data, error } = await supabase
  .from('agent_memory')
  .update({ content: 'Updated...' })
  .eq('id', 123);

// Delete
const { error } = await supabase
  .from('task_log')
  .delete()
  .eq('status', 'error');
```

### Example

```javascript
// Find most expensive tasks
const { data: tasks } = await supabase
  .from('task_log')
  .select('*')
  .order('cost', { ascending: false })
  .limit(5);

console.log('Top 5 Most Expensive Tasks:');
tasks.forEach(t => {
  console.log(`${t.task_name}: $${t.cost.toFixed(4)}`);
});

// Get failed tasks in last 24 hours
const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
const { data: failures } = await supabase
  .from('task_log')
  .select('*')
  .eq('status', 'error')
  .gte('created_at', yesterday);

console.log(`Failed tasks (24h): ${failures.length}`);
failures.forEach(f => {
  console.log(`- ${f.task_name}: ${f.error_message}`);
});
```

---

## Integration Patterns

### Pattern 1: Log with Try-Catch

```javascript
async function executeTask() {
  const start = Date.now();
  try {
    const result = await doSomething();
    
    await logTask({
      task_name: 'do-something',
      model_used: 'claude-haiku',
      tokens_used: 2000,
      cost: 0.04,
      duration_ms: Date.now() - start,
      status: 'success'
    });
    
    return result;
  } catch (err) {
    await logTask({
      task_name: 'do-something',
      model_used: 'claude-haiku',
      tokens_used: 500,
      cost: 0.01,
      duration_ms: Date.now() - start,
      status: 'error',
      error_message: err.message
    });
    throw err;
  }
}
```

### Pattern 2: Model Selection

```javascript
async function selectBestModel(taskType) {
  const metrics = await calculateMetrics();
  
  // Choose cheapest model
  let cheapest = Object.entries(metrics.modelBreakdown)
    .map(([model, data]) => ({
      model,
      costPerToken: data.cost / data.tokens
    }))
    .sort((a, b) => a.costPerToken - b.costPerToken)[0];
  
  await saveMemory(
    'session-123',
    'decision',
    `Using ${cheapest.model} for ${taskType} (${cheapest.costPerToken.toFixed(6)}/token)`
  );
  
  return cheapest.model;
}
```

### Pattern 3: Alert on Threshold

```javascript
async function checkAndAlert() {
  const metrics = await calculateMetrics();
  
  if (metrics.totalCost > 10) {
    await sendEmail({
      to: 'abundancep@icloud.com',
      subject: '⚠️ Daily Cost Alert',
      html: `<h1>Cost Threshold Exceeded</h1>
             <p>Daily cost: <strong>$${metrics.totalCost.toFixed(2)}</strong></p>
             <p>Tasks: ${metrics.totalTasks}</p>
             <p>Success rate: ${metrics.successRate.toFixed(1)}%</p>`
    });
  }
  
  if (metrics.successRate < 80) {
    await saveMemory(
      'session-123',
      'error',
      `Low success rate: ${metrics.successRate.toFixed(1)}%. Investigate failures.`,
      { threshold: 80 }
    );
  }
}
```

---

## Error Handling

All functions handle errors gracefully. They log to console and return null/empty arrays on error.

```javascript
// Safe usage - won't throw
const result = await logTask({...});
if (!result) console.error('Failed to log task');

// Check before using
const tasks = await getRecentTasks();
if (tasks.length === 0) console.log('No tasks found');

// Catch exceptions if needed
try {
  const metrics = await calculateMetrics();
} catch (err) {
  console.error('Failed to calculate metrics:', err);
}
```

---

## Environment Variables

Required in `.env.local`:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_KEY=eyJ...
MAILGUN_API_KEY=mg-...
MAILGUN_DOMAIN=sandbox...
ALERT_EMAIL=user@example.com
COST_THRESHOLD_DAILY=10.0
```

---

## Common Queries

### Get Most Expensive Task (Last 24h)

```javascript
const { data } = await supabase
  .from('task_log')
  .select('*')
  .gte('created_at', new Date(Date.now() - 24*60*60*1000).toISOString())
  .order('cost', { ascending: false })
  .limit(1);

console.log(`Most expensive: ${data[0].task_name} ($${data[0].cost.toFixed(4)})`);
```

### Get Success Rate by Model

```javascript
const { data } = await supabase
  .from('task_log')
  .select('model_used, status')
  .gte('created_at', new Date(Date.now() - 24*60*60*1000).toISOString());

const byModel = {};
data.forEach(d => {
  if (!byModel[d.model_used]) byModel[d.model_used] = { success: 0, total: 0 };
  byModel[d.model_used].total++;
  if (d.status === 'success') byModel[d.model_used].success++;
});

Object.entries(byModel).forEach(([model, stats]) => {
  const rate = (stats.success / stats.total * 100).toFixed(1);
  console.log(`${model}: ${rate}% success`);
});
```

### Find Slow Tasks

```javascript
const { data } = await supabase
  .from('task_log')
  .select('*')
  .gte('duration_ms', 5000)  // Longer than 5 seconds
  .order('duration_ms', { ascending: false });

console.log('Slow tasks:');
data.forEach(t => {
  console.log(`${t.task_name}: ${t.duration_ms}ms`);
});
```

---

## Troubleshooting

### "Cannot read property 'from' of undefined"

The Supabase client failed to initialize. Check:
- `.env.local` has `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Supabase project is active (not paused)

### "Cannot POST to Mailgun"

Check:
- `.env.local` has `MAILGUN_API_KEY` and `MAILGUN_DOMAIN`
- API key is correct
- If sandbox: email recipient is authorized

### "Functions timeout"

Supabase might be slow. Add timeout handling:
```javascript
const timeout = (ms) => new Promise(r => setTimeout(r, ms));
Promise.race([logTask(...), timeout(10000)]);
```

---

## Performance Tips

1. **Batch operations** - Log multiple tasks at once
2. **Use indexes** - Query by model_used, status, created_at
3. **Limit results** - Use `.limit()` in queries
4. **Cache metrics** - Don't recalculate constantly
5. **Archive old data** - Keep only 90 days in Supabase

---

**Last Updated:** 2024-01-15  
**Version:** 1.0.0  
