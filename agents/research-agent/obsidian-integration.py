#!/usr/bin/env python3
"""
Obsidian Integration Module
Creates wiki-linked files, folders, and graph connections automatically
as research agent processes knowledge inputs
"""

import os
import json
from datetime import datetime
from pathlib import Path

class ObsidianIntegration:
    def __init__(self, vault_path="/Users/abundance/.openclaw/workspace/memory"):
        self.vault = Path(vault_path)
        self.vault.mkdir(parents=True, exist_ok=True)
        
    def create_research_folder(self, topic):
        """Create dated research folder"""
        folder = self.vault / f"research-{datetime.now().strftime('%Y-%m-%d')}"
        folder.mkdir(exist_ok=True)
        return folder
    
    def create_linked_note(self, title, content, tags=None, links=None):
        """Create markdown file with wiki-style links and tags"""
        folder = self.create_research_folder("master-key")
        
        # Sanitize filename
        filename = f"{title.lower().replace(' ', '-')}.md"
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
- [[Videos 1-3: Power of Thought & Attraction]]
- [[Videos 4-7: Supply, Vibration, Giving, Mental Image]]
- [[Videos 8-10: Action, Subconscious, Science of Getting Rich]]

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

# Usage example
if __name__ == "__main__":
    obsidian = ObsidianIntegration()
    
    # Create index
    obsidian.create_index()
    
    # Create linked notes for each video recap
    obsidian.create_linked_note(
        "Videos 1-3: Power of Thought & Attraction",
        "- The Power of Thought: Thoughts are blueprints for reality\n"
        "- Principle of Attraction: Like attracts like\n"
        "- Mental Wealth: Wealth starts in mind before bank\n",
        tags=["thought", "attraction", "manifestation"],
        links=["RESEARCH-INDEX"]
    )
    
    print("✅ Obsidian integration active")
    print("✅ Research folders created")
    print("✅ Index file generated")
