#!/usr/bin/env python3
"""
Test Report Generation and Validation
Validates that reports match the exact email requirements
"""
import sys
import os
from datetime import datetime
import re
from typing import Dict, List

# Add current directory to Python path  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main_enhanced_intelligence import EnhancedHealthcareIntelligence
from scraper_optimized import OptimizedScraper


class ReportValidator:
    """Validates reports match email requirements exactly"""
    
    def __init__(self):
        self.required_sections = [
            "Company Name:",
            "News Event:",
            "News Summary:",
            "Standout Points:",
            "Additional Developments:"
        ]
        
    def validate_report_structure(self, report_content: str) -> Dict:
        """Validate report structure matches email requirements"""
        
        results = {
            'valid': True,
            'issues': [],
            'word_counts': {},
            'section_analysis': {}
        }
        
        # 1. Check all required sections are present
        for section in self.required_sections:
            if section not in report_content:
                results['valid'] = False
                results['issues'].append(f"Missing required section: {section}")
        
        # 2. Extract and analyze each section
        sections = self._extract_sections(report_content)
        
        for section_name, section_content in sections.items():
            word_count = len(section_content.split())
            results['word_counts'][section_name] = word_count
            
            # Validate specific sections
            if section_name == "News Summary":
                sentence_count = len([s for s in section_content.split('.') if s.strip()])
                if sentence_count < 4 or sentence_count > 6:
                    results['issues'].append(f"News Summary should have exactly 5 sentences, found {sentence_count}")
            
            elif section_name == "Standout Points":
                # Should be the meatiest section
                total_words = sum(results['word_counts'].values())
                if total_words > 0 and word_count < total_words * 0.3:
                    results['issues'].append(f"Standout Points too short ({word_count} words) - should be meatiest section")
                
                # Check for quantifiable data
                if not self._has_quantifiable_data(section_content):
                    results['issues'].append("Standout Points missing quantifiable data (percentages, numbers, etc.)")
        
        # 3. Check overall word count
        total_words = sum(results['word_counts'].values())
        if total_words < 550 or total_words > 650:
            results['issues'].append(f"Total word count {total_words} outside target range (550-650)")
        
        # 4. Check for specific formatting requirements
        if not self._has_proper_formatting(report_content):
            results['issues'].append("Report formatting issues detected")
        
        if results['issues']:
            results['valid'] = False
            
        return results
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from report content"""
        sections = {}
        
        for i, section_header in enumerate(self.required_sections):
            start_idx = content.find(section_header)
            if start_idx == -1:
                continue
                
            # Find the end of this section (start of next section or end of content)
            if i < len(self.required_sections) - 1:
                next_header = self.required_sections[i + 1]
                end_idx = content.find(next_header, start_idx + len(section_header))
                if end_idx == -1:
                    section_content = content[start_idx + len(section_header):].strip()
                else:
                    section_content = content[start_idx + len(section_header):end_idx].strip()
            else:
                section_content = content[start_idx + len(section_header):].strip()
            
            section_name = section_header.replace(":", "").strip()
            sections[section_name] = section_content
        
        return sections
    
    def _has_quantifiable_data(self, content: str) -> bool:
        """Check if content has quantifiable data"""
        # Look for percentages, numbers, dollar amounts, dates, etc.
        patterns = [
            r'\d+%',           # Percentages
            r'\$\d+',          # Dollar amounts
            r'n=\d+',          # Patient numbers
            r'p<0\.\d+',       # P-values
            r'\d+\s*(patients|subjects|participants)',  # Patient counts
            r'Q[1-4]\s*20\d\d', # Quarter/year dates
            r'\d+\s*(million|billion|M|B)',  # Large numbers
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _has_proper_formatting(self, content: str) -> bool:
        """Check for proper formatting"""
        # Basic formatting checks
        if not content.strip():
            return False
        
        # Check for reasonable section lengths
        sections = self._extract_sections(content)
        if not sections:
            return False
        
        return True
    
    def generate_test_report(self) -> str:
        """Generate a test report to validate the system"""
        
        print("🧪 Generating Test Report...")
        
        try:
            # Initialize the intelligence system
            intelligence = EnhancedHealthcareIntelligence()
            
            # Create sample article data for testing
            sample_article = type('Article', (), {
                'title': 'Test Biotech Company Announces Positive Phase III Results',
                'content': '''
                Test Biotech Inc. (NASDAQ: TEST) today announced positive topline results from its Phase III clinical trial 
                evaluating TEST-001 in patients with advanced cancer. The trial met its primary endpoint with a 45% 
                objective response rate compared to 15% in the control arm (p<0.001). The study enrolled 300 patients 
                across 50 sites globally. CEO Dr. Sarah Johnson stated, "We expect to file our BLA with the FDA by Q4 2024 
                and anticipate potential approval by mid-2025." The company also announced a $50 million milestone payment 
                from its partner and expects to complete enrollment in its Phase II combination study by September 2024.
                Safety data showed manageable side effects with only 8% of patients discontinuing due to adverse events.
                ''',
                'url': 'https://test-url.com',
                'date': datetime.now()
            })()
            
            # Generate summary using the system
            summary = intelligence.ai_generator.generate_summary(sample_article)
            
            if summary:
                print("✅ Test report generated successfully!")
                return summary
            else:
                print("❌ Failed to generate test report")
                return None
                
        except Exception as e:
            print(f"❌ Error generating test report: {e}")
            return None
    
    def run_validation_test(self):
        """Run complete validation test"""
        
        print("🔍 HEALTHCARE REPORT VALIDATION TEST")
        print("=" * 50)
        
        # Generate test report
        test_report = self.generate_test_report()
        
        if not test_report:
            print("❌ Cannot validate - test report generation failed")
            return
        
        print("\n📊 VALIDATING REPORT STRUCTURE...")
        
        # Validate the report
        validation_results = self.validate_report_structure(test_report)
        
        print(f"\n{'✅ VALIDATION PASSED' if validation_results['valid'] else '❌ VALIDATION FAILED'}")
        
        # Show word count breakdown
        print(f"\n📝 WORD COUNT ANALYSIS:")
        total_words = sum(validation_results['word_counts'].values())
        print(f"Total Words: {total_words} (Target: 550-650)")
        
        for section, count in validation_results['word_counts'].items():
            percentage = (count / total_words * 100) if total_words > 0 else 0
            print(f"• {section}: {count} words ({percentage:.1f}%)")
        
        # Show any issues found
        if validation_results['issues']:
            print(f"\n⚠️ ISSUES FOUND ({len(validation_results['issues'])}):")
            for issue in validation_results['issues']:
                print(f"• {issue}")
        
        # Show the generated report for review
        print(f"\n📄 GENERATED REPORT:")
        print("-" * 50)
        print(test_report)
        print("-" * 50)
        
        return validation_results


def main():
    """Main function to run report validation"""
    validator = ReportValidator()
    validator.run_validation_test()


if __name__ == '__main__':
    main() 