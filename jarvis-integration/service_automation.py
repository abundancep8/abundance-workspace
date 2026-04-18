"""
Service Automation - Lead Gen, Sales Pipeline, CRM

Handles:
- Lead generation and enrichment
- Sales pipeline tracking
- Proposal generation
- Email prospecting
- Meeting scheduling
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List
from uuid import uuid4

log = logging.getLogger("service_automation")


class DealStage(Enum):
    """Sales pipeline stages"""
    PROSPECT = "prospect"  # Initial lead
    QUALIFIED = "qualified"  # Verified fit
    ENGAGED = "engaged"  # Active conversation
    PROPOSED = "proposed"  # Quote sent
    NEGOTIATING = "negotiating"  # Terms discussion
    CLOSED_WON = "closed_won"  # Signed
    CLOSED_LOST = "closed_lost"  # Lost


class LeadSource(Enum):
    """Where the lead came from"""
    LINKEDIN = "linkedin"
    EMAIL = "email"
    REFERRAL = "referral"
    INBOUND = "inbound"
    OUTREACH = "outreach"
    WEBSITE = "website"


@dataclass
class Lead:
    """Lead record"""
    id: str
    name: str
    email: str
    company: str
    title: str
    source: LeadSource
    created_date: datetime
    last_contacted: Optional[datetime] = None
    notes: str = ""
    fit_score: float = 0.0  # 0.0-1.0
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict = field(default_factory=dict)


@dataclass
class Deal:
    """Sales deal"""
    id: str
    lead_id: str
    value: float  # USD
    stage: DealStage
    created_date: datetime
    expected_close: datetime
    last_updated: datetime
    probability: float = 0.0  # 0.0-1.0
    notes: str = ""
    email_count: int = 0
    meeting_count: int = 0


@dataclass
class Proposal:
    """Generated proposal"""
    id: str
    deal_id: str
    created_date: datetime
    content: str
    status: str  # draft, sent, accepted, rejected
    value: float
    template_used: str = "default"


class ServiceAutomation:
    """Service business automation engine"""

    def __init__(self, db_path: str = "service_automation.db"):
        """Initialize service automation"""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Leads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT UNIQUE,
                company TEXT,
                title TEXT,
                source TEXT,
                created_date TEXT,
                last_contacted TEXT,
                notes TEXT,
                fit_score REAL,
                tags TEXT,
                custom_fields TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Deals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deals (
                id TEXT PRIMARY KEY,
                lead_id TEXT,
                value REAL,
                stage TEXT,
                created_date TEXT,
                expected_close TEXT,
                last_updated TEXT,
                probability REAL,
                notes TEXT,
                email_count INTEGER DEFAULT 0,
                meeting_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads(id)
            )
        """)
        
        # Proposals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proposals (
                id TEXT PRIMARY KEY,
                deal_id TEXT,
                created_date TEXT,
                content TEXT,
                status TEXT,
                value REAL,
                template_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deal_id) REFERENCES deals(id)
            )
        """)
        
        # Email log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_log (
                id TEXT PRIMARY KEY,
                lead_id TEXT,
                subject TEXT,
                sent_date TEXT,
                opened BOOLEAN,
                clicked BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads(id)
            )
        """)
        
        # Meetings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id TEXT PRIMARY KEY,
                deal_id TEXT,
                scheduled_date TEXT,
                duration_minutes INTEGER,
                meeting_type TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deal_id) REFERENCES deals(id)
            )
        """)
        
        conn.commit()
        conn.close()

    def add_lead(self, name: str, email: str, company: str, title: str,
                source: LeadSource, fit_score: float = 0.0, 
                tags: List[str] = None) -> Lead:
        """Add a new lead"""
        lead_id = str(uuid4())
        lead = Lead(
            id=lead_id,
            name=name,
            email=email,
            company=company,
            title=title,
            source=source,
            created_date=datetime.now(),
            fit_score=fit_score,
            tags=tags or [],
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO leads
                (id, name, email, company, title, source, created_date, fit_score, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead.id, lead.name, lead.email, lead.company, lead.title,
                lead.source.value, lead.created_date.isoformat(),
                lead.fit_score, json.dumps(lead.tags)
            ))
            conn.commit()
            log.info(f"Added lead: {name} ({email}) from {source.value}")
        except sqlite3.IntegrityError:
            log.warning(f"Lead {email} already exists")
        finally:
            conn.close()
        
        return lead

    def create_deal(self, lead_id: str, value: float, 
                   expected_close: datetime) -> Deal:
        """Create a deal for a lead"""
        deal_id = str(uuid4())
        deal = Deal(
            id=deal_id,
            lead_id=lead_id,
            value=value,
            stage=DealStage.PROSPECT,
            created_date=datetime.now(),
            expected_close=expected_close,
            last_updated=datetime.now(),
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO deals
            (id, lead_id, value, stage, created_date, expected_close, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            deal.id, deal.lead_id, deal.value, deal.stage.value,
            deal.created_date.isoformat(), deal.expected_close.isoformat(),
            deal.last_updated.isoformat()
        ))
        conn.commit()
        conn.close()
        
        log.info(f"Created deal: {deal_id} for lead {lead_id} (${value:.2f})")
        return deal

    def update_deal_stage(self, deal_id: str, new_stage: DealStage, 
                         notes: str = ""):
        """Update deal stage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE deals
            SET stage = ?, last_updated = ?, notes = ?
            WHERE id = ?
        """, (new_stage.value, datetime.now().isoformat(), notes, deal_id))
        
        conn.commit()
        conn.close()
        
        log.info(f"Deal {deal_id} moved to {new_stage.value}")

    def log_email(self, lead_id: str, subject: str) -> str:
        """Log sent email"""
        email_id = str(uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO email_log
            (id, lead_id, subject, sent_date)
            VALUES (?, ?, ?, ?)
        """, (email_id, lead_id, subject, datetime.now().isoformat()))
        
        # Increment deal email count
        cursor.execute("""
            UPDATE deals
            SET email_count = email_count + 1
            WHERE lead_id = ?
        """, (lead_id,))
        
        conn.commit()
        conn.close()
        
        log.info(f"Logged email to {lead_id}: {subject[:40]}...")
        return email_id

    def schedule_meeting(self, deal_id: str, scheduled_date: datetime,
                        duration_minutes: int = 30, meeting_type: str = "call") -> str:
        """Schedule a meeting"""
        meeting_id = str(uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO meetings
            (id, deal_id, scheduled_date, duration_minutes, meeting_type)
            VALUES (?, ?, ?, ?, ?)
        """, (meeting_id, deal_id, scheduled_date.isoformat(), 
              duration_minutes, meeting_type))
        
        # Increment deal meeting count
        cursor.execute("""
            UPDATE deals
            SET meeting_count = meeting_count + 1
            WHERE id = ?
        """, (deal_id,))
        
        conn.commit()
        conn.close()
        
        log.info(f"Scheduled {meeting_type} for deal {deal_id}")
        return meeting_id

    def generate_proposal(self, deal_id: str, template: str = "default") -> Proposal:
        """Generate proposal from template"""
        # Get deal details
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM deals WHERE id = ?", (deal_id,))
        deal_data = cursor.fetchone()
        
        if not deal_data:
            conn.close()
            raise ValueError(f"Deal {deal_id} not found")
        
        # Get lead details
        lead_id = deal_data[1]
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        lead_data = cursor.fetchone()
        conn.close()
        
        if not lead_data:
            raise ValueError(f"Lead {lead_id} not found")
        
        # Generate proposal content
        proposal_content = self._render_proposal_template(
            template, lead_data, deal_data
        )
        
        proposal_id = str(uuid4())
        proposal = Proposal(
            id=proposal_id,
            deal_id=deal_id,
            created_date=datetime.now(),
            content=proposal_content,
            status="draft",
            value=deal_data[2],
            template_used=template,
        )
        
        # Store proposal
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO proposals
            (id, deal_id, created_date, content, status, value, template_used)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (proposal.id, proposal.deal_id, proposal.created_date.isoformat(),
              proposal.content, proposal.status, proposal.value, proposal.template_used))
        conn.commit()
        conn.close()
        
        log.info(f"Generated proposal {proposal_id} for deal {deal_id}")
        return proposal

    def _render_proposal_template(self, template: str, lead_data: tuple, 
                                  deal_data: tuple) -> str:
        """Render proposal from template"""
        # Basic template
        lead_name, lead_email = lead_data[1], lead_data[2]
        deal_value, deal_stage = deal_data[2], deal_data[3]
        
        return f"""PROPOSAL

To: {lead_name} ({lead_email})

Proposal Value: ${deal_value:,.2f}

SCOPE OF WORK
{self._get_template_by_name(template)}

TIMELINE
- Week 1-2: Discovery & Planning
- Week 3-4: Implementation
- Week 5: Review & Refinement
- Week 6: Delivery & Training

INVESTMENT
Total Project Cost: ${deal_value:,.2f}

NEXT STEPS
Please confirm acceptance of this proposal. We'll schedule a kickoff meeting 
to begin immediately upon your approval.

Best regards,
[Your Name]
"""

    def _get_template_by_name(self, name: str) -> str:
        """Get template content"""
        templates = {
            "default": "- Comprehensive assessment of current situation\n- Custom solution design\n- Implementation & deployment\n- Training & documentation\n- 30-day support period",
            "web": "- Website design & development\n- Responsive mobile optimization\n- SEO implementation\n- Analytics & tracking setup\n- 3 months of support",
            "consulting": "- Initial consultation & assessment\n- Strategic recommendations\n- Implementation roadmap\n- Quarterly check-ins\n- Documentation",
        }
        return templates.get(name, templates["default"])

    def get_pipeline_summary(self) -> Dict:
        """Get sales pipeline summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count deals by stage
        cursor.execute("""
            SELECT stage, COUNT(*) as count, SUM(value) as total_value
            FROM deals
            GROUP BY stage
        """)
        
        stage_data = {}
        total_pipeline = 0
        for row in cursor.fetchall():
            stage_data[row[0]] = {"count": row[1], "value": row[2] or 0}
            total_pipeline += row[2] or 0
        
        # Get leads by source
        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM leads
            GROUP BY source
        """)
        
        source_data = {}
        for row in cursor.fetchall():
            source_data[row[0]] = row[1]
        
        # Upcoming meetings
        tomorrow = (datetime.now() + timedelta(days=1)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM meetings
            WHERE scheduled_date <= ?
        """, (tomorrow,))
        
        upcoming_meetings = cursor.fetchone()[0]
        conn.close()
        
        return {
            "total_pipeline": total_pipeline,
            "stage_breakdown": stage_data,
            "leads_by_source": source_data,
            "upcoming_meetings": upcoming_meetings,
            "total_leads": sum(source_data.values()),
        }

    def get_high_priority_deals(self, limit: int = 5) -> List[Dict]:
        """Get deals that need attention"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deals close to due date, no recent contact
        cursor.execute("""
            SELECT d.id, l.name, d.value, d.expected_close, d.stage
            FROM deals d
            JOIN leads l ON d.lead_id = l.id
            WHERE d.stage NOT IN ('closed_won', 'closed_lost')
            ORDER BY d.expected_close ASC
            LIMIT ?
        """, (limit,))
        
        deals = []
        for row in cursor.fetchall():
            deals.append({
                "deal_id": row[0],
                "lead_name": row[1],
                "value": row[2],
                "expected_close": row[3],
                "stage": row[4],
            })
        
        conn.close()
        return deals

    def health_check(self) -> Dict:
        """Check service automation health"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM leads")
        lead_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM deals")
        deal_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(value) FROM deals WHERE stage = 'closed_won'")
        revenue = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_leads": lead_count,
            "total_deals": deal_count,
            "revenue": revenue,
            "db_path": self.db_path,
            "db_accessible": Path(self.db_path).exists(),
        }


