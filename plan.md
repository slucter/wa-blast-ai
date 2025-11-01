# WhatsApp CLI Messaging Tool - Development Prompt

## Project Overview
Create a Python-based CLI tool for sending WhatsApp messages with built-in anti-spam protection and rate limiting to ensure compliance with WhatsApp's policies and prevent account suspension.

## Core Requirements

### 1. Messaging Capabilities
- **Single Message**: Send individual messages to specific contacts
- **Bulk Messages**: Send messages to multiple contacts from a list
- **Template Support**: Load message content from text files
- **Contact Management**: Import recipient numbers from text files

### 2. Anti-Spam & Safety Features
```python
# Implement these safety measures:
- Random delay between messages (5-15 seconds minimum)
- Daily message limit (max 50-100 messages/day)
- Unique message variations to avoid detection
- Session breaks after every 10-15 messages
- Human-like typing simulation
- Business hours restriction (9 AM - 8 PM)
- Cooldown period between campaigns
```

### 3. Phone Number Handling
```python
def format_phone_number(phone):
    """
    Auto-format phone numbers to WhatsApp standards:
    - Remove spaces, dashes, parentheses
    - Add country code if missing
    - Validate number format
    - Support international formats
    """
    # Example formats to handle:
    # 08123456789 -> 628123456789 (Indonesia)
    # +1-555-123-4567 -> 15551234567 (US)
    # (021) 1234567 -> 62211234567
```

### 4. CLI Arguments Structure
```bash
# Single message
python wa_cli.py --single --phone "628123456789" --message "Hello" --delay 5

# Bulk messaging
python wa_cli.py --bulk --contacts "contacts.txt" --template "template.txt" \
                 --delay-min 5 --delay-max 15 --batch-size 10 \
                 --cooldown 300 --daily-limit 50

# Additional arguments
--country-code [62]  # Default country code
--start-time [09:00] # Start sending time
--end-time [20:00]   # Stop sending time
--dry-run            # Test without sending
--log-file           # Save logs
--randomize          # Randomize contact order
```

## Technical Implementation

### 5. Required Libraries
```python
# Core dependencies
import argparse
import time
import random
import re
import logging
from datetime import datetime
import json
import csv

# WhatsApp library options (choose most stable):
# Option 1: yowsup (requires registration)
# Option 2: python-whatsapp-bot
# Option 3: WhatsApp Web automation (selenium-based)
```

### 6. Project Structure
```
whatsapp-cli/
├── wa_cli.py           # Main CLI application
├── config/
│   ├── settings.json   # Configuration file
│   └── limits.json     # Rate limiting rules
├── modules/
│   ├── __init__.py
│   ├── sender.py       # Message sending logic
│   ├── formatter.py    # Number formatting
│   ├── validator.py    # Input validation
│   ├── rate_limiter.py # Anti-spam logic
│   └── logger.py       # Logging utilities
├── templates/
│   └── sample.txt      # Message templates
├── data/
│   ├── contacts.txt    # Contact lists
│   └── sent_log.csv    # Sending history
├── requirements.txt
└── README.md
```

### 7. Core Components

#### 7.1 Main CLI Handler
```python
# wa_cli.py
import argparse
from modules import sender, formatter, validator, rate_limiter

def main():
    parser = argparse.ArgumentParser(description='WhatsApp CLI Messaging Tool')
    
    # Mode selection
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--single', action='store_true', help='Send single message')
    mode.add_argument('--bulk', action='store_true', help='Send bulk messages')
    
    # Contact arguments
    parser.add_argument('--phone', type=str, help='Phone number for single message')
    parser.add_argument('--contacts', type=str, help='Path to contacts file')
    
    # Message arguments
    parser.add_argument('--message', type=str, help='Direct message text')
    parser.add_argument('--template', type=str, help='Path to message template')
    
    # Rate limiting arguments
    parser.add_argument('--delay-min', type=int, default=5, help='Minimum delay (seconds)')
    parser.add_argument('--delay-max', type=int, default=15, help='Maximum delay (seconds)')
    parser.add_argument('--batch-size', type=int, default=10, help='Messages per batch')
    parser.add_argument('--cooldown', type=int, default=300, help='Cooldown between batches')
    parser.add_argument('--daily-limit', type=int, default=50, help='Daily message limit')
    
    # Additional options
    parser.add_argument('--country-code', type=str, default='62', help='Default country code')
    parser.add_argument('--start-time', type=str, default='09:00', help='Start time (HH:MM)')
    parser.add_argument('--end-time', type=str, default='20:00', help='End time (HH:MM)')
    parser.add_argument('--dry-run', action='store_true', help='Test run without sending')
    parser.add_argument('--log-file', type=str, help='Log file path')
    parser.add_argument('--randomize', action='store_true', help='Randomize contact order')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not validator.validate_args(args):
        return
    
    # Initialize rate limiter
    limiter = rate_limiter.RateLimiter(
        daily_limit=args.daily_limit,
        batch_size=args.batch_size,
        cooldown=args.cooldown
    )
    
    # Process based on mode
    if args.single:
        send_single_message(args, limiter)
    else:
        send_bulk_messages(args, limiter)
```

