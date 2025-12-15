import time
import logging
import os
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(filename='security_log.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Notifier:
    def __init__(self):
        self.last_alert_time = 0
        self.alert_cooldown = 10  # Seconds between alerts
        self.safe_contacts = ["Authority (911)", "Guardian", "Nearby Volunteer"]
        self.recent_logs = [] # Store logs for UI
        
        # Twilio Configuration (Replace with your credentials or use Env Vars)
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID', 'YOUR_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN', 'YOUR_AUTH_TOKEN')
        self.from_phone = os.environ.get('TWILIO_FROM_PHONE', '+1234567890')
        self.to_phone = os.environ.get('TWILIO_TO_PHONE', '+9876543210')
        
        self.client = None
        try:
            if 'YOUR_' not in self.account_sid:
                self.client = Client(self.account_sid, self.auth_token)
                print(f" [SUCCESS] Twilio Client Initialized. Alerts will be sent to {self.to_phone}")
            else:
                 print(" [WARNING] Twilio credentials not found/default. SMS alerts disabled.")
        except Exception as e:
            print(f"Twilio Init Failed: {e}")

    def alert(self, emotion, score=None, alert_type="Emotion"):
        current_time = time.time()
        if current_time - self.last_alert_time > self.alert_cooldown:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Log to console
            print(f"\n[URGENT] {alert_type} Threat Detected at {timestamp}!")
            print(f"Trigger: {emotion.upper()}")
            
            # Simulate sending digital alerts
            self._send_digital_alerts(emotion, timestamp, alert_type)
            
            # Send Real Twilio SMS if configured
            if self.client:
                self._send_twilio_alert(emotion, timestamp, alert_type)
            
            # Log to file
            logging.warning(f"Threat Detected: {emotion}. Type: {alert_type}.")
            
            # Update UI Log
            log_entry = {
                "timestamp": timestamp,
                "message": f"Threat Detected: {alert_type} ({emotion})",
                "type": "alert"
            }
            self.recent_logs.insert(0, log_entry) # Prepend
            if len(self.recent_logs) > 10: self.recent_logs.pop()
            
            self.last_alert_time = current_time
            return True
        return False

    def _send_twilio_alert(self, emotion, timestamp, alert_type):
        try:
            message = self.client.messages.create(
                body=f"SOS ALERT! Threat ({alert_type}: {emotion}) detected at {timestamp}. Immediate assistance required.",
                from_=self.from_phone,
                to=self.to_phone
            )
            print(f" >> Twilio SMS Sent: {message.sid}")
            
            # Optional: Make a call
            # call = self.client.calls.create(...)
        except Exception as e:
            print(f" >> Twilio Send Failed: {e}")

    def _send_digital_alerts(self, emotion, timestamp, alert_type):
        print("--- Initiating Preventive Security Protocols ---")
        for contact in self.safe_contacts:
            print(f" >> Sending Alert to {contact}: 'Distress detected ({emotion}) at {timestamp}.'")
        print("--- Alerts Dispatched Successfully ---\n")
