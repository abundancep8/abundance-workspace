"""
Integration Adapter - Wires Kimi Router, Chief of Staff, and Service Automation into JARVIS

This adapter sits between the JARVIS server and the new integration layers.
It provides a clean interface for routing, memory, and service automation.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Optional, Tuple
from pathlib import Path

from kimi_router import get_router, LLMRouter, TaskCategory, RoutingDecision
from chief_of_staff import get_chief, ChiefOfStaff
from service_automation import get_automation, ServiceAutomation, LeadSource, DealStage

log = logging.getLogger("integration_adapter")


class JARVISIntegrationAdapter:
    """Adapter that integrates all layers into JARVIS"""

    def __init__(self, vault_path: str = "~/Obsidian", budget_limit: float = 50.0):
        """
        Initialize the integration adapter
        
        Args:
            vault_path: Path to Obsidian vault for Chief of Staff
            budget_limit: Daily budget limit for Kimi/Claude routing
        """
        self.router = get_router(budget_limit=budget_limit)
        self.chief = get_chief(vault_path=vault_path)
        self.automation = get_automation()
        
        self.session_metadata = {
            "created_at": datetime.now().isoformat(),
            "budget_limit": budget_limit,
            "vault_path": vault_path,
        }

    def process_user_input(self, user_input: str, context: Dict = None) -> Dict:
        """
        Process user input through all integration layers
        
        Returns:
            {
                "task_id": str,
                "routing": RoutingDecision,
                "context": str,  # Enhanced context from Chief of Staff
                "service_actions": List[str],  # Any service automation to trigger
            }
        """
        context = context or {}
        task_id = str(uuid.uuid4())[:8]

        # 1. Route the task
        routing = self.router.route(task_id, user_input, context)
        
        # 2. Extract context from Chief of Staff
        chief_context = self._extract_chief_context(user_input)
        
        # 3. Detect service automation triggers
        service_actions = self._detect_service_actions(user_input)
        
        # 4. Log the decision if it's important
        if routing.category in [TaskCategory.CRITICAL, TaskCategory.PLANNING]:
            self.chief.log_decision(
                decision=user_input[:100],
                context=routing.reasoning,
                rationale=f"Router confidence: {routing.confidence:.0%}",
                tags=[routing.category.value]
            )
        
        return {
            "task_id": task_id,
            "routing": routing,
            "chief_context": chief_context,
            "service_actions": service_actions,
            "enhanced_system_prompt": self._build_enhanced_system_prompt(),
        }

    def _extract_chief_context(self, user_input: str) -> str:
        """Extract relevant memories from Chief of Staff"""
        # Search for relevant memories
        memories = self.chief.search_memories(user_input)
        
        if not memories:
            return ""
        
        context = "## Relevant Context from Memory\n"
        for mem in memories:
            context += f"- **{mem.category}**: {mem.content}\n"
        
        return context

    def _detect_service_actions(self, user_input: str) -> list:
        """Detect if service automation should be triggered"""
        input_lower = user_input.lower()
        actions = []
        
        if any(phrase in input_lower for phrase in [
            "add lead", "new prospect", "add contact", "found a lead"
        ]):
            actions.append("prompt_for_lead_details")
        
        if any(phrase in input_lower for phrase in [
            "create deal", "qualified", "move to proposed", "send proposal"
        ]):
            actions.append("prompt_for_deal_action")
        
        if any(phrase in input_lower for phrase in [
            "pipeline", "sales status", "how many deals", "what's my pipeline"
        ]):
            actions.append("show_pipeline_summary")
        
        if any(phrase in input_lower for phrase in [
            "schedule meeting", "book call", "set up meeting"
        ]):
            actions.append("prompt_for_meeting")
        
        if any(phrase in input_lower for phrase in [
            "send email", "outreach", "follow up"
        ]):
            actions.append("prompt_for_email")
        
        return actions

    def _build_enhanced_system_prompt(self) -> str:
        """Build enhanced system prompt with routing and memory context"""
        metrics = self.router.get_today_metrics()
        budget_info = self.router.get_cost_breakdown()
        chief_health = self.chief.health_check()
        automation_health = self.automation.health_check()
        
        vault_status = "✓ Connected" if chief_health["vault_accessible"] else "✗ Disconnected"
        
        context = {
            **budget_info,
            "memory_count": chief_health["memory_count"],
            "decision_count": chief_health["decision_count"],
            "vault_status": vault_status,
            "lead_count": automation_health["total_leads"],
            "deal_count": automation_health["total_deals"],
            "revenue": automation_health["revenue"],
        }
        
        prompt = """