# Global instance
_automation = None


def get_automation(db_path: str = "service_automation.db") -> ServiceAutomation:
    """Get or create global service automation instance"""
    global _automation
    if _automation is None:
        _automation = ServiceAutomation(db_path=db_path)
    return _automation


if __name__ == "__main__":
    # Quick test
    automation = ServiceAutomation()
    
    print("=" * 80)
    print("SERVICE AUTOMATION TEST")
    print("=" * 80)
    
    # Add a lead
    lead = automation.add_lead(
        name="John Smith",
        email="john@acmecorp.com",
        company="Acme Corp",
        title="VP of Engineering",
        source=LeadSource.LINKEDIN,
        fit_score=0.85,
        tags=["enterprise", "tech"]
    )
    print(f"\nAdded lead: {lead.name} ({lead.email})")
    
    # Create a deal
    deal = automation.create_deal(
        lead_id=lead.id,
        value=50000.0,
        expected_close=datetime.now() + timedelta(days=30)
    )
    print(f"Created deal: ${deal.value:,.2f}")
    
    # Log email
    automation.log_email(lead.id, "Introduction + Portfolio")
    
    # Update deal stage
    automation.update_deal_stage(deal.id, DealStage.QUALIFIED)
    
    # Generate proposal
    proposal = automation.generate_proposal(deal.id)
    print(f"Generated proposal: {proposal.id}")
    
    # Get pipeline summary
    summary = automation.get_pipeline_summary()
    print(f"\nPipeline Summary:")
    print(f"  Total Pipeline: ${summary['total_pipeline']:,.2f}")
    print(f"  Total Leads: {summary['total_leads']}")
