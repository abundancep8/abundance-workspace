"""
Chief of Staff - Obsidian Memory + Decision Intelligence Layer

Integrates with user's Obsidian vault for persistent memory, pattern extraction,
decision logging, and context awareness. Bridges JARVIS with Chief of Staff intelligence.
"""

import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import re

log = logging.getLogger("chief_of_staff")


@dataclass
class Decision:
    """Logged decision record"""
    id: str
    date: datetime
    context: str
    decision: str
    rationale: str
    outcome: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    related_decisions: List[str] = field(default_factory=list)


@dataclass
class Memory:
    """Memory record with metadata"""
    id: str
    date: datetime
    category: str  # fact, preference, decision, lesson, goal
    content: str
    source: str  # where this came from
    confidence: float  # 0.0-1.0
    tags: List[str] = field(default_factory=list)


class ChiefOfStaff:
    """Intelligence layer bridging JARVIS with Obsidian vault"""

    def __init__(self, vault_path: str, db_path: str = "chief_of_staff.db"):
        """
        Initialize Chief of Staff
        
        Args:
            vault_path: Path to user's Obsidian vault
            db_path: SQLite database for additional tracking
        """
        self.vault_path = Path(vault_path).expanduser()
        self.db_path = db_path
        self.memories_dir = self.vault_path / "JARVIS_MEMORIES"
        self.decisions_dir = self.vault_path / "JARVIS_DECISIONS"
        
        self._ensure_vault_structure()
        self._init_db()

    def _ensure_vault_structure(self):
        """Create necessary directories in Obsidian vault"""
        self.memories_dir.mkdir(parents=True, exist_ok=True)
        self.decisions_dir.mkdir(parents=True, exist_ok=True)
        
        # Create index files if they don't exist
        memories_index = self.vault_path / "JARVIS_MEMORIES.md"
        if not memories_index.exists():
            memories_index.write_text("""# JARVIS Memories
Persistent memory extracted and refined from conversations.

## Categories
- Facts: Information about user preferences, goals, context
- Preferences: How the user prefers things done
- Decisions: Important decisions made
- Lessons: Learnings and patterns discovered
- Goals: User's stated goals and objectives

## Quick Access
- [[JARVIS_MEMORIES/facts]]
- [[JARVIS_MEMORIES/preferences]]
- [[JARVIS_MEMORIES/lessons]]
- [[JARVIS_MEMORIES/goals]]
""")
        
        decisions_index = self.vault_path / "JARVIS_DECISIONS.md"
        if not decisions_index.exists():
            decisions_index.write_text("""# JARVIS Decision Log
Important decisions logged with context and rationale.

Used to:
- Maintain consistency in future decisions
- Learn patterns in user preferences
- Provide historical context
- Support decision-making intelligence

## Recent Decisions
See [[JARVIS_DECISIONS/index]] for full log.
""")

    def _init_db(self):
        """Initialize SQLite database for decision/memory tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                date TEXT,
                category TEXT,
                content TEXT,
                source TEXT,
                confidence REAL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                date TEXT,
                context TEXT,
                decision TEXT,
                rationale TEXT,
                outcome TEXT,
                tags TEXT,
                related_decisions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                pattern TEXT,
                frequency INTEGER,
                category TEXT,
                confidence REAL,
                examples TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()

    def remember_fact(self, fact: str, category: str = "fact", 
                     tags: List[str] = None, source: str = "conversation") -> Memory:
        """Store a persistent memory/fact"""
        tags = tags or []
        memory_id = f"mem_{str(uuid.uuid4())[:8]}"
        
        memory = Memory(
            id=memory_id,
            date=datetime.now(),
            category=category,
            content=fact,
            source=source,
            confidence=0.9,
            tags=tags,
        )
        
        # Store in Obsidian
        memory_file = self.memories_dir / f"{memory_id}.md"
        memory_file.write_text(self._format_memory_for_vault(memory))
        
        # Store in database
        self._store_memory_db(memory)
        
        log.info(f"Remembered: {fact[:50]}... (category={category})")
        return memory

    def log_decision(self, decision: str, context: str, rationale: str,
                    tags: List[str] = None) -> Decision:
        """Log an important decision"""
        tags = tags or []
        decision_id = f"dec_{str(uuid.uuid4())[:8]}"
        
        decision_record = Decision(
            id=decision_id,
            date=datetime.now(),
            context=context,
            decision=decision,
            rationale=rationale,
            tags=tags,
        )
        
        # Store in Obsidian
        decision_file = self.decisions_dir / f"{decision_id}.md"
        decision_file.write_text(self._format_decision_for_vault(decision_record))
        
        # Store in database
        self._store_decision_db(decision_record)
        
        log.info(f"Decision logged: {decision[:50]}...")
        return decision_record

    def search_memories(self, query: str, category: str = None) -> List[Memory]:
        """Full-text search memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT id, date, category, content, source, confidence, tags
                FROM memories
                WHERE (content LIKE ? OR tags LIKE ?) AND category = ?
                ORDER BY created_at DESC
            """, (f"%{query}%", f"%{query}%", category))
        else:
            cursor.execute("""
                SELECT id, date, category, content, source, confidence, tags
                FROM memories
                WHERE content LIKE ? OR tags LIKE ?
                ORDER BY created_at DESC
            """, (f"%{query}%", f"%{query}%"))
        
        results = cursor.fetchall()
        conn.close()
        
        memories = []
        for r in results:
            memories.append(Memory(
                id=r[0],
                date=datetime.fromisoformat(r[1]),
                category=r[2],
                content=r[3],
                source=r[4],
                confidence=r[5],
                tags=json.loads(r[6]) if r[6] else [],
            ))
        
        return memories

    def search_decisions(self, query: str) -> List[Decision]:
        """Search decision log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, date, context, decision, rationale, outcome, tags, related_decisions
            FROM decisions
            WHERE context LIKE ? OR decision LIKE ? OR rationale LIKE ?
            ORDER BY created_at DESC
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        
        results = cursor.fetchall()
        conn.close()
        
        decisions = []
        for r in results:
            decisions.append(Decision(
                id=r[0],
                date=datetime.fromisoformat(r[1]),
                context=r[2],
                decision=r[3],
                rationale=r[4],
                outcome=r[5],
                tags=json.loads(r[6]) if r[6] else [],
                related_decisions=json.loads(r[7]) if r[7] else [],
            ))
        
        return decisions

    def extract_patterns(self, limit: int = 10) -> List[Dict]:
        """Extract behavioral patterns from memories and decisions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find common tags and categories
        cursor.execute("""
            SELECT tags, COUNT(*) as freq FROM memories
            WHERE tags IS NOT NULL
            GROUP BY tags
            ORDER BY freq DESC
            LIMIT ?
        """, (limit,))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                "type": "tag_frequency",
                "pattern": row[0],
                "frequency": row[1],
            })
        
        conn.close()
        return patterns

    def build_context_for_decision(self, decision_type: str) -> str:
        """Build decision context from relevant memories and past decisions"""
        # Search for relevant memories
        relevant_memories = self.search_memories(decision_type)
        
        # Search for related decisions
        related_decisions = self.search_decisions(decision_type)
        
        context = f"## Decision Context: {decision_type}\n\n"
        
        if relevant_memories:
            context += "### Related Memories\n"
            for mem in relevant_memories[:3]:
                context += f"- **{mem.category}**: {mem.content}\n"
            context += "\n"
        
        if related_decisions:
            context += "### Related Decisions\n"
            for dec in related_decisions[:3]:
                context += f"- **{dec.decision}** (rationale: {dec.rationale})\n"
            context += "\n"
        
        return context

    def _format_memory_for_vault(self, memory: Memory) -> str:
        """Format memory as Obsidian note"""
        tags_str = " ".join([f"#{tag}" for tag in memory.tags])
        
        return f"""# {memory.category.title()}: {memory.content[:50]}...

