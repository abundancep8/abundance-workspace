"""
Comment Logger
Logs comments to JSONL format with structured records.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class CommentLogger:
    """
    Logs comments to JSONL file.
    
    Each line is a complete comment record with:
    - timestamp
    - commenter_name
    - comment_text
    - category
    - response_status
    """
    
    def __init__(self, cache_dir: Path):
        """
        Initialize logger.
        
        Args:
            cache_dir: Directory to store JSONL file
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.comments_file = self.cache_dir / "youtube-comments.jsonl"
        self.log = logging.getLogger('logger')
    
    
    def log_comment(self, record: Dict) -> bool:
        """
        Log a single comment record.
        
        Args:
            record: Comment record dictionary
            
        Returns:
            True if successful
        """
        try:
            with open(self.comments_file, 'a') as f:
                f.write(json.dumps(record) + '\n')
            return True
        except Exception as e:
            self.log.error(f"Failed to log comment: {e}")
            return False
    
    
    def log_batch(self, records: List[Dict]) -> int:
        """
        Log multiple comment records.
        
        Args:
            records: List of comment records
            
        Returns:
            Number of successfully logged records
        """
        count = 0
        for record in records:
            if self.log_comment(record):
                count += 1
        return count
    
    
    def read_comments(self, limit: int = None, offset: int = 0) -> List[Dict]:
        """
        Read logged comments.
        
        Args:
            limit: Max records to return
            offset: Start from Nth record
            
        Returns:
            List of comment records
        """
        comments = []
        
        if not self.comments_file.exists():
            return comments
        
        try:
            with open(self.comments_file, 'r') as f:
                for i, line in enumerate(f):
                    if i < offset:
                        continue
                    if limit and len(comments) >= limit:
                        break
                    
                    try:
                        record = json.loads(line.strip())
                        comments.append(record)
                    except json.JSONDecodeError:
                        self.log.warning(f"Invalid JSON on line {i+1}")
        
        except Exception as e:
            self.log.error(f"Failed to read comments: {e}")
        
        return comments
    
    
    def generate_report(self) -> Dict:
        """
        Generate report from logged comments.
        
        Returns:
            Report dictionary with statistics
        """
        comments = self.read_comments()
        
        report = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'total_comments': len(comments),
            'by_category': {
                '1_questions': 0,
                '2_praise': 0,
                '3_spam': 0,
                '4_sales': 0,
            },
            'by_status': {
                'sent': 0,
                'pending_review': 0,
                'skipped': 0,
                'failed': 0,
            },
            'timeline': self._analyze_timeline(comments),
        }
        
        # Count by category and status
        for comment in comments:
            category = comment.get('category', 'unknown')
            status = comment.get('response_status', 'unknown')
            
            if category in report['by_category']:
                report['by_category'][category] += 1
            
            if status in report['by_status']:
                report['by_status'][status] += 1
        
        return report
    
    
    def _analyze_timeline(self, comments: List[Dict]) -> Dict:
        """Analyze comment timeline."""
        timeline = {}
        
        for comment in comments:
            try:
                timestamp = comment.get('timestamp', '')
                date = timestamp.split('T')[0]
                
                if date not in timeline:
                    timeline[date] = 0
                timeline[date] += 1
            except Exception:
                pass
        
        return timeline
    
    
    def save_report(self, report: Dict = None, filename: str = None) -> bool:
        """
        Save report to JSON file.
        
        Args:
            report: Report dictionary (generates if not provided)
            filename: Output filename (default: youtube-comments-report.json)
            
        Returns:
            True if successful
        """
        if report is None:
            report = self.generate_report()
        
        if filename is None:
            filename = "youtube-comments-report.json"
        
        try:
            report_file = self.cache_dir / filename
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            self.log.info(f"Saved report to {report_file}")
            return True
        except Exception as e:
            self.log.error(f"Failed to save report: {e}")
            return False
    
    
    def export_csv(self, filename: str = "youtube-comments.csv") -> bool:
        """
        Export comments to CSV format.
        
        Args:
            filename: Output filename
            
        Returns:
            True if successful
        """
        import csv
        
        comments = self.read_comments()
        if not comments:
            return False
        
        try:
            csv_file = self.cache_dir / filename
            
            # Get all possible keys
            fieldnames = set()
            for comment in comments:
                fieldnames.update(comment.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(comments)
            
            self.log.info(f"Exported {len(comments)} comments to {csv_file}")
            return True
        
        except Exception as e:
            self.log.error(f"Failed to export CSV: {e}")
            return False
