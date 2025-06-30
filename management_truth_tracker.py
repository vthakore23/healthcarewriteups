"""
Management Truth Tracker™ - Track and verify biotech executive promises
Provides accountability and credibility scoring for management teams
"""
import sqlite3
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from bs4 import BeautifulSoup
import hashlib
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


class PromiseStatus(Enum):
    """Status of a tracked promise"""
    PENDING = "pending"
    DELIVERED_ON_TIME = "delivered_on_time"
    DELIVERED_LATE = "delivered_late"
    FAILED = "failed"
    MODIFIED = "modified"
    IN_PROGRESS = "in_progress"
    UNCLEAR = "unclear"


class PromiseType(Enum):
    """Types of promises executives make"""
    CLINICAL_TIMELINE = "clinical_timeline"
    FDA_SUBMISSION = "fda_submission"
    DATA_READOUT = "data_readout"
    PARTNERSHIP = "partnership"
    REVENUE_GUIDANCE = "revenue_guidance"
    ENROLLMENT_COMPLETION = "enrollment_completion"
    MANUFACTURING = "manufacturing"
    REGULATORY_APPROVAL = "regulatory_approval"
    PRODUCT_LAUNCH = "product_launch"
    FINANCING = "financing"


@dataclass
class ExecutivePromise:
    """Represents a promise made by an executive"""
    promise_id: str
    company: str
    executive_name: str
    executive_title: str
    promise_text: str
    promise_type: PromiseType
    date_made: datetime
    deadline: Optional[datetime]
    source: str  # URL or document reference
    confidence_language: str  # "confident", "on track", "expect", etc.
    specific_metrics: Dict[str, any]  # Quantifiable targets
    status: PromiseStatus
    outcome_date: Optional[datetime]
    outcome_details: Optional[str]
    delay_days: Optional[int]
    credibility_impact: Optional[float]


