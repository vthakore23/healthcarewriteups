"""
Email sender for healthcare news reports
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from jinja2 import Template
import config

# SendGrid import (optional)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

logger = logging.getLogger(__name__)


class EmailSender:
    """Send email reports using SendGrid or SMTP"""
    
    def __init__(self):
        self.use_sendgrid = SENDGRID_AVAILABLE and config.SENDGRID_API_KEY
        
        if self.use_sendgrid:
            self.sg_client = SendGridAPIClient(config.SENDGRID_API_KEY)
            logger.info("Using SendGrid for email delivery")
        else:
            logger.info("Using SMTP for email delivery")
    
    def send_report(self, summaries, analyses, date=None):
        """Send the daily report email"""
        if date is None:
            date = datetime.now()
        
        subject = f"Healthcare News Summary - {date.strftime('%B %d, %Y')}"
        html_content = self._generate_html_content(summaries, analyses, date)
        text_content = self._generate_text_content(summaries, analyses, date)
        
        try:
            if self.use_sendgrid:
                return self._send_via_sendgrid(subject, html_content, text_content)
            else:
                return self._send_via_smtp(subject, html_content, text_content)
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            # Try fallback method
            if self.use_sendgrid:
                logger.info("Trying SMTP as fallback...")
                return self._send_via_smtp(subject, html_content, text_content)
            raise
    
    def _send_via_sendgrid(self, subject, html_content, text_content):
        """Send email using SendGrid API"""
        message = Mail(
            from_email=Email(config.EMAIL_FROM),
            to_emails=[To(email) for email in config.EMAIL_RECIPIENTS],
            subject=subject,
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )
        
        response = self.sg_client.send(message)
        logger.info(f"Email sent via SendGrid. Status code: {response.status_code}")
        return response.status_code == 202
    
    def _send_via_smtp(self, subject, html_content, text_content):
        """Send email using SMTP"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config.EMAIL_FROM
        msg['To'] = ', '.join(config.EMAIL_RECIPIENTS)
        
        # Attach parts
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            if config.SMTP_USERNAME and config.SMTP_PASSWORD:
                server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info("Email sent via SMTP")
        return True
    
    def _generate_html_content(self, summaries, analyses, date):
        """Generate HTML email content"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fafafa;
        }
        h1 {
            color: #2c5282;
            border-bottom: 3px solid #2c5282;
            padding-bottom: 15px;
            font-size: 2.2em;
            text-align: center;
        }
        h2 {
            color: #2d3748;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-left: 5px solid #3182ce;
            padding-left: 15px;
        }
        h3 {
            color: #1a365d;
            font-size: 1.3em;
            margin-bottom: 10px;
        }
        .summary {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 5px solid #3182ce;
            padding: 20px;
            margin: 25px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .analysis {
            background-color: #fff8e7;
            border: 1px solid #f6e05e;
            border-left: 5px solid #f39c12;
            padding: 25px;
            margin: 30px 0;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .article-title {
            font-size: 1.4em;
            font-weight: bold;
            color: #1a365d;
            margin-bottom: 15px;
            padding: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 6px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        .company-name {
            font-weight: bold;
            color: #2c5282;
            background-color: #e6fffa;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
            margin: 5px 0;
        }
        .news-event {
            font-style: italic;
            color: #718096;
            background-color: #f7fafc;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.9em;
        }
        .section-title {
            font-weight: bold;
            color: #2d3748;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .standout-points {
            background-color: #f0fff4;
            border-left: 4px solid #38a169;
            padding: 15px;
            margin: 15px 0;
            border-radius: 6px;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #e2e8f0;
            font-size: 0.9em;
            color: #718096;
            text-align: center;
        }
        .highlight {
            background-color: #fff5f5;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 3px solid #f56565;
        }
        .article-link {
            display: inline-block;
            background-color: #3182ce;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            margin: 10px 0;
            font-weight: 500;
        }
        .article-link:hover {
            background-color: #2c5282;
        }
        .stats-bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }
        .analysis-header {
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
            color: white;
            padding: 15px;
            border-radius: 8px 8px 0 0;
            margin: -25px -25px 20px -25px;
            font-size: 1.2em;
            font-weight: bold;
        }
        .external-research {
            background-color: #e6f7ff;
            border-left: 4px solid #1890ff;
            padding: 12px;
            margin: 10px 0;
            border-radius: 4px;
            font-style: italic;
        }
        .source-citation {
            font-size: 0.9em;
            color: #666;
            background-color: #f5f5f5;
            padding: 8px;
            border-radius: 4px;
            margin: 8px 0;
        }
    </style>
</head>
<body>
    <h1>🧬 Daily Healthcare Investment Intelligence Report</h1>
    
    <div class="stats-bar">
        <strong>📊 Daily Summary:</strong> {{ summaries|length }} healthcare/biotech articles analyzed | {{ analyses|length }} detailed investment insights | Real-time research included
    </div>
    
    <p style="font-size: 1.1em; text-align: center; color: #4a5568; margin-bottom: 30px;">
        <strong>Daily healthcare and biotech news analysis from lifesciencereport.com/newsroom</strong><br>
        Structured using investment-grade format | Target: ~600 words per summary
    </p>
    
    <h2>📈 Daily Article Summaries</h2>
    <p style="background-color: #e6fffa; padding: 15px; border-radius: 8px; border-left: 4px solid #38b2ac;">
        <strong>🎯 Format:</strong> Each summary follows the exact investment analysis structure with "Standout Points" as the meatiest section containing all quantifiable data, mechanisms, and competitive differentiation.
    </p>
    
    {% for summary in summaries %}
    <div class="summary">
        <div class="article-title">
            📋 Article {{ loop.index }}: {{ summary.title }}
        </div>
        
        {% if summary.company_name %}
        <div class="company-name">🏢 Company: {{ summary.company_name }}</div>
        {% endif %}
        
        <a href="{{ summary.url }}" class="article-link" target="_blank">🔗 View Original Article</a>
        
        <div style="margin-top: 15px;">
            {% set summary_parts = summary.summary.split('Standout Points:') %}
            {% if summary_parts|length > 1 %}
                {{ summary_parts[0] | replace('\n\n', '</p><p>') | replace('\n', '<br>') | safe }}
                <div class="standout-points">
                    <div class="section-title">⭐ Standout Points (Meatiest Section):</div>
                    {% set remaining = summary_parts[1].split('Additional Developments:') %}
                    {{ remaining[0] | replace('\n\n', '</p><p>') | replace('\n', '<br>') | safe }}
                </div>
                {% if remaining|length > 1 %}
                    <div class="section-title">📈 Additional Developments:</div>
                    {{ remaining[1] | replace('\n\n', '</p><p>') | replace('\n', '<br>') | safe }}
                {% endif %}
            {% else %}
                {{ summary.summary | replace('\n\n', '</p><p>') | replace('\n', '<br>') | safe }}
            {% endif %}
        </div>
    </div>
    {% endfor %}
    
    {% if analyses %}
    <h2>🔍 Additional Analysis: Why These Events Are Interesting</h2>
    <p style="background-color: #fff8e7; padding: 15px; border-radius: 8px; border-left: 4px solid #f39c12;">
        <strong>🎯 Investment Focus:</strong> The following {{ analyses|length }} article(s) were selected for additional analysis focusing on <em>why they're interesting</em> and their <em>longer-term implications</em>. External research sources are cited when used.
    </p>
    
    {% for analysis in analyses %}
    <div class="analysis">
        <div class="analysis-header">
            💡 WHY INTERESTING & IMPLICATIONS: {{ analysis.title }}
            {% if analysis.company_name %}
            <br><span style="font-size: 0.9em; opacity: 0.9;">🏢 {{ analysis.company_name }}</span>
            {% endif %}
        </div>
        
        <div style="background-color: white; padding: 15px; border-radius: 6px; margin: 10px 0;">
            {% set analysis_text = analysis.analysis %}
            {% if 'According to' in analysis_text or 'Industry data' in analysis_text or 'Market research' in analysis_text %}
                <div class="external-research">
                    🔍 <strong>Note:</strong> This analysis includes external research sources beyond the original press release, properly cited within the text.
                </div>
            {% endif %}
            {{ analysis_text | replace('\n\n', '</p><p>') | replace('\n', '<br>') | safe }}
        </div>
    </div>
    {% endfor %}
    {% endif %}
    
    <div class="footer">
        <p><strong>🤖 Automated Healthcare Investment Intelligence Platform</strong></p>
        <p>Generated: {{ date }} | Structured per investment analysis format | Sources cited for external research</p>
        <p><em>Each summary targets ~600 words with "Standout Points" as the meatiest section containing all quantifiable data</em></p>
    </div>
</body>
</html>
        """)
        
        return template.render(
            date=date.strftime('%B %d, %Y'),
            summaries=summaries,
            analyses=analyses
        )
    
    def _generate_text_content(self, summaries, analyses, date):
        """Generate plain text email content"""
        template = Template("""
Healthcare News Summary - {{ date }}

Good morning,

Here is today's healthcare and biotech news summary from lifesciencereport.com:

==============================================================================
DAILY SUMMARIES
==============================================================================

{% for summary in summaries %}
{{ loop.index }}. {{ summary.title }}
   Link: {{ summary.url }}

{{ summary.summary }}

------------------------------------------------------------------------------
{% endfor %}

{% if analyses %}
==============================================================================
IN-DEPTH ANALYSIS
==============================================================================

The following {{ analyses|length }} article(s) were selected as particularly interesting:

{% for analysis in analyses %}
{{ analysis.title }}

ADDITIONAL ANALYSIS:
{{ analysis.analysis }}

------------------------------------------------------------------------------
{% endfor %}
{% endif %}

This report was automatically generated by the Healthcare News Automation system.
For questions or feedback, please reply to this email.
        """)
        
        return template.render(
            date=date.strftime('%B %d, %Y'),
            summaries=summaries,
            analyses=analyses
        ) 