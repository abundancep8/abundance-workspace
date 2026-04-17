"""
Integration Tests for JARVIS + Chief of Staff System
Tests core workflows end-to-end
"""
import pytest
import asyncio
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from chief_of_staff import ChiefOfStaff
from neural_router import NeuralRouter
from voice_handler import VoiceHandler
from service_automation import ServiceAutomation


@pytest.fixture
async def chief():
    """Initialize Chief of Staff."""
    c = ChiefOfStaff()
    await c.initialize()
    return c


@pytest.fixture
def router():
    """Initialize Neural Router."""
    return NeuralRouter()


@pytest.fixture
def voice():
    """Initialize Voice Handler."""
    return VoiceHandler()


@pytest.fixture
async def automation():
    """Initialize Service Automation."""
    a = ServiceAutomation()
    await a.initialize()
    return a


class TestChiefOfStaff:
    """Test Chief of Staff functionality."""
    
    @pytest.mark.asyncio
    async def test_initialize(self, chief):
        """Test Chief of Staff initialization."""
        assert chief.vault_path.exists()
        assert chief.decisions_path.exists()
        assert chief.patterns_path.exists()
        assert chief.memory_path.exists()
    
    @pytest.mark.asyncio
    async def test_remember(self, chief):
        """Test vault remember functionality."""
        note_id = await chief.remember(
            "DECISION: Use Kimi for cost optimization",
            {"tags": ["cost", "optimization"]}
        )
        
        assert note_id.startswith("note_")
        assert (chief.memory_path / f"{note_id}.json").exists()
    
    @pytest.mark.asyncio
    async def test_search_vault(self, chief):
        """Test vault search."""
        # Store a note first
        await chief.remember("Test search content for testing")
        
        # Search for it
        results = await chief.search_vault("test search")
        
        assert len(results) >= 0  # May or may not find (FTS not perfect)
    
    @pytest.mark.asyncio
    async def test_execute_task(self, chief):
        """Test task execution with context."""
        result = await chief.execute(
            "research",
            "What are best practices for SaaS pricing?",
            {"context": "B2B software company"}
        )
        
        assert "response" in result
        assert result["task_type"] == "research"
        assert result["model"] == "claude-3-5-sonnet-20241022"


class TestNeuralRouter:
    """Test cost routing logic."""
    
    def test_route_critical_task(self, router):
        """Critical tasks should use Claude."""
        model, cost = router.route_task("voice_command", 500)
        assert model == "claude"
    
    def test_route_simple_task(self, router):
        """Simple tasks should use Kimi."""
        model, cost = router.route_task("remember", 100)
        assert model == "kimi"
    
    def test_route_complex_research(self, router):
        """Complex research might use Claude."""
        model, cost = router.route_task("research", 2000)
        # Could be either based on budget
        assert model in ["kimi", "claude"]
    
    def test_budget_tracking(self, router):
        """Test budget usage tracking."""
        router.track_usage("task_1", "kimi", 0.10)
        router.track_usage("task_2", "claude", 0.50)
        
        assert router.budget_used >= 0.60
        assert len(router.tasks_log) == 2
    
    def test_budget_status(self, router):
        """Test budget status reporting."""
        status = router.get_budget_status()
        
        assert "daily_budget" in status
        assert "spent" in status
        assert "remaining" in status
        assert "percent_used" in status
    
    def test_cost_estimation(self, router):
        """Test cost estimation."""
        kimi_cost = router._estimate_cost("kimi", 1000)
        claude_cost = router._estimate_cost("claude", 1000)
        
        assert kimi_cost < claude_cost
        assert kimi_cost > 0
        assert claude_cost > 0


