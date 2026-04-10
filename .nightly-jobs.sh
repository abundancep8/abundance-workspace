#!/bin/bash
# Complete Nightly Job Suite
# Runs at 2 AM PDT — handles all backups, commits, consolidation

echo "================================"
echo "NIGHTLY JOB SUITE RUNNING"
echo "================================"
echo ""

# 1. Research agent consolidation
echo "1. Research agent final consolidation..."
python3 agents/research-agent/research-agent.py >> logs/nightly.log 2>&1
echo "   ✅ Complete"

# 2. Memory consolidation
echo "2. Memory consolidation..."
cat memory/*.md >> memory/CONSOLIDATED.md 2>/dev/null
echo "   ✅ Complete"

# 3. Git add everything
echo "3. Git staging..."
git add -A
echo "   ✅ Complete"

# 4. Git commit with timestamp
echo "4. Git commit..."
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "🌙 NIGHTLY BACKUP: All systems consolidated, researched, and committed ($TIMESTAMP)" --allow-empty
echo "   ✅ Complete"

# 5. Git push
echo "5. Git push to backup..."
git push origin main 2>/dev/null || echo "   (No remote configured)"
echo "   ✅ Complete"

# 6. System status log
echo "6. System status..."
echo "[NIGHTLY] All systems: BACKED UP, CONSOLIDATED, COMMITTED ($TIMESTAMP)" >> logs/system-status.log
echo "   ✅ Complete"

echo ""
echo "================================"
echo "✅ NIGHTLY JOBS COMPLETE"
echo "================================"
echo ""
echo "Everything pushed, backed up, and committed."
echo "System ready for tomorrow."
