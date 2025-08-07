import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import json
from datetime import datetime, timedelta
from bulk_email_sender import BulkEmailSender
from bulk_whatsapp_sender import BulkWhatsAppSender

class BulkMessengerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Messenger - Email & WhatsApp")
        self.root.geometry("800x600")
        
        # Initialize senders
        self.email_sender = BulkEmailSender()
        self.whatsapp_sender = BulkWhatsAppSender()
        
        # Variables
        self.contacts_file = tk.StringVar()
        self.email_subject = tk.StringVar()
        self.message_template = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Email tab
        email_frame = ttk.Frame(notebook)
        notebook.add(email_frame, text="Email Bulk Sender")
        self.setup_email_tab(email_frame)
        
        # WhatsApp tab
        whatsapp_frame = ttk.Frame(notebook)
        notebook.add(whatsapp_frame, text="WhatsApp Bulk Sender")
        self.setup_whatsapp_tab(whatsapp_frame)
        
        # Settings tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        self.setup_settings_tab(settings_frame)
        
        # Logs tab
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Logs")
        self.setup_logs_tab(logs_frame)
    
    def setup_email_tab(self, parent):
        """Setup email bulk sender tab."""
        # Email configuration frame
        config_frame = ttk.LabelFrame(parent, text="Email Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(config_frame, text="SMTP Server:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.smtp_server_var = tk.StringVar(value="smtp.gmail.com")
        ttk.Entry(config_frame, textvariable=self.smtp_server_var, width=30).grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.email_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.email_var, width=30).grid(row=1, column=1, padx=5)
        
        ttk.Label(config_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.email_password_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.email_password_var, width=30, show="*").grid(row=2, column=1, padx=5)
        
        ttk.Button(config_frame, text="Test Connection", command=self.test_email_connection).grid(row=3, column=1, pady=5)
        
        # Contacts frame
        contacts_frame = ttk.LabelFrame(parent, text="Contacts", padding=10)
        contacts_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(contacts_frame, text="Contacts File:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(contacts_frame, textvariable=self.contacts_file, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(contacts_frame, text="Browse", command=self.browse_contacts_file).grid(row=0, column=2, padx=5)
        ttk.Button(contacts_frame, text="Create Sample", command=self.create_sample_email_contacts).grid(row=0, column=3, padx=5)
        
        # Message frame
        message_frame = ttk.LabelFrame(parent, text="Email Message", padding=10)
        message_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(message_frame, text="Subject:").pack(anchor=tk.W)
        ttk.Entry(message_frame, textvariable=self.email_subject, width=60).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(message_frame, text="Message Template (use {name}, {email}, {company} for personalization):").pack(anchor=tk.W)
        self.email_message_text = scrolledtext.ScrolledText(message_frame, height=8, width=70)
        self.email_message_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Send frame
        send_frame = ttk.Frame(parent)
        send_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(send_frame, text="Delay between emails (seconds):").pack(side=tk.LEFT, padx=5)
        self.email_delay_var = tk.StringVar(value="2")
        ttk.Entry(send_frame, textvariable=self.email_delay_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(send_frame, text="Send Bulk Emails", command=self.send_bulk_emails).pack(side=tk.RIGHT, padx=5)
    
    def setup_whatsapp_tab(self, parent):
        """Setup WhatsApp bulk sender tab."""
        # Method selection frame
        method_frame = ttk.LabelFrame(parent, text="WhatsApp Method", padding=10)
        method_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.whatsapp_method_var = tk.StringVar(value="pywhatkit")
        ttk.Radiobutton(method_frame, text="PyWhatKit (Scheduled)", variable=self.whatsapp_method_var, value="pywhatkit").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(method_frame, text="Selenium (Immediate)", variable=self.whatsapp_method_var, value="selenium").pack(side=tk.LEFT, padx=10)
        
        # Contacts frame
        wa_contacts_frame = ttk.LabelFrame(parent, text="WhatsApp Contacts", padding=10)
        wa_contacts_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(wa_contacts_frame, text="Contacts File:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.wa_contacts_file = tk.StringVar()
        ttk.Entry(wa_contacts_frame, textvariable=self.wa_contacts_file, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(wa_contacts_frame, text="Browse", command=self.browse_wa_contacts_file).grid(row=0, column=2, padx=5)
        ttk.Button(wa_contacts_frame, text="Create Sample", command=self.create_sample_wa_contacts).grid(row=0, column=3, padx=5)
        
        # Scheduling frame (for PyWhatKit)
        schedule_frame = ttk.LabelFrame(parent, text="Scheduling (PyWhatKit Only)", padding=10)
        schedule_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(schedule_frame, text="Start Hour:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.start_hour_var = tk.StringVar(value=str((datetime.now() + timedelta(minutes=1)).hour))
        ttk.Entry(schedule_frame, textvariable=self.start_hour_var, width=5).grid(row=0, column=1, padx=5)
        
        ttk.Label(schedule_frame, text="Start Minute:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.start_minute_var = tk.StringVar(value=str((datetime.now() + timedelta(minutes=1)).minute))
        ttk.Entry(schedule_frame, textvariable=self.start_minute_var, width=5).grid(row=0, column=3, padx=5)
        
        ttk.Label(schedule_frame, text="Interval (minutes):").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.interval_var = tk.StringVar(value="2")
        ttk.Entry(schedule_frame, textvariable=self.interval_var, width=5).grid(row=0, column=5, padx=5)
        
        # Message frame
        wa_message_frame = ttk.LabelFrame(parent, text="WhatsApp Message", padding=10)
        wa_message_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(wa_message_frame, text="Message Template (use {name}, {phone} for personalization):").pack(anchor=tk.W)
        self.wa_message_text = scrolledtext.ScrolledText(wa_message_frame, height=8, width=70)
        self.wa_message_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Send frame
        wa_send_frame = ttk.Frame(parent)
        wa_send_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(wa_send_frame, text="Delay between messages (seconds):").pack(side=tk.LEFT, padx=5)
        self.wa_delay_var = tk.StringVar(value="5")
        ttk.Entry(wa_send_frame, textvariable=self.wa_delay_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(wa_send_frame, text="Send Bulk WhatsApp", command=self.send_bulk_whatsapp).pack(side=tk.RIGHT, padx=5)
    
    def setup_settings_tab(self, parent):
        """Setup settings tab."""
        # Email settings
        email_settings_frame = ttk.LabelFrame(parent, text="Default Email Settings", padding=10)
        email_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(email_settings_frame, text="These settings are saved automatically when you test the connection.").pack(anchor=tk.W)
        
        # Sample messages
        samples_frame = ttk.LabelFrame(parent, text="Sample Templates", padding=10)
        samples_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(samples_frame, text="Load Email Template", command=self.load_email_template).pack(pady=5)
        ttk.Button(samples_frame, text="Load WhatsApp Template", command=self.load_whatsapp_template).pack(pady=5)
        
        # File management
        files_frame = ttk.LabelFrame(parent, text="File Management", padding=10)
        files_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(files_frame, text="Open Logs Folder", command=self.open_logs_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(files_frame, text="Clear All Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
    
    def setup_logs_tab(self, parent):
        """Setup logs tab."""
        # Log display
        self.log_text = scrolledtext.ScrolledText(parent, height=20, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control frame
        log_control_frame = ttk.Frame(parent)
        log_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_control_frame, text="Refresh Email Logs", command=self.refresh_email_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_control_frame, text="Refresh WhatsApp Logs", command=self.refresh_whatsapp_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_control_frame, text="Clear Display", command=self.clear_log_display).pack(side=tk.RIGHT, padx=5)
    
    def browse_contacts_file(self):
        """Browse for email contacts file."""
        filename = filedialog.askopenfilename(
            title="Select Email Contacts CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.contacts_file.set(filename)
    
    def browse_wa_contacts_file(self):
        """Browse for WhatsApp contacts file."""
        filename = filedialog.askopenfilename(
            title="Select WhatsApp Contacts CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.wa_contacts_file.set(filename)
    
    def create_sample_email_contacts(self):
        """Create sample email contacts file."""
        self.email_sender.create_sample_contacts_csv()
        self.contacts_file.set("contacts.csv")
        messagebox.showinfo("Success", "Sample email contacts file created: contacts.csv")
    
    def create_sample_wa_contacts(self):
        """Create sample WhatsApp contacts file."""
        self.whatsapp_sender.create_sample_whatsapp_contacts_csv()
        self.wa_contacts_file.set("whatsapp_contacts.csv")
        messagebox.showinfo("Success", "Sample WhatsApp contacts file created: whatsapp_contacts.csv")
    
    def test_email_connection(self):
        """Test email connection."""
        if not self.email_var.get() or not self.email_password_var.get():
            messagebox.showerror("Error", "Please enter email and password")
            return
        
        self.email_sender.update_config(
            self.email_var.get(),
            self.email_password_var.get(),
            self.smtp_server_var.get()
        )
        
        success = self.email_sender.connect_smtp()
        if success:
            self.email_sender.disconnect_smtp()
            messagebox.showinfo("Success", "Email connection successful!")
        else:
            messagebox.showerror("Error", "Failed to connect to email server")
    
    def send_bulk_emails(self):
        """Send bulk emails in a separate thread."""
        if not self.contacts_file.get():
            messagebox.showerror("Error", "Please select a contacts file")
            return
        
        if not self.email_subject.get() or not self.email_message_text.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "Please enter subject and message")
            return
        
        def email_thread():
            try:
                contacts = self.email_sender.load_contacts_from_csv(self.contacts_file.get())
                if not contacts:
                    messagebox.showerror("Error", "No contacts loaded")
                    return
                
                message = self.email_message_text.get("1.0", tk.END).strip()
                delay = int(self.email_delay_var.get()) if self.email_delay_var.get().isdigit() else 2
                
                success = self.email_sender.send_bulk_emails(
                    contacts, self.email_subject.get(), message, delay_seconds=delay
                )
                
                if success:
                    messagebox.showinfo("Success", "Bulk emails sent successfully!")
                else:
                    messagebox.showerror("Error", "Failed to send bulk emails")
                    
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        threading.Thread(target=email_thread, daemon=True).start()
    
    def send_bulk_whatsapp(self):
        """Send bulk WhatsApp messages in a separate thread."""
        if not self.wa_contacts_file.get():
            messagebox.showerror("Error", "Please select a WhatsApp contacts file")
            return
        
        if not self.wa_message_text.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "Please enter a message")
            return
        
        def whatsapp_thread():
            try:
                contacts = self.whatsapp_sender.load_contacts_from_csv(self.wa_contacts_file.get())
                if not contacts:
                    messagebox.showerror("Error", "No contacts loaded")
                    return
                
                message = self.wa_message_text.get("1.0", tk.END).strip()
                method = self.whatsapp_method_var.get()
                
                if method == "pywhatkit":
                    start_hour = int(self.start_hour_var.get()) if self.start_hour_var.get().isdigit() else None
                    start_minute = int(self.start_minute_var.get()) if self.start_minute_var.get().isdigit() else None
                    interval = int(self.interval_var.get()) if self.interval_var.get().isdigit() else 2
                    
                    success = self.whatsapp_sender.send_bulk_messages_pywhatkit(
                        contacts, message, start_hour, start_minute, interval
                    )
                else:
                    delay = int(self.wa_delay_var.get()) if self.wa_delay_var.get().isdigit() else 5
                    success = self.whatsapp_sender.send_bulk_messages_selenium(
                        contacts, message, delay
                    )
                
                if success:
                    messagebox.showinfo("Success", "Bulk WhatsApp messages sent/scheduled successfully!")
                else:
                    messagebox.showerror("Error", "Failed to send bulk WhatsApp messages")
                    
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        threading.Thread(target=whatsapp_thread, daemon=True).start()
    
    def load_email_template(self):
        """Load sample email template."""
        template = """Dear {name},

I hope this email finds you well. I wanted to reach out to discuss some exciting opportunities that might interest you.

As someone working at {company}, I believe you'd find our new services particularly valuable.

Please feel free to reach out if you'd like to learn more.

Best regards,
Your Name"""
        
        self.email_subject.set("Exciting Opportunity for {name}")
        self.email_message_text.delete("1.0", tk.END)
        self.email_message_text.insert("1.0", template)
    
    def load_whatsapp_template(self):
        """Load sample WhatsApp template."""
        template = """Hello {name}! 👋

Hope you're doing well! I wanted to share some exciting news with you.

Let me know if you'd like to chat more about it!

Best regards! 😊"""
        
        self.wa_message_text.delete("1.0", tk.END)
        self.wa_message_text.insert("1.0", template)
    
    def refresh_email_logs(self):
        """Refresh email logs display."""
        try:
            if os.path.exists("email_send_log.json"):
                with open("email_send_log.json", 'r') as f:
                    logs = json.load(f)
                
                self.log_text.delete("1.0", tk.END)
                self.log_text.insert(tk.END, "EMAIL SEND LOGS:\n" + "="*50 + "\n\n")
                
                for log in logs[-10:]:  # Show last 10 entries
                    self.log_text.insert(tk.END, f"Timestamp: {log['timestamp']}\n")
                    self.log_text.insert(tk.END, f"Total Contacts: {log['total_contacts']}\n")
                    self.log_text.insert(tk.END, f"Successful: {log['successful_sends']}\n")
                    self.log_text.insert(tk.END, f"Failed: {log['failed_sends']}\n")
                    self.log_text.insert(tk.END, f"Success Rate: {log['success_rate']}\n")
                    self.log_text.insert(tk.END, "-" * 30 + "\n\n")
            else:
                self.log_text.delete("1.0", tk.END)
                self.log_text.insert(tk.END, "No email logs found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load email logs: {str(e)}")
    
    def refresh_whatsapp_logs(self):
        """Refresh WhatsApp logs display."""
        try:
            if os.path.exists("whatsapp_send_log.json"):
                with open("whatsapp_send_log.json", 'r') as f:
                    logs = json.load(f)
                
                self.log_text.delete("1.0", tk.END)
                self.log_text.insert(tk.END, "WHATSAPP SEND LOGS:\n" + "="*50 + "\n\n")
                
                for log in logs[-10:]:  # Show last 10 entries
                    self.log_text.insert(tk.END, f"Timestamp: {log['timestamp']}\n")
                    self.log_text.insert(tk.END, f"Method: {log['method']}\n")
                    self.log_text.insert(tk.END, f"Total Contacts: {log['total_contacts']}\n")
                    self.log_text.insert(tk.END, f"Successful: {log['successful_sends']}\n")
                    self.log_text.insert(tk.END, f"Failed: {log['failed_sends']}\n")
                    self.log_text.insert(tk.END, f"Success Rate: {log['success_rate']}\n")
                    self.log_text.insert(tk.END, "-" * 30 + "\n\n")
            else:
                self.log_text.delete("1.0", tk.END)
                self.log_text.insert(tk.END, "No WhatsApp logs found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load WhatsApp logs: {str(e)}")
    
    def clear_log_display(self):
        """Clear log display."""
        self.log_text.delete("1.0", tk.END)
    
    def open_logs_folder(self):
        """Open logs folder."""
        import subprocess
        import platform
        
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer {os.getcwd()}')
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(f'open {os.getcwd()}', shell=True)
        else:  # Linux
            subprocess.Popen(f'xdg-open {os.getcwd()}', shell=True)
    
    def clear_logs(self):
        """Clear all log files."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all logs?"):
            try:
                if os.path.exists("email_send_log.json"):
                    os.remove("email_send_log.json")
                if os.path.exists("whatsapp_send_log.json"):
                    os.remove("whatsapp_send_log.json")
                messagebox.showinfo("Success", "All logs cleared successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear logs: {str(e)}")

def main():
    root = tk.Tk()
    app = BulkMessengerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()