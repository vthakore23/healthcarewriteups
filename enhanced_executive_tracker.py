#!/usr/bin/env python3
"""
Enhanced Executive Truth Tracker
Automatically tracks promises from ANY executive at ANY company
Extracts and monitors promises from earnings calls, press releases, and more
"""
import sys
import os
from datetime import datetime, timedelta
import sqlite3
import json
import re
import hashlib
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass, asdict
from enum import Enum

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from management_truth_tracker import (
    ManagementTruthTracker, ExecutivePromise, PromiseStatus, PromiseType
)


class EnhancedExecutiveTracker(ManagementTruthTracker):
    """Enhanced tracker that automatically handles any executive"""
    
    def __init__(self, db_path: str = "management_promises.db"):
        super().__init__(db_path)
        self._init_enhanced_tables()
        self._init_industry_patterns()
        
    def _init_enhanced_tables(self):
        """Initialize enhanced database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add table for tracking unknown executives
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executive_discovery (
                executive_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                company TEXT NOT NULL,
                title TEXT,
                first_seen DATE,
                last_seen DATE,
                data_sources TEXT,
                aliases TEXT,
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add table for tracking company aliases and variations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_aliases (
                alias TEXT PRIMARY KEY,
                canonical_name TEXT NOT NULL,
                ticker TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add table for tracking promise patterns by industry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS industry_promise_patterns (
                pattern_id TEXT PRIMARY KEY,
                industry TEXT NOT NULL,
                pattern_regex TEXT NOT NULL,
                promise_type TEXT NOT NULL,
                confidence REAL,
                examples TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _init_industry_patterns(self):
        """Initialize industry-specific promise patterns"""
        self.industry_patterns = {
            'biotech': {
                'trial_results': [
                    r"(?:topline|primary endpoint|data) results? (?:expected|anticipated) (?:in|by) ([QH][1-4] \d{4}|\w+ \d{4})",
                    r"(?:phase \d|pivotal) (?:trial|study) (?:to )?(?:read out|complete) (?:in|by) ([QH][1-4] \d{4}|\w+ \d{4})",
                ],
                'regulatory': [
                    r"(?:FDA|EMA) (?:submission|filing|approval) (?:expected|targeted) (?:in|by) ([QH][1-4] \d{4}|\w+ \d{4})",
                    r"PDUFA date (?:set for|of) (\w+ \d+, \d{4})",
                ],
                'partnership': [
                    r"(?:partnership|collaboration|licensing) (?:deal|agreement) (?:expected|anticipated) (?:in|by) ([QH][1-4] \d{4}|\w+ \d{4})",
                ]
            },
            'pharma': {
                'launch': [
                    r"(?:commercial )?launch (?:planned|expected|targeted) (?:for|in) ([QH][1-4] \d{4}|\w+ \d{4})",
                    r"(?:market entry|commercialization) (?:in|by) ([QH][1-4] \d{4}|\w+ \d{4})",
                ],
                'sales': [
                    r"(?:peak sales|revenue) (?:of|reaching) \$?([\d.]+) (?:billion|million)",
                    r"(?:guidance|forecast) (?:of|for) \$?([\d.]+) (?:billion|million)",
                ]
            },
            'medtech': {
                'approval': [
                    r"510\(k\) (?:clearance|approval) (?:expected|anticipated) (?:in|by) ([QH][1-4] \d{4}|\w+ \d{4})",
                    r"CE mark (?:expected|anticipated) (?:in|by) ([QH][1-4] \d{4}|\w+ \d{4})",
                ],
                'product': [
                    r"(?:product|device) launch (?:planned|expected) (?:in|by) ([QH][1-4] \d{4}|\w+ \d{4})",
                ]
            }
        }
    
    def discover_executive(self, text: str, source: str = None) -> List[Dict[str, str]]:
        """Automatically discover executive information from text"""
        executives = []
        
        # Patterns to identify executives speaking
        exec_patterns = [
            # "John Smith, CEO:" format
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+),\s*(?:Chief\s+)?(\w+(?:\s+\w+)?)\s*(?:Officer|President|Director|VP|Executive|Head)(?:\s+(?:of|&)\s+\w+)?:?",
            # "Dr. Jane Doe, Chief Medical Officer" format
            r"(?:Dr\.|Mr\.|Ms\.|Mrs\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+),\s*(?:Chief\s+)?(\w+(?:\s+\w+)?)\s*(?:Officer|President|Director|VP|Executive|Head)",
            # Conference call operator introductions
            r"(?:turn the call over to|introduce|joined by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+),\s*(?:the\s+)?(?:company's?\s+)?(\w+(?:\s+\w+)?)\s*(?:Officer|President|Director|VP|Executive|Head)",
        ]
        
        for pattern in exec_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1).strip()
                title = match.group(2).strip()
                
                # Normalize the title
                title = self._normalize_title(title)
                
                executives.append({
                    'name': name,
                    'title': title,
                    'source': source or 'Unknown',
                    'context': text[max(0, match.start()-50):min(len(text), match.end()+50)]
                })
        
        return executives
    
    def _normalize_title(self, title: str) -> str:
        """Normalize executive titles to standard forms"""
        title_mappings = {
            'ceo': 'Chief Executive Officer',
            'cfo': 'Chief Financial Officer',
            'coo': 'Chief Operating Officer',
            'cto': 'Chief Technology Officer',
            'cmo': 'Chief Medical Officer',
            'cso': 'Chief Scientific Officer',
            'president': 'President',
            'vp': 'Vice President',
            'evp': 'Executive Vice President',
            'svp': 'Senior Vice President',
        }
        
        title_lower = title.lower()
        for abbrev, full in title_mappings.items():
            if abbrev in title_lower:
                return full
        
        return title
    
    def auto_track_promise(self, text: str, source_url: str, 
                          company_hint: str = None) -> List[Dict]:
        """Automatically extract and track promises from any text"""
        tracked_promises = []
        
        # Step 1: Discover executives in the text
        executives = self.discover_executive(text, source_url)
        
        # Step 2: Try to identify the company
        company = company_hint or self._extract_company_from_text(text)
        
        # Step 3: Determine industry for better pattern matching
        industry = self._determine_industry(company, text)
        
        # Step 4: Extract promises using both general and industry-specific patterns
        all_patterns = dict(self.promise_patterns)
        if industry in self.industry_patterns:
            for ptype, patterns in self.industry_patterns[industry].items():
                if ptype not in all_patterns:
                    all_patterns[ptype] = patterns
                else:
                    all_patterns[ptype].extend(patterns)
        
        # Step 5: For each executive found, extract their promises
        for exec_info in executives:
            # Find text segments where this executive is speaking
            exec_segments = self._find_executive_segments(text, exec_info['name'])
            
            for segment in exec_segments:
                # Extract promises from this segment
                promises = self._extract_promises_from_segment(
                    segment, company, exec_info, source_url, all_patterns
                )
                
                for promise in promises:
                    # Save to database
                    if self.save_promise(promise):
                        tracked_promises.append({
                            'executive': exec_info['name'],
                            'title': exec_info['title'],
                            'company': company,
                            'promise_type': promise.promise_type.value,
                            'deadline': promise.deadline.isoformat() if promise.deadline else None,
                            'promise_text': promise.promise_text[:200] + '...',
                            'confidence': promise.confidence_language
                        })
                    
                    # Also save executive discovery info
                    self._save_executive_discovery(exec_info, company)
        
        # Step 6: If no executives found, try general promise extraction
        if not executives:
            general_promises = self.extract_promise_from_text(
                text, company, "Unknown Executive", "Unknown Title", 
                source_url, datetime.now()
            )
            
            for promise in general_promises:
                if self.save_promise(promise):
                    tracked_promises.append({
                        'executive': 'Unknown',
                        'company': company,
                        'promise_type': promise.promise_type.value,
                        'deadline': promise.deadline.isoformat() if promise.deadline else None,
                        'promise_text': promise.promise_text[:200] + '...'
                    })
        
        return tracked_promises
    
    def _extract_company_from_text(self, text: str) -> str:
        """Extract company name from text"""
        # Look for common patterns
        patterns = [
            r"(?:NYSE|NASDAQ|AMEX):\s*([A-Z]+)",  # Stock ticker
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc\.|Corp\.|Corporation|Company|Ltd\.|LLC|Pharma|Pharmaceuticals|Therapeutics|Bio|Biotech)",
            r"(?:conference call|earnings call) of ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "Unknown Company"
    
    def _determine_industry(self, company: str, text: str) -> str:
        """Determine industry from company name or text content"""
        text_lower = text.lower()
        company_lower = company.lower()
        
        biotech_keywords = ['biotech', 'therapeutics', 'bio', 'genomics', 'cell therapy']
        pharma_keywords = ['pharmaceutical', 'pharma', 'drug']
        medtech_keywords = ['medical device', 'medtech', 'diagnostic', 'surgical']
        
        if any(kw in company_lower or kw in text_lower for kw in biotech_keywords):
            return 'biotech'
        elif any(kw in company_lower or kw in text_lower for kw in pharma_keywords):
            return 'pharma'
        elif any(kw in company_lower or kw in text_lower for kw in medtech_keywords):
            return 'medtech'
        
        return 'general'
    
    def _find_executive_segments(self, text: str, exec_name: str) -> List[str]:
        """Find text segments where an executive is speaking"""
        segments = []
        
        # Look for patterns like "John Smith:" or "Mr. Smith said"
        patterns = [
            rf"{exec_name}:\s*(.+?)(?=\n[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:|$)",
            rf"{exec_name}\s+(?:said|stated|mentioned|noted|added|explained)[\s,]+[\"'](.+?)[\"']",
            rf"(?:Mr\.|Ms\.|Dr\.)\s+{exec_name.split()[-1]}:\s*(.+?)(?=\n|$)",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                segments.append(match.group(1))
        
        return segments
    
    def _extract_promises_from_segment(self, segment: str, company: str, 
                                     exec_info: Dict, source: str, 
                                     patterns: Dict) -> List[ExecutivePromise]:
        """Extract promises from a text segment"""
        promises = []
        
        for promise_type_str, pattern_list in patterns.items():
            # Convert string to PromiseType enum
            try:
                if isinstance(promise_type_str, str):
                    promise_type = PromiseType[promise_type_str.upper()]
                else:
                    promise_type = promise_type_str
            except (KeyError, AttributeError):
                continue
                
            for pattern in pattern_list:
                matches = re.finditer(pattern, segment, re.IGNORECASE)
                for match in matches:
                    # Extract promise details
                    promise_text = segment[max(0, match.start()-100):min(len(segment), match.end()+100)]
                    
                    # Extract deadline
                    deadline = None
                    if match.groups():
                        deadline_text = match.group(1)
                        deadline = self._parse_deadline(deadline_text)
                    
                    # Create promise
                    promise = ExecutivePromise(
                        promise_id=self._generate_promise_id(
                            company, exec_info['name'], promise_type, 
                            datetime.now(), promise_text
                        ),
                        company=company,
                        executive_name=exec_info['name'],
                        executive_title=exec_info['title'],
                        promise_text=promise_text.strip(),
                        promise_type=promise_type,
                        date_made=datetime.now(),
                        deadline=deadline,
                        source=source,
                        confidence_language=self._extract_confidence_language(promise_text),
                        specific_metrics=self._extract_metrics(promise_text, promise_type),
                        status=PromiseStatus.PENDING,
                        outcome_date=None,
                        outcome_details=None,
                        delay_days=None,
                        credibility_impact=None
                    )
                    
                    promises.append(promise)
        
        return promises
    
    def _parse_deadline(self, deadline_text: str) -> Optional[datetime]:
        """Parse deadline from various text formats"""
        if not deadline_text:
            return None
            
        # Try various parsing methods
        for extractor in self.timeline_extractors.values():
            deadline = extractor(deadline_text)
            if deadline:
                return deadline
        
        return None
    
    def _save_executive_discovery(self, exec_info: Dict, company: str):
        """Save discovered executive information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            normalized_name = exec_info['name'].lower().strip()
            exec_id = hashlib.md5(f"{normalized_name}_{company}".encode()).hexdigest()
            
            cursor.execute("""
                INSERT OR REPLACE INTO executive_discovery (
                    executive_id, full_name, normalized_name, company,
                    title, first_seen, last_seen, data_sources
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                exec_id, exec_info['name'], normalized_name, company,
                exec_info['title'], datetime.now(), datetime.now(),
                json.dumps([exec_info.get('source', 'Unknown')])
            ))
            
            conn.commit()
        except Exception as e:
            print(f"Error saving executive discovery: {e}")
        finally:
            conn.close()
    
    def get_all_tracked_executives(self, company: str = None) -> List[Dict]:
        """Get all executives being tracked"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if company:
                query = """
                    SELECT DISTINCT e.full_name, e.title, e.company, 
                           COUNT(p.promise_id) as promise_count,
                           ec.credibility_score
                    FROM executive_discovery e
                    LEFT JOIN promises p ON e.full_name = p.executive_name 
                                        AND e.company = p.company
                    LEFT JOIN executive_credibility ec ON e.full_name = ec.executive_name 
                                                      AND e.company = ec.company
                    WHERE LOWER(e.company) LIKE LOWER(?)
                    GROUP BY e.full_name, e.company
                    ORDER BY promise_count DESC
                """
                cursor.execute(query, (f"%{company}%",))
            else:
                query = """
                    SELECT DISTINCT e.full_name, e.title, e.company, 
                           COUNT(p.promise_id) as promise_count,
                           ec.credibility_score
                    FROM executive_discovery e
                    LEFT JOIN promises p ON e.full_name = p.executive_name 
                                        AND e.company = p.company
                    LEFT JOIN executive_credibility ec ON e.full_name = ec.executive_name 
                                                      AND e.company = ec.company
                    GROUP BY e.full_name, e.company
                    ORDER BY promise_count DESC
                """
                cursor.execute(query)
            
            executives = []
            for row in cursor.fetchall():
                executives.append({
                    'name': row[0],
                    'title': row[1],
                    'company': row[2],
                    'promise_count': row[3],
                    'credibility_score': row[4] if row[4] else 'No score yet'
                })
            
            return executives
            
        except Exception as e:
            print(f"Error getting tracked executives: {e}")
            return []
        finally:
            conn.close()
    
    def analyze_new_text(self, text: str, source_type: str = "earnings_call") -> Dict:
        """Analyze any text for executive promises"""
        results = {
            'executives_found': [],
            'promises_tracked': [],
            'companies_mentioned': [],
            'summary': {}
        }
        
        # Discover executives
        executives = self.discover_executive(text)
        results['executives_found'] = executives
        
        # Extract companies
        companies = set()
        company_patterns = [
            r"(?:NYSE|NASDAQ):\s*([A-Z]+)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc\.|Corp\.|Corporation|Pharmaceuticals|Therapeutics)"
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            companies.update(matches)
        
        results['companies_mentioned'] = list(companies)
        
        # Track promises
        for company in companies:
            promises = self.auto_track_promise(text, source_type, company)
            results['promises_tracked'].extend(promises)
        
        # Generate summary
        results['summary'] = {
            'total_executives': len(executives),
            'total_companies': len(companies),
            'total_promises': len(results['promises_tracked']),
            'promise_types': {}
        }
        
        # Count promise types
        for promise in results['promises_tracked']:
            ptype = promise.get('promise_type', 'unknown')
            results['summary']['promise_types'][ptype] = \
                results['summary']['promise_types'].get(ptype, 0) + 1
        
        return results


def test_enhanced_tracker():
    """Test the enhanced executive tracker"""
    tracker = EnhancedExecutiveTracker()
    
    # Test with sample earnings call text
    sample_text = """
    Moderna Q3 2024 Earnings Call Transcript
    
    Stephane Bancel, CEO: Thank you for joining us today. I'm pleased to report 
    strong progress across our pipeline. We expect to report topline data from our 
    personalized cancer vaccine trial in Q1 2025. Additionally, we remain on track 
    to submit our RSV vaccine for FDA approval by the end of Q2 2025.
    
    Dr. Stephen Hoge, President: Building on Stephane's comments, our CMV vaccine 
    program continues to advance well. We anticipate completing enrollment for the 
    Phase 3 trial by March 2025, with data readout expected in H2 2025.
    
    NYSE: MRNA
    """
    
    print("🧪 Testing Enhanced Executive Tracker")
    print("=" * 60)
    
    # Analyze the text
    results = tracker.analyze_new_text(sample_text, "earnings_call")
    
    print(f"\n📊 Analysis Results:")
    print(f"Executives found: {len(results['executives_found'])}")
    for exec in results['executives_found']:
        print(f"  • {exec['name']} - {exec['title']}")
    
    print(f"\nCompanies mentioned: {results['companies_mentioned']}")
    
    print(f"\nPromises tracked: {len(results['promises_tracked'])}")
    for promise in results['promises_tracked']:
        print(f"  • {promise['executive']}: {promise['promise_type']} - {promise.get('deadline', 'No deadline')}")
    
    print(f"\nSummary: {json.dumps(results['summary'], indent=2)}")
    
    # Get all tracked executives
    print(f"\n👥 All Tracked Executives:")
    all_execs = tracker.get_all_tracked_executives()
    for exec in all_execs[:10]:  # Show top 10
        print(f"  • {exec['name']} ({exec['company']}) - {exec['promise_count']} promises")


if __name__ == "__main__":
    test_enhanced_tracker() 