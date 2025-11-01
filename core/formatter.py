"""
Phone number formatting and validation
"""
import re


class PhoneFormatter:
    """Format and validate phone numbers for WhatsApp"""
    
    def __init__(self, default_country_code='62'):
        self.default_country_code = default_country_code
        
    def format(self, phone):
        """Format phone number to WhatsApp standard"""
        # Remove all non-numeric characters
        phone = re.sub(r'\D', '', str(phone))
        
        # Handle different formats
        if phone.startswith('0'):
            # Local number, add country code
            phone = self.default_country_code + phone[1:]
        elif phone.startswith('+'):
            # Remove + sign
            phone = phone[1:]
        elif not phone.startswith(self.default_country_code):
            # Assume it needs country code
            if len(phone) < 12:  # Likely missing country code
                phone = self.default_country_code + phone
        
        # Validate length (adjust based on country)
        if self.default_country_code == '62':  # Indonesia
            if not (10 <= len(phone) <= 15):
                raise ValueError(f"Invalid phone number length: {phone}")
        
        return phone
    
    def validate(self, phone):
        """Validate phone number format"""
        try:
            formatted = self.format(phone)
            pattern = r'^\d{10,15}$'
            return bool(re.match(pattern, formatted))
        except:
            return False