#### 7.2 Rate Limiter Module
```python
# modules/rate_limiter.py
import time
import random
import json
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, daily_limit=50, batch_size=10, cooldown=300):
        self.daily_limit = daily_limit
        self.batch_size = batch_size
        self.cooldown = cooldown
        self.sent_today = self.load_daily_count()
        self.batch_count = 0
        
    def can_send(self):
        """Check if we can send a message"""
        if self.sent_today >= self.daily_limit:
            print(f"Daily limit reached ({self.daily_limit})")
            return False
            
        if not self.is_business_hours():
            print("Outside business hours")
            return False
            
        return True
    
    def apply_delay(self, min_delay=5, max_delay=15):
        """Apply random delay with typing simulation"""
        delay = random.uniform(min_delay, max_delay)
        
        # Add typing simulation
        typing_time = random.uniform(1, 3)
        print(f"Typing for {typing_time:.1f} seconds...")
        time.sleep(typing_time)
        
        print(f"Waiting {delay:.1f} seconds...")
        time.sleep(delay)
        
        self.batch_count += 1
        self.sent_today += 1
        
        # Apply cooldown after batch
        if self.batch_count >= self.batch_size:
            print(f"Batch limit reached. Cooldown for {self.cooldown} seconds...")
            time.sleep(self.cooldown)
            self.batch_count = 0
    
    def is_business_hours(self, start="09:00", end="20:00"):
        """Check if current time is within business hours"""
        now = datetime.now().time()
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()
        return start_time <= now <= end_time
```

#### 7.3 Phone Number Formatter
```python
# modules/formatter.py
import re

class PhoneFormatter:
    def __init__(self, default_country_code='62'):
        self.default_country_code = default_country_code
        
    def format(self, phone):
        """Format phone number to WhatsApp standard"""
        # Remove all non-numeric characters
        phone = re.sub(r'\D', '', phone)
        
        # Handle different formats
        if phone.startswith('0'):
            # Local number, add country code
            phone = self.default_country_code + phone[1:]
        elif not phone.startswith(self.default_country_code):
            # Assume it needs country code
            if len(phone) < 12:  # Likely missing country code
                phone = self.default_country_code + phone
        
        # Validate length (adjust based on country)
        if self.default_country_code == '62':  # Indonesia
            if not (10 <= len(phone) <= 15):
                raise ValueError(f"Invalid phone number: {phone}")
        
        return phone
    
    def validate(self, phone):
        """Validate phone number format"""
        pattern = r'^\d{10,15}$'
        return bool(re.match(pattern, phone))
```

#### 7.4 Message Sender
```python
# modules/sender.py
import random

class MessageSender:
    def __init__(self, api_client):
        self.api_client = api_client
        self.variations = []
        
    def add_variations(self, message):
        """Add message variations to avoid spam detection"""
        variations = [
            message,
            f"Hi! {message}",
            f"{message} 😊",
            f"Hello, {message}",
        ]
        return random.choice(variations)
    
    def personalize(self, template, contact_name=""):
        """Personalize message with contact details"""
        return template.replace("{name}", contact_name)
    
    def send(self, phone, message, dry_run=False):
        """Send message with safety checks"""
        if dry_run:
            print(f"[DRY RUN] Would send to {phone}: {message[:50]}...")
            return True
        
        try:
            # Add variation to message
            final_message = self.add_variations(message)
            
            # Send via API
            result = self.api_client.send_message(phone, final_message)
            
            if result.success:
                print(f"✓ Sent to {phone}")
                self.log_success(phone, message)
            else:
                print(f"✗ Failed to send to {phone}: {result.error}")
                self.log_failure(phone, result.error)
                
            return result.success
            
        except Exception as e:
            print(f"Error sending to {phone}: {str(e)}")
            return False
```

### 8. WhatsApp API Integration

