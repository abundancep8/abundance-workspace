"""
Kimi K2.5 Router - Smart Task Classification & Cost Optimization

Routes tasks to Kimi (70% - research, batch, long-context) or Claude (30% - real-time, critical, quality)
Maintains cost tracking, budget alerts, and routing metrics.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import sqlite3

log = logging.getLogger("kimi_router")


class TaskCategory(Enum):
    """Task categorization for routing"""
    RESEARCH = "research"  # Web searches, data gathering, analysis
    BATCH = "batch"  # Multiple items processing, long lists
    LONG_CONTEXT = "long_context"  # Large documents, code review, summaries
    REAL_TIME = "real_time"  # Immediate responses needed (voice chat)
    CRITICAL = "critical"  # Safety-sensitive, financial, legal
    CREATIVE = "creative"  # Writing, design, ideation
    CODE = "code"  # Software development, debugging
    PLANNING = "planning"  # Task planning, workflow design


class LLMRouter(Enum):
    """LLM selection"""
    KIMI = "kimi_k2_5"  # Cost-optimized, great for research & batch
    CLAUDE = "claude"  # Quality-focused, fast, for real-time & critical
    AUTO = "auto"  # Router decides


@dataclass
class RoutingDecision:
    """Single routing decision"""
    task_id: str
    category: TaskCategory
    router: LLMRouter
    confidence: float  # 0.0-1.0
    reasoning: str
    estimated_cost: float  # USD estimate
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_estimated: int = 0


@dataclass
class RoutingMetrics:
    """Daily routing metrics"""
    date: str
    total_tasks: int = 0
    kimi_tasks: int = 0
    claude_tasks: int = 0
    kimi_cost: float = 0.0
    claude_cost: float = 0.0
    total_cost: float = 0.0
    kimi_avg_latency: float = 0.0
    claude_avg_latency: float = 0.0
    savings_vs_all_claude: float = 0.0


class KimiRouter:
    """Smart task router with cost optimization"""

    # Routing rules: task characteristics → router decision
    ROUTING_RULES = {
        TaskCategory.RESEARCH: (LLMRouter.KIMI, 0.95),  # Perfect for Kimi
        TaskCategory.BATCH: (LLMRouter.KIMI, 0.90),  # Excellent batch handler
        TaskCategory.LONG_CONTEXT: (LLMRouter.KIMI, 0.85),  # Good with long docs
        TaskCategory.REAL_TIME: (LLMRouter.CLAUDE, 0.95),  # Claude is faster
        TaskCategory.CRITICAL: (LLMRouter.CLAUDE, 0.99),  # Quality over cost
        TaskCategory.CREATIVE: (LLMRouter.CLAUDE, 0.80),  # Slightly better creativity
        TaskCategory.CODE: (LLMRouter.CLAUDE, 0.85),  # More reliable for code
        TaskCategory.PLANNING: (LLMRouter.KIMI, 0.75),  # Both good, Kimi cheaper
    }

    # Cost model (per 1M tokens)
    COST_MODEL = {
        LLMRouter.KIMI: {
            "input": 0.14,  # $0.14 per 1M input tokens
            "output": 0.42,  # $0.42 per 1M output tokens
        },
        LLMRouter.CLAUDE: {
            "input": 3.0,  # $3.00 per 1M input tokens (Haiku)
            "output": 15.0,  # $15.00 per 1M output tokens
        },
    }

    # Target distribution (70% Kimi, 30% Claude)
    TARGET_DISTRIBUTION = {
        LLMRouter.KIMI: 0.70,
        LLMRouter.CLAUDE: 0.30,
    }

    def __init__(self, db_path: str = "routing_metrics.db", budget_limit: float = 50.0):
        """Initialize router with metrics tracking"""
        self.db_path = db_path
        self.budget_limit = budget_limit
        self.budget_spent_today = 0.0
        self.tasks_today = []
        self._init_db()

    def _init_db(self):
        """Initialize SQLite metrics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routing_decisions (
                task_id TEXT PRIMARY KEY,
                category TEXT,
                router TEXT,
                confidence REAL,
                reasoning TEXT,
                estimated_cost REAL,
                actual_cost REAL,
                tokens_input INTEGER,
                tokens_output INTEGER,
                latency_ms REAL,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_metrics (
                date TEXT PRIMARY KEY,
                total_tasks INTEGER,
                kimi_tasks INTEGER,
                claude_tasks INTEGER,
                kimi_cost REAL,
                claude_cost REAL,
                total_cost REAL,
                kimi_avg_latency REAL,
                claude_avg_latency REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def classify_task(self, user_input: str, context: Dict = None) -> TaskCategory:
        """Classify task based on input and context"""
        context = context or {}
        input_lower = user_input.lower()

        # Research indicators
        if any(phrase in input_lower for phrase in [
            "search", "research", "find out", "what is", "tell me about",
            "how does", "explain", "investigate", "analyze", "what are"
        ]):
            return TaskCategory.RESEARCH

        # Batch indicators
        if any(phrase in input_lower for phrase in [
            "list all", "summarize", "process", "review all", "go through",
            "batch", "bulk", "multiple", "each of"
        ]):
            return TaskCategory.BATCH

        # Long context indicators
        if context.get("document_length", 0) > 2000 or any(phrase in input_lower for phrase in [
            "review this code", "summarize this", "analyze this document", "read this"
        ]):
            return TaskCategory.LONG_CONTEXT

        # Real-time indicators
        if any(phrase in input_lower for phrase in [
            "quick", "fast", "right now", "immediately", "quickly", "asap"
        ]):
            return TaskCategory.REAL_TIME

        # Critical/sensitive indicators
        if any(phrase in input_lower for phrase in [
            "money", "legal", "contract", "financial", "medical", "personal data",
            "privacy", "secure", "dangerous"
        ]):
            return TaskCategory.CRITICAL

        # Creative indicators
        if any(phrase in input_lower for phrase in [
            "write", "create", "design", "brainstorm", "story", "poem", "generate",
            "imagine", "come up with", "artistic"
        ]):
            return TaskCategory.CREATIVE

        # Code indicators
        if any(phrase in input_lower for phrase in [
            "code", "debug", "fix", "build", "programming", "function", "class",
            "refactor", "test"
        ]):
            return TaskCategory.CODE

        # Planning indicators
        if any(phrase in input_lower for phrase in [
            "plan", "organize", "schedule", "workflow", "roadmap", "strategy",
            "prioritize"
        ]):
            return TaskCategory.PLANNING

        # Default: real-time conversation
        return TaskCategory.REAL_TIME

    def estimate_tokens(self, text: str) -> Tuple[int, int]:
        """Rough estimation: ~1.3 tokens per word (input), 1.2-1.5x input for output"""
        words = len(text.split())
        input_tokens = int(words * 1.3)
        output_tokens = int(input_tokens * 0.8)  # Typical response shorter than input
        return input_tokens, output_tokens

    def estimate_cost(self, router: LLMRouter, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD"""
        cost_model = self.COST_MODEL[router]
        input_cost = (input_tokens / 1_000_000) * cost_model["input"]
        output_cost = (output_tokens / 1_000_000) * cost_model["output"]
        return input_cost + output_cost

    def route(self, task_id: str, user_input: str, context: Dict = None) -> RoutingDecision:
        """Make routing decision for a task"""
        context = context or {}

        # 1. Classify task
        category = self.classify_task(user_input, context)

        # 2. Get recommended router and confidence
        recommended_router, base_confidence = self.ROUTING_RULES.get(
            category, (LLMRouter.CLAUDE, 0.5)
        )

        # 3. Adjust based on budget constraints
        if self.budget_spent_today >= self.budget_limit:
            # Over budget - force Kimi (unless critical)
            if category != TaskCategory.CRITICAL:
                recommended_router = LLMRouter.KIMI
                base_confidence = max(0.5, base_confidence - 0.2)

        # 4. Adjust based on distribution target
        kimi_ratio = (self.tasks_today.count(LLMRouter.KIMI) / max(1, len(self.tasks_today)))
        if kimi_ratio < self.TARGET_DISTRIBUTION[LLMRouter.KIMI]:
            # Need more Kimi tasks to hit 70% target
            if category not in [TaskCategory.REAL_TIME, TaskCategory.CRITICAL]:
                recommended_router = LLMRouter.KIMI

        # 5. Estimate tokens and cost
        input_tokens, output_tokens = self.estimate_tokens(user_input)
        estimated_cost = self.estimate_cost(recommended_router, input_tokens, output_tokens)

        # 6. Create decision record
        decision = RoutingDecision(
            task_id=task_id,
            category=category,
            router=recommended_router,
            confidence=base_confidence,
            reasoning=f"Category: {category.value}, Budget: ${self.budget_spent_today:.2f}/{self.budget_limit:.2f}",
            estimated_cost=estimated_cost,
            tokens_estimated=input_tokens + output_tokens,
        )

        # 7. Update tracking
        self.tasks_today.append(recommended_router)
        self.budget_spent_today += estimated_cost

        # 8. Store in database
        self._store_routing_decision(decision)

        log.info(
            f"Routed {task_id} to {recommended_router.value} "
            f"(category={category.value}, cost=${estimated_cost:.4f})"
        )

        return decision

    def _store_routing_decision(self, decision: RoutingDecision):
        """Store routing decision in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO routing_decisions
            (task_id, category, router, confidence, reasoning, estimated_cost, tokens_input, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision.task_id,
            decision.category.value,
            decision.router.value,
            decision.confidence,
            decision.reasoning,
            decision.estimated_cost,
            decision.tokens_estimated,
            decision.timestamp.isoformat(),
        ))
        conn.commit()
        conn.close()

    def get_today_metrics(self) -> RoutingMetrics:
        """Get today's routing metrics"""
        today = datetime.now().strftime("%Y-%m-%d")
        total = len(self.tasks_today)
        kimi_count = self.tasks_today.count(LLMRouter.KIMI)
        claude_count = self.tasks_today.count(LLMRouter.CLAUDE)

        # Calculate cost comparison (all Claude vs hybrid)
        if total > 0:
            all_claude_cost = sum(
                self.estimate_cost(LLMRouter.CLAUDE, 3000, 2400) for _ in range(total)
            )
            savings = all_claude_cost - self.budget_spent_today
        else:
            savings = 0.0

        return RoutingMetrics(
            date=today,
            total_tasks=total,
            kimi_tasks=kimi_count,
            claude_tasks=claude_count,
            kimi_cost=self.budget_spent_today * (kimi_count / max(1, total)),
            claude_cost=self.budget_spent_today * (claude_count / max(1, total)),
            total_cost=self.budget_spent_today,
            savings_vs_all_claude=savings,
        )

    def get_routing_history(self, limit: int = 20) -> List[Dict]:
        """Get recent routing decisions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT task_id, category, router, confidence, estimated_cost, timestamp
            FROM routing_decisions
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        results = cursor.fetchall()
        conn.close()

        return [
            {
                "task_id": r[0],
                "category": r[1],
                "router": r[2],
                "confidence": r[3],
                "cost": r[4],
                "timestamp": r[5],
            }
            for r in results
        ]

    def get_cost_breakdown(self) -> Dict:
        """Get cost breakdown for dashboard"""
        metrics = self.get_today_metrics()
        return {
            "budget_limit": self.budget_limit,
            "budget_spent": self.budget_spent_today,
            "budget_remaining": max(0, self.budget_limit - self.budget_spent_today),
            "budget_percentage": (self.budget_spent_today / self.budget_limit * 100) if self.budget_limit > 0 else 0,
            "total_tasks": metrics.total_tasks,
            "kimi_tasks": metrics.kimi_tasks,
            "kimi_percentage": (metrics.kimi_tasks / max(1, metrics.total_tasks) * 100),
            "claude_tasks": metrics.claude_tasks,
            "claude_percentage": (metrics.claude_tasks / max(1, metrics.total_tasks) * 100),
            "total_cost": metrics.total_cost,
            "savings": metrics.savings_vs_all_claude,
        }


# Global router instance
_router = None


def get_router(db_path: str = "routing_metrics.db", budget_limit: float = 50.0) -> KimiRouter:
    """Get or create global router instance"""
    global _router
    if _router is None:
        _router = KimiRouter(db_path=db_path, budget_limit=budget_limit)
    return _router


def route_task(task_id: str, user_input: str, context: Dict = None) -> RoutingDecision:
    """Route a single task"""
    router = get_router()
    return router.route(task_id, user_input, context)


if __name__ == "__main__":
    # Quick test
    router = KimiRouter()

    # Test routing various tasks
    test_cases = [
        ("research_task_1", "Search for the latest AI breakthroughs in 2024"),
        ("real_time_1", "What time is my next meeting?"),
        ("critical_1", "How should I structure this investment agreement?"),
        ("creative_1", "Write me a funny poem about debugging"),
        ("batch_1", "Process these 50 customer feedback items and categorize them"),
        ("code_1", "Debug this Python function - it's not sorting correctly"),
    ]

    print("=" * 80)
    print("KIMI ROUTER TEST")
    print("=" * 80)

    for task_id, prompt in test_cases:
        decision = router.route(task_id, prompt)
        print(f"\nTask: {task_id}")
        print(f"  Category: {decision.category.value}")
        print(f"  Router: {decision.router.value}")
        print(f"  Confidence: {decision.confidence:.2%}")
        print(f"  Estimated Cost: ${decision.estimated_cost:.4f}")

    metrics = router.get_today_metrics()
    print("\n" + "=" * 80)
    print("TODAY'S METRICS")
    print("=" * 80)
    print(f"Total Tasks: {metrics.total_tasks}")
    print(f"Kimi: {metrics.kimi_tasks} ({metrics.kimi_tasks/max(1, metrics.total_tasks):.0%})")
    print(f"Claude: {metrics.claude_tasks} ({metrics.claude_tasks/max(1, metrics.total_tasks):.0%})")
    print(f"Total Cost: ${metrics.total_cost:.4f}")
    print(f"Savings vs All Claude: ${metrics.savings_vs_all_claude:.4f}")
