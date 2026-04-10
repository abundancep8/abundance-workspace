#!/usr/bin/env python3
"""
Research Agent v2 — Full Obsidian Integration
Processes videos, creates linked notes, builds graph connections
"""

import os
import json
from datetime import datetime
from pathlib import Path

class ObsidianIntegration:
    def __init__(self, vault_path="/Users/abundance/.openclaw/workspace/memory"):
        self.vault = Path(vault_path)
        self.vault.mkdir(parents=True, exist_ok=True)
        
    def create_research_folder(self):
        """Create dated research folder"""
        folder = self.vault / f"research-{datetime.now().strftime('%Y-%m-%d')}"
        folder.mkdir(exist_ok=True)
        return folder
    
    def create_linked_note(self, title, content, tags=None, links=None):
        """Create markdown file with wiki-style links and tags"""
        folder = self.create_research_folder()
        
        # Sanitize filename
        filename = f"{title.lower().replace(' ', '-').replace('&', 'and')}.md"
        filepath = folder / filename
        
        # Build frontmatter
        frontmatter = f"""---
title: {title}
date: {datetime.now().isoformat()}
tags: [research, master-key, manifestation"""
        if tags:
            frontmatter += f", {', '.join(tags)}"
        frontmatter += "]\n---\n\n"
        
        # Add backlinks if provided
        if links:
            frontmatter += "## Related\n"
            for link in links:
                frontmatter += f"- [[{link}]]\n"
            frontmatter += "\n"
        
        # Write file
        with open(filepath, 'w') as f:
            f.write(frontmatter)
            f.write(content)
        
        return filepath
    
    def create_index(self):
        """Create master index with all research connections"""
        index = self.vault / "RESEARCH-INDEX.md"
        content = """---
title: Research Index
---

# Master Key Society Research

## Video Series
- [[Videos 1-3: Power of Thought and Attraction]]
- [[Videos 4-7: Supply, Vibration, Giving, Mental Image]]
- [[Videos 8-10: Law of Attraction in Action, Subconscious, Science of Getting Rich]]

## Key Principles
- [[Law of Attraction]]
- [[Manifestation Science]]
- [[Wealth Consciousness]]
- [[Subconscious Programming]]

## Integration Points
- [[System Architecture]]
- [[Revenue Generation]]
- [[Daily Practice]]
"""
        with open(index, 'w') as f:
            f.write(content)
        return index

class ResearchAgent:
    def __init__(self):
        self.obsidian = ObsidianIntegration()
        self.processed = []
    
    def process_video_recap(self, title, recap_content, tags=None, related=None):
        """Process video recap and create Obsidian note"""
        
        # Create linked note in Obsidian
        filepath = self.obsidian.create_linked_note(
            title=title,
            content=recap_content,
            tags=tags or [],
            links=related or []
        )
        
        self.processed.append({
            "title": title,
            "filepath": str(filepath),
            "timestamp": datetime.now().isoformat()
        })
        
        return filepath
    
    def finalize(self):
        """Create master index and consolidate"""
        self.obsidian.create_index()
        
        # Log processing
        log_file = Path(self.obsidian.vault) / "PROCESSING-LOG.json"
        with open(log_file, 'w') as f:
            json.dump(self.processed, f, indent=2)
        
        return log_file

# Auto-run if called directly
if __name__ == "__main__":
    agent = ResearchAgent()
    
    # Process existing recaps
    agent.process_video_recap(
        "Videos 1-3: Power of Thought and Attraction",
        """## Key Teachings
- Thoughts are blueprints for reality
- Like attracts like
- Wealth starts in mind before bank account

## Integration
These principles form the foundation of our system.
""",
        tags=["thought", "attraction", "power"],
        related=["RESEARCH-INDEX", "Law of Attraction"]
    )
    
    agent.process_video_recap(
        "Videos 4-7: Supply, Vibration, Giving, Mental Image",
        """## Key Teachings
- Supply is infinite
- Everything vibrates at frequency
- Giving activates receiving
- Mental image determines reality

## Integration
Why we scale without fear, maintain consistency, give value first, visualize success.
""",
        tags=["supply", "vibration", "giving", "visualization"],
        related=["RESEARCH-INDEX"]
    )
    
    agent.process_video_recap(
        "Videos 8-10: Law of Attraction in Action, Subconscious, Science of Getting Rich",
        """## Key Teachings
- Thought + emotion + action must align
- Subconscious accepts repeated impressions
- Getting rich follows scientific principles

## Integration
Why our consistency, repetition, and definite principles guarantee results.
""",
        tags=["action", "subconscious", "science"],
        related=["RESEARCH-INDEX"]
    )
    
    # Finalize
    agent.finalize()
    print("✅ Research agent: All recaps processed and linked in Obsidian")
    print("✅ Graph connections created")
    print("✅ Index updated")
