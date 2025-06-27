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
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c5282;
            border-bottom: 3px solid #2c5282;
            padding-bottom: 10px;
        }
        h2 {
            color: #2d3748;
            margin-top: 30px;
        }
        h3 {
            color: #4a5568;
        }
        .summary {
            background-color: #f7fafc;
            border-left: 4px solid #3182ce;
            padding: 15px;
            margin: 20px 0;
        }
        .analysis {
            background-color: #fef5e7;
            border-left: 4px solid #f39c12;
            padding: 15px;
            margin: 20px 0;
        }
        .company-name {
            font-weight: bold;
            color: #2c5282;
        }
        .news-event {
            font-style: italic;
            color: #718096;
        }
        .section-title {
            font-weight: bold;
            color: #2d3748;
            margin-top: 15px;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            font-size: 0.9em;
            color: #718096;
        }
        .highlight {
            background-color: #fff5f5;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>Healthcare News Summary - {{ date }}</h1>
    
    <p>Good morning,</p>
    <p>Here is today's healthcare and biotech news summary from lifesciencereport.com:</p>
    
    <h2>📊 Daily Summaries</h2>
    
    {% for summary in summaries %}
    <div class="summary">
        <h3>{{ loop.index }}. {{ summary.title }}</h3>
        <p><a href="{{ summary.url }}">View Original Article</a></p>
        
        {{ summary.summary | replace('\n\n', '</p><p>') | replace('\n', '<br>') | safe }}
    </div>
    {% endfor %}
    
    {% if analyses %}
    <h2>🔍 In-Depth Analysis</h2>
    <p>The following {{ analyses|length }} article(s) were selected as particularly interesting:</p>
    
    {% for analysis in analyses %}
    <div class="analysis">
        <h3>{{ analysis.title }}</h3>
        
        <div class="section-title">Additional Analysis:</div>
        {{ analysis.analysis | replace('\n\n', '</p><p>') | replace('\n', '<br>') | safe }}
    </div>
    {% endfor %}
    {% endif %}
    
    <div class="footer">
        <p>This report was automatically generated by the Healthcare News Automation system.</p>
        <p>For questions or feedback, please reply to this email.</p>
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