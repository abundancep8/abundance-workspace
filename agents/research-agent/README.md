# Research Agent — Knowledge Intake System

## Purpose
Feed videos, documents, links, and knowledge to the research agent.
The agent extracts insights and automatically adds them to Obsidian memory.

## How It Works

### 1. Input Folder
```
agents/research-agent/knowledge-intake/
```
Drop files here:
- Video files (MP4, MOV, MKV) → transcribed + analyzed
- PDFs/Documents → summarized + key points extracted
- Links/URLs → content fetched + insights extracted
- Text files → categorized + connected to existing knowledge

### 2. Processing
Research agent automatically:
- Extracts metadata
- Generates summaries
- Identifies key learnings
- Finds connections to existing concepts
- Creates insight documents

### 3. Memory Integration
Processed insights automatically:
- Added to daily research log in Obsidian
- Linked to relevant existing files
- Tagged with source + timestamp
- Indexed for graph connections

### 4. Knowledge Graph Growth
Every input grows the graph:
- New concepts become nodes
- Connections to existing ideas become edges
- Patterns emerge over time
- Memory becomes richer + more interconnected

## File Structure
```
agents/research-agent/
├── knowledge-intake/      ← DROP YOUR INPUTS HERE
├── processed/             ← Processed files stored
├── extracted-insights/    ← Key learnings extracted
├── research-agent.py      ← Core processing script
└── README.md             ← This file
```

## Supported Input Types
- **Videos**: YouTube links, local MP4/MOV files
- **Documents**: PDFs, markdown files, text files
- **Knowledge**: Articles, research papers, guides
- **Links**: Web URLs (content fetched + analyzed)
- **Audio**: Podcast links, voice recordings

## Example Workflow

1. You find a valuable TikTok creator's video
   - Copy the link
   - Paste into knowledge-intake folder

2. Research agent processes it
   - Extracts key concepts
   - Identifies applicable frameworks
   - Connects to existing knowledge

3. Obsidian memory updates
   - New research-DATE.md file created
   - Insights linked to relevant files
   - Graph visualization updates

4. System learns
   - Compound knowledge growth
   - Patterns become visible
   - Decision-making improves

## Commands
```bash
# Run research agent
cd ~/.openclaw/workspace
python3 agents/research-agent/research-agent.py

# Check processed files
ls agents/research-agent/processed/

# View extracted insights
ls agents/research-agent/extracted-insights/
```

## Integration
Research agent feeds directly into:
- Obsidian vault (automatic updates)
- Git backup (versioned)
- Memory graph (indexed)
- Daily knowledge logs

**System grows continuously with every input you provide.**
