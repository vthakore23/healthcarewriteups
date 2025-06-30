#!/usr/bin/env python3
"""
Simplified Social Media Sentiment Analysis Web Interface
Healthcare Investment Intelligence Platform
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import logging
import asyncio
from datetime import datetime
import json
import traceback

# Import just the social media components
from social_media_sentiment import SocialMediaSentimentAnalyzer, DrugDatabase
from stock_ticker_intelligence import HealthcareCompanyIntelligence
from management_truth_tracker import ManagementTruthTracker
from fda_decision_analyzer import FDADecisionAnalyzer
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize components directly (without the integrated system)
drug_db = DrugDatabase()
truth_tracker = ManagementTruthTracker()
fda_analyzer = FDADecisionAnalyzer()
stock_intel = HealthcareCompanyIntelligence()

# Global sentiment analyzer instance
sentiment_analyzer = None

def init_sentiment_analyzer():
    """Initialize the sentiment analyzer"""
    global sentiment_analyzer
    if not sentiment_analyzer:
        sentiment_analyzer = SocialMediaSentimentAnalyzer()
    return sentiment_analyzer

# Initialize on startup
init_sentiment_analyzer()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard_social.html')

@app.route('/api/search_ticker', methods=['GET'])
def search_ticker():
    """Search for company ticker"""
    query = request.args.get('ticker', '').upper()
    
    try:
        # Use stock intelligence to validate ticker
        intelligence = stock_intel.get_company_intelligence(query)
        
        if "error" not in intelligence:
            return jsonify({
                'valid': True,
                'ticker': query,
                'company_name': intelligence.get('company_name', query),
                'sector': intelligence.get('sector', 'Healthcare')
            })
        else:
            return jsonify({
                'valid': False,
                'error': intelligence['error']
            })
    except Exception as e:
        logger.error(f"Error validating ticker: {e}")
        return jsonify({'valid': False, 'error': str(e)})

@app.route('/api/drug_sentiment/<drug_name>')
def get_drug_sentiment(drug_name):
    """Get sentiment analysis for a specific drug"""
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        sentiment_data = loop.run_until_complete(
            sentiment_analyzer.analyze_drug_sentiment(drug_name)
        )
        
        return jsonify(sentiment_data)
    except Exception as e:
        logger.error(f"Error analyzing drug sentiment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/company_sentiment/<ticker>')
def get_company_sentiment(ticker):
    """Get sentiment analysis for all drugs from a company"""
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        sentiment_data = loop.run_until_complete(
            sentiment_analyzer.analyze_company_drugs(ticker)
        )
        
        return jsonify(sentiment_data)
    except Exception as e:
        logger.error(f"Error analyzing company sentiment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_drugs', methods=['GET'])
def search_drugs():
    """Search for drugs by name"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'drugs': []})
    
    try:
        drugs = []
        seen = set()
        
        # Search in drug database
        results = drug_db.find_drug(query)
        
        # Process find_drug results (3 values: drug_name, company, ticker)
        for drug_name, company, ticker in results:
            key = f"{drug_name}_{company}"
            if key not in seen:
                seen.add(key)
                drugs.append({
                    'drug_name': drug_name,
                    'generic_name': '',
                    'company': company,
                    'ticker': ticker,
                    'type': 'drug'
                })
        
        # Also check if it's a ticker
        if query.upper() == query and 2 <= len(query) <= 5:  # Likely a ticker
            company_drugs = drug_db.get_company_drugs(query)
            for drug in company_drugs:
                key = f"{drug['drug_name']}_ticker"
                if key not in seen:
                    seen.add(key)
                    drugs.append({
                        'drug_name': drug['drug_name'],
                        'generic_name': drug.get('generic_name', ''),
                        'company': f"Company ticker: {query}",
                        'ticker': query,
                        'type': 'company'
                    })
        
        # If no results found and query is substantial, add it as unknown drug
        if not drugs and len(query) >= 3:
            drugs.append({
                'drug_name': query.title(),
                'generic_name': 'Unknown drug - search anyway',
                'company': 'Unknown Company',
                'ticker': 'N/A',
                'type': 'unknown'
            })
        
        # Add some helpful suggestions if the search is empty or limited
        if len(drugs) < 3:
            suggestions = [
                {'drug_name': 'Humira', 'generic_name': 'adalimumab', 'company': 'AbbVie', 'ticker': 'ABBV', 'type': 'suggestion'},
                {'drug_name': 'Keytruda', 'generic_name': 'pembrolizumab', 'company': 'Merck', 'ticker': 'MRK', 'type': 'suggestion'},
                {'drug_name': 'Ozempic', 'generic_name': 'semaglutide', 'company': 'Novo Nordisk', 'ticker': 'NVO', 'type': 'suggestion'},
                {'drug_name': 'Mounjaro', 'generic_name': 'tirzepatide', 'company': 'Eli Lilly', 'ticker': 'LLY', 'type': 'suggestion'},
            ]
            # Add suggestions that don't duplicate existing results
            for sug in suggestions:
                if not any(d['drug_name'] == sug['drug_name'] for d in drugs):
                    if len(drugs) < 5:
                        drugs.append(sug)
        
        return jsonify({'drugs': drugs[:10]})  # Limit to 10 results
    except Exception as e:
        logger.error(f"Error searching drugs: {e}")
        logger.error(traceback.format_exc())
        # Return empty results with 200 status
        return jsonify({'drugs': [], 'error': str(e)}), 200