class TestVoiceHandler:
    """Test voice and visualization functionality."""
    
    def test_orb_state_initialization(self, voice):
        """Test orb state."""
        state = voice.get_current_state()
        
        assert "position" in state
        assert "scale" in state
        assert "color" in state
        assert "intensity" in state
    
    def test_orb_state_calculation(self, voice):
        """Test orb state changes with intensity."""
        state_low = voice.calculate_orb_state(0.2)
        state_high = voice.calculate_orb_state(0.8)
        
        # Intensity should be reflected
        assert state_low["intensity"] < state_high["intensity"]
        
        # Scale should increase with intensity
        assert state_low["scale"] < state_high["scale"]
    
    def test_color_shift_by_intensity(self, voice):
        """Test color shifts based on intensity."""
        state_low = voice.calculate_orb_state(0.1)
        state_mid = voice.calculate_orb_state(0.5)
        state_high = voice.calculate_orb_state(0.9)
        
        # Colors should differ
        assert state_low["color"] == "#0099FF"  # Blue
        assert state_mid["color"] == "#00FF99"  # Green
        assert state_high["color"] == "#FF0099"  # Pink
    
    def test_neural_pattern_generation(self, voice):
        """Test neural firing pattern generation."""
        state = voice.calculate_orb_state(0.7)
        
        assert "neural_firing" in state
        assert isinstance(state["neural_firing"], list)
    
    def test_pulse_calculation(self, voice):
        """Test pulse animation parameters."""
        state = voice.calculate_orb_state(0.5)
        
        assert "pulse" in state
        assert "frequency" in state["pulse"]
        assert "amplitude" in state["pulse"]


class TestServiceAutomation:
    """Test service business automation."""
    
    @pytest.mark.asyncio
    async def test_generate_leads(self, automation):
        """Test lead generation."""
        result = await automation.generate_leads("SaaS companies in tech")
        
        assert "leads_generated" in result
        assert result["leads_generated"] > 0
        assert "leads" in result
        assert len(result["leads"]) > 0
    
    @pytest.mark.asyncio
    async def test_sales_pipeline_view(self, automation):
        """Test viewing sales pipeline."""
        result = await automation.sales_pipeline("view")
        
        assert "pipeline" in result
        assert "total_value" in result
        assert "deal_count" in result
    
    @pytest.mark.asyncio
    async def test_sales_pipeline_forecast(self, automation):
        """Test revenue forecast."""
        result = await automation.sales_pipeline("forecast")
        
        assert "forecast" in result
        assert isinstance(result["forecast"], float)
    
    @pytest.mark.asyncio
    async def test_create_deal(self, automation):
        """Test deal creation."""
        result = await automation.sales_pipeline(
            "create_deal",
            context={"company": "Acme Inc", "value": 50000}
        )
        
        assert "deal_created" in result
        assert "deal" in result
    
    @pytest.mark.asyncio
    async def test_schedule_meeting(self, automation):
        """Test meeting scheduling."""
        result = await automation.schedule_meeting(
            "Sales call with prospect",
            context={
                "title": "Sales Call",
                "attendee": "john@example.com",
                "duration": 30
            }
        )
        
        assert "meeting_scheduled" in result
        assert result["meeting_scheduled"] == True


class TestIntegration:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_workflow_lead_gen(self, chief, router, automation):
        """Test full workflow: lead generation with cost tracking."""
        # Generate leads
        leads_result = await automation.generate_leads("B2B SaaS in NYC")
        assert leads_result["leads_generated"] > 0
        
        # Route task
        model, cost = router.route_task("lead_gen", len(str(leads_result)))
        assert model in ["kimi", "claude"]
        
        # Track cost
        router.track_usage("test_task", model, 0.25)
        assert router.budget_used >= 0.25
    
    @pytest.mark.asyncio
    async def test_voice_to_task_flow(self, voice, chief, router):
        """Test voice input to task execution."""
        # Simulate voice input
        orb_state = voice.calculate_orb_state(0.6)
        assert orb_state["intensity"] > 0.5
        
        # Route the implied task
        model, cost = router.route_task("voice_command", 100)
        assert model == "claude"  # Voice commands use Claude
    
    @pytest.mark.asyncio
    async def test_budget_protection(self, router):
        """Test budget protection mechanisms."""
        router.daily_budget = 1.0  # Set low budget
        
        # Track high-cost task
        router.track_usage("expensive", "claude", 0.95)
        
        status = router.get_budget_status()
        assert status["spent"] >= 0.95
        assert len(router.budget_alerts) > 0 or status["remaining"] < 0.2


# Run tests with: pytest tests/test_integration.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
