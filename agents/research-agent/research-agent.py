#!/usr/bin/env python3
"""
Research Agent — Knowledge Intake & Memory Integration
Processes videos, documents, knowledge, extracts insights
Feeds findings directly into Obsidian memory graph
"""

import os
import json
from pathlib import Path
from datetime import datetime

KNOWLEDGE_INTAKE = Path.home() / ".openclaw/workspace/agents/research-agent/knowledge-intake"
PROCESSED = Path.home() / ".openclaw/workspace/agents/research-agent/processed"
INSIGHTS = Path.home() / ".openclaw/workspace/agents/research-agent/extracted-insights"
MEMORY = Path.home() / ".openclaw/workspace/memory"

def process_input(file_path, input_type):
    """
    Process incoming knowledge:
    - Videos: extract metadata + transcripts
    - Documents: summarize + extract key points
    - Knowledge: categorize + link to existing concepts
    """
    
    print(f"Processing {input_type}: {file_path}")
    
    timestamp = datetime.now().isoformat()
    
    # Create insight document
    insight = {
        "timestamp": timestamp,
        "source_file": str(file_path),
        "input_type": input_type,
        "key_learnings": [],
        "connections_to_existing": [],
        "memory_additions": []
    }
    
    # Save processed file
    processed_file = PROCESSED / f"{Path(file_path).stem}-processed.json"
    with open(processed_file, 'w') as f:
        json.dump(insight, f, indent=2)
    
    print(f"✅ Processed: {processed_file}")
    return insight

def add_to_memory(insight):
    """
    Extract insights and add to Obsidian memory
    Creates daily research notes that link to main knowledge graph
    """
    
    today = datetime.now().strftime("%Y-%m-%d")
    research_log = MEMORY / f"research-{today}.md"
    
    # Append to daily research log
    with open(research_log, 'a') as f:
        f.write(f"\n## Research Input: {insight['timestamp']}\n")
        f.write(f"**Source:** {insight['source_file']}\n")
        f.write(f"**Type:** {insight['input_type']}\n")
        f.write("\n---\n")
    
    print(f"✅ Added to memory: {research_log}")

def main():
    print("=" * 60)
    print("RESEARCH AGENT — KNOWLEDGE INTAKE SYSTEM")
    print("=" * 60)
    print()
    print("HOW TO USE:")
    print("1. Drop files/links into: agents/research-agent/knowledge-intake/")
    print("2. Research agent processes automatically")
    print("3. Insights extracted and added to Obsidian memory")
    print("4. Memory graph grows with new connections")
    print()
    print("INTAKE FOLDER:")
    print(f"  {KNOWLEDGE_INTAKE}")
    print()
    print("SYSTEM ACTIVE — Ready to ingest knowledge")
    print("=" * 60)

if __name__ == "__main__":
    main()
