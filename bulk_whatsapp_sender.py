import pywhatkit as pwk
import csv
import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import urllib.parse

class BulkWhatsAppSender:
    def __init__(self, use_selenium: bool = False):
        """Initialize the bulk WhatsApp sender."""
        self.use_selenium = use_selenium
        self.driver = None
        self.wait = None
        
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
    
    def create_sample_whatsapp_contacts_csv(self, filename: str = "whatsapp_contacts.csv"):
        """Create a sample WhatsApp contacts CSV file."""
        sample_contacts = [
            {"name": "John Doe", "phone": "+1234567890", "country_code": "+1"},
            {"name": "Jane Smith", "phone": "+1987654321", "country_code": "+1"},
            {"name": "Bob Johnson", "phone": "+1555123456", "country_code": "+1"}
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if sample_contacts:
                writer = csv.DictWriter(f, fieldnames=sample_contacts[0].keys())
                writer.writeheader()
                writer.writerows(sample_contacts)
        
        print(f"Sample WhatsApp contacts file created: {filename}")
        print("Please update it with real contact information.")
        print("Note: Phone numbers should include country code (e.g., +1234567890)")
    
    def personalize_message(self, template: str, contact: Dict) -> str:
        """Personalize message template with contact information."""
        personalized = template
        for key, value in contact.items():
            placeholder = f"{{{key}}}"
            personalized = personalized.replace(placeholder, str(value))
        return personalized
    
    def format_phone_number(self, phone: str, country_code: str = "") -> str:
        """Format phone number for WhatsApp."""
        # Remove any non-digit characters except +
        phone = ''.join(char for char in phone if char.isdigit() or char == '+')
        
        # If no + and country code provided, add it
        if not phone.startswith('+') and country_code:
            if not country_code.startswith('+'):
                country_code = '+' + country_code
            phone = country_code + phone
        
        # Remove + for pywhatkit (it expects just numbers)
        return phone.replace('+', '')
    
    def send_message_pywhatkit(self, phone: str, message: str, hour: int, minute: int, wait_time: int = 20):
        """Send WhatsApp message using pywhatkit."""
        try:
            formatted_phone = self.format_phone_number(phone)
            pwk.sendwhatmsg(f"+{formatted_phone}", message, hour, minute, wait_time)
            return True
        except Exception as e:
            print(f"Error sending message to {phone}: {e}")
            return False
    
    def init_selenium_driver(self):
        """Initialize Selenium WebDriver for WhatsApp Web."""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--user-data-dir=./whatsapp_session")  # Save session
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
            
            # Open WhatsApp Web
            self.driver.get("https://web.whatsapp.com")
            print("WhatsApp Web opened. Please scan QR code if not already logged in.")
            
            # Wait for user to scan QR code and login
            try:
                # Wait for the main chat interface to load
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='chat-list']")))
                print("Successfully logged into WhatsApp Web!")
                return True
            except:
                print("Please scan the QR code and try again.")
                return False
                
        except Exception as e:
            print(f"Error initializing Selenium driver: {e}")
            return False
    
    def send_message_selenium(self, phone: str, message: str) -> bool:
        """Send WhatsApp message using Selenium."""
        try:
            formatted_phone = self.format_phone_number(phone)
            
            # Navigate to chat with the contact
            chat_url = f"https://web.whatsapp.com/send?phone={formatted_phone}&text={urllib.parse.quote(message)}"
            self.driver.get(chat_url)
            
            # Wait for the page to load and find send button
            time.sleep(3)
            
            # Try to find and click send button
            try:
                send_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='send']"))
                )
                send_button.click()
                time.sleep(2)
                return True
            except:
                # Alternative method - press Enter
                message_box = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='conversation-compose-box-input']")
                message_box.send_keys("\n")
                time.sleep(2)
                return True
                
        except Exception as e:
            print(f"Error sending message to {phone} via Selenium: {e}")
            return False
    
    def close_selenium_driver(self):
        """Close Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
    
    def send_bulk_messages_pywhatkit(self, contacts: List[Dict], message_template: str, 
                                   start_hour: int = None, start_minute: int = None, 
                                   interval_minutes: int = 2):
        """Send bulk WhatsApp messages using pywhatkit with scheduling."""
        successful_sends = 0
        failed_sends = 0
        
        # Set default start time if not provided
        if start_hour is None or start_minute is None:
            now = datetime.now() + timedelta(minutes=1)
            start_hour = now.hour
            start_minute = now.minute
        
        current_hour = start_hour
        current_minute = start_minute
        
        print(f"Starting bulk WhatsApp messaging to {len(contacts)} contacts...")
        print(f"First message scheduled for {current_hour:02d}:{current_minute:02d}")
        
        for i, contact in enumerate(contacts, 1):
            try:
                phone = contact.get("phone", "")
                if not phone:
                    print(f"✗ Skipping contact {i}: No phone number")
                    failed_sends += 1
                    continue
                
                # Personalize message
                personalized_message = self.personalize_message(message_template, contact)
                
                # Send message
                success = self.send_message_pywhatkit(
                    phone, personalized_message, current_hour, current_minute
                )
                
                if success:
                    successful_sends += 1
                    print(f"✓ Message {i}/{len(contacts)} scheduled for {contact.get('name', 'Unknown')} ({phone}) at {current_hour:02d}:{current_minute:02d}")
                else:
                    failed_sends += 1
                    print(f"✗ Failed to schedule message {i}/{len(contacts)} for {contact.get('name', 'Unknown')}")
                
                # Calculate next send time
                next_time = datetime.now().replace(hour=current_hour, minute=current_minute) + timedelta(minutes=interval_minutes)
                current_hour = next_time.hour
                current_minute = next_time.minute
                
            except Exception as e:
                failed_sends += 1
                print(f"✗ Error with contact {i}/{len(contacts)}: {e}")
        
        print(f"\nBulk WhatsApp messaging scheduled!")
        print(f"Successful: {successful_sends}")
        print(f"Failed: {failed_sends}")
        
        # Log results
        self.log_bulk_send_results(successful_sends, failed_sends, len(contacts), "pywhatkit")
        
        return successful_sends > 0
    
    def send_bulk_messages_selenium(self, contacts: List[Dict], message_template: str, delay_seconds: int = 5):
        """Send bulk WhatsApp messages using Selenium."""
        if not self.init_selenium_driver():
            return False
        
        successful_sends = 0
        failed_sends = 0
        
        print(f"Starting bulk WhatsApp messaging to {len(contacts)} contacts...")
        
        for i, contact in enumerate(contacts, 1):
            try:
                phone = contact.get("phone", "")
                if not phone:
                    print(f"✗ Skipping contact {i}: No phone number")
                    failed_sends += 1
                    continue
                
                # Personalize message
                personalized_message = self.personalize_message(message_template, contact)
                
                # Send message
                success = self.send_message_selenium(phone, personalized_message)
                
                if success:
                    successful_sends += 1
                    print(f"✓ Message {i}/{len(contacts)} sent to {contact.get('name', 'Unknown')} ({phone})")
                else:
                    failed_sends += 1
                    print(f"✗ Failed to send message {i}/{len(contacts)} to {contact.get('name', 'Unknown')}")
                
                # Add delay between messages
                if delay_seconds > 0:
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                failed_sends += 1
                print(f"✗ Error with contact {i}/{len(contacts)}: {e}")
        
        self.close_selenium_driver()
        
        print(f"\nBulk WhatsApp messaging completed!")
        print(f"Successful: {successful_sends}")
        print(f"Failed: {failed_sends}")
        
        # Log results
        self.log_bulk_send_results(successful_sends, failed_sends, len(contacts), "selenium")
        
        return successful_sends > 0
    
    def log_bulk_send_results(self, successful: int, failed: int, total: int, method: str):
        """Log bulk send results to a file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "total_contacts": total,
            "successful_sends": successful,
            "failed_sends": failed,
            "success_rate": f"{(successful/total)*100:.1f}%" if total > 0 else "0%"
        }
        
        log_file = "whatsapp_send_log.json"
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
    whatsapp_sender = BulkWhatsAppSender(use_selenium=False)  # Set to True for Selenium method
    
    # Create sample contacts file if it doesn't exist
    if not os.path.exists("whatsapp_contacts.csv"):
        whatsapp_sender.create_sample_whatsapp_contacts_csv()
    
    # Example: Load contacts and send bulk messages
    # contacts = whatsapp_sender.load_contacts_from_csv("whatsapp_contacts.csv")
    # message = """Hello {name}! 👋
    # 
    # Hope you're doing well! I wanted to share some exciting news with you.
    # 
    # Best regards!"""
    # 
    # # Using pywhatkit (scheduled messages)
    # whatsapp_sender.send_bulk_messages_pywhatkit(
    #     contacts, message, start_hour=14, start_minute=30, interval_minutes=2
    # )
    # 
    # # Or using Selenium (immediate sending)
    # # whatsapp_sender.use_selenium = True
    # # whatsapp_sender.send_bulk_messages_selenium(contacts, message, delay_seconds=10)