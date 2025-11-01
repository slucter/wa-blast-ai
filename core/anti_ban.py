"""
Advanced anti-detection system based on WhatsApp behavior analysis
"""
import random
import time
from datetime import datetime


class AntiBanEngine:
    """
    Advanced anti-detection system based on WhatsApp behavior analysis
    """
    
    def __init__(self):
        self.message_patterns = self.load_patterns()
        self.behavior_profile = self.generate_human_profile()
        
    def load_patterns(self):
        """Load message patterns for variation"""
        return {
            'greetings': [
                'Hi', 'Hello', 'Hey', 'Halo', 'Good day',
                'Greetings', '', 'Hope you\'re well'
            ],
            'endings': [
                'Thanks!', 'Best regards', 'Cheers', '',
                'Thank you', 'Regards', '👍', '😊'
            ],
            'connectors': [
                ', ', ' - ', '. ', '! ', '... ', ' ',
            ]
        }
        
    def generate_human_profile(self):
        """Generate human-like behavior profile"""
        return {
            'typing_speed': random.uniform(2.5, 4.5),
            'thinking_time': random.uniform(0.5, 2.0),
            'correction_rate': 0.3
        }
    
    def calculate_optimal_delay(self, message_count, session_age=0):
        """
        Dynamic delay calculation based on multiple factors
        
        OPTIMAL SETTINGS DISCOVERED:
        - First 10 messages: 8-15 seconds delay
        - Messages 11-50: 5-12 seconds delay  
        - Messages 51-200: 3-8 seconds delay
        - Messages 200+: 2-5 seconds delay
        - After every 50 messages: 30-60 second break
        """
        
        if message_count <= 10:
            # New session, be careful
            base_delay = random.uniform(8, 15)
        elif message_count <= 50:
            # Warming up
            base_delay = random.uniform(5, 12)
        elif message_count <= 200:
            # Established session
            base_delay = random.uniform(3, 8)
        else:
            # Trusted session
            base_delay = random.uniform(2, 5)
        
        # Add variance based on time of day
        hour = datetime.now().hour
        if 2 <= hour <= 6:  # Late night
            base_delay *= 1.5
        elif 9 <= hour <= 17:  # Business hours
            base_delay *= 0.8
        
        # Add micro-pauses (human-like)
        if random.random() < 0.1:  # 10% chance
            base_delay += random.uniform(5, 15)  # Longer pause
            
        # Mandatory break every 50 messages
        if message_count > 0 and message_count % 50 == 0:
            print(f"[BREAK] Cooling down for safety...")
            time.sleep(random.uniform(30, 60))
            
        return base_delay
    
    def generate_typing_pattern(self, message_length):
        """
        Simulate realistic typing speed
        Average human: 40 words/minute = ~200 chars/minute
        """
        chars_per_second = random.uniform(2.5, 4.5)
        typing_time = message_length / chars_per_second
        
        # Add thinking time for longer messages
        if message_length > 100:
            typing_time += random.uniform(1, 3)
            
        # Add corrections (backspace simulation)
        if random.random() < 0.3:
            typing_time += random.uniform(0.5, 1.5)
            
        return min(typing_time, 10)  # Cap at 10 seconds
    
    def message_variation_engine(self, template):
        """
        Advanced message variation to avoid pattern detection
        """
        variations = {
            'greetings': [
                'Hi', 'Hello', 'Hey', 'Halo', 'Good day',
                'Greetings', '', 'Hope you\'re well'
            ],
            'endings': [
                'Thanks!', 'Best regards', 'Cheers', '',
                'Thank you', 'Regards', '👍', '😊'
            ],
            'connectors': [
                ', ', ' - ', '. ', '! ', '... ', ' ',
            ]
        }
        
        # Add random greeting
        if random.random() < 0.7:
            greeting = random.choice(variations['greetings'])
            if greeting:
                template = f"{greeting}{random.choice(variations['connectors'])}{template}"
        
        # Add random ending
        if random.random() < 0.5:
            ending = random.choice(variations['endings'])
            if ending:
                template = f"{template} {ending}"
            
        # Add Unicode variation (invisible characters)
        if random.random() < 0.3:
            invisible_chars = ['\u200b', '\u200c', '\u200d']
            pos = random.randint(0, len(template))
            template = template[:pos] + random.choice(invisible_chars) + template[pos:]
            
        return template
    
    def session_rotation_strategy(self, sessions):
        """
        Rotate between multiple sessions for load distribution
        """
        # Weight sessions by their health score
        weighted_sessions = []
        for session in sessions:
            health = session.get('health_score', 100)  # 0-100
            messages_sent = session.get('messages_sent', 0)
            
            # Calculate weight
            if messages_sent < 50:
                weight = health * 2  # Prefer fresh sessions
            elif messages_sent < 200:
                weight = health
            else:
                weight = health * 0.5  # Reduce usage of heavily used sessions
                
            weighted_sessions.append((session, weight))
        
        if not weighted_sessions:
            return None
        
        # Select session based on weights
        total_weight = sum(w for _, w in weighted_sessions)
        r = random.uniform(0, total_weight)
        upto = 0
        for session, weight in weighted_sessions:
            if upto + weight >= r:
                return session
            upto += weight
        
        return weighted_sessions[0][0]  # Fallback

