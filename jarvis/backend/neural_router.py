"""
Neural Router - Kimi K2.5 vs Claude Cost Optimization
Routes tasks intelligently based on cost, complexity, and latency requirements.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class NeuralRouter:
    """
    Intelligent task router that chooses between:
    - Kimi K2.5 (70% of tasks) - Lower cost, proven performance
    - Claude (30% of tasks) - Critical/real-time, premium quality
    """
    
    # Pricing (per 1M tokens)
    KIMI_COST = 0.50  # Much cheaper
    CLAUDE_COST = 3.00  # Premium but faster
    
    def __init__(self):
        self.daily_budget = 50.0  # $50/day default
        self.budget_used = 0.0
        self.tasks_log = []
        self.cost_log_path = Path.home() / ".openclaw" / "workspace" / "cost_tracking.json"
        self.task_history_path = Path.home() / ".openclaw" / "workspace" / "task_history.json"
        self.budget_alerts = []
        self._load_history()
    
    def route_task(self, task_type: str, complexity: int, budget: Optional[float] = None) -> Tuple[str, float]:
        """
        Route task to optimal model based on:
        - Task type (some need Claude, some work with Kimi)
        - Input complexity
        - Available budget
        - Time sensitivity
        
        Returns: (model, cost_estimate)
        """
        # Check budget
        if budget is None:
            budget = self.daily_budget - self.budget_used
        
        # Task type routing rules
        critical_tasks = {"voice_command", "real_time", "urgent", "customer_support"}
        research_heavy = {"research", "analysis", "deep_dive"}
        simple_tasks = {"remember", "list", "categorize", "tag"}
        
        # Default: Kimi for 70% (cost optimization)
        # Claude for 30% (critical/complex)
        
        if task_type in critical_tasks:
            # Critical tasks: must use Claude
            model = "claude"
            cost_estimate = self._estimate_cost("claude", complexity)
        elif task_type in research_heavy and complexity > 1000:
            # Complex research: Claude for better quality
            model = "claude"
            cost_estimate = self._estimate_cost("claude", complexity)
        elif task_type in simple_tasks:
            # Simple tasks: always Kimi
            model = "kimi"
            cost_estimate = self._estimate_cost("kimi", complexity)
        else:
            # Default logic: Kimi unless too expensive
            kimi_cost = self._estimate_cost("kimi", complexity)
            claude_cost = self._estimate_cost("claude", complexity)
            
            # If budget tight, always use Kimi
            if self.budget_used + kimi_cost < budget:
                model = "kimi"
                cost_estimate = kimi_cost
            elif self.budget_used + claude_cost < budget:
                model = "claude"
                cost_estimate = claude_cost
            else:
                # Emergency: cheapest option
                model = "kimi"
                cost_estimate = kimi_cost
        
        logger.info(f"📊 Routed {task_type} to {model} (est. cost: ${cost_estimate:.4f})")
        return model, cost_estimate
    
    def _estimate_cost(self, model: str, complexity: int) -> float:
        """Estimate cost based on input complexity."""
        # Approximate tokens from character count
        estimated_tokens = complexity / 4
        
        if model == "kimi":
            return (estimated_tokens / 1_000_000) * self.KIMI_COST
        else:  # claude
            return (estimated_tokens / 1_000_000) * self.CLAUDE_COST
    
    def calculate_cost(self, model: str, output_length: int) -> float:
        """Calculate actual cost after execution."""
        output_tokens = output_length / 4
        
        if model == "kimi":
            cost = (output_tokens / 1_000_000) * self.KIMI_COST
        else:
            cost = (output_tokens / 1_000_000) * self.CLAUDE_COST
        
        return cost
    
    def track_usage(self, task_id: str, model: str, cost: float):
        """Track task execution and cost."""
        self.budget_used += cost
        
        task_record = {
            "task_id": task_id,
            "model": model,
            "cost": cost,
            "timestamp": datetime.now().isoformat(),
            "running_total": self.budget_used
        }
        
        self.tasks_log.append(task_record)
        
        # Log to file
        self._append_to_log(task_record)
        
        # Check budget threshold
        if self.budget_used > self.daily_budget * 0.8:
            logger.warning(f"⚠️ Budget alert: {self.budget_used:.2f}/{self.daily_budget:.2f}")
            self.budget_alerts.append({
                "timestamp": datetime.now().isoformat(),
                "spent": self.budget_used,
                "budget": self.daily_budget,
                "percent": (self.budget_used / self.daily_budget) * 100
            })
        
        logger.info(f"💰 Task {task_id}: {model} cost ${cost:.4f} (total: ${self.budget_used:.2f})")
    
    def get_budget_status(self) -> Dict:
        """Get current budget status."""
        remaining = self.daily_budget - self.budget_used
        percent_used = (self.budget_used / self.daily_budget) * 100
        
        return {
            "daily_budget": self.daily_budget,
            "spent": round(self.budget_used, 2),
            "remaining": round(remaining, 2),
            "percent_used": round(percent_used, 1),
            "status": "🟢 healthy" if remaining > 10 else "🟡 warning" if remaining > 5 else "🔴 critical",
            "reset_at": (datetime.now() + timedelta(days=1)).isoformat()
        }
    
    def get_cost_summary(self) -> Dict:
        """Get cost breakdown by model and task type."""
        summary = {
            "period": datetime.now().date().isoformat(),
            "by_model": {},
            "by_task_type": {},
            "total_tasks": len(self.tasks_log),
            "average_cost_per_task": round(self.budget_used / max(len(self.tasks_log), 1), 4)
        }
        
        # Aggregate by model
        for task in self.tasks_log:
            model = task["model"]
            cost = task["cost"]
            
            if model not in summary["by_model"]:
                summary["by_model"][model] = {"count": 0, "cost": 0}
            
            summary["by_model"][model]["count"] += 1
            summary["by_model"][model]["cost"] += cost
        
        # Calculate savings from Kimi routing
        if "kimi" in summary["by_model"] and "claude" in summary["by_model"]:
            kimi_count = summary["by_model"]["kimi"]["count"]
            claude_count = summary["by_model"]["claude"]["count"]
            
            # If those tasks had been Claude
            hypothetical_claude_cost = kimi_count * self.CLAUDE_COST / 1_000_000 * 500  # avg tokens
            actual_kimi_cost = summary["by_model"]["kimi"]["cost"]
            
            savings = hypothetical_claude_cost - actual_kimi_cost
            summary["estimated_savings"] = round(savings, 2)
        
        return summary
    
    def get_recent_tasks(self, limit: int = 10) -> List[Dict]:
        """Get recent task executions."""
        return self.tasks_log[-limit:]
    
    def set_alert_threshold(self, threshold: float):
        """Set budget alert threshold (percent)."""
        self.alert_threshold = threshold
        logger.info(f"📌 Budget alert set to {threshold}% of daily budget")
    
    def _append_to_log(self, task_record: Dict):
        """Append task to cost log file."""
        try:
            if self.cost_log_path.exists():
                logs = json.loads(self.cost_log_path.read_text())
            else:
                logs = []
            
            logs.append(task_record)
            self.cost_log_path.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            logger.error(f"Failed to write cost log: {e}")
    
    def _load_history(self):
        """Load task history from file."""
        try:
            if self.cost_log_path.exists():
                self.tasks_log = json.loads(self.cost_log_path.read_text())
                
                # Sum up costs from today
                today = datetime.now().date()
                for task in self.tasks_log:
                    task_date = datetime.fromisoformat(task["timestamp"]).date()
                    if task_date == today:
                        self.budget_used += task["cost"]
        except Exception as e:
            logger.error(f"Failed to load cost history: {e}")
    
    def daily_report(self) -> Dict:
        """Generate daily cost report."""
        summary = self.get_cost_summary()
        status = self.get_budget_status()
        
        return {
            "date": datetime.now().date().isoformat(),
            "budget_status": status,
            "cost_summary": summary,
            "alerts": self.budget_alerts,
            "recommendations": self._generate_recommendations(summary)
        }
    
    def _generate_recommendations(self, summary: Dict) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        if summary["by_model"].get("claude", {}).get("count", 0) > 10:
            recommendations.append("Consider batching more tasks for Kimi K2.5 routing")
        
        if self.budget_used > self.daily_budget * 0.9:
            recommendations.append("⚠️ Daily budget almost exhausted - slow down task submission")
        
        if summary.get("estimated_savings", 0) > 10:
            recommendations.append(f"✅ Routing optimization saving ${summary['estimated_savings']:.2f}/day")
        
        return recommendations