class ManagementTruthTracker:
    """Track and analyze management promises vs. delivery"""
    
    def __init__(self, db_path: str = "management_promises.db"):
        self.db_path = db_path
        self._init_database()
        self.promise_patterns = self._init_promise_patterns()
        self.timeline_extractors = self._init_timeline_extractors()
        
    def _init_database(self):
        """Initialize SQLite database for promise tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main promises table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS promises (
                promise_id TEXT PRIMARY KEY,
                company TEXT NOT NULL,
                executive_name TEXT NOT NULL,
                executive_title TEXT NOT NULL,
                promise_text TEXT NOT NULL,
                promise_type TEXT NOT NULL,
                date_made TIMESTAMP NOT NULL,
                deadline TIMESTAMP,
                source TEXT NOT NULL,
                confidence_language TEXT,
                specific_metrics TEXT,
                status TEXT NOT NULL,
                outcome_date TIMESTAMP,
                outcome_details TEXT,
                delay_days INTEGER,
                credibility_impact REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Executive credibility scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executive_credibility (
                executive_id TEXT PRIMARY KEY,
                executive_name TEXT NOT NULL,
                company TEXT NOT NULL,
                current_title TEXT,
                total_promises INTEGER DEFAULT 0,
                delivered_on_time INTEGER DEFAULT 0,
                delivered_late INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                average_delay_days REAL,
                credibility_score REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Company credibility scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_credibility (
                company TEXT PRIMARY KEY,
                total_promises INTEGER DEFAULT 0,
                delivered_on_time INTEGER DEFAULT 0,
                delivered_late INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                average_delay_days REAL,
                credibility_score REAL,
                promise_types_accuracy TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Historical patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS promise_patterns (
                pattern_id TEXT PRIMARY KEY,
                promise_type TEXT NOT NULL,
                confidence_language TEXT,
                typical_delay_days REAL,
                success_rate REAL,
                sample_size INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _init_promise_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for detecting promises in text"""
        return {
            PromiseType.CLINICAL_TIMELINE: [
                r"expect(?:ed|ing)?\s+(?:to\s+)?(?:report|announce|release)\s+(?:topline\s+)?(?:data|results)\s+(?:in|by|during)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
                r"(?:trial|study)\s+(?:data|results)\s+(?:expected|anticipated)\s+(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
                r"(?:plan|planning|plans)\s+to\s+(?:report|announce)\s+(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
                r"(?:on\s+track|remains?\s+on\s+track)\s+(?:to|for)\s+(?:report|complete|deliver).*?(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
            ],
            PromiseType.FDA_SUBMISSION: [
                r"(?:plan|expect|anticipate)\s+to\s+(?:submit|file)\s+(?:the\s+)?(?:NDA|BLA|IND|510k|PMA).*?(?:in|by|during)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
                r"(?:NDA|BLA|IND|510k|PMA)\s+(?:submission|filing)\s+(?:expected|anticipated|planned)\s+(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
                r"targeting\s+(?:a|an)?\s*(?:NDA|BLA|IND|510k|PMA)\s+(?:submission|filing)\s+(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
            ],
            PromiseType.DATA_READOUT: [
                r"data\s+(?:readout|read-out)\s+(?:expected|anticipated)\s+(?:in|by|during)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
                r"expect\s+(?:the\s+)?data\s+(?:from|for).*?(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
                r"(?:topline|top-line)\s+(?:data|results)\s+(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
            ],
            PromiseType.ENROLLMENT_COMPLETION: [
                r"(?:enrollment|enrolment)\s+(?:expected|anticipated)\s+to\s+(?:complete|finish)\s+(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
                r"(?:complete|finish)\s+(?:enrollment|enrolment)\s+(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
                r"(?:on\s+track|targeting)\s+(?:to\s+)?(?:complete|finish)\s+(?:enrollment|enrolment).*?(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
            ],
            PromiseType.PRODUCT_LAUNCH: [
                r"(?:launch|commercial\s+launch)\s+(?:expected|anticipated|planned)\s+(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
                r"(?:plan|planning|expect)\s+to\s+launch.*?(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
                r"(?:targeting|target)\s+(?:a\s+)?(?:launch|commercial\s+launch)\s+(?:in|by)\s+([QH][1-4]\s+\d{4}|\w+\s+\d{4})",
            ]
        }
    
    def _init_timeline_extractors(self) -> Dict[str, callable]:
        """Initialize functions to extract timelines from different formats"""
        return {
            'quarter': self._extract_quarter_date,
            'month': self._extract_month_date,
            'half': self._extract_half_year_date,
            'specific': self._extract_specific_date
        }
    
    def _extract_quarter_date(self, text: str) -> Optional[datetime]:
        """Extract quarter-based dates (Q1 2024, etc.)"""
        pattern = r'[QH]([1-4])\s+(\d{4})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            quarter = int(match.group(1))
            year = int(match.group(2))
            # Return last day of quarter
            if quarter == 1:
                return datetime(year, 3, 31)
            elif quarter == 2:
                return datetime(year, 6, 30)
            elif quarter == 3:
                return datetime(year, 9, 30)
            elif quarter == 4:
                return datetime(year, 12, 31)
        return None
    
    def _extract_month_date(self, text: str) -> Optional[datetime]:
        """Extract month-based dates (June 2024, etc.)"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        pattern = r'(\w+)\s+(\d{4})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            month_str = match.group(1).lower()
            year = int(match.group(2))
            if month_str in months:
                # Return last day of month
                month = months[month_str]
                if month == 2:
                    day = 29 if year % 4 == 0 else 28
                elif month in [4, 6, 9, 11]:
                    day = 30
                else:
                    day = 31
                return datetime(year, month, day)
        return None
    
    def _extract_half_year_date(self, text: str) -> Optional[datetime]:
        """Extract half-year dates (H1 2024, first half 2024, etc.)"""
        pattern = r'(?:H([12])|(?:first|second)\s+half)\s+(?:of\s+)?(\d{4})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if match.group(1):
                half = int(match.group(1))
            else:
                half = 1 if 'first' in match.group(0).lower() else 2
            year = int(match.group(2))
            
            if half == 1:
                return datetime(year, 6, 30)
            else:
                return datetime(year, 12, 31)
        return None
    
    def _extract_specific_date(self, text: str) -> Optional[datetime]:
        """Extract specific dates in various formats"""
        patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if pattern.startswith(r'(\d{4})'):
                        year, month, day = map(int, match.groups())
                    else:
                        month, day, year = map(int, match.groups())
                    return datetime(year, month, day)
                except ValueError:
                    continue
        return None
    
    def extract_promise_from_text(self, text: str, company: str, executive_name: str, 
                                 executive_title: str, source: str, 
                                 date_made: datetime) -> List[ExecutivePromise]:
        """Extract promises from text (earnings call, PR, etc.)"""
        promises = []
        
        # Normalize text
        text = ' '.join(text.split())
        
        for promise_type, patterns in self.promise_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Extract the promise context (surrounding text)
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    promise_context = text[start:end]
                    
                    # Extract deadline
                    deadline = None
                    deadline_text = match.group(1) if match.groups() else None
                    if deadline_text:
                        # Try different extraction methods
                        for extractor in self.timeline_extractors.values():
                            deadline = extractor(deadline_text)
                            if deadline:
                                break
                    
                    # Extract confidence language
                    confidence_language = self._extract_confidence_language(promise_context)
                    
                    # Extract specific metrics
                    specific_metrics = self._extract_metrics(promise_context, promise_type)
                    
                    # Generate unique ID
                    promise_id = self._generate_promise_id(
                        company, executive_name, promise_type, date_made, promise_context
                    )
                    
                    promise = ExecutivePromise(
                        promise_id=promise_id,
                        company=company,
                        executive_name=executive_name,
                        executive_title=executive_title,
                        promise_text=promise_context.strip(),
                        promise_type=promise_type,
                        date_made=date_made,
                        deadline=deadline,
                        source=source,
                        confidence_language=confidence_language,
                        specific_metrics=specific_metrics,
                        status=PromiseStatus.PENDING,
                        outcome_date=None,
                        outcome_details=None,
                        delay_days=None,
                        credibility_impact=None
                    )
                    
                    promises.append(promise)
        
        return promises
    
    def _extract_confidence_language(self, text: str) -> str:
        """Extract confidence indicators from promise text"""
        confidence_patterns = {
            'very_confident': [
                r'highly\s+confident',
                r'very\s+confident',
                r'strong(?:ly)?\s+believe',
                r'definitely',
                r'certainly',
                r'without\s+question'
            ],
            'confident': [
                r'confident',
                r'on\s+track',
                r'progressing\s+well',
                r'expect\s+to\s+meet',
                r'remain\s+on\s+schedule'
            ],
            'moderate': [
                r'anticipate',
                r'expect',
                r'plan(?:ning)?',
                r'target(?:ing)?',
                r'aim(?:ing)?'
            ],
            'cautious': [
                r'hope',
                r'believe',
                r'think',
                r'if\s+everything\s+goes',
                r'assuming',
                r'provided'
            ],
            'hedged': [
                r'may\s+be\s+able',
                r'could\s+potentially',
                r'possible',
                r'exploring',
                r'evaluating'
            ]
        }
        
        text_lower = text.lower()
        
        for confidence_level, patterns in confidence_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return confidence_level
        
        return 'neutral'
    
    def _extract_metrics(self, text: str, promise_type: PromiseType) -> Dict[str, any]:
        """Extract quantifiable metrics from promise text"""
        metrics = {}
        
        # Extract percentages
        percent_pattern = r'(\d+(?:\.\d+)?)\s*%'
        percentages = re.findall(percent_pattern, text)
        if percentages:
            metrics['percentages'] = [float(p) for p in percentages]
        
        # Extract dollar amounts
        dollar_pattern = r'\$(\d+(?:\.\d+)?)\s*(million|billion|M|B)?'
        dollars = re.findall(dollar_pattern, text, re.IGNORECASE)
        if dollars:
            metrics['financial_figures'] = []
            for amount, unit in dollars:
                value = float(amount)
                if unit and unit.lower() in ['million', 'm']:
                    value *= 1_000_000
                elif unit and unit.lower() in ['billion', 'b']:
                    value *= 1_000_000_000
                metrics['financial_figures'].append(value)
        
        # Extract patient numbers
        patient_pattern = r'(\d+)\s*(?:patient|subject|participant)s?'
        patients = re.findall(patient_pattern, text, re.IGNORECASE)
        if patients:
            metrics['patient_numbers'] = [int(p) for p in patients]
        
        # Extract trial sites
        site_pattern = r'(\d+)\s*(?:site|center|location)s?'
        sites = re.findall(site_pattern, text, re.IGNORECASE)
        if sites:
            metrics['trial_sites'] = [int(s) for s in sites]
        
        # Promise-type specific metrics
        if promise_type == PromiseType.ENROLLMENT_COMPLETION:
            # Extract enrollment targets
            enrollment_pattern = r'(?:enroll|recruit)\s*(\d+)'
            enrollment = re.search(enrollment_pattern, text, re.IGNORECASE)
            if enrollment:
                metrics['enrollment_target'] = int(enrollment.group(1))
        
        return metrics
    
    def _generate_promise_id(self, company: str, executive: str, 
                           promise_type: PromiseType, date: datetime, 
                           text: str) -> str:
        """Generate unique ID for a promise"""
        content = f"{company}_{executive}_{promise_type.value}_{date.isoformat()}_{text[:50]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def save_promise(self, promise: ExecutivePromise) -> bool:
        """Save a promise to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO promises (
                    promise_id, company, executive_name, executive_title,
                    promise_text, promise_type, date_made, deadline,
                    source, confidence_language, specific_metrics,
                    status, outcome_date, outcome_details, delay_days,
                    credibility_impact, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                promise.promise_id, promise.company, promise.executive_name,
                promise.executive_title, promise.promise_text, promise.promise_type.value,
                promise.date_made, promise.deadline, promise.source,
                promise.confidence_language, json.dumps(promise.specific_metrics),
                promise.status.value, promise.outcome_date, promise.outcome_details,
                promise.delay_days, promise.credibility_impact
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving promise: {e}")
            return False
        finally:
            conn.close()
    
    def update_promise_outcome(self, promise_id: str, status: PromiseStatus,
                             outcome_date: datetime, outcome_details: str) -> bool:
        """Update the outcome of a promise"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get the original promise
            cursor.execute("""
                SELECT deadline, date_made FROM promises WHERE promise_id = ?
            """, (promise_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            deadline, date_made = result
            
            # Calculate delay
            delay_days = None
            if deadline and status in [PromiseStatus.DELIVERED_ON_TIME, 
                                      PromiseStatus.DELIVERED_LATE]:
                deadline_dt = datetime.fromisoformat(deadline)
                delay_days = (outcome_date - deadline_dt).days
                
                # Update status based on delay
                if delay_days <= 0:
                    status = PromiseStatus.DELIVERED_ON_TIME
                else:
                    status = PromiseStatus.DELIVERED_LATE
            
            # Calculate credibility impact
            credibility_impact = self._calculate_credibility_impact(
                status, delay_days
            )
            
            # Update the promise
            cursor.execute("""
                UPDATE promises SET
                    status = ?, outcome_date = ?, outcome_details = ?,
                    delay_days = ?, credibility_impact = ?, updated_at = CURRENT_TIMESTAMP
                WHERE promise_id = ?
            """, (
                status.value, outcome_date, outcome_details,
                delay_days, credibility_impact, promise_id
            ))
            
            conn.commit()
            
            # Update executive and company credibility scores
            self._update_credibility_scores(promise_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating promise outcome: {e}")
            return False
        finally:
            conn.close()
    
    def _calculate_credibility_impact(self, status: PromiseStatus, 
                                    delay_days: Optional[int]) -> float:
        """Calculate impact on credibility score"""
        if status == PromiseStatus.DELIVERED_ON_TIME:
            return 1.0
        elif status == PromiseStatus.DELIVERED_LATE:
            if delay_days:
                # Penalize more for longer delays
                if delay_days <= 30:
                    return 0.8
                elif delay_days <= 90:
                    return 0.6
                elif delay_days <= 180:
                    return 0.4
                else:
                    return 0.2
            return 0.5
        elif status == PromiseStatus.FAILED:
            return 0.0
        elif status == PromiseStatus.MODIFIED:
            return 0.3
        else:
            return 0.5
    
    def _update_credibility_scores(self, promise_id: str):
        """Update executive and company credibility scores"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get promise details
            cursor.execute("""
                SELECT company, executive_name, status, delay_days
                FROM promises WHERE promise_id = ?
            """, (promise_id,))
            
            result = cursor.fetchone()
            if not result:
                return
            
            company, executive_name, status, delay_days = result
            
            # Update executive credibility
            self._update_executive_credibility(cursor, executive_name, company)
            
            # Update company credibility
            self._update_company_credibility(cursor, company)
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error updating credibility scores: {e}")
        finally:
            conn.close()
    
    def _update_executive_credibility(self, cursor, executive_name: str, company: str):
        """Update credibility score for an executive"""
        # Get executive stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'delivered_on_time' THEN 1 ELSE 0 END) as on_time,
                SUM(CASE WHEN status = 'delivered_late' THEN 1 ELSE 0 END) as late,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(CASE WHEN delay_days IS NOT NULL THEN delay_days ELSE 0 END) as avg_delay
            FROM promises
            WHERE executive_name = ? AND company = ?
            AND status IN ('delivered_on_time', 'delivered_late', 'failed')
        """, (executive_name, company))
        
        stats = cursor.fetchone()
        if stats and stats[0] > 0:  # Has completed promises
            total, on_time, late, failed, avg_delay = stats
            
            # Calculate credibility score (weighted average)
            score = (on_time * 1.0 + late * 0.5 + failed * 0.0) / total
            
            # Generate executive ID
            exec_id = hashlib.md5(f"{executive_name}_{company}".encode()).hexdigest()
            
            cursor.execute("""
                INSERT OR REPLACE INTO executive_credibility (
                    executive_id, executive_name, company, total_promises,
                    delivered_on_time, delivered_late, failed,
                    average_delay_days, credibility_score, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                exec_id, executive_name, company, total,
                on_time, late, failed, avg_delay or 0, score
            ))
    
    def _update_company_credibility(self, cursor, company: str):
        """Update credibility score for a company"""
        # Get company stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'delivered_on_time' THEN 1 ELSE 0 END) as on_time,
                SUM(CASE WHEN status = 'delivered_late' THEN 1 ELSE 0 END) as late,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(CASE WHEN delay_days IS NOT NULL THEN delay_days ELSE 0 END) as avg_delay
            FROM promises
            WHERE company = ?
            AND status IN ('delivered_on_time', 'delivered_late', 'failed')
        """, (company,))
        
        stats = cursor.fetchone()
        if stats and stats[0] > 0:  # Has completed promises
            total, on_time, late, failed, avg_delay = stats
            
            # Calculate credibility score
            score = (on_time * 1.0 + late * 0.5 + failed * 0.0) / total
            
            # Get promise type accuracy
            cursor.execute("""
                SELECT promise_type, 
                       COUNT(*) as total,
                       SUM(CASE WHEN status = 'delivered_on_time' THEN 1 ELSE 0 END) as success
                FROM promises
                WHERE company = ? AND status IN ('delivered_on_time', 'delivered_late', 'failed')
                GROUP BY promise_type
            """, (company,))
            
            type_accuracy = {}
            for row in cursor.fetchall():
                ptype, total_type, success = row
                type_accuracy[ptype] = success / total_type if total_type > 0 else 0
            
            cursor.execute("""
                INSERT OR REPLACE INTO company_credibility (
                    company, total_promises, delivered_on_time, delivered_late,
                    failed, average_delay_days, credibility_score,
                    promise_types_accuracy, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                company, total, on_time, late, failed,
                avg_delay or 0, score, json.dumps(type_accuracy)
            ))
    
    def get_executive_credibility(self, executive_name: str, 
                                company: str) -> Dict:
        """Get credibility score and history for an executive"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            exec_id = hashlib.md5(f"{executive_name}_{company}".encode()).hexdigest()
            
            # First check if we have this executive in the credibility table
            cursor.execute("""
                SELECT * FROM executive_credibility WHERE executive_id = ?
            """, (exec_id,))
            
            result = cursor.fetchone()
            if result:
                cols = [desc[0] for desc in cursor.description]
                credibility_data = dict(zip(cols, result))
            else:
                # If not in credibility table, calculate from promises
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'delivered_on_time' THEN 1 ELSE 0 END) as on_time,
                        SUM(CASE WHEN status = 'delivered_late' THEN 1 ELSE 0 END) as late,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                        AVG(CASE WHEN delay_days IS NOT NULL THEN delay_days ELSE 0 END) as avg_delay
                    FROM promises
                    WHERE executive_name = ? AND company LIKE ?
                """, (executive_name, f"%{company}%"))
                
                stats = cursor.fetchone()
                if stats:
                    total, on_time, late, failed, avg_delay = stats
                    score = (on_time * 1.0 + late * 0.5 + failed * 0.0) / total if total > 0 else 0
                    
                    credibility_data = {
                        'executive_id': exec_id,
                        'executive_name': executive_name,
                        'company': company,
                        'total_promises': total or 0,
                        'delivered_on_time': on_time or 0,
                        'delivered_late': late or 0,
                        'failed': failed or 0,
                        'average_delay_days': avg_delay or 0,
                        'credibility_score': score
                    }
                else:
                    # No data at all
                    credibility_data = {
                        'executive_id': exec_id,
                        'executive_name': executive_name,
                        'company': company,
                        'total_promises': 0,
                        'delivered_on_time': 0,
                        'delivered_late': 0,
                        'failed': 0,
                        'average_delay_days': 0,
                        'credibility_score': 0
                    }
            
            # Ensure all fields are present
            required_fields = ['delivered_on_time', 'delivered_late', 'failed', 
                             'total_promises', 'average_delay_days', 'credibility_score']
            for field in required_fields:
                if field not in credibility_data:
                    credibility_data[field] = 0
            
            # Add aliases for backward compatibility
            credibility_data['delivered'] = credibility_data['delivered_on_time']
            credibility_data['pending'] = credibility_data['total_promises'] - (
                credibility_data['delivered_on_time'] + 
                credibility_data['delivered_late'] + 
                credibility_data['failed']
            )
            
            return credibility_data
            
        except Exception as e:
            logger.error(f"Error getting executive credibility: {e}")
            # Return default structure on error
            return {
                'executive_id': hashlib.md5(f"{executive_name}_{company}".encode()).hexdigest(),
                'executive_name': executive_name,
                'company': company,
                'total_promises': 0,
                'delivered': 0,
                'delivered_on_time': 0,
                'delivered_late': 0,
                'failed': 0,
                'pending': 0,
                'average_delay_days': 0,
                'credibility_score': 0
            }
        finally:
            conn.close()
    
    def get_company_credibility(self, company: str) -> Dict:
        """Get credibility score and history for a company"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # First check if we have this company in the credibility table
            cursor.execute("""
                SELECT * FROM company_credibility WHERE company = ?
            """, (company,))
            
            result = cursor.fetchone()
            if result:
                cols = [desc[0] for desc in cursor.description]
                data = dict(zip(cols, result))
                # Parse JSON fields
                if data.get('promise_types_accuracy'):
                    data['promise_types_accuracy'] = json.loads(data['promise_types_accuracy'])
                else:
                    data['promise_types_accuracy'] = {}
            else:
                # Calculate from promises
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'delivered_on_time' THEN 1 ELSE 0 END) as on_time,
                        SUM(CASE WHEN status = 'delivered_late' THEN 1 ELSE 0 END) as late,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                        AVG(CASE WHEN delay_days IS NOT NULL THEN delay_days ELSE 0 END) as avg_delay,
                        COUNT(DISTINCT executive_name) as total_executives
                    FROM promises
                    WHERE company = ?
                """, (company,))
                
                stats = cursor.fetchone()
                if stats:
                    total, on_time, late, failed, avg_delay, total_executives = stats
                    score = (on_time * 1.0 + late * 0.5 + failed * 0.0) / total if total > 0 else 0
                    
                    # Get promise type breakdown
                    cursor.execute("""
                        SELECT promise_type, 
                               COUNT(*) as total,
                               SUM(CASE WHEN status = 'delivered_on_time' THEN 1 ELSE 0 END) as success
                        FROM promises
                        WHERE company = ? AND status IN ('delivered_on_time', 'delivered_late', 'failed')
                        GROUP BY promise_type
                    """, (company,))
                    
                    type_accuracy = {}
                    for row in cursor.fetchall():
                        ptype, total_type, success = row
                        type_accuracy[ptype] = {
                            'total': total_type,
                            'success_rate': success / total_type if total_type > 0 else 0
                        }
                    
                    data = {
                        'company': company,
                        'total_promises': total or 0,
                        'delivered_on_time': on_time or 0,
                        'delivered_late': late or 0,
                        'failed': failed or 0,
                        'average_delay_days': avg_delay or 0,
                        'credibility_score': score,
                        'total_executives': total_executives or 0,
                        'promise_types_accuracy': type_accuracy,
                        'overall_credibility': score
                    }
                else:
                    # No data
                    data = {
                        'company': company,
                        'total_promises': 0,
                        'delivered_on_time': 0,
                        'delivered_late': 0,
                        'failed': 0,
                        'average_delay_days': 0,
                        'credibility_score': 0,
                        'total_executives': 0,
                        'promise_types_accuracy': {},
                        'overall_credibility': 0
                    }
            
            # Ensure we have the right structure
            if 'overall_credibility' not in data:
                data['overall_credibility'] = data.get('credibility_score', 0)
            if 'total_executives' not in data:
                data['total_executives'] = 0
            if 'by_promise_type' not in data and 'promise_types_accuracy' in data:
                data['by_promise_type'] = data['promise_types_accuracy']
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting company credibility: {e}")
            # Return default structure
            return {
                'company': company,
                'total_promises': 0,
                'delivered_on_time': 0,
                'delivered_late': 0,
                'failed': 0,
                'average_delay_days': 0,
                'credibility_score': 0,
                'overall_credibility': 0,
                'total_executives': 0,
                'promise_types_accuracy': {},
                'by_promise_type': {}
            }
        finally:
            conn.close()
    
    def analyze_promise_language(self, text: str) -> Dict[str, any]:
        """Analyze the language used in a promise for red flags"""
        analysis = {
            'red_flags': [],
            'positive_signals': [],
            'confidence_score': 0.5,
            'hedging_score': 0.0,
            'specificity_score': 0.0
        }
        
        text_lower = text.lower()
        
        # Red flag phrases
        red_flags = {
            'vague_timeline': [
                'in due course', 'when appropriate', 'at the right time',
                'as soon as possible', 'in the near future', 'eventually'
            ],
            'heavy_hedging': [
                'we hope to', 'we may be able to', 'it\'s possible that',
                'depending on', 'if everything goes', 'assuming'
            ],
            'qualification': [
                'subject to', 'provided that', 'unless', 'except',
                'barring any', 'contingent upon'
            ],
            'uncertainty': [
                'we believe', 'we think', 'in our opinion', 'we estimate',
                'approximately', 'roughly'
            ]
        }
        
        # Positive signal phrases
        positive_signals = {
            'strong_commitment': [
                'we will', 'we are committed', 'definitely', 'certainly',
                'without question', 'guaranteed'
            ],
            'specific_timeline': [
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # Specific dates
                r'\b[QH][1-4]\s+\d{4}\b',  # Specific quarters
                r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b'
            ],
            'quantifiable_metrics': [
                r'\b\d+\s*(?:patients?|subjects?)\b',
                r'\b\d+\s*(?:sites?|centers?)\b',
                r'\$\d+(?:\.\d+)?\s*(?:million|billion)\b',
                r'\b\d+(?:\.\d+)?%\b'
            ],
            'track_record_reference': [
                'as we have done', 'similar to our previous', 'track record',
                'historically', 'consistently delivered'
            ]
        }
        
        # Check for red flags
        for flag_type, phrases in red_flags.items():
            for phrase in phrases:
                if phrase in text_lower:
                    analysis['red_flags'].append(f"{flag_type}: '{phrase}'")
                    analysis['hedging_score'] += 0.1
        
        # Check for positive signals
        for signal_type, patterns in positive_signals.items():
            for pattern in patterns:
                if signal_type == 'strong_commitment':
                    if pattern in text_lower:
                        analysis['positive_signals'].append(f"{signal_type}: '{pattern}'")
                        analysis['confidence_score'] += 0.1
                else:
                    if re.search(pattern, text_lower):
                        analysis['positive_signals'].append(signal_type)
                        analysis['specificity_score'] += 0.1
        
        # Cap scores at 1.0
        analysis['confidence_score'] = min(1.0, analysis['confidence_score'])
        analysis['hedging_score'] = min(1.0, analysis['hedging_score'])
        analysis['specificity_score'] = min(1.0, analysis['specificity_score'])
        
        # Overall assessment
        if analysis['hedging_score'] > 0.5:
            analysis['overall_assessment'] = 'High Risk - Heavy hedging detected'
        elif analysis['specificity_score'] < 0.2:
            analysis['overall_assessment'] = 'Medium Risk - Lacks specific details'
        elif analysis['confidence_score'] > 0.7 and analysis['specificity_score'] > 0.5:
            analysis['overall_assessment'] = 'Low Risk - Strong commitment with specifics'
        else:
            analysis['overall_assessment'] = 'Medium Risk - Mixed signals'
        
        return analysis
    
    def generate_credibility_report(self, company: str) -> Dict[str, any]:
        """Generate comprehensive credibility report for a company"""
        report = {
            'company': company,
            'generated_at': datetime.now().isoformat(),
            'company_credibility': self.get_company_credibility(company),
            'executives': {},
            'recent_promises': [],
            'promise_patterns': {},
            'recommendations': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all executives for the company
            cursor.execute("""
                SELECT DISTINCT executive_name, executive_title
                FROM promises WHERE company = ?
            """, (company,))
            
            for exec_name, exec_title in cursor.fetchall():
                exec_cred = self.get_executive_credibility(exec_name, company)
                if exec_cred:
                    report['executives'][exec_name] = {
                        'title': exec_title,
                        'credibility': exec_cred
                    }
            
            # Get recent promises
            cursor.execute("""
                SELECT * FROM promises 
                WHERE company = ? 
                ORDER BY date_made DESC 
                LIMIT 10
            """, (company,))
            
            cols = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                promise_dict = dict(zip(cols, row))
                if promise_dict.get('specific_metrics'):
                    promise_dict['specific_metrics'] = json.loads(promise_dict['specific_metrics'])
                report['recent_promises'].append(promise_dict)
            
            # Analyze promise patterns
            cursor.execute("""
                SELECT promise_type, 
                       COUNT(*) as total,
                       AVG(CASE WHEN delay_days IS NOT NULL THEN delay_days ELSE 0 END) as avg_delay,
                       SUM(CASE WHEN status = 'delivered_on_time' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate
                FROM promises
                WHERE company = ? AND status IN ('delivered_on_time', 'delivered_late', 'failed')
                GROUP BY promise_type
            """, (company,))
            
            for ptype, total, avg_delay, success_rate in cursor.fetchall():
                report['promise_patterns'][ptype] = {
                    'total_promises': total,
                    'average_delay_days': avg_delay,
                    'success_rate': success_rate
                }
            
            # Generate recommendations
            if report['company_credibility']:
                score = report['company_credibility']['credibility_score']
                avg_delay = report['company_credibility']['average_delay_days']
                
                if score < 0.5:
                    report['recommendations'].append(
                        "⚠️ HIGH RISK: Company has poor track record of meeting promises. "
                        "Apply significant discount to timeline guidance."
                    )
                elif score < 0.7:
                    report['recommendations'].append(
                        "⚠️ MEDIUM RISK: Company occasionally misses deadlines. "
                        f"Add {int(avg_delay)} days buffer to timeline expectations."
                    )
                else:
                    report['recommendations'].append(
                        "✅ LOW RISK: Company has strong track record of delivery. "
                        "Timeline guidance likely reliable."
                    )
                
                # Promise type specific recommendations
                for ptype, stats in report['promise_patterns'].items():
                    if stats['success_rate'] < 0.5:
                        report['recommendations'].append(
                            f"🚨 Be especially cautious with {ptype} promises - "
                            f"only {stats['success_rate']*100:.0f}% success rate"
                        )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating credibility report: {e}")
            return report
        finally:
            conn.close()
    
    def track_promise(self, executive_name: str, executive_title: str,
                     company_name: str, promise_text: str,
                     promise_type: PromiseType, promise_date: datetime,
                     deadline_date: Optional[datetime], source_url: str,
                     confidence_language: str) -> str:
        """Convenience method to create and save a promise"""
        # Generate promise ID
        promise_id = self._generate_promise_id(
            company_name, executive_name, promise_type, promise_date, promise_text
        )
        
        # Create promise object
        promise = ExecutivePromise(
            promise_id=promise_id,
            company=company_name,
            executive_name=executive_name,
            executive_title=executive_title,
            promise_text=promise_text,
            promise_type=promise_type,
            date_made=promise_date,
            deadline=deadline_date,
            source=source_url,
            confidence_language=confidence_language,
            specific_metrics={},
            status=PromiseStatus.PENDING,
            outcome_date=None,
            outcome_details=None,
            delay_days=None,
            credibility_impact=None
        )
        
        # Save to database
        self.save_promise(promise)
        
        return promise_id
    
    def update_promise_status(self, promise_id: str, status: PromiseStatus,
                            outcome_date: datetime, outcome_details: str) -> bool:
        """Convenience method to update promise status"""
        return self.update_promise_outcome(promise_id, status, outcome_date, outcome_details)
    
    def check_promises_due(self, days_ahead: int = 30) -> List[Dict]:
        """Check for promises coming due in the next N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            deadline_date = datetime.now() + timedelta(days=days_ahead)
            
            cursor.execute("""
                SELECT * FROM promises
                WHERE status = 'pending'
                AND deadline IS NOT NULL
                AND deadline <= ?
                ORDER BY deadline ASC
            """, (deadline_date,))
            
            cols = [desc[0] for desc in cursor.description]
            promises_due = []
            
            for row in cursor.fetchall():
                promise_dict = dict(zip(cols, row))
                if promise_dict.get('specific_metrics'):
                    promise_dict['specific_metrics'] = json.loads(promise_dict['specific_metrics'])
                
                # Add days until deadline
                if promise_dict['deadline']:
                    deadline_dt = datetime.fromisoformat(promise_dict['deadline'])
                    promise_dict['days_until_deadline'] = (deadline_dt - datetime.now()).days
                
                promises_due.append(promise_dict)
            
            return promises_due
            
        except Exception as e:
            logger.error(f"Error checking promises due: {e}")
            return []
        finally:
            conn.close()
    
    def get_executive_promise_details(self, executive_name: str, company: str) -> Dict:
        """Get detailed promise history for an executive including failures"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all promises for this executive - use LIKE for flexible company matching
            cursor.execute("""
                SELECT promise_id, promise_text, promise_type, date_made, deadline,
                       source, confidence_language, status, outcome_date, 
                       outcome_details, delay_days, specific_metrics, company
                FROM promises
                WHERE executive_name = ? AND company LIKE ?
                ORDER BY date_made DESC
            """, (executive_name, f"%{company}%"))
            
            cols = [desc[0] for desc in cursor.description]
            promises = []
            
            for row in cursor.fetchall():
                promise_dict = dict(zip(cols, row))
                
                # Parse JSON fields
                if promise_dict.get('specific_metrics'):
                    try:
                        promise_dict['specific_metrics'] = json.loads(promise_dict['specific_metrics'])
                    except:
                        promise_dict['specific_metrics'] = {}
                
                # Add human-readable status
                if promise_dict['status'] == 'failed':
                    promise_dict['status_display'] = '❌ FAILED'
                elif promise_dict['status'] == 'delivered_late':
                    promise_dict['status_display'] = f'⚠️ LATE ({promise_dict.get("delay_days", 0)} days)'
                elif promise_dict['status'] == 'delivered_on_time':
                    promise_dict['status_display'] = '✅ DELIVERED'
                elif promise_dict['status'] == 'pending':
                    if promise_dict['deadline']:
                        deadline_dt = datetime.fromisoformat(promise_dict['deadline'])
                        days_left = (deadline_dt - datetime.now()).days
                        if days_left < 0:
                            promise_dict['status_display'] = f'⏰ OVERDUE ({abs(days_left)} days)'
                        else:
                            promise_dict['status_display'] = f'⏳ PENDING ({days_left} days left)'
                    else:
                        promise_dict['status_display'] = '⏳ PENDING'
                else:
                    promise_dict['status_display'] = promise_dict['status'].upper()
                
                promises.append(promise_dict)
            
            # Get credibility summary - use actual company from first promise if available
            actual_company = promises[0]['company'] if promises else company
            credibility = self.get_executive_credibility(executive_name, actual_company)
            
            # Categorize promises
            failed_promises = [p for p in promises if p['status'] == 'failed']
            late_promises = [p for p in promises if p['status'] == 'delivered_late']
            on_time_promises = [p for p in promises if p['status'] == 'delivered_on_time']
            pending_promises = [p for p in promises if p['status'] == 'pending']
            
            return {
                'executive_name': executive_name,
                'company': company,
                'credibility_summary': credibility,
                'total_promises': len(promises),
                'all_promises': promises,
                'failed_promises': failed_promises,
                'late_promises': late_promises,
                'on_time_promises': on_time_promises,
                'pending_promises': pending_promises,
                'failure_rate': len(failed_promises) / len(promises) if promises else 0,
                'late_rate': len(late_promises) / len(promises) if promises else 0,
                'on_time_rate': len(on_time_promises) / len(promises) if promises else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting executive promise details: {e}")
            return {
                'executive_name': executive_name,
                'company': company,
                'error': str(e),
                'all_promises': []
            }
        finally:
            conn.close()
    
    def generate_executive_accountability_report(self, executive_name: str, company: str) -> str:
        """Generate a detailed accountability report for an executive"""
        details = self.get_executive_promise_details(executive_name, company)
        
        if details.get('error'):
            return f"Error generating report: {details['error']}"
        
        report = []
        report.append(f"🔍 EXECUTIVE ACCOUNTABILITY REPORT")
        report.append(f"{'='*60}")
        report.append(f"Executive: {executive_name}")
        report.append(f"Company: {company}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")
        
        # Credibility summary
        cred = details['credibility_summary']
        report.append(f"📊 CREDIBILITY SCORE: {cred['credibility_score']:.1%}")
        report.append(f"Total Promises Tracked: {details['total_promises']}")
        report.append(f"  • ✅ Delivered on time: {len(details['on_time_promises'])}")
        report.append(f"  • ⚠️  Delivered late: {len(details['late_promises'])}")
        report.append(f"  • ❌ Failed: {len(details['failed_promises'])}")
        report.append(f"  • ⏳ Pending: {len(details['pending_promises'])}")
        
        if cred.get('average_delay_days', 0) > 0:
            report.append(f"Average Delay: {cred['average_delay_days']:.1f} days")
        
        # Red flags
        if cred['credibility_score'] < 0.5:
            report.append("")
            report.append("🚨 RED FLAGS:")
            report.append(f"  • Low credibility score ({cred['credibility_score']:.1%})")
            if len(details['failed_promises']) > len(details['on_time_promises']):
                report.append("  • More failures than successes")
            if cred.get('average_delay_days', 0) > 60:
                report.append(f"  • Chronic delays (avg {cred['average_delay_days']:.0f} days)")
        
        # Failed promises detail
        if details['failed_promises']:
            report.append("")
            report.append(f"❌ FAILED PROMISES ({len(details['failed_promises'])})")
            report.append("-" * 60)
            
            for promise in details['failed_promises'][:10]:  # Show up to 10
                report.append("")
                report.append(f"Date: {promise['date_made'][:10]}")
                report.append(f"Type: {promise['promise_type']}")
                report.append(f"Promise: {promise['promise_text'][:200]}...")
                if promise['deadline']:
                    report.append(f"Deadline: {promise['deadline'][:10]}")
                if promise['outcome_details']:
                    report.append(f"Outcome: {promise['outcome_details']}")
                report.append(f"Confidence: {promise['confidence_language']}")
                report.append(f"Source: {promise['source']}")
        
        # Late deliveries
        if details['late_promises']:
            report.append("")
            report.append(f"⚠️  LATE DELIVERIES ({len(details['late_promises'])})")
            report.append("-" * 60)
            
            for promise in details['late_promises'][:5]:  # Show up to 5
                report.append("")
                report.append(f"Date: {promise['date_made'][:10]}")
                report.append(f"Type: {promise['promise_type']}")
                report.append(f"Promise: {promise['promise_text'][:150]}...")
                report.append(f"Delay: {promise['delay_days']} days")
        
        # Pending promises at risk
        overdue_pending = [p for p in details['pending_promises'] 
                          if 'OVERDUE' in p.get('status_display', '')]
        if overdue_pending:
            report.append("")
            report.append(f"⏰ OVERDUE PROMISES ({len(overdue_pending)})")
            report.append("-" * 60)
            
            for promise in overdue_pending[:5]:
                report.append("")
                report.append(f"Type: {promise['promise_type']}")
                report.append(f"Promise: {promise['promise_text'][:150]}...")
                report.append(f"Status: {promise['status_display']}")
        
        # Recommendation
        report.append("")
        report.append("💡 INVESTMENT RECOMMENDATION:")
        if cred['credibility_score'] >= 0.8:
            report.append("✅ HIGH CREDIBILITY - Timeline guidance likely reliable")
        elif cred['credibility_score'] >= 0.6:
            report.append("⚠️  MODERATE CREDIBILITY - Add buffer to timeline expectations")
        else:
            report.append("🚨 LOW CREDIBILITY - Significant risk of delays/failures")
            report.append("   Consider reducing position ahead of key deadlines")
        
        return "\n".join(report)

    def search_executives(self, query: str) -> List[Dict]:
        """Search for executives or companies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            results = []
            query_lower = query.lower()
            
            # Search companies
            cursor.execute("""
                SELECT DISTINCT company
                FROM promises
                WHERE LOWER(company) LIKE ?
                LIMIT 10
            """, (f'%{query_lower}%',))
            
            for row in cursor.fetchall():
                results.append({
                    'type': 'company',
                    'name': row[0],
                    'display': f"{row[0]} (Company)"
                })
            
            # Search executives
            cursor.execute("""
                SELECT DISTINCT executive_name, company, executive_title
                FROM promises
                WHERE LOWER(executive_name) LIKE ?
                LIMIT 10
            """, (f'%{query_lower}%',))
            
            for row in cursor.fetchall():
                results.append({
                    'type': 'executive',
                    'name': row[0],
                    'company': row[1],
                    'title': row[2],
                    'display': f"{row[0]} - {row[2]} at {row[1]}"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching executives: {e}")
            return []
        finally:
            conn.close()
    
    def analyze_company_credibility(self, ticker: str) -> Dict:
        """Alias for get_company_credibility to match the web interface"""
        return self.get_company_credibility(ticker)

# Create a global instance for easy access
truth_tracker = ManagementTruthTracker() 