@app.route('/api/executive_credibility/<ticker>')
def get_executive_credibility(ticker):
    """Get executive credibility for a company"""
    try:
        # Map ticker to company name
        stock_data = stock_intel.get_company_intelligence(ticker)
        
        if "error" in stock_data:
            return jsonify({'error': f'Invalid ticker: {ticker}', 'overall_credibility': 0})
        
        company_name = stock_data.get('company_name', ticker)
        
        # Get credibility data
        credibility = truth_tracker.get_company_credibility(company_name)
        
        # Ensure we have the expected structure
        if not isinstance(credibility, dict):
            credibility = {'overall_credibility': 0, 'total_promises': 0}
        
        return jsonify(credibility)
    except Exception as e:
        logger.error(f"Error getting executive credibility: {e}")
        return jsonify({'error': str(e), 'overall_credibility': 0})

@app.route('/api/fda_predictions/<ticker>')
def get_fda_predictions(ticker):
    """Get FDA predictions for a company"""
    try:
        # Map ticker to company name
        stock_data = stock_intel.get_company_intelligence(ticker)
        
        if "error" in stock_data:
            return jsonify({'error': f'Invalid ticker: {ticker}', 'submissions': []})
        
        company_name = stock_data.get('company_name', ticker)
        
        # Get FDA submissions data from stock intelligence (already has this)
        fda_data = stock_data.get('fda_submissions', {})
        
        # Format for frontend
        response = {
            'company': company_name,
            'ticker': ticker,
            'total_submissions': fda_data.get('total_submissions', 0),
            'pending_decisions': fda_data.get('pending_decisions', 0),
            'approvals': fda_data.get('approvals', 0),
            'crl_count': fda_data.get('complete_response_letters', 0),
            'approval_rate': fda_data.get('approval_rate', 'N/A'),
            'recent_submissions': fda_data.get('recent_submissions', [])
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error getting FDA predictions: {e}")
        return jsonify({'error': str(e), 'submissions': []})

@app.route('/api/stock_price/<ticker>')
def get_stock_price(ticker):
    """Get real-time stock price and comprehensive intelligence"""
    try:
        intelligence = stock_intel.get_company_intelligence(ticker)
        
        if "error" in intelligence:
            return jsonify({'error': intelligence['error']}), 400
        
        # Format financial health data for better display
        financial = intelligence.get('financial_health', {})
        
        return jsonify({
            'ticker': ticker,
            'company_name': intelligence.get('company_name'),
            'current_price': intelligence.get('current_price'),
            'market_cap': intelligence.get('market_cap'),
            '52_week_high': intelligence.get('52_week_high'),
            '52_week_low': intelligence.get('52_week_low'),
            'financial_health': {
                'cash_position': financial.get('cash_position', 'N/A'),
                'debt': financial.get('debt', 'N/A'),
                'burn_rate': financial.get('cash_burn_rate', 'N/A'),
                'runway': financial.get('runway_months', 'N/A'),
                'revenue': financial.get('revenue_ttm', 'N/A'),
                'margins': financial.get('gross_margins', 'N/A')
            },
            'pipeline': intelligence.get('pipeline', [])[:5],  # Top 5 pipeline items
            'recent_developments': intelligence.get('recent_developments', [])[:5],
            'clinical_trials': intelligence.get('clinical_trials', {}),
            'management_credibility': intelligence.get('management_credibility', {})
        })
    except Exception as e:
        logger.error(f"Error getting stock price: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Simplified Social Media Sentiment Platform")
    logger.info("📊 Access the platform at http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001) 