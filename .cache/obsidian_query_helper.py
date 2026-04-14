#!/usr/bin/env python3
"""
Obsidian Vault Query Helper for OpenClaw Cron Jobs

Allows cron jobs to query DECISIONS.md, PATTERNS.md, MEMORY.md directly.
No MCP required — direct file access.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional

VAULT_PATH = Path.home() / "Obsidian Vaults" / "My Second Brain"

def get_vault_path() -> Path:
    """Get Obsidian vault path."""
    if VAULT_PATH.exists():
        return VAULT_PATH
    raise FileNotFoundError(f"Obsidian vault not found at {VAULT_PATH}")

def read_file(filename: str) -> str:
    """Read a file from the Obsidian vault."""
    vault_path = get_vault_path()
    file_path = vault_path / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"{filename} not found in vault")
    
    with open(file_path, 'r') as f:
        return f.read()

def search_vault(query: str, file_types: Optional[List[str]] = None) -> List[Dict]:
    """
    Search vault for files matching query.
    
    Args:
        query: Search term
        file_types: List of files to search (default: all)
    
    Returns:
        List of dicts with file, preview, relevance
    """
    vault_path = get_vault_path()
    results = []
    
    # Files to search
    files_to_search = [
        "DECISIONS.md",
        "PATTERNS.md",
        "MEMORY.md",
        "SOUL.md",
        "INDEX.md",
        "README.md"
    ]
    
    if file_types:
        files_to_search = [f for f in files_to_search if any(t in f for t in file_types)]
    
    for filename in files_to_search:
        try:
            content = read_file(filename)
            
            # Simple relevance scoring
            query_lower = query.lower()
            occurrences = content.lower().count(query_lower)
            
            if occurrences > 0:
                # Extract preview around first match
                idx = content.lower().find(query_lower)
                start = max(0, idx - 100)
                end = min(len(content), idx + 200)
                preview = content[start:end].strip()
                
                results.append({
                    "file": filename,
                    "matches": occurrences,
                    "relevance": min(1.0, occurrences / 10),  # Cap at 1.0
                    "preview": preview
                })
        except FileNotFoundError:
            continue
    
    # Sort by relevance
    return sorted(results, key=lambda x: x["relevance"], reverse=True)

def search_by_tag(tag: str) -> List[Dict]:
    """Search vault for files tagged with #tag."""
    vault_path = get_vault_path()
    results = []
    
    for filepath in vault_path.rglob("*.md"):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
                # Look for #tag in file
                if f"#{tag}" in content:
                    # Get file relative path
                    rel_path = filepath.relative_to(vault_path)
                    
                    results.append({
                        "file": filepath.name,
                        "path": str(rel_path),
                        "full_path": str(filepath),
                        "preview": content[:300]
                    })
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    return results

def get_decisions() -> str:
    """Get DECISIONS.md content."""
    return read_file("DECISIONS.md")

def get_patterns() -> str:
    """Get PATTERNS.md content."""
    return read_file("PATTERNS.md")

def get_memory() -> str:
    """Get MEMORY.md content."""
    return read_file("MEMORY.md")

def get_soul() -> str:
    """Get SOUL.md content (identity + principles)."""
    return read_file("SOUL.md")

def get_section(filename: str, section_header: str) -> Optional[str]:
    """
    Extract a section from a file (by header).
    
    Args:
        filename: File to read
        section_header: Section header (e.g., "Boil the Ocean" or "Service Business Strategy")
    
    Returns:
        Section content or None if not found
    """
    content = read_file(filename)
    
    # Find header
    lines = content.split('\n')
    start_idx = None
    
    for i, line in enumerate(lines):
        if section_header.lower() in line.lower() and line.startswith('#'):
            start_idx = i
            break
    
    if start_idx is None:
        return None
    
    # Find next header at same or higher level
    header_level = len(lines[start_idx]) - len(lines[start_idx].lstrip('#'))
    end_idx = len(lines)
    
    for i in range(start_idx + 1, len(lines)):
        if lines[i].startswith('#'):
            current_level = len(lines[i]) - len(lines[i].lstrip('#'))
            if current_level <= header_level:
                end_idx = i
                break
    
    return '\n'.join(lines[start_idx:end_idx])

# Usage examples for cron jobs:
if __name__ == "__main__":
    # Example 1: Get all patterns
    print("=== PATTERNS ===")
    patterns = get_patterns()
    print(patterns[:500])  # Print first 500 chars
    
    # Example 2: Search for something
    print("\n=== SEARCH FOR 'service business' ===")
    results = search_vault("service business")
    for result in results:
        print(f"- {result['file']} (relevance: {result['relevance']:.2f})")
    
    # Example 3: Get section
    print("\n=== SERVICE BUSINESS STRATEGY DECISION ===")
    section = get_section("DECISIONS.md", "Service Business Strategy")
    print(section)
    
    # Example 4: Search by tag
    print("\n=== FILES TAGGED #service-business ===")
    tagged = search_by_tag("service-business")
    for item in tagged:
        print(f"- {item['path']}")