**Date**: {memory.date.strftime('%Y-%m-%d %H:%M:%S')}
**Category**: {memory.category}
**Source**: {memory.source}
**Confidence**: {memory.confidence:.0%}

## Content
{memory.content}

## Tags
{tags_str}

---
*Logged by JARVIS Chief of Staff*
"""

    def _format_decision_for_vault(self, decision: Decision) -> str:
        """Format decision as Obsidian note"""
        tags_str = " ".join([f"#{tag}" for tag in decision.tags])
        
        return f"""# Decision: {decision.decision[:50]}...

**Date**: {decision.date.strftime('%Y-%m-%d %H:%M:%S')}

## Context
{decision.context}

## Decision
{decision.decision}

## Rationale
{decision.rationale}

{f'## Outcome\n{decision.outcome}\n' if decision.outcome else ''}

## Related Decisions
{('- ' + '\\n- '.join(decision.related_decisions)) if decision.related_decisions else 'None yet'}

## Tags
{tags_str}

---
*Logged by JARVIS Chief of Staff*
"""

    def _store_memory_db(self, memory: Memory):
        """Store memory in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO memories
            (id, date, category, content, source, confidence, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.id,
            memory.date.isoformat(),
            memory.category,
            memory.content,
            memory.source,
            memory.confidence,
            json.dumps(memory.tags),
        ))
        conn.commit()
        conn.close()

    def _store_decision_db(self, decision: Decision):
        """Store decision in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO decisions
            (id, date, context, decision, rationale, outcome, tags, related_decisions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision.id,
            decision.date.isoformat(),
            decision.context,
            decision.decision,
            decision.rationale,
            decision.outcome,
            json.dumps(decision.tags),
            json.dumps(decision.related_decisions),
        ))
        conn.commit()
        conn.close()

    def get_recent_memories(self, limit: int = 10) -> List[Memory]:
        """Get recent memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, category, content, source, confidence, tags
            FROM memories
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        memories = []
        for r in results:
            memories.append(Memory(
                id=r[0],
                date=datetime.fromisoformat(r[1]),
                category=r[2],
                content=r[3],
                source=r[4],
                confidence=r[5],
                tags=json.loads(r[6]) if r[6] else [],
            ))
        
        return memories

    def health_check(self) -> Dict:
        """Check Chief of Staff health"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM memories")
        memory_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM decisions")
        decision_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "vault_path": str(self.vault_path),
            "vault_accessible": self.vault_path.exists(),
            "memory_count": memory_count,
            "decision_count": decision_count,
            "db_path": self.db_path,
            "db_accessible": Path(self.db_path).exists(),
        }


# Global instance
_chief = None


def get_chief(vault_path: str, db_path: str = "chief_of_staff.db") -> ChiefOfStaff:
    """Get or create global Chief of Staff instance"""
    global _chief
    if _chief is None:
        _chief = ChiefOfStaff(vault_path=vault_path, db_path=db_path)
    return _chief


if __name__ == "__main__":
    # Quick test
    import tempfile
    import time
    
    with tempfile.TemporaryDirectory() as tmpdir:
        chief = ChiefOfStaff(vault_path=tmpdir)
        
        print("=" * 80)
        print("CHIEF OF STAFF TEST")
        print("=" * 80)
        
        # Test remembering facts (with small delay to avoid ID collision)
        chief.remember_fact(
            "Prefers React over Vue for frontend projects",
            category="preference",
            tags=["technology", "frontend"]
        )
        time.sleep(0.1)
        
        chief.remember_fact(
            "Key goal: Complete JARVIS integration by EOQ",
            category="goal",
            tags=["project", "deadline"]
        )
        time.sleep(0.1)
        
        # Test logging decisions
        chief.log_decision(
            decision="Chose Kimi K2.5 for 70% of tasks",
            context="Cost optimization for JARVIS",
            rationale="Kimi is 5-10x cheaper than Claude for research/batch tasks",
            tags=["architecture", "cost-optimization"]
        )
        
        # Test search
        results = chief.search_memories("React")
        print(f"\nSearch results for 'React': {len(results)} found")
        for mem in results:
            print(f"  - {mem.content}")
        
        # Test health check
        health = chief.health_check()
        print(f"\nChief of Staff Status:")
        print(f"  Vault: {health['vault_accessible']}")
        print(f"  Memories: {health['memory_count']}")
        print(f"  Decisions: {health['decision_count']}")
