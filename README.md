# Bulk Messenger - Email & WhatsApp

A comprehensive Python application for sending bulk messages via both **Email** and **WhatsApp**. Features a user-friendly GUI and supports contact management, message personalization, and detailed logging.

## Features

### 📧 Email Bulk Sending
- **SMTP Support**: Works with Gmail, Outlook, Yahoo, and other SMTP servers
- **Message Personalization**: Use placeholders like `{name}`, `{email}`, `{company}` 
- **Attachment Support**: Send files with your emails
- **Configurable Delays**: Prevent server overload with customizable delays
- **Detailed Logging**: Track success/failure rates and timestamps

### 📱 WhatsApp Bulk Messaging
- **Two Methods**: 
  - **PyWhatKit**: Scheduled messaging (requires WhatsApp Desktop)
  - **Selenium**: Immediate sending via WhatsApp Web
- **Phone Number Formatting**: Automatic international format handling
- **Message Personalization**: Use placeholders like `{name}`, `{phone}`
- **Scheduling**: Schedule messages for specific times
- **Session Management**: Saves WhatsApp Web login for Selenium method

### 🖥️ User Interface
- **Tabbed Interface**: Separate tabs for Email, WhatsApp, Settings, and Logs
- **Contact Management**: CSV-based contact lists with sample generators
- **Template Support**: Pre-built message templates
- **Real-time Logging**: View sending progress and results
- **Configuration Management**: Save and load email settings

## Installation

### 1. Clone or Download
```bash
git clone <repository-url>
cd bulk-messenger
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Chrome WebDriver (for WhatsApp Selenium method)
The application will automatically download ChromeDriver when needed, but you can also install it manually:
```bash
# On Linux
sudo apt-get install chromium-chromedriver

# On macOS
brew install chromedriver

# On Windows
# Download from https://chromedriver.chromium.org/
```

## Quick Start

### 1. Run the Application
```bash
python bulk_messenger_gui.py
```

### 2. Email Setup
1. Go to the **Email Bulk Sender** tab
2. Enter your email credentials:
   - **Gmail**: Use an App Password (not your regular password)
   - **Other SMTP**: Configure server and port settings
3. Click **Test Connection** to verify settings
4. Create or load a contacts CSV file
5. Compose your message and send!

### 3. WhatsApp Setup
1. Go to the **WhatsApp Bulk Sender** tab
2. Choose your method:
   - **PyWhatKit**: For scheduled messages
   - **Selenium**: For immediate sending (requires QR scan)
3. Create or load a WhatsApp contacts CSV file
4. Compose your message and send!

## File Formats

### Email Contacts CSV Format
```csv
name,email,company
John Doe,john@example.com,Tech Corp
Jane Smith,jane@example.com,Design Studio
```

### WhatsApp Contacts CSV Format
```csv
name,phone,country_code
John Doe,+1234567890,+1
Jane Smith,+1987654321,+1
```

## Message Personalization

Use placeholders in your messages for personalization:

### Email
- `{name}` - Contact's name
- `{email}` - Contact's email
- `{company}` - Contact's company

### WhatsApp
- `{name}` - Contact's name
- `{phone}` - Contact's phone number

### Example
```
Hello {name}!

Hope you're doing well at {company}. I wanted to share some exciting news...

Best regards!
```

## Gmail Setup (Important!)

For Gmail users, you **MUST** use an App Password:

1. Enable 2-Factor Authentication on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app password for "Mail"
4. Use this 16-character password in the application

## WhatsApp Methods

### PyWhatKit Method
- **Pros**: Reliable, runs in background
- **Cons**: Requires scheduling, needs WhatsApp Desktop app
- **Setup**: Install WhatsApp Desktop application
- **Usage**: Messages are scheduled and sent automatically

### Selenium Method  
- **Pros**: Immediate sending, more flexible
- **Cons**: Requires browser interaction, may need QR scan
- **Setup**: Automatically opens WhatsApp Web
- **Usage**: Scan QR code once, then sends immediately

## Security & Privacy

- **Credentials**: Email passwords are stored locally in `email_config.json`
- **Logs**: All activity is logged locally for troubleshooting
- **No Cloud**: No data is sent to external servers except for sending messages
- **WhatsApp Session**: Selenium saves session data locally

## Troubleshooting

### Email Issues
- **Authentication Failed**: Use App Password for Gmail
- **Connection Timeout**: Check SMTP server and port settings
- **Rate Limiting**: Increase delay between emails

### WhatsApp Issues
- **PyWhatKit Not Working**: Ensure WhatsApp Desktop is installed
- **Selenium QR Code**: Keep WhatsApp Web tab open during QR scan
- **Phone Number Format**: Ensure numbers include country code

### General Issues
- **Contacts Not Loading**: Check CSV file format
- **GUI Not Responsive**: Operations run in background threads
- **Dependencies Missing**: Run `pip install -r requirements.txt`

## Advanced Usage

### Custom SMTP Settings
Edit `email_config.json` for custom SMTP servers:
```json
{
    "smtp_server": "mail.yourserver.com",
    "smtp_port": 587,
    "email": "your@email.com",
    "password": "your_password",
    "use_tls": true
}
```

### Bulk Operations
- **Email**: Recommended delay: 2-5 seconds between emails
- **WhatsApp**: Recommended delay: 5-10 seconds between messages
- **Large Lists**: Process in batches of 50-100 contacts

### Logging
- **Email logs**: `email_send_log.json`
- **WhatsApp logs**: `whatsapp_send_log.json`
- **View logs**: Use the Logs tab in the application

## File Structure
```
bulk-messenger/
├── bulk_email_sender.py      # Email functionality
├── bulk_whatsapp_sender.py   # WhatsApp functionality  
├── bulk_messenger_gui.py     # Main GUI application
├── requirements.txt          # Python dependencies
├── config_template.json      # Configuration template
├── README.md                # This file
├── contacts.csv             # Sample email contacts (auto-generated)
├── whatsapp_contacts.csv    # Sample WhatsApp contacts (auto-generated)
├── email_config.json        # Email settings (auto-generated)
├── email_send_log.json      # Email sending logs (auto-generated)
└── whatsapp_send_log.json   # WhatsApp sending logs (auto-generated)
```

## Legal & Ethical Use

- **Consent**: Only send messages to people who have consented
- **Spam**: Avoid sending unsolicited promotional messages
- **Rate Limits**: Respect platform rate limits and terms of service
- **Privacy**: Protect contact information and message content
- **Compliance**: Follow applicable laws (CAN-SPAM, GDPR, etc.)

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review log files for error details
3. Ensure all dependencies are installed correctly
4. Verify contact file formats

## Version History

- **v1.0**: Initial release with email and WhatsApp bulk messaging
- GUI interface with contact management
- Support for message personalization and logging

---

**Note**: This tool is for legitimate bulk messaging purposes only. Please use responsibly and in compliance with applicable laws and platform terms of service.