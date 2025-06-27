"""
Healthcare News Automation - Web Interface
Simple, beautiful interface for running news analysis and downloading reports
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import json
import threading
import time
from datetime import datetime, timedelta
import glob
from main_optimized import main as run_analysis
import logging

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
        
        # Run the main analysis
        results = run_analysis(
            demo_mode=False,
            schedule_mode=False,
            test_email=False,
            send_email=False  # Explicitly disable email
        )
        
        analysis_status['progress'] = 100
        analysis_status['message'] = 'Analysis complete!'
        analysis_status['results'] = results
        analysis_status['running'] = False
        
    except Exception as e:
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
        html_files = glob.glob(os.path.join(reports_dir, 'report_*.html'))
        json_files = glob.glob(os.path.join(reports_dir, 'report_*.json'))
        
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
    
    return render_template('dashboard.html', 
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

def create_dashboard_template():
    """Create the dashboard HTML template"""
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Healthcare Writeups - Daily Analysis Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #2c5aa0 0%, #1e3c72 25%, #2a3b70 50%, #1a237e 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="dna" x="0" y="0" width="50" height="50" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="2" fill="rgba(255,255,255,0.03)"/><circle cx="12.5" cy="12.5" r="1" fill="rgba(255,255,255,0.02)"/><circle cx="37.5" cy="37.5" r="1" fill="rgba(255,255,255,0.02)"/></pattern></defs><rect width="100" height="100" fill="url(%23dna)"/></svg>') repeat;
            z-index: -1;
            pointer-events: none;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 24px;
            padding: 35px;
            box-shadow: 0 25px 60px rgba(0,0,0,0.15), 0 0 0 1px rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .header {
            text-align: center;
            margin-bottom: 45px;
            padding-bottom: 25px;
            border-bottom: 3px solid #e3f2fd;
            position: relative;
        }
        
        .header::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 3px;
            background: linear-gradient(90deg, #1976d2, #42a5f5);
            border-radius: 3px;
        }
        
        .header h1 {
            font-size: 2.8em;
            background: linear-gradient(135deg, #1565c0, #1976d2, #42a5f5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 12px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        .header p {
            font-size: 1.3em;
            color: #546e7a;
            font-weight: 400;
        }
        
        .medical-icon {
            display: inline-block;
            margin-right: 12px;
            font-size: 1.1em;
            color: #1976d2;
        }
        
        .controls {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #1565c0, #1976d2, #1e88e5);
            color: white;
            position: relative;
            overflow: hidden;
        }
        
        .btn-primary::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.6s;
        }
        
        .btn-primary:hover::before {
            left: 100%;
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(25, 118, 210, 0.4);
            background: linear-gradient(135deg, #1976d2, #1e88e5, #2196f3);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #455a64, #546e7a);
            color: white;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .btn-secondary:hover {
            background: linear-gradient(135deg, #546e7a, #607d8b);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(84, 110, 122, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .status-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            border-left: 5px solid #3498db;
        }
        
        .progress-bar {
            width: 100%;
            height: 10px;
            background: #ecf0f1;
            border-radius: 5px;
            overflow: hidden;
            margin: 15px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            transition: width 0.3s ease;
        }
        
        .reports-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .report-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .report-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        
        .report-date {
            font-size: 1.1em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .report-meta {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 15px;
        }
        
        .report-actions {
            display: flex;
            gap: 10px;
        }
        
        .btn-small {
            padding: 8px 16px;
            font-size: 14px;
        }
        
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .emoji {
            font-size: 1.2em;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="medical-icon">🧬</span>Healthcare Writeups<span class="medical-icon">📊</span></h1>
            <p>AI-Powered Daily Healthcare News Analysis & Investment Intelligence</p>
        </div>
        
        <div class="controls">
            <button id="runAnalysis" class="btn btn-primary" onclick="runAnalysis()">
                <span class="emoji">🔬</span>
                Generate Daily Writeups
            </button>
            <button class="btn btn-secondary" onclick="location.reload()">
                <span class="emoji">📈</span>
                Refresh Dashboard
            </button>
        </div>
        
        <div id="statusCard" class="status-card" style="display: none;">
            <h3 id="statusMessage">Ready to analyze</h3>
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill" style="width: 0%"></div>
            </div>
            <p id="statusDetails"></p>
        </div>
        
        {% if reports %}
        <div class="reports-section">
            <h2>🗂️ Healthcare Analysis Archive</h2>
            <div class="reports-grid">
                {% for report in reports %}
                <div class="report-card">
                    <div class="report-date">📅 {{ report.date }}</div>
                    <div class="report-meta">
                        <span class="medical-icon">🕒</span>Generated: {{ report.created.strftime('%I:%M %p') }}<br>
                        <span class="medical-icon">📊</span>Size: {{ "%.1f"|format(report.size/1024) }} KB
                    </div>
                    <div class="report-actions">
                        <a href="{{ url_for('view_report', filename=report.html_file) }}" 
                           class="btn btn-primary btn-small" target="_blank">
                            <span class="emoji">🔬</span>
                            View Analysis
                        </a>
                        <a href="{{ url_for('download_file', filename=report.html_file) }}" 
                           class="btn btn-secondary btn-small">
                            <span class="emoji">📋</span>
                            Download Report
                        </a>
                        {% if report.json_file %}
                        <a href="{{ url_for('download_file', filename=report.json_file) }}" 
                           class="btn btn-secondary btn-small">
                            <span class="emoji">🧬</span>
                            Raw Data
                        </a>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% else %}
        <div class="alert alert-info">
            <strong>🔬 Ready for Analysis!</strong> Generate your first healthcare writeups to begin tracking market intelligence.
        </div>
        {% endif %}
    </div>
    
    <script>
        let statusInterval;
        
        function runAnalysis() {
            const button = document.getElementById('runAnalysis');
            const statusCard = document.getElementById('statusCard');
            
            button.disabled = true;
            button.innerHTML = '<div class="loading"></div> Analyzing Healthcare Market...';
            statusCard.style.display = 'block';
            
            fetch('/run-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Start polling for status updates
                statusInterval = setInterval(checkStatus, 2000);
            })
            .catch(error => {
                button.disabled = false;
                button.innerHTML = '<span class="emoji">🚀</span> Run Full Analysis';
                alert('Error starting analysis: ' + error.message);
            });
        }
        
        function checkStatus() {
            fetch('/status')
            .then(response => response.json())
            .then(status => {
                const statusMessage = document.getElementById('statusMessage');
                const progressFill = document.getElementById('progressFill');
                const statusDetails = document.getElementById('statusDetails');
                const button = document.getElementById('runAnalysis');
                
                statusMessage.textContent = status.message;
                progressFill.style.width = status.progress + '%';
                
                if (!status.running) {
                    clearInterval(statusInterval);
                    button.disabled = false;
                    button.innerHTML = '<span class="emoji">🚀</span> Run Full Analysis';
                    
                    if (status.error) {
                        statusDetails.textContent = 'Error: ' + status.error;
                        statusDetails.style.color = '#e74c3c';
                    } else if (status.results) {
                        statusDetails.textContent = 'Analysis completed! Refresh to see new reports.';
                        statusDetails.style.color = '#27ae60';
                        
                        // Auto-refresh after 3 seconds
                        setTimeout(() => {
                            location.reload();
                        }, 3000);
                    }
                }
            })
            .catch(error => {
                console.error('Error checking status:', error);
            });
        }
    </script>
</body>
</html>'''
    
    # Write the template
    with open('templates/dashboard.html', 'w') as f:
        f.write(template_content)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML template
    create_dashboard_template()
    
    print("🚀 Healthcare News Automation Interface")
    print("📊 Starting web interface at http://localhost:5001")
    print("💡 Use this interface to run analysis and download reports")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 