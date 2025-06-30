#!/usr/bin/env python3
"""
Healthcare Investment Intelligence Service
Runs permanently with web interface and scheduled analysis
"""
import os
import sys
import time
import signal
import logging
from datetime import datetime, time as dt_time
import threading
import subprocess
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_interface import app
from main_enhanced_intelligence import EnhancedHealthcareIntelligence

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('healthcare_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HealthcareService:
    """Permanent service for healthcare intelligence platform"""
    
    def __init__(self):
        self.running = True
        self.web_process = None
        self.intelligence_engine = EnhancedHealthcareIntelligence()
        self.scheduled_times = [
            dt_time(7, 1),   # 7:01 AM
            dt_time(8, 0),   # 8:00 AM  
            dt_time(9, 0),   # 9:00 AM
        ]
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        if self.web_process:
            self.web_process.terminate()
            
    def start_web_interface(self):
        """Start the web interface in a separate process"""
        try:
            logger.info("Starting web interface on http://localhost:5001")
            # Use threading instead of subprocess for better integration
            def run_flask():
                app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
            
            web_thread = threading.Thread(target=run_flask, daemon=True)
            web_thread.start()
            logger.info("✅ Web interface started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start web interface: {e}")
            return False
    
    def should_run_analysis(self, current_time):
        """Check if it's time to run scheduled analysis"""
        for scheduled_time in self.scheduled_times:
            # Check if current time matches scheduled time (within 1 minute)
            if (current_time.hour == scheduled_time.hour and 
                current_time.minute == scheduled_time.minute):
                return True
        return False
    
    def run_scheduled_analysis(self):
        """Run the daily intelligence analysis"""
        try:
            logger.info("🚀 Starting scheduled intelligence analysis...")
            self.intelligence_engine.run_daily_intelligence(send_email=True)
            logger.info("✅ Scheduled analysis completed successfully")
        except Exception as e:
            logger.error(f"❌ Scheduled analysis failed: {e}")
    
    def run_service(self):
        """Main service loop"""
        logger.info("🎯 Healthcare Investment Intelligence Service Starting...")
        logger.info("=" * 60)
        logger.info("Features:")
        logger.info("  • Web Interface: http://localhost:5001")
        logger.info("  • Management Truth Tracker™")
        logger.info("  • FDA Decision Analyzer")
        logger.info("  • Automated Daily Analysis (7:01 AM, 8:00 AM, 9:00 AM)")
        logger.info("  • Real-time Market Intelligence")
        logger.info("=" * 60)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start web interface
        if not self.start_web_interface():
            logger.error("Failed to start web interface, exiting...")
            return False
        
        # Track last analysis to avoid duplicates
        last_analysis_day = None
        last_analysis_hour = None
        
        logger.info("🔄 Service running... Press Ctrl+C to stop")
        logger.info("📊 Access your dashboard at: http://localhost:5001")
        
        # Main service loop
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check if it's time for scheduled analysis
                if self.should_run_analysis(current_time):
                    # Avoid running multiple times in the same hour
                    if (last_analysis_day != current_time.date() or 
                        last_analysis_hour != current_time.hour):
                        
                        self.run_scheduled_analysis()
                        last_analysis_day = current_time.date()
                        last_analysis_hour = current_time.hour
                
                # Sleep for 30 seconds before checking again
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                self.running = False
            except Exception as e:
                logger.error(f"Service error: {e}")
                time.sleep(60)  # Wait a minute before retrying
        
        logger.info("🛑 Healthcare Investment Intelligence Service Stopped")
        return True

def main():
    """Main entry point"""
    service = HealthcareService()
    return service.run_service()

if __name__ == "__main__":
    sys.exit(0 if main() else 1) 