## INTEGRATION LAYER STATUS

### Cost Optimization (Kimi K2.5 Router)
- Daily Budget: ${budget_limit:.2f}
- Spent Today: ${budget_spent:.2f} ({budget_percentage:.0f}%)
- Remaining: ${budget_remaining:.2f}
- Tasks Routed to Kimi: {kimi_percentage:.0%}
- Tasks Routed to Claude: {claude_percentage:.0%}
- Estimated Savings vs All-Claude: ${savings:.2f}

**Note to JARVIS**: When the user asks you to do research, summarization, or batch processing,
you're likely being routed to Kimi K2.5 (70% cheaper). For real-time conversations and critical
decisions, Claude is used. This is transparent to the user - just respond normally.

### Chief of Staff Intelligence
- Memory Records: {memory_count}
- Decision Log Entries: {decision_count}
- Vault Status: {vault_status}

**Note to JARVIS**: Use memories to maintain consistency. When making decisions or 
remembering user preferences, explicitly reference past decisions from the log.

### Service Automation
- Total Leads: {lead_count}
- Active Deals: {deal_count}
- Pipeline Value: ${revenue:,.2f}

**Note to JARVIS**: When the user mentions sales, deals, or pipeline, offer to 
update their status or generate proposals. Service automation is ready to help.
""".format(**context)
        
        return prompt

    def handle_memory_action(self, action: str, content: str, 
                           category: str = "fact", tags: list = None):
        """Handle memory-related actions from JARVIS"""
        if action == "remember":
            self.chief.remember_fact(content, category=category, tags=tags or [])
        
        elif action == "search":
            return self.chief.search_memories(content, category=category)

    def handle_service_action(self, action: str, params: Dict) -> Dict:
        """Handle service automation actions from JARVIS"""
        result = {}
        
        if action == "add_lead":
            lead = self.automation.add_lead(
                name=params.get("name", ""),
                email=params.get("email", ""),
                company=params.get("company", ""),
                title=params.get("title", ""),
                source=LeadSource[params.get("source", "OUTREACH").upper()],
                fit_score=params.get("fit_score", 0.5),
                tags=params.get("tags", []),
            )
            result["status"] = "success"
            result["lead_id"] = lead.id
            result["message"] = f"Added lead: {lead.name}"
        
        elif action == "create_deal":
            deal = self.automation.create_deal(
                lead_id=params.get("lead_id", ""),
                value=params.get("value", 0),
                expected_close=datetime.fromisoformat(params.get("expected_close", datetime.now().isoformat()))
            )
            result["status"] = "success"
            result["deal_id"] = deal.id
            result["message"] = f"Created deal: ${deal.value:,.2f}"
        
        elif action == "update_deal_stage":
            stage = DealStage[params.get("stage", "PROSPECT").upper()]
            self.automation.update_deal_stage(
                deal_id=params.get("deal_id", ""),
                new_stage=stage,
                notes=params.get("notes", "")
            )
            result["status"] = "success"
            result["message"] = f"Deal moved to {stage.value}"
        
        elif action == "get_pipeline":
            pipeline = self.automation.get_pipeline_summary()
            result["status"] = "success"
            result["pipeline"] = pipeline
        
        elif action == "generate_proposal":
            proposal = self.automation.generate_proposal(
                deal_id=params.get("deal_id", ""),
                template=params.get("template", "default")
            )
            result["status"] = "success"
            result["proposal_id"] = proposal.id
            result["preview"] = proposal.content[:200] + "..."
        
        elif action == "log_email":
            email_id = self.automation.log_email(
                lead_id=params.get("lead_id", ""),
                subject=params.get("subject", "")
            )
            result["status"] = "success"
            result["email_id"] = email_id
        
        elif action == "schedule_meeting":
            meeting_id = self.automation.schedule_meeting(
                deal_id=params.get("deal_id", ""),
                scheduled_date=datetime.fromisoformat(params.get("scheduled_date", "")),
                duration_minutes=params.get("duration_minutes", 30),
                meeting_type=params.get("meeting_type", "call")
            )
            result["status"] = "success"
            result["meeting_id"] = meeting_id
        
        else:
            result["status"] = "error"
            result["message"] = f"Unknown service action: {action}"
        
        return result

    def get_dashboard_data(self) -> Dict:
        """Get data for dashboard display"""
        routing_metrics = self.router.get_today_metrics()
        cost_breakdown = self.router.get_cost_breakdown()
        pipeline_summary = self.automation.get_pipeline_summary()
        chief_health = self.chief.health_check()
        
        return {
            "routing": {
                "metrics": {
                    "total_tasks": routing_metrics.total_tasks,
                    "kimi_tasks": routing_metrics.kimi_tasks,
                    "claude_tasks": routing_metrics.claude_tasks,
                    "kimi_percentage": routing_metrics.kimi_tasks / max(1, routing_metrics.total_tasks),
                    "claude_percentage": routing_metrics.claude_tasks / max(1, routing_metrics.total_tasks),
                },
                "cost": cost_breakdown,
            },
            "chief_of_staff": {
                "memory_count": chief_health["memory_count"],
                "decision_count": chief_health["decision_count"],
                "vault_connected": chief_health["vault_accessible"],
            },
            "service": {
                "total_leads": pipeline_summary["total_leads"],
                "total_pipeline": pipeline_summary["total_pipeline"],
                "stage_breakdown": pipeline_summary["stage_breakdown"],
            },
            "timestamp": datetime.now().isoformat(),
        }

    def health_check(self) -> Dict:
        """Health check for all integration layers"""
        return {
            "status": "operational",
            "router": {
                "tasks_today": len(self.router.tasks_today),
                "budget_remaining": self.router.budget_limit - self.router.budget_spent_today,
            },
            "chief": self.chief.health_check(),
            "service": self.automation.health_check(),
            "timestamp": datetime.now().isoformat(),
        }


# Global adapter instance
_adapter = None


def get_adapter(vault_path: str = "~/Obsidian", 
               budget_limit: float = 50.0) -> JARVISIntegrationAdapter:
    """Get or create global adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = JARVISIntegrationAdapter(vault_path=vault_path, budget_limit=budget_limit)
    return _adapter


if __name__ == "__main__":
    # Quick test
    adapter = get_adapter(budget_limit=50.0)
    
    print("=" * 80)
    print("INTEGRATION ADAPTER TEST")
    print("=" * 80)
    
    # Test processing user input
    test_inputs = [
        "Search for the latest AI trends in 2024",
        "What's my schedule today?",
        "Add a new lead: John Smith from Acme Corp",
        "Where are we on the sales pipeline?",
    ]
    
    for user_input in test_inputs:
        print(f"\nProcessing: {user_input}")
        result = adapter.process_user_input(user_input)
        print(f"  Task ID: {result['task_id']}")
        print(f"  Routing: {result['routing'].router.value}")
        print(f"  Service Actions: {result['service_actions']}")
    
    # Get dashboard data
    print("\n" + "=" * 80)
    print("DASHBOARD DATA")
    print("=" * 80)
    dashboard = adapter.get_dashboard_data()
    print(json.dumps(dashboard, indent=2, default=str))
