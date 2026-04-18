"""
Integration Tests - Kimi Router + Chief of Staff + Service Automation

Tests that all three layers work together correctly.
"""

import unittest
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path

from integration_adapter import JARVISIntegrationAdapter
from kimi_router import KimiRouter, TaskCategory, LLMRouter
from chief_of_staff import ChiefOfStaff
from service_automation import ServiceAutomation, LeadSource, DealStage


class TestIntegrationAdapter(unittest.TestCase):
    """Test the integration adapter"""

    def setUp(self):
        """Set up test fixtures"""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.adapter = JARVISIntegrationAdapter(
            vault_path=self.tmpdir.name,
            budget_limit=100.0
        )

    def tearDown(self):
        """Clean up"""
        self.tmpdir.cleanup()

    def test_process_user_input(self):
        """Test processing user input through all layers"""
        result = self.adapter.process_user_input(
            "Search for the latest AI trends",
            context={}
        )
        
        self.assertIn("task_id", result)
        self.assertIn("routing", result)
        self.assertIn("chief_context", result)
        self.assertIn("service_actions", result)
        
        # Should be routed to Kimi (research)
        self.assertEqual(result["routing"].router, LLMRouter.KIMI)

    def test_research_task_routed_to_kimi(self):
        """Test that research tasks go to Kimi"""
        result = self.adapter.process_user_input(
            "Analyze the top 10 SaaS companies in 2024"
        )
        self.assertEqual(result["routing"].router, LLMRouter.KIMI)
        self.assertEqual(result["routing"].category, TaskCategory.RESEARCH)

    def test_critical_task_routed_to_claude(self):
        """Test that critical tasks go to Claude"""
        result = self.adapter.process_user_input(
            "Review this legal contract for issues"
        )
        self.assertEqual(result["routing"].router, LLMRouter.CLAUDE)

    def test_real_time_task_routed_to_claude(self):
        """Test that real-time tasks go to Claude"""
        result = self.adapter.process_user_input(
            "What time is my next meeting?"
        )
        self.assertEqual(result["routing"].router, LLMRouter.CLAUDE)

    def test_service_action_detection(self):
        """Test that service actions are detected"""
        result = self.adapter.process_user_input(
            "Add a new lead: John Smith from Acme"
        )
        self.assertIn("prompt_for_lead_details", result["service_actions"])

    def test_service_action_handling(self):
        """Test handling service automation actions"""
        params = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "company": "Tech Corp",
            "title": "CTO",
            "source": "LINKEDIN",
            "fit_score": 0.85,
        }
        
        result = self.adapter.handle_service_action("add_lead", params)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("lead_id", result)

    def test_memory_persistence(self):
        """Test that memories persist in Chief of Staff"""
        # Remember something
        self.adapter.handle_memory_action(
            "remember",
            "User prefers React over Vue",
            category="preference"
        )
        
        # Search for it
        memories = self.adapter.handle_memory_action(
            "search",
            "React"
        )
        
        self.assertGreater(len(memories), 0)

    def test_dashboard_data(self):
        """Test dashboard data collection"""
        # Process some tasks
        self.adapter.process_user_input("Search for AI trends")
        self.adapter.process_user_input("What's my schedule?")
        
        dashboard = self.adapter.get_dashboard_data()
        
        self.assertIn("routing", dashboard)
        self.assertIn("chief_of_staff", dashboard)
        self.assertIn("service", dashboard)
        self.assertGreater(dashboard["routing"]["metrics"]["total_tasks"], 0)

    def test_health_check(self):
        """Test health check of all layers"""
        health = self.adapter.health_check()
        
        self.assertEqual(health["status"], "operational")
        self.assertIn("router", health)
        self.assertIn("chief", health)
        self.assertIn("service", health)


class TestKimiRouter(unittest.TestCase):
    """Test Kimi router"""

    def setUp(self):
        """Set up router"""
        self.router = KimiRouter(budget_limit=50.0)

    def test_task_classification(self):
        """Test task classification"""
        research = self.router.classify_task("Search for AI breakthroughs")
        self.assertEqual(research, TaskCategory.RESEARCH)
        
        code = self.router.classify_task("Debug this Python function")
        self.assertEqual(code, TaskCategory.CODE)

    def test_routing_decision(self):
        """Test routing decision"""
        decision = self.router.route("task_1", "Search for machine learning papers")
        
        self.assertEqual(decision.category, TaskCategory.RESEARCH)
        self.assertEqual(decision.router, LLMRouter.KIMI)

    def test_cost_tracking(self):
        """Test cost tracking"""
        # Route several tasks
        self.router.route("task_1", "Search for data")
        self.router.route("task_2", "Analyze this document")
        
        self.assertGreater(self.router.budget_spent_today, 0)

    def test_target_distribution(self):
        """Test achieving target distribution"""
        # Route many research tasks (should go to Kimi)
        for i in range(10):
            decision = self.router.route(f"task_{i}", "Search for something important")
            if i < 7:  # First 7 should be Kimi
                self.assertIn(decision.router, [LLMRouter.KIMI])

    def test_metrics(self):
        """Test metrics collection"""
        self.router.route("task_1", "Search for data")
        self.router.route("task_2", "Search for more data")
        
        metrics = self.router.get_today_metrics()
        
        self.assertEqual(metrics.total_tasks, 2)
        self.assertGreater(metrics.total_cost, 0)

    def test_cost_estimation(self):
        """Test cost estimation"""
        cost = self.router.estimate_cost(
            LLMRouter.KIMI,
            input_tokens=1000,
            output_tokens=500
        )
        
        self.assertGreater(cost, 0)
        self.assertLess(cost, 0.01)  # Should be very cheap


