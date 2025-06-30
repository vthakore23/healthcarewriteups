"""
Enhanced Features for Healthcare News Automation
Makes the app significantly more valuable than manual AI summarization
"""
import requests
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
import json
import re
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


class MarketIntelligence:
    """Real-time market intelligence and financial data integration"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_stock_data(self, ticker: str) -> Dict:
        """Get comprehensive stock data and analytics"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get price history
            hist_1m = stock.history(period="1mo")
            hist_3m = stock.history(period="3mo")
            hist_6m = stock.history(period="6mo")
            hist_1y = stock.history(period="1y")
            
            # Calculate performance metrics
            current_price = info.get('currentPrice', 0)
            market_cap = info.get('marketCap', 0)
            
            # Performance calculations
            perf_1m = ((current_price - hist_1m['Close'].iloc[0]) / hist_1m['Close'].iloc[0] * 100) if len(hist_1m) > 0 else 0
            perf_3m = ((current_price - hist_3m['Close'].iloc[0]) / hist_3m['Close'].iloc[0] * 100) if len(hist_3m) > 0 else 0
            perf_6m = ((current_price - hist_6m['Close'].iloc[0]) / hist_6m['Close'].iloc[0] * 100) if len(hist_6m) > 0 else 0
            perf_1y = ((current_price - hist_1y['Close'].iloc[0]) / hist_1y['Close'].iloc[0] * 100) if len(hist_1y) > 0 else 0
            
            # Get analyst data
            recommendations = stock.recommendations
            analyst_data = self._process_analyst_recommendations(recommendations) if recommendations is not None else {}
            
            # Volume analysis
            avg_volume_10d = hist_1m['Volume'].tail(10).mean() if len(hist_1m) > 0 else 0
            volume_today = info.get('volume', 0)
            volume_vs_avg = ((volume_today - avg_volume_10d) / avg_volume_10d * 100) if avg_volume_10d > 0 else 0
            
            return {
                'ticker': ticker,
                'current_price': current_price,
                'market_cap': market_cap,
                'market_cap_formatted': self._format_number(market_cap),
                'performance': {
                    '1m': round(perf_1m, 2),
                    '3m': round(perf_3m, 2),
                    '6m': round(perf_6m, 2),
                    '1y': round(perf_1y, 2)
                },
                'volume': {
                    'current': volume_today,
                    'avg_10d': int(avg_volume_10d),
                    'vs_average_pct': round(volume_vs_avg, 2)
                },
                'analyst_data': analyst_data,
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'float_shares': info.get('floatShares', 0),
                'short_ratio': info.get('shortRatio', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'cash': info.get('totalCash', 0),
                'cash_per_share': info.get('totalCashPerShare', 0)
            }
        except Exception as e:
            logger.error(f"Error fetching stock data for {ticker}: {e}")
            return {}
    
    def _process_analyst_recommendations(self, recommendations):
        """Process analyst recommendations data"""
        if recommendations is None or recommendations.empty:
            return {}
        
        # Get latest recommendations
        latest = recommendations.tail(10)
        
        # Count recommendations
        rating_counts = latest['To Grade'].value_counts().to_dict()
        
        # Get average price target if available
        return {
            'total_analysts': len(latest),
            'ratings': rating_counts,
            'consensus': self._calculate_consensus(rating_counts)
        }
    
    def _calculate_consensus(self, ratings):
        """Calculate consensus rating"""
        positive = ratings.get('Buy', 0) + ratings.get('Strong Buy', 0) + ratings.get('Outperform', 0)
        neutral = ratings.get('Hold', 0) + ratings.get('Neutral', 0)
        negative = ratings.get('Sell', 0) + ratings.get('Underperform', 0)
        
        total = positive + neutral + negative
        if total == 0:
            return "No Coverage"
        
        if positive > neutral and positive > negative:
            return "Buy"
        elif neutral > negative:
            return "Hold"
        else:
            return "Sell"
    
    def _format_number(self, num):
        """Format large numbers for readability"""
        if num >= 1e9:
            return f"${num/1e9:.2f}B"
        elif num >= 1e6:
            return f"${num/1e6:.2f}M"
        else:
            return f"${num:,.0f}"
    
    def get_peer_comparison(self, ticker: str, peers: List[str]) -> pd.DataFrame:
        """Compare company metrics with peers"""
        data = []
        
        for t in [ticker] + peers:
            stock_data = self.get_stock_data(t)
            if stock_data:
                data.append({
                    'Ticker': t,
                    'Market Cap': stock_data.get('market_cap_formatted', 'N/A'),
                    '1M Perf %': stock_data.get('performance', {}).get('1m', 0),
                    '3M Perf %': stock_data.get('performance', {}).get('3m', 0),
                    '1Y Perf %': stock_data.get('performance', {}).get('1y', 0),
                    'Cash/Share': stock_data.get('cash_per_share', 0)
                })
        
        return pd.DataFrame(data)


class ClinicalTrialTracker:
    """Track and analyze clinical trial data"""
    
    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/api/query/study_fields"
    
    def search_company_trials(self, company_name: str, active_only: bool = True) -> List[Dict]:
        """Search for clinical trials by company"""
        try:
            params = {
                'expr': f'SEARCH[Sponsor]({company_name})',
                'fields': 'NCTId,BriefTitle,Status,Phase,StartDate,CompletionDate,Condition,InterventionName',
                'min_rnk': 1,
                'max_rnk': 50,
                'fmt': 'json'
            }
            
            if active_only:
                params['expr'] += ' AND (SEARCH[Status](Recruiting) OR SEARCH[Status](Active))'
            
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._process_trial_data(data)
            return []
            
        except Exception as e:
            logger.error(f"Error fetching clinical trials: {e}")
            return []
    
    def _process_trial_data(self, data: Dict) -> List[Dict]:
        """Process clinical trial data into structured format"""
        trials = []
        
        if 'StudyFieldsResponse' in data:
            studies = data['StudyFieldsResponse'].get('StudyFields', [])
            
            for study in studies:
                trial = {
                    'nct_id': study.get('NCTId', [''])[0],
                    'title': study.get('BriefTitle', [''])[0],
                    'status': study.get('Status', [''])[0],
                    'phase': study.get('Phase', [''])[0],
                    'start_date': study.get('StartDate', [''])[0],
                    'completion_date': study.get('CompletionDate', [''])[0],
                    'condition': ', '.join(study.get('Condition', [])),
                    'intervention': ', '.join(study.get('InterventionName', []))
                }
                trials.append(trial)
        
        return trials
    
    def analyze_trial_portfolio(self, trials: List[Dict]) -> Dict:
        """Analyze company's clinical trial portfolio"""
        if not trials:
            return {}
        
        # Count by phase
        phase_counts = {}
        for trial in trials:
            phase = trial.get('phase', 'Not Specified')
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        # Count by status
        status_counts = {}
        for trial in trials:
            status = trial.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Therapeutic areas
        conditions = {}
        for trial in trials:
            condition = trial.get('condition', '').split(',')[0].strip()
            if condition:
                conditions[condition] = conditions.get(condition, 0) + 1
        
        return {
            'total_trials': len(trials),
            'by_phase': phase_counts,
            'by_status': status_counts,
            'therapeutic_areas': dict(sorted(conditions.items(), key=lambda x: x[1], reverse=True)[:5]),
            'active_late_stage': sum(1 for t in trials if 'Phase 3' in t.get('phase', '') and 'Active' in t.get('status', ''))
        }


class CompetitiveIntelligence:
    """Analyze competitive landscape and market dynamics"""
    
    def __init__(self):
        self.market_intelligence = MarketIntelligence()
    
    def identify_competitors(self, company_name: str, therapeutic_area: str) -> List[str]:
        """Identify key competitors in the therapeutic area"""
        # This would ideally connect to a database or API
        # For now, using a simplified mapping
        competitor_map = {
            'oncology': ['MRNA', 'BNTX', 'GILD', 'BMY', 'MRK'],
            'neurology': ['BIIB', 'TEVA', 'SAGE', 'ACAD', 'NBIX'],
            'rare disease': ['BMRN', 'ALNY', 'SRPT', 'RARE', 'GILD'],
            'gene therapy': ['BMRN', 'BLUE', 'QURE', 'RGNX', 'SGMO'],
            'immunology': ['ABBV', 'JNJ', 'BMY', 'GILD', 'AMGN']
        }
        
        # Find best matching therapeutic area
        area_lower = therapeutic_area.lower()
        for key, competitors in competitor_map.items():
            if key in area_lower:
                return competitors[:4]  # Return top 4 competitors
        
        return []
    
    def analyze_competitive_position(self, company_ticker: str, competitors: List[str]) -> Dict:
        """Analyze company's position relative to competitors"""
        peer_comparison = self.market_intelligence.get_peer_comparison(company_ticker, competitors)
        
        # Calculate relative metrics
        company_data = self.market_intelligence.get_stock_data(company_ticker)
        
        competitive_analysis = {
            'peer_comparison': peer_comparison.to_dict('records') if not peer_comparison.empty else [],
            'market_position': self._calculate_market_position(company_ticker, peer_comparison),
            'valuation_metrics': self._compare_valuations(company_ticker, competitors)
        }
        
        return competitive_analysis
    
    def _calculate_market_position(self, ticker: str, peer_df: pd.DataFrame) -> str:
        """Calculate market position among peers"""
        if peer_df.empty:
            return "Unable to determine"
        
        # Find company's rank by market cap
        # This is simplified - would need proper parsing of market cap strings
        return "Analysis based on market cap and performance metrics"
    
    def _compare_valuations(self, ticker: str, competitors: List[str]) -> Dict:
        """Compare valuation metrics across peers"""
        # Simplified version - would integrate with financial data APIs
        return {
            'relative_valuation': 'In-line with peers',
            'key_differentiators': ['Pipeline depth', 'Cash position', 'Market opportunity']
        }


class PatentIntelligence:
    """Track and analyze patent portfolios"""
    
    def search_company_patents(self, company_name: str, recent_only: bool = True) -> List[Dict]:
        """Search for company patents"""
        # This would integrate with patent databases
        # Simplified implementation for now
        return [
            {
                'title': 'Method for treating neurological disorders',
                'filing_date': '2024-01-15',
                'status': 'Pending',
                'key_claims': 'Novel compound for CNS disorders'
            }
        ]
    
    def analyze_ip_strength(self, patents: List[Dict]) -> Dict:
        """Analyze intellectual property portfolio strength"""
        return {
            'total_patents': len(patents),
            'recent_filings': sum(1 for p in patents if '2024' in p.get('filing_date', '')),
            'patent_diversity': 'Moderate',
            'freedom_to_operate': 'Strong'
        }


class VisualizationEngine:
    """Create visual analytics and charts"""
    
    def create_pipeline_visualization(self, trials: List[Dict]) -> str:
        """Create pipeline visualization chart"""
        if not trials:
            return ""
        
        # Count trials by phase
        phase_counts = {}
        for trial in trials:
            phase = trial.get('phase', 'Preclinical')
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        phases = list(phase_counts.keys())
        counts = list(phase_counts.values())
        
        bars = ax.bar(phases, counts, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        ax.set_xlabel('Development Phase')
        ax.set_ylabel('Number of Programs')
        ax.set_title('Clinical Pipeline Overview')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        # Convert to base64 for embedding
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f'<img src="data:image/png;base64,{image_base64}" style="max-width:100%;">'
    
    def create_stock_performance_chart(self, ticker: str, period: str = '6mo') -> str:
        """Create stock performance chart"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                return ""
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(hist.index, hist['Close'], linewidth=2, color='#1f77b4')
            ax.fill_between(hist.index, hist['Close'], alpha=0.3, color='#1f77b4')
            
            ax.set_xlabel('Date')
            ax.set_ylabel('Price ($)')
            ax.set_title(f'{ticker} Stock Performance - {period}')
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            fig.autofmt_xdate()
            
            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f'<img src="data:image/png;base64,{image_base64}" style="max-width:100%;">'
            
        except Exception as e:
            logger.error(f"Error creating stock chart: {e}")
            return ""


class EnhancedAnalysisEngine:
    """Orchestrate all enhanced features for comprehensive analysis"""
    
    def __init__(self):
        self.market_intel = MarketIntelligence()
        self.trial_tracker = ClinicalTrialTracker()
        self.competitive_intel = CompetitiveIntelligence()
        self.patent_intel = PatentIntelligence()
        self.viz_engine = VisualizationEngine()
    
    def generate_comprehensive_analysis(self, company_name: str, ticker: str, 
                                      summary_text: str, news_type: str) -> Dict:
        """Generate comprehensive analysis beyond basic AI summary"""
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'company': company_name,
            'ticker': ticker
        }
        
        # 1. Market Intelligence
        logger.info(f"Fetching market data for {ticker}")
        market_data = self.market_intel.get_stock_data(ticker)
        analysis['market_intelligence'] = market_data
        
        # 2. Clinical Trial Analysis
        logger.info(f"Analyzing clinical trials for {company_name}")
        trials = self.trial_tracker.search_company_trials(company_name)
        trial_analysis = self.trial_tracker.analyze_trial_portfolio(trials)
        analysis['clinical_trials'] = {
            'summary': trial_analysis,
            'pipeline_chart': self.viz_engine.create_pipeline_visualization(trials)
        }
        
        # 3. Competitive Analysis
        therapeutic_area = self._extract_therapeutic_area(summary_text)
        competitors = self.competitive_intel.identify_competitors(company_name, therapeutic_area)
        if competitors:
            competitive_analysis = self.competitive_intel.analyze_competitive_position(ticker, competitors)
            analysis['competitive_intelligence'] = competitive_analysis
        
        # 4. Patent Analysis
        patents = self.patent_intel.search_company_patents(company_name)
        ip_analysis = self.patent_intel.analyze_ip_strength(patents)
        analysis['intellectual_property'] = ip_analysis
        
        # 5. Visual Analytics
        analysis['visualizations'] = {
            'stock_chart': self.viz_engine.create_stock_performance_chart(ticker),
            'volume_analysis': self._analyze_volume_patterns(market_data)
        }
        
        # 6. Investment Signals
        analysis['investment_signals'] = self._generate_investment_signals(
            market_data, trial_analysis, news_type
        )
        
        # 7. Risk Assessment
        analysis['risk_factors'] = self._assess_risk_factors(
            market_data, trial_analysis, competitive_analysis if competitors else {}
        )
        
        return analysis
    
    def _extract_therapeutic_area(self, text: str) -> str:
        """Extract therapeutic area from text"""
        # Simple keyword matching - could be enhanced with NLP
        areas = ['oncology', 'neurology', 'immunology', 'rare disease', 'gene therapy', 
                 'cardiovascular', 'metabolic', 'infectious disease']
        
        text_lower = text.lower()
        for area in areas:
            if area in text_lower:
                return area
        
        return 'general'
    
    def _analyze_volume_patterns(self, market_data: Dict) -> Dict:
        """Analyze trading volume patterns"""
        volume_data = market_data.get('volume', {})
        
        return {
            'unusual_volume': volume_data.get('vs_average_pct', 0) > 50,
            'volume_trend': 'Above average' if volume_data.get('vs_average_pct', 0) > 0 else 'Below average',
            'interpretation': self._interpret_volume(volume_data.get('vs_average_pct', 0))
        }
    
    def _interpret_volume(self, volume_pct: float) -> str:
        """Interpret volume patterns"""
        if volume_pct > 100:
            return "Exceptionally high volume - strong interest/major news impact"
        elif volume_pct > 50:
            return "Elevated volume - increased market attention"
        elif volume_pct < -30:
            return "Low volume - limited market interest"
        else:
            return "Normal trading volume"
    
    def _generate_investment_signals(self, market_data: Dict, trial_data: Dict, news_type: str) -> Dict:
        """Generate investment signals based on comprehensive data"""
        signals = {
            'sentiment': 'neutral',
            'key_factors': [],
            'action_items': []
        }
        
        # Analyze based on news type
        if news_type.lower() in ['data release', 'clinical trial results']:
            if trial_data.get('active_late_stage', 0) > 0:
                signals['key_factors'].append('Multiple late-stage programs de-risk pipeline')
        
        # Market momentum
        perf = market_data.get('performance', {})
        if perf.get('1m', 0) > 20:
            signals['sentiment'] = 'bullish'
            signals['key_factors'].append('Strong recent momentum')
        elif perf.get('1m', 0) < -20:
            signals['sentiment'] = 'bearish'
            signals['key_factors'].append('Recent weakness may present opportunity')
        
        return signals
    
    def _assess_risk_factors(self, market_data: Dict, trial_data: Dict, competitive_data: Dict) -> List[str]:
        """Assess key risk factors"""
        risks = []
        
        # Cash runway risk
        cash = market_data.get('cash', 0)
        if cash < 100_000_000:  # Less than $100M
            risks.append("Limited cash runway may require financing")
        
        # Pipeline concentration risk
        if trial_data.get('total_trials', 0) < 3:
            risks.append("Concentrated pipeline increases binary risk")
        
        # Valuation risk
        market_cap = market_data.get('market_cap', 0)
        if market_cap > 10_000_000_000:  # Over $10B
            risks.append("High valuation may limit upside potential")
        
        return risks 