#### Option 1: Using WAHA (WhatsApp HTTP API)
```python
# Free self-hosted solution
import requests

class WAHAClient:
    def __init__(self, api_url="http://localhost:3000"):
        self.api_url = api_url
        self.session = "default"
        
    def send_message(self, phone, message):
        endpoint = f"{self.api_url}/api/sendText"
        payload = {
            "session": self.session,
            "phone": phone,
            "text": message
        }
        response = requests.post(endpoint, json=payload)
        return response.json()
```

#### Option 2: Using Selenium (WhatsApp Web)
```python
# Browser automation approach
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib.parse

class WhatsAppWebClient:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://web.whatsapp.com")
        input("Scan QR Code and press Enter...")
        
    def send_message(self, phone, message):
        url = f"https://web.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(message)}"
        self.driver.get(url)
        # Wait and click send button
        # Implementation details...
```

### 9. Configuration Files

#### settings.json
```json
{
  "api": {
    "type": "waha",
    "url": "http://localhost:3000",
    "timeout": 30
  },
  "limits": {
    "daily_limit": 50,
    "batch_size": 10,
    "cooldown_seconds": 300,
    "min_delay": 5,
    "max_delay": 15
  },
  "business_hours": {
    "start": "09:00",
    "end": "20:00",
    "timezone": "Asia/Jakarta"
  },
  "formatting": {
    "default_country_code": "62",
    "remove_duplicates": true,
    "validate_numbers": true
  }
}
```

### 10. Safety & Compliance Features

```python
# Additional safety measures
class ComplianceManager:
    def __init__(self):
        self.blacklist = self.load_blacklist()
        self.whitelist = self.load_whitelist()
        
    def check_compliance(self, phone, message):
        """Verify message compliance"""
        # Check if number is blacklisted
        if phone in self.blacklist:
            return False, "Number is blacklisted"
        
        # Check message content
        spam_keywords = ['viagra', 'casino', 'lottery']
        if any(keyword in message.lower() for keyword in spam_keywords):
            return False, "Message contains spam keywords"
        
        # Check message length
        if len(message) > 4096:
            return False, "Message too long"
        
        return True, "OK"
    
    def add_opt_out(self, phone):
        """Handle opt-out requests"""
        self.blacklist.add(phone)
        self.save_blacklist()
```

### 11. Installation & Usage

#### Requirements.txt
```
requests>=2.28.0
selenium>=4.0.0
python-dotenv>=1.0.0
colorama>=0.4.6
pandas>=1.5.0
```

#### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Single message
python wa_cli.py --single --phone "628123456789" --message "Hello World"

# Bulk messaging with template
python wa_cli.py --bulk \
    --contacts "contacts.txt" \
    --template "templates/welcome.txt" \
    --delay-min 5 \
    --delay-max 15 \
    --daily-limit 50

# Dry run to test
python wa_cli.py --bulk \
    --contacts "contacts.txt" \
    --template "templates/test.txt" \
    --dry-run
```

### 12. Important Legal & Ethical Considerations

**⚠️ CRITICAL COMPLIANCE REQUIREMENTS:**

1. **User Consent**: Only message users who have explicitly opted in
2. **Opt-out Mechanism**: Always include unsubscribe option
3. **Privacy Compliance**: Follow GDPR, CCPA, and local privacy laws
4. **WhatsApp Terms**: Strictly follow WhatsApp Business API policies
5. **Anti-Spam Laws**: Comply with CAN-SPAM, TCPA, and local regulations
6. **Message Content**: No misleading, harmful, or illegal content
7. **Rate Limits**: Respect WhatsApp's rate limiting to avoid bans

### 13. Testing Strategy

```python
# test_suite.py
import unittest

class TestWhatsAppCLI(unittest.TestCase):
    def test_phone_formatting(self):
        formatter = PhoneFormatter('62')
        assert formatter.format('08123456789') == '628123456789'
        assert formatter.format('+62-812-3456-789') == '628123456789'
    
    def test_rate_limiter(self):
        limiter = RateLimiter(daily_limit=10)
        for i in range(10):
            assert limiter.can_send() == True
            limiter.sent_today += 1
        assert limiter.can_send() == False
    
    def test_message_variations(self):
        sender = MessageSender(None)
        message = "Test message"
        variation = sender.add_variations(message)
        assert message in variation
```

## Final Implementation Notes

- Start with a simple MVP focusing on basic sending with rate limiting
- Implement comprehensive logging for debugging and compliance
- Add monitoring and alerting for failed messages
- Consider implementing a web dashboard for easier management
- Always prioritize user privacy and consent
- Regularly update to comply with changing WhatsApp policies

Remember: This tool should only be used for legitimate business communications with proper user consent. Misuse can result in account suspension and legal consequences.