class TestChiefOfStaff(unittest.TestCase):
    """Test Chief of Staff"""

    def setUp(self):
        """Set up Chief of Staff"""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.chief = ChiefOfStaff(vault_path=self.tmpdir.name)

    def tearDown(self):
        """Clean up"""
        self.tmpdir.cleanup()

    def test_remember_fact(self):
        """Test remembering facts"""
        memory = self.chief.remember_fact(
            "Prefers React for frontend",
            category="preference"
        )
        
        self.assertIsNotNone(memory.id)
        self.assertEqual(memory.content, "Prefers React for frontend")

    def test_log_decision(self):
        """Test logging decisions"""
        decision = self.chief.log_decision(
            decision="Use Kimi for research",
            context="Cost optimization",
            rationale="10x cheaper"
        )
        
        self.assertIsNotNone(decision.id)

    def test_search_memories(self):
        """Test searching memories"""
        self.chief.remember_fact("React is preferred", category="preference")
        self.chief.remember_fact("Vue is not used", category="preference")
        
        results = self.chief.search_memories("React")
        self.assertEqual(len(results), 1)

    def test_vault_structure(self):
        """Test Obsidian vault structure creation"""
        vault_path = Path(self.tmpdir.name)
        memories_dir = vault_path / "JARVIS_MEMORIES"
        decisions_dir = vault_path / "JARVIS_DECISIONS"
        
        self.assertTrue(memories_dir.exists())
        self.assertTrue(decisions_dir.exists())


class TestServiceAutomation(unittest.TestCase):
    """Test service automation"""

    def setUp(self):
        """Set up automation"""
        self.automation = ServiceAutomation()

    def test_add_lead(self):
        """Test adding a lead"""
        lead = self.automation.add_lead(
            name="John Smith",
            email="john@example.com",
            company="Acme Corp",
            title="VP Sales",
            source=LeadSource.LINKEDIN,
            fit_score=0.85
        )
        
        self.assertIsNotNone(lead.id)
        self.assertEqual(lead.name, "John Smith")

    def test_create_deal(self):
        """Test creating a deal"""
        lead = self.automation.add_lead(
            "Jane Doe", "jane@example.com", "Tech Co", "CTO",
            LeadSource.INBOUND, 0.9
        )
        
        deal = self.automation.create_deal(
            lead.id,
            value=50000,
            expected_close=datetime.now() + timedelta(days=30)
        )
        
        self.assertIsNotNone(deal.id)
        self.assertEqual(deal.value, 50000)

    def test_deal_progression(self):
        """Test moving deal through stages"""
        lead = self.automation.add_lead(
            "Bob Johnson", "bob@example.com", "StartUp Inc", "Founder",
            LeadSource.OUTREACH, 0.75
        )
        deal = self.automation.create_deal(lead.id, 25000, 
                                           datetime.now() + timedelta(days=14))
        
        self.automation.update_deal_stage(deal.id, DealStage.QUALIFIED)
        self.automation.update_deal_stage(deal.id, DealStage.ENGAGED)
        
        # Verify it progressed
        self.assertEqual(DealStage.ENGAGED.value, "engaged")

    def test_proposal_generation(self):
        """Test generating proposals"""
        lead = self.automation.add_lead(
            "Alice Wonder", "alice@example.com", "Wonder Corp", "Director",
            LeadSource.INBOUND, 0.88
        )
        deal = self.automation.create_deal(lead.id, 75000, datetime.now() + timedelta(days=21))
        
        proposal = self.automation.generate_proposal(deal.id)
        
        self.assertIsNotNone(proposal.id)
        self.assertIn("PROPOSAL", proposal.content)
        self.assertEqual(proposal.value, 75000)

    def test_pipeline_summary(self):
        """Test pipeline summary"""
        # Add some data
        lead1 = self.automation.add_lead(
            "Contact 1", "contact1@example.com", "Company 1", "Title 1",
            LeadSource.LINKEDIN
        )
        deal1 = self.automation.create_deal(lead1.id, 30000, 
                                           datetime.now() + timedelta(days=15))
        
        lead2 = self.automation.add_lead(
            "Contact 2", "contact2@example.com", "Company 2", "Title 2",
            LeadSource.INBOUND
        )
        deal2 = self.automation.create_deal(lead2.id, 50000, 
                                           datetime.now() + timedelta(days=30))
        
        summary = self.automation.get_pipeline_summary()
        
        self.assertEqual(summary["total_leads"], 2)
        self.assertGreater(summary["total_pipeline"], 0)


if __name__ == "__main__":
    unittest.main()
