"""
Enhanced Web Interface with Social Media Sentiment Analysis
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import asyncio
import json
import os
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.utils

# Import existing modules
from stock_ticker_intelligence import HealthcareCompanyIntelligence
from management_truth_tracker import ManagementTruthTracker
from fda_decision_analyzer import FDADecisionAnalyzer
from social_media_sentiment import SocialMediaSentimentAnalyzer, DrugDatabase
from integrated_intelligence_system import IntegratedIntelligenceSystem

app = Flask(__name__)
CORS(app)

# Initialize components
stock_intel = HealthcareCompanyIntelligence()
truth_tracker = ManagementTruthTracker()
fda_analyzer = FDADecisionAnalyzer()
drug_db = DrugDatabase()
sentiment_analyzer = None  # Will be initialized asynchronously
intelligence_system = IntegratedIntelligenceSystem()

def init_sentiment_analyzer():
    """Initialize sentiment analyzer in async context"""
    global sentiment_analyzer
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sentiment_analyzer = SocialMediaSentimentAnalyzer()

# Initialize sentiment analyzer
init_sentiment_analyzer()

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('dashboard_social.html')

@app.route('/api/search_ticker', methods=['GET'])
def search_ticker():
    """Search for company by ticker"""
    ticker = request.args.get('ticker', '').upper()
    if not ticker:
        return jsonify({'error': 'No ticker provided'}), 400
    
    try:
        analysis = stock_intel.analyze_ticker(ticker)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def get_drug_sentiment(drug_name):
    """Get sentiment analysis for a specific drug"""
    try:
        if not sentiment_analyzer:
            return jsonify({'error': 'Sentiment analyzer not initialized'}), 500
        
        # Run async analysis
        analysis = await sentiment_analyzer.analyze_drug_sentiment(drug_name)
        
        # Create visualization data
        if 'sentiment_distribution' in analysis:
            sentiment_chart = create_sentiment_chart(analysis['sentiment_distribution'])
            analysis['sentiment_chart'] = sentiment_chart
        
        if 'platforms_analyzed' in analysis:
            platform_chart = create_platform_chart(analysis['platforms_analyzed'])
            analysis['platform_chart'] = platform_chart
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def get_company_sentiment(ticker):
    """Get sentiment analysis for all drugs from a company"""
    try:
        if not sentiment_analyzer:
            return jsonify({'error': 'Sentiment analyzer not initialized'}), 500
        
        # Run async analysis
        analysis = await sentiment_analyzer.analyze_company_drugs(ticker)
        
        # Add visualization data
        if 'drug_sentiments' in analysis:
            drug_comparison = create_drug_comparison_chart(analysis['drug_sentiments'])
            analysis['drug_comparison_chart'] = drug_comparison
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_drugs', methods=['GET'])
def search_drugs():
    """Search for drugs by name or company"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    try:
        # Search in drug database
        all_drugs = []
        
        # Search by drug name
        drugs_by_name = drug_db.find_drug(query)
        for drug in drugs_by_name:
            all_drugs.append({
                'drug_name': drug[0],
                'company': drug[1],
                'ticker': drug[2],
                'type': 'drug'
            })
        
        # Search by company ticker
        if len(query) <= 5:  # Likely a ticker
            company_drugs = drug_db.get_company_drugs(query.upper())
            for drug in company_drugs:
                all_drugs.append({
                    'drug_name': drug['drug_name'],
                    'company': query.upper(),
                    'ticker': query.upper(),
                    'type': 'company_drug'
                })
        
        # Remove duplicates
        seen = set()
        unique_drugs = []
        for drug in all_drugs:
            key = f"{drug['drug_name']}_{drug['ticker']}"
            if key not in seen:
                seen.add(key)
                unique_drugs.append(drug)
        
        return jsonify(unique_drugs[:10])  # Return top 10 results
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/executive_credibility/<ticker>')
def get_executive_credibility(ticker):
    """Get executive credibility analysis"""
    try:
        analysis = truth_tracker.analyze_company_credibility(ticker)
        
        # Add visualization
        if analysis and 'promises' in analysis:
            timeline_chart = create_promise_timeline(analysis['promises'])
            analysis['timeline_chart'] = timeline_chart
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fda_predictions/<ticker>')
def get_fda_predictions(ticker):
    """Get FDA decision predictions for a company"""
    try:
        company_drugs = fda_analyzer.get_company_pipeline(ticker)
        predictions = []
        
        for drug in company_drugs:
            if drug['phase'] in ['Phase 3', 'NDA/BLA']:
                prediction = fda_analyzer.predict_approval_probability(
                    drug['drug_name'],
                    drug['indication'],
                    drug['phase']
                )
                predictions.append(prediction)
        
        return jsonify({
            'ticker': ticker,
            'predictions': predictions,
            'pipeline_summary': company_drugs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/integrated_analysis/<ticker>')
def get_integrated_analysis(ticker):
    """Get comprehensive integrated analysis"""
    try:
        analysis = intelligence_system.generate_comprehensive_analysis(ticker)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Visualization helper functions
def create_sentiment_chart(sentiment_dist):
    """Create sentiment distribution chart"""
    categories = ['Very Positive', 'Positive', 'Neutral', 'Negative', 'Very Negative']
    values = [
        sentiment_dist.get('very_positive', 0),
        sentiment_dist.get('positive', 0),
        sentiment_dist.get('neutral', 0),
        sentiment_dist.get('negative', 0),
        sentiment_dist.get('very_negative', 0)
    ]
    
    colors = ['#2E7D32', '#66BB6A', '#FFC107', '#FF7043', '#D32F2F']
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=values,
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title='Sentiment Distribution',
        xaxis_title='Sentiment Category',
        yaxis_title='Number of Mentions',
        height=400,
        template='plotly_white'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_platform_chart(platform_data):
    """Create platform distribution chart"""
    platforms = list(platform_data.keys())
    values = list(platform_data.values())
    
    fig = go.Figure(data=[
        go.Pie(
            labels=platforms,
            values=values,
            hole=0.4,
            marker=dict(
                colors=['#1DA1F2', '#FF4500', '#4267B2', '#BD081C', '#0077B5']
            )
        )
    ])
    
    fig.update_layout(
        title='Mentions by Platform',
        height=400,
        template='plotly_white'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_drug_comparison_chart(drug_sentiments):
    """Create drug comparison chart"""
    drugs = []
    sentiments = []
    
    for drug, analysis in drug_sentiments.items():
        if 'average_sentiment' in analysis:
            drugs.append(drug)
            sentiments.append(analysis['average_sentiment'])
    
    # Sort by sentiment
    sorted_data = sorted(zip(drugs, sentiments), key=lambda x: x[1], reverse=True)
    drugs, sentiments = zip(*sorted_data) if sorted_data else ([], [])
    
    # Color based on sentiment
    colors = ['#2E7D32' if s > 0.3 else '#FFC107' if s > -0.3 else '#D32F2F' 
              for s in sentiments]
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(drugs),
            y=list(sentiments),
            marker_color=colors,
            text=[f"{s:.2f}" for s in sentiments],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title='Drug Sentiment Comparison',
        xaxis_title='Drug Name',
        yaxis_title='Average Sentiment Score',
        height=500,
        template='plotly_white',
        yaxis=dict(range=[-1, 1])
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_promise_timeline(promises):
    """Create executive promise timeline"""
    if not promises:
        return None
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(promises)
    df['promise_date'] = pd.to_datetime(df['promise_date'])
    df['deadline'] = pd.to_datetime(df['deadline'])
    
    # Create timeline
    fig = go.Figure()
    
    # Add promises
    for _, promise in df.iterrows():
        color = '#2E7D32' if promise['status'] == 'kept' else '#D32F2F' if promise['status'] == 'broken' else '#FFC107'
        
        fig.add_trace(go.Scatter(
            x=[promise['promise_date'], promise['deadline']],
            y=[promise['executive'], promise['executive']],
            mode='lines+markers',
            name=promise['promise'][:50] + '...',
            line=dict(color=color, width=3),
            marker=dict(size=10),
            hovertext=promise['promise']
        ))
    
    fig.update_layout(
        title='Executive Promise Timeline',
        xaxis_title='Date',
        yaxis_title='Executive',
        height=600,
        template='plotly_white',
        showlegend=False
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/stock_price/<ticker>')
def get_stock_price(ticker):
    """Get current stock price and recent performance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        history = stock.history(period="1mo")
        
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        
        return jsonify({
            'ticker': ticker,
            'current_price': current_price,
            'change': info.get('regularMarketChange', 0),
            'change_percent': info.get('regularMarketChangePercent', 0),
            'volume': info.get('volume', 0),
            'market_cap': info.get('marketCap', 0),
            'price_history': history['Close'].to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Background task runner for async routes
def run_async(coro):
    """Run async coroutine in Flask context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Replace async route decorators with proper wrappers
@app.route('/api/drug_sentiment/<drug_name>')
def drug_sentiment_wrapper(drug_name):
    return run_async(get_drug_sentiment(drug_name))

@app.route('/api/company_sentiment/<ticker>')
def company_sentiment_wrapper(ticker):
    return run_async(get_company_sentiment(ticker))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 