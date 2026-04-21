# 🎬 YouTube Monitor — Quick Access

## View Latest Comments
```bash
tail -10 .cache/youtube-comments.jsonl | jq '.'
```

## View Latest Report
```bash
cat .cache/youtube-comments-report.txt
```

## Count by Category
```bash
echo "Questions:" && jq 'select(.category=="questions") | 1' .cache/youtube-comments.jsonl | wc -l
echo "Praise:" && jq 'select(.category=="praise") | 1' .cache/youtube-comments.jsonl | wc -l
echo "Spam:" && jq 'select(.category=="spam") | 1' .cache/youtube-comments.jsonl | wc -l
echo "Sales:" && jq 'select(.category=="sales") | 1' .cache/youtube-comments.jsonl | wc -l
```

## Find Flagged Items
```bash
jq 'select(.response_status=="flagged_for_review")' .cache/youtube-comments.jsonl
```

## Find Auto-Responded Comments
```bash
jq 'select(.auto_replied==true)' .cache/youtube-comments.jsonl
```

## Monitor in Real-Time
```bash
tail -f .cache/youtube-cron-exec.log
```

## View Detailed Status
```bash
cat .cache/.youtube-monitor-state.json | jq '.'
```

---

**All logs are in:** `.cache/youtube-comments.jsonl` (JSONL format)  
**Reports are in:** `.cache/youtube-comments-report.txt`  
**Status is in:** `.cache/.youtube-monitor-state.json`

