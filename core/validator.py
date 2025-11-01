"""
Input validation utilities
"""
from pathlib import Path


class Validator:
    """Validate CLI arguments and inputs"""
    
    @staticmethod
    def validate_args(args):
        """Validate CLI arguments"""
        errors = []
        
        # Single message mode
        if args.single or getattr(args, 'action', None) == 'send':
            if not args.phone and not args.numbers:
                errors.append("Phone number or contacts file required")
            
            if not args.message and not args.template:
                errors.append("Message or template file required")
        
        # Bulk message mode
        if args.bulk or getattr(args, 'action', None) == 'send':
            if not args.contacts and not args.numbers:
                errors.append("Contacts file required for bulk messaging")
            
            if not args.message and not args.template:
                errors.append("Message or template file required")
        
        # Validate file paths
        if args.contacts and not Path(args.contacts).exists():
            errors.append(f"Contacts file not found: {args.contacts}")
        
        if args.template and not Path(args.template).exists():
            errors.append(f"Template file not found: {args.template}")
        
        if args.numbers and not Path(args.numbers).exists():
            errors.append(f"Numbers file not found: {args.numbers}")
        
        # Validate delay ranges
        if hasattr(args, 'delay_min') and hasattr(args, 'delay_max'):
            if args.delay_min > args.delay_max:
                errors.append("Minimum delay cannot be greater than maximum delay")
        
        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"  ✗ {error}")
            return False
        
        return True
    
    @staticmethod
    def validate_phone(phone, formatter):
        """Validate phone number"""
        try:
            return formatter.validate(phone)
        except:
            return False
    
    @staticmethod
    def validate_message(message):
        """Validate message content"""
        if not message or len(message.strip()) == 0:
            return False, "Message cannot be empty"
        
        if len(message) > 4096:
            return False, "Message too long (max 4096 characters)"
        
        return True, "OK"

