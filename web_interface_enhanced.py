"""
Healthcare News Automation - Enhanced Web Interface with Stock Intelligence
Includes stock ticker lookup with Management Truth Tracker™ and FDA Analyzer
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import json
import threading
import time
from datetime import datetime, timedelta
import glob
import logging
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_ticker_intelligence import HealthcareCompanyIntelligence

app = Flask(__name__)
app.secret_key = 'healthcare-news-automation-secret-key'

# Global variable to track analysis status
analysis_status = {
    'running': False,
    'progress': 0,
    'message': '',
    'results': None,
    'error': None
}

def run_analysis_async():
    """Run analysis in background thread"""
    global analysis_status
    try:
        analysis_status['running'] = True
        analysis_status['progress'] = 10
        analysis_status['message'] = 'Starting analysis...'
        
        # Import and run the analysis
        from main_enhanced_intelligence import EnhancedHealthcareIntelligence
        
        analysis_status['progress'] = 20
        analysis_status['message'] = 'Initializing automation system...'
        
        automation = EnhancedHealthcareIntelligence()
        
        analysis_status['progress'] = 30
        analysis_status['message'] = 'Running healthcare news analysis...'
        
        # Run the analysis
        automation.run_daily_task(send_email=False)  # Disable email for web interface
        
        analysis_status['progress'] = 100
        analysis_status['message'] = 'Analysis complete!'
        analysis_status['results'] = True
        analysis_status['running'] = False
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Analysis error: {error_details}")
        analysis_status['error'] = str(e)
        analysis_status['running'] = False
        analysis_status['message'] = f'Error: {str(e)}'

@app.route('/')
def index():
    """Main dashboard"""
    # Get recent reports
    reports_dir = 'reports'
    recent_reports = []
    
    if os.path.exists(reports_dir):
        html_files = glob.glob(os.path.join(reports_dir, '*report_*.html'))
        json_files = glob.glob(os.path.join(reports_dir, '*report_*.json'))
        
        for html_file in sorted(html_files, reverse=True)[:10]:
            basename = os.path.basename(html_file)
            date_str = basename.replace('report_', '').replace('.html', '')
            json_file = html_file.replace('.html', '.json')
            
            report_info = {
                'date': date_str,
                'html_file': html_file,
                'json_file': json_file if os.path.exists(json_file) else None,
                'size': os.path.getsize(html_file),
                'created': datetime.fromtimestamp(os.path.getctime(html_file))
            }
            recent_reports.append(report_info)
    
    return render_template('dashboard_enhanced.html', 
                         reports=recent_reports,
                         status=analysis_status)

@app.route('/run-analysis', methods=['POST'])
def run_analysis_endpoint():
    """Start analysis in background"""
    global analysis_status
    
    if analysis_status['running']:
        return jsonify({'error': 'Analysis already running'}), 400
    
    # Reset status
    analysis_status = {
        'running': True,
        'progress': 0,
        'message': 'Initializing...',
        'results': None,
        'error': None
    }
    
    # Start analysis in background thread
    thread = threading.Thread(target=run_analysis_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Analysis started'})

@app.route('/status')
def get_status():
    """Get current analysis status"""
    return jsonify(analysis_status)

@app.route('/stock-lookup/<ticker>')
def stock_lookup(ticker):
    """Look up stock ticker intelligence"""
    try:
        intel = HealthcareCompanyIntelligence()
        data = intel.get_company_intelligence(ticker)
        
        if "error" in data:
            # Return proper JSON error response
            return jsonify(data), 200  # Return 200 with error in JSON, not 404
        
        # Format the response for web display
        response = {
            "success": True,
            "ticker": data["ticker"],
            "company_name": data["company_name"],
            "market_cap": data["market_cap"],
            "current_price": data["current_price"],
            "financial_health": data["financial_health"],
            "management_credibility": data["management_credibility"],
            "fda_submissions": data["fda_submissions"],
            "recent_developments": data["recent_developments"][:5] if data.get("recent_developments") else [],
            "investment_analysis": data["investment_analysis"],
            "description": data["description"][:500] + "..." if data.get("description") and len(data["description"]) > 500 else data.get("description", "")
        }
        
        return jsonify(response)
        
    except Exception as e:
        # Check if it's a rate limit error
        if "429" in str(e) or "Too Many Requests" in str(e):
            return jsonify({
                "error": "Rate limit reached. Please wait a moment and try again.",
                "ticker": ticker
            }), 200
        else:
            return jsonify({"error": f"Failed to fetch data: {str(e)}", "ticker": ticker}), 200

@app.route('/stock-report/<ticker>')
def stock_report(ticker):
    """Generate full stock report"""
    try:
        intel = HealthcareCompanyIntelligence()
        report = intel.generate_report(ticker)
        
        # Create a temporary HTML file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"reports/stock_report_{ticker}_{timestamp}.html"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{ticker} Healthcare Intelligence Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }}
        pre {{
            background: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 14px;
            border: 1px solid #e5e7eb;
        }}
        h1 {{
            color: #4f46e5;
            text-align: center;
            margin-bottom: 40px;
        }}
    </style>
</head>
<body>
    <h1>Healthcare Stock Intelligence Report</h1>
    <pre>{report}</pre>
</body>
</html>
"""
        
        os.makedirs('reports', exist_ok=True)
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        return send_file(report_file)
        
    except Exception as e:
        return f"Error generating report: {str(e)}", 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download report file"""
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/view-report/<path:filename>')
def view_report(filename):
    """View HTML report in browser"""
    try:
        return send_file(filename)
    except Exception as e:
        flash(f'Error viewing report: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/executive-check')
def executive_check():
    """Executive credibility check page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Executive Credibility Checker</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            input {
                padding: 15px;
                font-size: 16px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.3);
                background: rgba(255,255,255,0.2);
                color: white;
                width: 300px;
                margin: 10px;
            }
            input::placeholder {
                color: rgba(255,255,255,0.7);
            }
            button {
                padding: 15px 30px;
                font-size: 16px;
                background: #14b8a6;
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                margin: 10px;
            }
            button:hover {
                background: #0d9488;
            }
            a {
                color: #14b8a6;
                text-decoration: none;
            }
            .results {
                margin-top: 30px;
                text-align: left;
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 10px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🕵️ Executive Credibility Checker</h1>
            <p>Check the promise delivery track record of healthcare executives</p>
            
            <div>
                <input type="text" id="executiveName" placeholder="Executive Name (e.g., Stéphane Bancel)">
                <input type="text" id="companyName" placeholder="Company (e.g., Moderna, Inc.)">
                <br>
                <button onclick="checkCredibility()">Check Credibility</button>
                <button onclick="window.location.href='/'">Back to Dashboard</button>
            </div>
            
            <div id="results" class="results"></div>
        </div>
        
        <script>
            function checkCredibility() {
                const executive = document.getElementById('executiveName').value;
                const company = document.getElementById('companyName').value;
                const resultsDiv = document.getElementById('results');
                
                if (!executive || !company) {
                    alert('Please enter both executive name and company');
                    return;
                }
                
                resultsDiv.innerHTML = 'Loading...';
                resultsDiv.style.display = 'block';
                
                fetch(`/executive-credibility/${encodeURIComponent(executive)}?company=${encodeURIComponent(company)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            resultsDiv.innerHTML = `<p style="color: #ef4444;">Error: ${data.error}</p>`;
                            return;
                        }
                        
                        let html = `
                            <h2>${data.executive_name}</h2>
                            <p><strong>Company:</strong> ${company}</p>
                            <p><strong>Credibility Score:</strong> <span style="font-size: 1.5em; font-weight: bold; color: ${data.credibility_score >= 70 ? '#10b981' : data.credibility_score >= 40 ? '#f59e0b' : '#ef4444'}">${data.credibility_score.toFixed(0)}%</span></p>
                            <p><strong>Total Promises:</strong> ${data.total_promises}</p>
                            <p><strong>✅ Delivered On Time:</strong> ${data.promises_kept}</p>
                            <p><strong>⚠️ Delivered Late:</strong> ${data.promise_details?.late_promises?.length || 0}</p>
                            <p><strong>❌ Failed:</strong> ${data.promises_broken}</p>
                            <p><strong>⏳ Pending:</strong> ${data.promises_pending}</p>
                        `;
                        
                        // Show failed promises with details
                        if (data.promise_details?.failed_promises?.length > 0) {
                            html += `
                                <h3 style="color: #ef4444;">❌ Failed Promises (${data.promise_details.failed_promises.length})</h3>
                                <div style="background: rgba(239, 68, 68, 0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
                            `;
                            data.promise_details.failed_promises.slice(0, 5).forEach(p => {
                                const promiseDate = new Date(p.date_made).toLocaleDateString();
                                const deadlineDate = p.deadline ? new Date(p.deadline).toLocaleDateString() : 'No deadline';
                                html += `
                                    <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.2);">
                                        <p><strong>${promiseDate}:</strong> "${p.promise_text}"</p>
                                        <p style="font-size: 0.9em;">
                                            <strong>Type:</strong> ${p.promise_type.replace(/_/g, ' ').toUpperCase()}<br>
                                            <strong>Deadline:</strong> ${deadlineDate}<br>
                                            <strong>Source:</strong> ${p.source.startsWith('http') ? `<a href="${p.source}" target="_blank" style="color: #14b8a6;">${p.source}</a>` : p.source}<br>
                                            ${p.outcome_details ? `<strong>What happened:</strong> ${p.outcome_details}` : ''}
                                        </p>
                                    </div>
                                `;
                            });
                            html += '</div>';
                        }
                        
                        // Show late promises
                        if (data.promise_details?.late_promises?.length > 0) {
                            html += `
                                <h3 style="color: #f59e0b;">⚠️ Late Deliveries (${data.promise_details.late_promises.length})</h3>
                                <div style="background: rgba(245, 158, 11, 0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
                            `;
                            data.promise_details.late_promises.slice(0, 3).forEach(p => {
                                const promiseDate = new Date(p.date_made).toLocaleDateString();
                                html += `
                                    <div style="margin-bottom: 10px;">
                                        <p><strong>${promiseDate}:</strong> "${p.promise_text}"</p>
                                        <p style="font-size: 0.9em;">
                                            <strong>Delay:</strong> ${p.delay_days} days late<br>
                                            <strong>Source:</strong> ${p.source.startsWith('http') ? `<a href="${p.source}" target="_blank" style="color: #14b8a6;">${p.source}</a>` : p.source}
                                        </p>
                                    </div>
                                `;
                            });
                            html += '</div>';
                        }
                        
                        // Investment recommendation
                        html += `<div style="margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;">`;
                        if (data.credibility_score >= 70) {
                            html += `<p style="color: #10b981;"><strong>✅ Investment Recommendation:</strong> HIGH CREDIBILITY - Timeline guidance likely reliable</p>`;
                        } else if (data.credibility_score >= 40) {
                            html += `<p style="color: #f59e0b;"><strong>⚠️ Investment Recommendation:</strong> MODERATE CREDIBILITY - Add buffer to timeline expectations</p>`;
                        } else {
                            html += `<p style="color: #ef4444;"><strong>🚨 Investment Recommendation:</strong> LOW CREDIBILITY - Significant risk of delays/failures. Consider reducing position ahead of key deadlines.</p>`;
                        }
                        html += '</div>';
                        
                        resultsDiv.innerHTML = html;
                    })
                    .catch(error => {
                        resultsDiv.innerHTML = `<p style="color: #ef4444;">Error: ${error.message}</p>`;
                    });
            }
        </script>
    </body>
    </html>
    """

@app.route('/executive-credibility/<executive_name>')
def executive_credibility(executive_name):
    """Get executive credibility details"""
    try:
        company = request.args.get('company', '')
        
        from management_truth_tracker import ManagementTruthTracker
        tracker = ManagementTruthTracker()
        
        # Get promise details with company filter
        if company:
            promise_details = tracker.get_executive_promise_details(executive_name, company)
        else:
            # Try to get without company (will need to be handled)
            promise_details = {"all_promises": [], "error": "Company name required"}
        
        # Extract data from promise details
        all_promises = promise_details.get('all_promises', [])
        
        response = {
            "success": True,
            "executive_name": executive_name,
            "credibility_score": promise_details.get('credibility_summary', {}).get('credibility_score', 0),
            "total_promises": len(all_promises),
            "promises_kept": len(promise_details.get('on_time_promises', [])),
            "promises_broken": len(promise_details.get('failed_promises', [])),
            "promises_pending": len(promise_details.get('pending_promises', [])),
            "promise_details": promise_details,
            "recent_promises": all_promises[:10]  # Last 10 promises
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch credibility data: {str(e)}"}), 500

@app.route('/fda-analysis/<company_name>')
def fda_analysis(company_name):
    """Get FDA submission analysis for a company"""
    try:
        from fda_decision_analyzer import FDADecisionAnalyzer
        analyzer = FDADecisionAnalyzer()
        
        submissions = analyzer.get_company_submissions(company_name)
        
        if submissions:
            pending = [s for s in submissions if not s.get("decision_date")]
            approved = [s for s in submissions if s.get("decision_type") == "approval"]
            
            response = {
                "success": True,
                "company_name": company_name,
                "total_submissions": len(submissions),
                "pending_decisions": len(pending),
                "approvals": len(approved),
                "approval_rate": f"{(len(approved)/len(submissions)*100):.1f}%" if submissions else "0%",
                "submissions": submissions[:10]  # Last 10 submissions
            }
        else:
            response = {
                "success": True,
                "company_name": company_name,
                "total_submissions": 0,
                "pending_decisions": 0,
                "approvals": 0,
                "approval_rate": "N/A",
                "submissions": []
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch FDA data: {str(e)}"}), 500

def create_enhanced_dashboard_template():
    """Create the enhanced dashboard HTML template with stock ticker functionality"""
    # The template would be too long to include here, but it would include:
    # 1. Stock ticker search box
    # 2. Results display area
    # 3. Executive credibility lookup
    # 4. FDA submission tracker
    # 5. All existing functionality
    pass

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Healthcare Investment Intelligence Platform")
    print("📊 Enhanced interface with Stock Ticker Intelligence")
    print("🕵️ Management Truth Tracker™ integrated")
    print("🧬 FDA Decision Analyzer integrated")
    print("💡 Starting at http://localhost:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 