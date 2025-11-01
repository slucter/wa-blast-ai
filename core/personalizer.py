"""
Message personalization engine
"""
from datetime import datetime
import re


class MessagePersonalizer:
    """Personalize messages with name, greeting, and address"""
    
    def __init__(self):
        self.greetings = {
            'pagi': ['Selamat pagi', 'Pagi', 'Good morning'],
            'siang': ['Selamat siang', 'Siang', 'Good afternoon'],
            'sore': ['Selamat sore', 'Sore', 'Good evening'],
            'malam': ['Selamat malam', 'Malam', 'Good night']
        }
    
    def get_time_greeting(self):
        """
        Get greeting based on current time
        Returns: greeting text (Indonesian)
        """
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return 'Selamat pagi'
        elif 12 <= hour < 15:
            return 'Selamat siang'
        elif 15 <= hour < 19:
            return 'Selamat sore'
        else:
            return 'Selamat malam'
    
    def personalize_message(self, message, name=None, address=None, use_greeting=True):
        """
        Personalize message with name and address
        
        Format:
        Selamat siang *nama*.
        
        Alamat : *alamat*
        
        *pesan nya
        
        Args:
            message: Base message template
            name: Contact name (optional)
            address: Contact address (optional)
            use_greeting: Whether to add time-based greeting
        
        Returns:
            Personalized message
        """
        parts = []
        
        # Add greeting if enabled
        if use_greeting:
            greeting = self.get_time_greeting()
            
            # Add name after greeting if available
            if name and name.strip():
                # Format: "Selamat siang *nama*." (hanya nama yang bold)
                name_bold = f"*{name.strip()}*"
                parts.append(f"{greeting} {name_bold}.")
            else:
                # No name, just greeting (tidak bold)
                parts.append(f"{greeting}.")
        elif name and name.strip():
            # If no greeting but has name, just add name
            name_bold = f"*{name.strip()}*"
            parts.append(f"Halo {name_bold}.")
        
        # Add address if available (tidak bold)
        if address and address.strip():
            parts.append(f"\nAlamat : {address.strip()}")
        
        # Add message (without bold formatting)
        if message and message.strip():
            # Don't add bold formatting to message content
            message_text = message.strip()
            parts.append(f"\n{message_text}")
        
        personalized = "\n".join(parts)
        
        # Replace placeholders if any (for backward compatibility)
        if '{name}' in personalized:
            personalized = personalized.replace('{name}', f"*{name}*" if name else "")
        if '{address}' in personalized:
            personalized = personalized.replace('{address}', f"*{address}*" if address else "")
        
        return personalized.strip()
    
    def parse_contact_line(self, line):
        """
        Parse contact line in format: nomor|nama|alamat
        
        Args:
            line: Contact line string
        
        Returns:
            dict with keys: number, name, address
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        
        parts = [p.strip() for p in line.split('|')]
        
        if len(parts) == 0:
            return None
        
        contact = {
            'number': parts[0] if len(parts) > 0 else None,
            'name': parts[1] if len(parts) > 1 and parts[1] else None,
            'address': parts[2] if len(parts) > 2 and parts[2] else None
        }
        
        return contact if contact['number'] else None

