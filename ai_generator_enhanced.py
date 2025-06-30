"""
Enhanced AI Generator with Integrated Market Intelligence
Combines AI summarization with real-time data for comprehensive analysis
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

from ai_generator_optimized import OptimizedAISummaryGenerator
from enhanced_features import (
    EnhancedAnalysisEngine,
    MarketIntelligence, 
    ClinicalTrialTracker,
    CompetitiveIntelligence,
    VisualizationEngine
)
import config

logger = logging.getLogger(__name__)


class EnhancedAIGenerator(OptimizedAISummaryGenerator):
    """Enhanced AI generator that includes market intelligence and competitive analysis"""
    
    def __init__(self, max_workers=3):
        super().__init__(max_workers)
        self.enhanced_engine = EnhancedAnalysisEngine()
        self.market_intel = MarketIntelligence()
    
    def generate_enhanced_summary(self, article, include_visuals=True):
        """Generate enhanced summary with integrated market intelligence"""
        
        # First, generate the base AI summary
        base_summary = self.generate_summary(article)
        
        if not base_summary:
            return None
        
        # Extract company info from summary
        company_name = article.company_name or self._extract_company_name(base_summary)
        ticker = self._extract_or_lookup_ticker(company_name)
        
        # If we have a ticker, enhance with market data
        enhanced_data = {
            'base_summary': base_summary,
            'company_name': company_name,
            'ticker': ticker
        }
        
        if ticker:
            try:
                # Get comprehensive market analysis
                market_analysis = self.enhanced_engine.generate_comprehensive_analysis(
                    company_name=company_name,
                    ticker=ticker,
                    summary_text=base_summary,
                    news_type=self._extract_news_type(base_summary)
                )
                
                # Add key insights to enhanced data
                enhanced_data['market_intelligence'] = {
                    'current_price': market_analysis['market_intelligence'].get('current_price'),
                    'market_cap': market_analysis['market_intelligence'].get('market_cap_formatted'),
                    'performance': market_analysis['market_intelligence'].get('performance'),
                    'volume_analysis': market_analysis['visualizations'].get('volume_analysis'),
                    'analyst_consensus': market_analysis['market_intelligence'].get('analyst_data', {}).get('consensus', 'N/A')
                }
                
                enhanced_data['clinical_pipeline'] = market_analysis.get('clinical_trials', {}).get('summary', {})
                enhanced_data['competitive_position'] = market_analysis.get('competitive_intelligence', {})
                enhanced_data['investment_signals'] = market_analysis.get('investment_signals', {})
                enhanced_data['risk_factors'] = market_analysis.get('risk_factors', [])
                
                if include_visuals:
                    enhanced_data['visualizations'] = {
                        'stock_chart': market_analysis['visualizations'].get('stock_chart'),
                        'pipeline_chart': market_analysis['clinical_trials'].get('pipeline_chart')
                    }
                
            except Exception as e:
                logger.error(f"Error enhancing summary with market data: {e}")
        
        # Generate enhanced summary text that incorporates the data
        enhanced_summary_text = self._create_enhanced_summary_text(enhanced_data)
        
        return {
            'summary_text': enhanced_summary_text,
            'enhanced_data': enhanced_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_or_lookup_ticker(self, company_name: str) -> Optional[str]:
        """Extract ticker from company name or look it up"""
        if not company_name:
            return None
        
        # Common biotech/pharma ticker mappings
        # In production, this would query a database or API
        ticker_map = {
            'moderna': 'MRNA',
            'pfizer': 'PFE',
            'biomarin': 'BMRN',
            'neurocrine': 'NBIX',
            'eli lilly': 'LLY',
            'lilly': 'LLY',
            'merck': 'MRK',
            'johnson & johnson': 'JNJ',
            'j&j': 'JNJ',
            'novartis': 'NVS',
            'roche': 'RHHBY',
            'gilead': 'GILD',
            'biogen': 'BIIB',
            'regeneron': 'REGN',
            'vertex': 'VRTX',
            'amgen': 'AMGN',
            'abbvie': 'ABBV'
        }
        
        company_lower = company_name.lower()
        for key, ticker in ticker_map.items():
            if key in company_lower:
                return ticker
        
        return None
    
    def _extract_news_type(self, summary_text: str) -> str:
        """Extract news event type from summary"""
        news_types = [
            'earnings', 'data release', 'clinical trial', 'fda approval',
            'partnership', 'acquisition', 'conference', 'leadership change'
        ]
        
        summary_lower = summary_text.lower()
        for news_type in news_types:
            if news_type in summary_lower:
                return news_type.title()
        
        return 'General News'
    
    def _create_enhanced_summary_text(self, enhanced_data: Dict) -> str:
        """Create enhanced summary text that incorporates market intelligence"""
        base_summary = enhanced_data['base_summary']
        
        # Add market intelligence section if available
        if enhanced_data.get('ticker') and enhanced_data.get('market_intelligence'):
            market_section = self._format_market_intelligence_section(enhanced_data['market_intelligence'])
            base_summary += f"\n\n{market_section}"
        
        # Add investment implications if available
        if enhanced_data.get('investment_signals'):
            signals_section = self._format_investment_signals_section(enhanced_data['investment_signals'])
            base_summary += f"\n\n{signals_section}"
        
        # Add risk factors if available
        if enhanced_data.get('risk_factors'):
            risk_section = self._format_risk_section(enhanced_data['risk_factors'])
            base_summary += f"\n\n{risk_section}"
        
        return base_summary
    
    def _format_market_intelligence_section(self, market_data: Dict) -> str:
        """Format market intelligence into readable text"""
        section = "**Market Intelligence:**\n"
        
        if market_data.get('current_price'):
            section += f"- Current Price: ${market_data['current_price']:.2f}\n"
        
        if market_data.get('market_cap'):
            section += f"- Market Cap: {market_data['market_cap']}\n"
        
        if market_data.get('performance'):
            perf = market_data['performance']
            section += f"- Performance: 1M: {perf.get('1m', 0):+.1f}%, 3M: {perf.get('3m', 0):+.1f}%, 1Y: {perf.get('1y', 0):+.1f}%\n"
        
        if market_data.get('volume_analysis'):
            vol = market_data['volume_analysis']
            if vol.get('unusual_volume'):
                section += f"- Volume Alert: {vol.get('interpretation', 'Unusual trading activity detected')}\n"
        
        if market_data.get('analyst_consensus'):
            section += f"- Analyst Consensus: {market_data['analyst_consensus']}\n"
        
        return section
    
    def _format_investment_signals_section(self, signals: Dict) -> str:
        """Format investment signals into readable text"""
        section = "**Investment Signals:**\n"
        
        sentiment = signals.get('sentiment', 'neutral').upper()
        section += f"- Overall Sentiment: {sentiment}\n"
        
        if signals.get('key_factors'):
            section += "- Key Factors:\n"
            for factor in signals['key_factors']:
                section += f"  • {factor}\n"
        
        return section
    
    def _format_risk_section(self, risks: List[str]) -> str:
        """Format risk factors into readable text"""
        if not risks:
            return ""
        
        section = "**Key Risk Factors:**\n"
        for risk in risks:
            section += f"- {risk}\n"
        
        return section
    
    def generate_comprehensive_report(self, articles: List, output_format='html'):
        """Generate comprehensive report with all enhanced features"""
        logger.info(f"Generating comprehensive report for {len(articles)} articles")
        
        # Process articles with enhanced features
        enhanced_summaries = []
        
        for idx, article in enumerate(articles):
            logger.info(f"Processing article {idx+1}/{len(articles)} with enhanced features")
            
            enhanced_summary = self.generate_enhanced_summary(article, include_visuals=True)
            if enhanced_summary:
                enhanced_summaries.append({
                    'article': article,
                    'enhanced_summary': enhanced_summary
                })
        
        # Generate report based on format
        if output_format == 'html':
            return self._generate_html_report(enhanced_summaries)
        elif output_format == 'pdf':
            return self._generate_pdf_report(enhanced_summaries)
        else:
            return self._generate_json_report(enhanced_summaries)
    
    def _generate_html_report(self, enhanced_summaries: List[Dict]) -> str:
        """Generate enhanced HTML report with visualizations"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Healthcare Investment Intelligence Report - {date}</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 40px; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .summary-card {{ background: white; padding: 30px; margin: 20px 0; 
                                border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .market-intel {{ background: #f0f9ff; padding: 20px; border-radius: 8px; 
                               margin: 15px 0; border-left: 4px solid #3182ce; }}
                .risk-factors {{ background: #fef2f2; padding: 20px; border-radius: 8px; 
                               margin: 15px 0; border-left: 4px solid #ef4444; }}
                .chart-container {{ margin: 20px 0; text-align: center; }}
                .investment-signals {{ background: #f0fdf4; padding: 20px; border-radius: 8px; 
                                     margin: 15px 0; border-left: 4px solid #10b981; }}
                h1 {{ margin: 0; }}
                h2 {{ color: #1a365d; margin-top: 30px; }}
                h3 {{ color: #2d3748; }}
                .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
                .metric-label {{ font-size: 12px; color: #6b7280; text-transform: uppercase; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #1a365d; }}
                .positive {{ color: #10b981; }}
                .negative {{ color: #ef4444; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧬 Healthcare Investment Intelligence Report</h1>
                <p>Generated: {date} | Enhanced with Real-Time Market Data & Competitive Analysis</p>
            </div>
            
            {content}
            
        </body>
        </html>
        """
        
        content_html = ""
        
        for item in enhanced_summaries:
            article = item['article']
            enhanced = item['enhanced_summary']
            data = enhanced['enhanced_data']
            
            # Build content for each article
            article_html = f"""
            <div class="summary-card">
                <h2>{article.title}</h2>
                <p><strong>Company:</strong> {data.get('company_name', 'Unknown')} 
                   {f"({data.get('ticker', '')})" if data.get('ticker') else ''}</p>
                
                <h3>Summary</h3>
                <div>{data['base_summary'].replace(chr(10), '<br>')}</div>
                
                {self._format_market_intel_html(data.get('market_intelligence', {}))}
                {self._format_investment_signals_html(data.get('investment_signals', {}))}
                {self._format_risk_factors_html(data.get('risk_factors', []))}
                {self._format_visualizations_html(data.get('visualizations', {}))}
            </div>
            """
            
            content_html += article_html
        
        return html_template.format(
            date=datetime.now().strftime('%B %d, %Y'),
            content=content_html
        )
    
    def _format_market_intel_html(self, market_data: Dict) -> str:
        """Format market intelligence for HTML"""
        if not market_data:
            return ""
        
        html = '<div class="market-intel"><h3>Market Intelligence</h3>'
        
        # Add metrics
        if market_data.get('current_price'):
            html += f'<div class="metric"><div class="metric-label">Stock Price</div>'
            html += f'<div class="metric-value">${market_data["current_price"]:.2f}</div></div>'
        
        if market_data.get('market_cap'):
            html += f'<div class="metric"><div class="metric-label">Market Cap</div>'
            html += f'<div class="metric-value">{market_data["market_cap"]}</div></div>'
        
        if market_data.get('performance'):
            perf = market_data['performance']
            for period, value in perf.items():
                color_class = 'positive' if value > 0 else 'negative'
                html += f'<div class="metric"><div class="metric-label">{period.upper()} Performance</div>'
                html += f'<div class="metric-value {color_class}">{value:+.1f}%</div></div>'
        
        html += '</div>'
        return html
    
    def _format_investment_signals_html(self, signals: Dict) -> str:
        """Format investment signals for HTML"""
        if not signals:
            return ""
        
        html = '<div class="investment-signals"><h3>Investment Signals</h3>'
        html += f'<p><strong>Sentiment:</strong> {signals.get("sentiment", "neutral").upper()}</p>'
        
        if signals.get('key_factors'):
            html += '<p><strong>Key Factors:</strong></p><ul>'
            for factor in signals['key_factors']:
                html += f'<li>{factor}</li>'
            html += '</ul>'
        
        html += '</div>'
        return html
    
    def _format_risk_factors_html(self, risks: List[str]) -> str:
        """Format risk factors for HTML"""
        if not risks:
            return ""
        
        html = '<div class="risk-factors"><h3>Risk Factors</h3><ul>'
        for risk in risks:
            html += f'<li>{risk}</li>'
        html += '</ul></div>'
        
        return html
    
    def _format_visualizations_html(self, visualizations: Dict) -> str:
        """Format visualizations for HTML"""
        if not visualizations:
            return ""
        
        html = '<div class="chart-container">'
        
        if visualizations.get('stock_chart'):
            html += f'<div>{visualizations["stock_chart"]}</div>'
        
        if visualizations.get('pipeline_chart'):
            html += f'<div>{visualizations["pipeline_chart"]}</div>'
        
        html += '</div>'
        return html
    
    def _generate_pdf_report(self, enhanced_summaries: List[Dict]) -> bytes:
        """Generate PDF report (placeholder - would use reportlab or similar)"""
        # This would use a PDF generation library
        # For now, return a placeholder
        return b"PDF generation would be implemented here"
    
    def _generate_json_report(self, enhanced_summaries: List[Dict]) -> str:
        """Generate JSON report with all data"""
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'Healthcare Investment Intelligence',
            'articles_analyzed': len(enhanced_summaries),
            'summaries': []
        }
        
        for item in enhanced_summaries:
            article = item['article']
            enhanced = item['enhanced_summary']
            
            summary_data = {
                'article': article.to_dict(),
                'enhanced_analysis': enhanced['enhanced_data'],
                'generated_at': enhanced['timestamp']
            }
            
            report_data['summaries'].append(summary_data)
        
        return json.dumps(report_data, indent=2, default=str) 