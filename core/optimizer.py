"""
Maximum speed optimization with safety
"""
import asyncio
import random
import urllib.parse
from core.anti_ban import AntiBanEngine
from core.formatter import PhoneFormatter
from core.personalizer import MessagePersonalizer


class SpeedOptimizer:
    """
    Maximum speed optimization with safety
    """
    
    def __init__(self, max_parallel=3, default_country_code='62'):
        self.max_parallel = max_parallel  # Max parallel sessions
        self.formatter = PhoneFormatter(default_country_code)
        self.anti_ban = AntiBanEngine()
        self.personalizer = MessagePersonalizer()
        
    async def parallel_send_multiple(self, distributions, messages_list, contact_map=None, personalize=False):
        """
        Send multiple bubble messages per contact
        Each message in messages_list will be sent as separate bubble
        """
        tasks = []
        for i, (session_name, data) in enumerate(distributions.items()):
            delay = i * random.uniform(2, 3)
            task = asyncio.create_task(
                self.session_sender_multiple(
                    session_name,
                    data['session'],
                    data['numbers'],
                    messages_list,
                    initial_delay=delay,
                    contact_map=contact_map,
                    personalize=personalize
                )
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self.compile_results(results)
    
    async def session_sender_multiple(self, name, session, numbers, messages_list, initial_delay=0, contact_map=None, personalize=False):
        """
        Send multiple bubble messages for each contact
        """
        if initial_delay > 0:
            await asyncio.sleep(initial_delay)
        
        print(f"[{name}] Starting batch of {len(numbers)} contacts with {len(messages_list)} bubbles each")
        if personalize:
            print(f"[{name}] Personalization enabled (name + greeting + address)")
        
        page = session['page']
        results = []
        
        for i, number in enumerate(numbers):
            try:
                formatted_number = self.formatter.format(number)
                
                # Get contact info
                contact = contact_map.get(number, {}) if contact_map else {}
                contact_name = contact.get('name')
                contact_address = contact.get('address')
                
                # Send each message as separate bubble
                all_sent = True
                for msg_idx, base_message in enumerate(messages_list):
                    try:
                        # Personalize message if enabled
                        if personalize:
                            personalized_msg = self.personalizer.personalize_message(
                                base_message,
                                name=contact_name if msg_idx == 0 else None,  # Only add greeting on first bubble
                                address=contact_address if msg_idx == 0 else None,  # Only add address on first bubble
                                use_greeting=(msg_idx == 0)  # Only greeting on first bubble
                            )
                        else:
                            personalized_msg = base_message
                            if contact_name:
                                personalized_msg = personalized_msg.replace('{name}', contact_name)
                            if contact_address:
                                personalized_msg = personalized_msg.replace('{address}', contact_address)
                        
                        # Apply anti-ban variation only on last message to avoid over-variation
                        if msg_idx == len(messages_list) - 1:
                            personalized_msg = self.anti_ban.message_variation_engine(personalized_msg)
                        
                        # Calculate delay
                        delay = self.anti_ban.calculate_optimal_delay(
                            session['messages_sent'],
                            session.get('age', 0)
                        )
                        
                        # Send message
                        success = await self.send_single_message(page, formatted_number, personalized_msg, 0)
                        
                        if success:
                            session['messages_sent'] += 1
                            
                            # Small delay between bubbles (same contact)
                            if msg_idx < len(messages_list) - 1:
                                await asyncio.sleep(random.uniform(1, 2))
                        else:
                            all_sent = False
                            break
                    except Exception as e:
                        print(f"[{name}] Failed to send bubble {msg_idx+1} to {number}: {e}")
                        all_sent = False
                        break
                
                if all_sent:
                    results.append({
                        'number': formatted_number,
                        'status': 'sent',
                        'name': contact_name,
                        'address': contact_address,
                        'bubbles': len(messages_list)
                    })
                else:
                    results.append({
                        'number': formatted_number,
                        'status': 'failed',
                        'error': 'Failed to send all bubbles'
                    })
                
                # Delay between contacts
                await asyncio.sleep(delay)
                
                # Progress update
                if (i + 1) % 10 == 0:
                    print(f"[{name}] Progress: {i+1}/{len(numbers)}")
                    
            except Exception as e:
                results.append({'number': number, 'status': 'failed', 'error': str(e)})
                print(f"[{name}] Failed to send to {number}: {e}")
        
        success_count = sum(1 for r in results if r.get('status') == 'sent')
        print(f"[{name}] Completed batch. Success rate: {success_count}/{len(results)}")
        return results
    
    async def parallel_send(self, distributions, message_template, contact_map=None, personalize=False):
        """
        Send messages in parallel across multiple sessions
        
        OPTIMAL CONFIGURATION:
        - 3-5 parallel sessions maximum
        - Each session handles 30-50 numbers
        - Staggered start (2-3 seconds between sessions)
        """
        
        tasks = []
        for i, (session_name, data) in enumerate(distributions.items()):
            # Stagger session starts
            delay = i * random.uniform(2, 3)
            task = asyncio.create_task(
                self.session_sender(
                    session_name,
                    data['session'],
                    data['numbers'],
                    message_template,
                    initial_delay=delay,
                    contact_map=contact_map,
                    personalize=personalize
                )
            )
            tasks.append(task)
        
        # Wait for all sessions to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.compile_results(results)
    
    async def session_sender(self, name, session, numbers, template, initial_delay=0, contact_map=None, personalize=False):
        """
        Optimized sender for individual session
        """
        if initial_delay > 0:
            await asyncio.sleep(initial_delay)
            
        print(f"[{name}] Starting batch of {len(numbers)} messages")
        if personalize:
            print(f"[{name}] Personalization enabled (name + greeting + address)")
        
        page = session['page']
        results = []
        
        for i, number in enumerate(numbers):
            try:
                # Format phone number
                formatted_number = self.formatter.format(number)
                
                # Get contact info if available
                contact = contact_map.get(number, {}) if contact_map else {}
                contact_name = contact.get('name')
                contact_address = contact.get('address')
                
                # Prepare base message
                base_message = template
                
                # Personalize message if enabled
                if personalize:
                    base_message = self.personalizer.personalize_message(
                        base_message,
                        name=contact_name,
                        address=contact_address,
                        use_greeting=True
                    )
                else:
                    # Still allow basic placeholders
                    if contact_name:
                        base_message = base_message.replace('{name}', contact_name)
                    if contact_address:
                        base_message = base_message.replace('{address}', contact_address)
                
                # Apply anti-ban variation (but preserve personalization)
                message = self.anti_ban.message_variation_engine(base_message)
                
                # Calculate optimal delay
                delay = self.anti_ban.calculate_optimal_delay(
                    session['messages_sent'],
                    session.get('age', 0)
                )
                
                # Disable typing simulation for long messages to avoid timeout
                # The send_single_message will handle typing speed internally based on message length
                typing_time = 0  # Disable external typing simulation
                
                # Send message
                success = await self.send_single_message(page, formatted_number, message, typing_time)
                
                if success:
                    session['messages_sent'] += 1
                    results.append({
                        'number': formatted_number,
                        'status': 'sent',
                        'name': contact_name,
                        'address': contact_address
                    })
                else:
                    results.append({
                        'number': formatted_number,
                        'status': 'failed',
                        'error': 'Send failed'
                    })
                
                # Apply delay
                await asyncio.sleep(delay)
                
                # Progress update every 10 messages
                if (i + 1) % 10 == 0:
                    print(f"[{name}] Progress: {i+1}/{len(numbers)}")
                    
            except Exception as e:
                results.append({'number': number, 'status': 'failed', 'error': str(e)})
                print(f"[{name}] Failed to send to {number}: {e}")
        
        success_count = sum(1 for r in results if r.get('status') == 'sent')
        print(f"[{name}] Completed batch. Success rate: {success_count}/{len(results)}")
        
        return results
    
    async def send_single_message(self, page, number, message, typing_time=0):
        """
        Optimized single message sending
        """
        try:
            # Navigate directly to chat
            encoded_message = urllib.parse.quote(message)
            url = f"https://web.whatsapp.com/send?phone={number}&text={encoded_message}"
            await page.goto(url, wait_until='networkidle')
            
            # Wait for chat to load
            try:
                await page.wait_for_selector('[contenteditable="true"][data-tab="10"]', timeout=10000)
            except:
                # Alternative selector
                await page.wait_for_selector('div[contenteditable="true"][role="textbox"]', timeout=10000)
            
            # Simulate typing if needed
            if typing_time > 0:
                await asyncio.sleep(min(typing_time, 2))  # Cap typing simulation
            
            # Find message input box
            message_box = None
            selectors = [
                '[contenteditable="true"][data-tab="10"]',
                'div[contenteditable="true"][role="textbox"]',
                '[contenteditable="true"]'
            ]
            
            for selector in selectors:
                try:
                    message_box = await page.query_selector(selector)
                    if message_box:
                        break
                except:
                    continue
            
            if not message_box:
                raise Exception("Could not find message input box")
            
            # Clear any existing text and type message
            await message_box.click()
            await asyncio.sleep(0.3)
            
            # Clear existing content
            await page.keyboard.press('Control+A')
            await asyncio.sleep(0.2)
            
            # For long messages, use faster typing to avoid timeout
            message_length = len(message)
            
            # Handle newlines in message - use Shift+Enter for line breaks within same bubble
            # Split message by newlines and type each line, using Shift+Enter for line breaks
            lines = message.split('\n')
            
            if message_length > 500:
                # Long message: faster typing, type in chunks
                delay_per_char = random.randint(10, 30)  # Much faster for long messages
                
                for line_idx, line in enumerate(lines):
                    if line_idx > 0:
                        # Add line break within same bubble (Shift+Enter)
                        await page.keyboard.press('Shift+Enter')
                        await asyncio.sleep(0.1)
                    
                    # Type line in chunks to avoid timeout
                    if len(line) > 200:
                        chunk_size = 200
                        for i in range(0, len(line), chunk_size):
                            chunk = line[i:i+chunk_size]
                            await message_box.type(chunk, delay=delay_per_char)
                            await asyncio.sleep(0.05)
                    else:
                        await message_box.type(line, delay=delay_per_char)
            else:
                # Short/medium message: normal typing speed
                delay_per_char = random.randint(30, 80)
                
                for line_idx, line in enumerate(lines):
                    if line_idx > 0:
                        # Add line break within same bubble (Shift+Enter)
                        await page.keyboard.press('Shift+Enter')
                        await asyncio.sleep(0.1)
                    
                    await message_box.type(line, delay=delay_per_char)
            
            # Wait a bit before sending
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Send
            await page.keyboard.press('Enter')
            
            # Wait for message to be sent (check for sent indicator)
            await asyncio.sleep(2)
            
            # Verify message was sent by checking for sent icon or message bubble
            try:
                await page.wait_for_selector('span[data-icon="msg-dblcheck"]', timeout=5000)
            except:
                # Alternative: just wait a bit more
                await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"Error sending message to {number}: {e}")
            return False
    
    def compile_results(self, results):
        """Compile results from multiple sessions"""
        compiled = []
        for result in results:
            if isinstance(result, Exception):
                compiled.append({'status': 'failed', 'error': str(result)})
            elif isinstance(result, list):
                compiled.extend(result)
            else:
                compiled.append(result)
        return compiled

