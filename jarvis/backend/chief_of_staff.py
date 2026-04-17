"""
Chief of Staff - Obsidian Vault + Claude Code Integration
Manages knowledge base, memory, context, and pattern recognition.
"""
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import anthropic
import logging

logger = logging.getLogger(__name__)

class ChiefOfStaff:
    """
    Chief of Staff orchestrates Obsidian vault, memory, and Claude Code execution.
    Acts as the decision-making engine + knowledge manager.
    """
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.vault_path = Path.home() / ".openclaw" / "workspace" / "vault"
        self.memory_path = Path.home() / ".openclaw" / "workspace" / "memory"
        self.decisions_path = self.vault_path / "decisions"
        self.patterns_path = self.vault_path / "patterns"
        self.neural_patterns = {}
        
    async def initialize(self):
        """Initialize vault structure and load patterns."""
        # Create vault directories
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.decisions_path.mkdir(parents=True, exist_ok=True)
        self.patterns_path.mkdir(parents=True, exist_ok=True)
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing neural patterns
        await self._load_patterns()
        logger.info(f"✅ Chief of Staff initialized with {len(self.neural_patterns)} patterns")
    
    async def execute(self, task_type: str, content: str, context: Optional[Dict] = None) -> Dict:
        """
        Execute task with Claude, using vault context.
        """
        # Gather context from vault
        vault_context = await self._gather_context(task_type, content)
        
        # Build system prompt with patterns
        system_prompt = self._build_system_prompt(vault_context, task_type)
        
        # Execute with Claude
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"{task_type.upper()}\n\n{content}\n\nContext: {json.dumps(context or {})}"
                }
            ]
        )
        
        result_text = response.content[0].text
        
        # Store execution pattern for learning
        await self._record_execution(task_type, content, result_text)
        
        return {
            "response": result_text,
            "task_type": task_type,
            "context_size": len(str(vault_context)),
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }
    
    async def research(self, topic: str, context: Optional[Dict] = None) -> Dict:
        """Deep research with vault memory augmentation."""
        # Search vault for related knowledge
        related_notes = await self.search_vault(topic)
        
        system_prompt = f"""You are a research expert with access to the following knowledge base:

{chr(10).join(related_notes[:5])}

Conduct thorough research on: {topic}
Provide structured analysis, key findings, and actionable insights."""
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            system=system_prompt,
            messages=[{"role": "user", "content": topic}]
        )
        
        analysis = response.content[0].text
        
        # Store research findings
        note_id = await self.remember(f"## Research: {topic}\n\n{analysis}", 
                                     {"tags": ["research", topic.lower().replace(" ", "-")]})
        
        return {
            "research": analysis,
            "note_id": note_id,
            "sources": len(related_notes),
            "timestamp": datetime.now().isoformat()
        }
    
    async def remember(self, content: str, metadata: Optional[Dict] = None) -> str:
        """
        Store knowledge in vault with backlinks and tags.
        Returns note_id.
        """
        note_id = f"note_{int(datetime.now().timestamp() * 1000)}"
        
        # Create structured note
        note = {
            "id": note_id,
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "metadata": metadata or {},
            "backlinks": []
        }
        
        # Save to vault
        note_path = self.memory_path / f"{note_id}.json"
        note_path.write_text(json.dumps(note, indent=2))
        
        # Extract and store patterns
        await self._extract_patterns(content, note_id)
        
        logger.info(f"💾 Remembered note {note_id}")
        return note_id
    
    async def search_vault(self, query: str, limit: int = 5) -> List[str]:
        """
        Full-text search across vault.
        Simplified version - production would use FTS5.
        """
        results = []
        
        # Search memory files
        if self.memory_path.exists():
            for note_file in self.memory_path.glob("*.json"):
                try:
                    note = json.loads(note_file.read_text())
                    if query.lower() in note["content"].lower():
                        results.append(f"[{note['id']}] {note['content'][:200]}...")
                except:
                    pass
        
        return results[:limit]
    
    async def _gather_context(self, task_type: str, content: str) -> Dict:
        """Gather relevant context from vault."""
        context = {
            "recent_decisions": await self._get_recent_decisions(limit=3),
            "relevant_patterns": self._get_relevant_patterns(task_type),
            "memory_bank": await self.search_vault(content, limit=3),
            "timestamp": datetime.now().isoformat()
        }
        return context
    
    def _build_system_prompt(self, vault_context: Dict, task_type: str) -> str:
        """Build system prompt with vault context and patterns."""
        return f"""You are JARVIS, an intelligent Chief of Staff AI system integrated with an Obsidian knowledge vault.

ACTIVE PATTERNS:
{chr(10).join(f"- {p}: {self.neural_patterns.get(p, '')}" for p in list(self.neural_patterns.keys())[:5])}

RECENT CONTEXT:
- Recent decisions: {len(vault_context['recent_decisions'])} on file
- Relevant patterns: {vault_context['relevant_patterns']}
- Memory references: {len(vault_context['memory_bank'])} notes available

TASK TYPE: {task_type.upper()}

Your role is to:
1. Use vault context to make informed decisions
2. Recognize and apply learned patterns
3. Maintain consistency with past decisions
4. Learn from each execution to improve future performance
5. Provide structured, actionable responses

Be direct, specific, and action-oriented."""
    
    async def _record_execution(self, task_type: str, input_text: str, result: str):
        """Record execution for pattern learning."""
        execution = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "input_length": len(input_text),
            "result_length": len(result),
            "quality_score": await self._score_quality(result)
        }
        
        # Store execution log
        log_path = self.decisions_path / f"exec_{int(datetime.now().timestamp() * 1000)}.json"
        log_path.write_text(json.dumps(execution, indent=2))
    
    async def _extract_patterns(self, content: str, note_id: str):
        """Extract and store patterns from content."""
        # Look for decision patterns, insights, frameworks
        if "DECISION:" in content or "PATTERN:" in content or "RULE:" in content:
            pattern_id = f"pattern_{note_id}"
            self.neural_patterns[pattern_id] = content[:100]
            logger.info(f"🧠 Extracted pattern: {pattern_id}")
    
    async def _load_patterns(self):
        """Load saved patterns from vault."""
        if self.patterns_path.exists():
            for pattern_file in self.patterns_path.glob("*.json"):
                try:
                    pattern = json.loads(pattern_file.read_text())
                    self.neural_patterns[pattern["id"]] = pattern["content"]
                except:
                    pass
    
    async def _get_recent_decisions(self, limit: int = 3) -> List[Dict]:
        """Get recent decisions from vault."""
        decisions = []
        if self.decisions_path.exists():
            files = sorted(self.decisions_path.glob("*.json"), reverse=True)
            for f in files[:limit]:
                try:
                    decisions.append(json.loads(f.read_text()))
                except:
                    pass
        return decisions
    
    def _get_relevant_patterns(self, task_type: str) -> List[str]:
        """Get patterns relevant to task type."""
        return [k for k in self.neural_patterns.keys() if task_type.lower() in k.lower()][:3]
    
    async def _score_quality(self, result: str) -> float:
        """Simple quality scoring."""
        factors = [
            len(result) > 50,  # Substantive response
            result.count(".") > 2,  # Multiple sentences
            len(set(result.split())) > 20  # Vocabulary diversity
        ]
        return sum(factors) / len(factors)
    
    def get_neural_patterns(self) -> Dict:
        """Return current neural pattern state."""
        return {
            "count": len(self.neural_patterns),
            "patterns": list(self.neural_patterns.keys())[:10],
            "timestamp": datetime.now().isoformat()
        }
