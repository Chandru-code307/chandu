import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv
import json
import os
from typing import List, Dict, Optional
import time
from datetime import datetime

class BulkEmailSender:
    def __init__(self, config_file: str = "email_config.json"):
        """Initialize the bulk email sender with configuration."""
        self.config_file = config_file
        self.config = self.load_config()
        self.smtp_server = None
        
    def load_config(self) -> Dict:
        """Load email configuration from JSON file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default config file
            default_config = {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email": "",
                "password": "",
                "use_tls": True
            }
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Created default config file: {self.config_file}")
            print("Please update it with your email credentials.")
            return default_config
    
    def update_config(self, email: str, password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        """Update email configuration."""
        self.config.update({
            "email": email,
            "password": password,
            "smtp_server": smtp_server,
            "smtp_port": smtp_port
        })
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
        print("Configuration updated successfully!")
    
    def connect_smtp(self):
        """Establish SMTP connection."""
        try:
            self.smtp_server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            if self.config.get("use_tls", True):
                self.smtp_server.starttls()
            self.smtp_server.login(self.config["email"], self.config["password"])
            print("SMTP connection established successfully!")
            return True
        except Exception as e:
            print(f"Failed to connect to SMTP server: {e}")
            return False
    
    def disconnect_smtp(self):
        """Close SMTP connection."""
        if self.smtp_server:
            self.smtp_server.quit()
            self.smtp_server = None
            print("SMTP connection closed.")
    
    def load_contacts_from_csv(self, csv_file: str) -> List[Dict]:
        """Load contacts from CSV file."""
        contacts = []
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    contacts.append(row)
            print(f"Loaded {len(contacts)} contacts from {csv_file}")
            return contacts
        except Exception as e:
            print(f"Error loading contacts from CSV: {e}")
            return []
    
    def create_sample_contacts_csv(self, filename: str = "contacts.csv"):
        """Create a sample contacts CSV file."""
        sample_contacts = [
            {"name": "John Doe", "email": "john@example.com", "company": "Tech Corp"},
            {"name": "Jane Smith", "email": "jane@example.com", "company": "Design Studio"},
            {"name": "Bob Johnson", "email": "bob@example.com", "company": "Marketing Inc"}
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if sample_contacts:
                writer = csv.DictWriter(f, fieldnames=sample_contacts[0].keys())
                writer.writeheader()
                writer.writerows(sample_contacts)
        
        print(f"Sample contacts file created: {filename}")
        print("Please update it with real contact information.")
    
    def personalize_message(self, template: str, contact: Dict) -> str:
        """Personalize message template with contact information."""
        personalized = template
        for key, value in contact.items():
            placeholder = f"{{{key}}}"
            personalized = personalized.replace(placeholder, str(value))
        return personalized
    
    def send_bulk_emails(self, contacts: List[Dict], subject: str, message_template: str, 
                        attachments: Optional[List[str]] = None, delay_seconds: int = 1):
        """Send bulk emails to a list of contacts."""
        if not self.connect_smtp():
            return False
        
        successful_sends = 0
        failed_sends = 0
        
        print(f"Starting bulk email sending to {len(contacts)} contacts...")
        
        for i, contact in enumerate(contacts, 1):
            try:
                # Create message
                msg = MIMEMultipart()
                msg['From'] = self.config["email"]
                msg['To'] = contact.get("email", "")
                msg['Subject'] = self.personalize_message(subject, contact)
                
                # Personalize message content
                personalized_message = self.personalize_message(message_template, contact)
                msg.attach(MIMEText(personalized_message, 'plain'))
                
                # Add attachments if provided
                if attachments:
                    for file_path in attachments:
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as attachment:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attachment.read())
                                encoders.encode_base64(part)
                                part.add_header(
                                    'Content-Disposition',
                                    f'attachment; filename= {os.path.basename(file_path)}'
                                )
                                msg.attach(part)
                
                # Send email
                self.smtp_server.send_message(msg)
                successful_sends += 1
                print(f"✓ Email {i}/{len(contacts)} sent to {contact.get('name', 'Unknown')} ({contact.get('email', 'No email')})")
                
                # Add delay to avoid overwhelming the server
                if delay_seconds > 0:
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                failed_sends += 1
                print(f"✗ Failed to send email {i}/{len(contacts)} to {contact.get('name', 'Unknown')}: {e}")
        
        self.disconnect_smtp()
        
        print(f"\nBulk email sending completed!")
        print(f"Successful: {successful_sends}")
        print(f"Failed: {failed_sends}")
        
        # Log results
        self.log_bulk_send_results(successful_sends, failed_sends, len(contacts))
        
        return successful_sends > 0
    
    def log_bulk_send_results(self, successful: int, failed: int, total: int):
        """Log bulk send results to a file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "total_contacts": total,
            "successful_sends": successful,
            "failed_sends": failed,
            "success_rate": f"{(successful/total)*100:.1f}%" if total > 0 else "0%"
        }
        
        log_file = "email_send_log.json"
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        print(f"Results logged to {log_file}")

# Example usage
if __name__ == "__main__":
    # Initialize sender
    email_sender = BulkEmailSender()
    
    # Create sample files if they don't exist
    if not os.path.exists("contacts.csv"):
        email_sender.create_sample_contacts_csv()
    
    # Example: Update configuration (replace with your actual credentials)
    # email_sender.update_config("your_email@gmail.com", "your_app_password")
    
    # Example: Load contacts and send bulk emails
    # contacts = email_sender.load_contacts_from_csv("contacts.csv")
    # subject = "Hello {name}!"
    # message = """Dear {name},
    # 
    # I hope this email finds you well. I wanted to reach out regarding exciting opportunities at {company}.
    # 
    # Best regards,
    # Your Name"""
    # 
    # email_sender.send_bulk_emails(contacts, subject, message, delay_seconds=2)