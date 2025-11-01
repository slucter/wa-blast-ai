"""
Advanced multi-session management with persistence
"""
import asyncio
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import qrcode
from io import BytesIO
import base64
from PIL import Image
import io
import random


class SessionManager:
    """
    Advanced multi-session management with persistence
    """
    
    def __init__(self, sessions_dir="./sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.active_sessions = {}
        self.session_health = {}
        self.playwright = None
        
    async def initialize_playwright(self):
        """Initialize playwright if not already done"""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
        
    async def create_session(self, session_name, headless=True, force_new=False):
        """
        Create new WhatsApp Web session with Playwright
        
        Args:
            session_name: Name of the session
            headless: Run browser in headless mode
            force_new: If True, delete existing session folder and create fresh session (force QR scan)
        """
        await self.initialize_playwright()
        
        # Create persistent context directory
        context_dir = self.sessions_dir / session_name
        
        # If force_new, delete existing session directory
        if force_new and context_dir.exists():
            import shutil
            print(f"⚠ Force creating new session: deleting existing '{session_name}'...")
            try:
                # Close session if it's active
                if session_name in self.active_sessions:
                    await self.close_session(session_name)
                # Delete directory
                shutil.rmtree(context_dir)
                await asyncio.sleep(0.5)  # Give time for cleanup
                print(f"✓ Old session '{session_name}' deleted")
            except Exception as e:
                print(f"⚠ Error deleting old session: {e}")
        
        # Check if session directory exists (even if empty or partial)
        session_exists = context_dir.exists() and any(context_dir.iterdir())
        
        context_dir.mkdir(parents=True, exist_ok=True)
        
        # Use launch_persistent_context for session persistence
        context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(context_dir),
            headless=headless,
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Get or create the first page
        if context.pages:
            page = context.pages[0]
        else:
            page = await context.new_page()
        
        await page.goto('https://web.whatsapp.com', wait_until='networkidle')
        
        # Check if already logged in
        await asyncio.sleep(3)  # Wait for page to load (increased for better detection)
        
        # If force_new, always require QR scan
        if force_new:
            print(f"⚠ Creating fresh session '{session_name}', QR code scan required...")
            await self.handle_qr_auth(page, session_name, headless=headless)
        elif not session_exists:
            # New session (folder didn't exist), always require QR scan
            print(f"⚠ Creating new session '{session_name}', QR code scan required...")
            await self.handle_qr_auth(page, session_name, headless=headless)
        else:
            # Existing session folder, check if logged in
            is_logged_in = await self.check_login_status(page)
            
            if not is_logged_in:
                print(f"⚠ Session {session_name} needs QR scan")
                await self.handle_qr_auth(page, session_name, headless=headless)
            else:
                print(f"✓ Session {session_name} already authenticated")
        
        self.active_sessions[session_name] = {
            'browser': None,  # Not needed with persistent context
            'context': context,
            'page': page,
            'messages_sent': 0,
            'health_score': 100,
            'created_at': datetime.now()
        }
        
        # Don't start health monitoring during session creation (only during active sending)
        # Health monitoring will be started when sessions are used for sending
        
        return self.active_sessions[session_name]
    
    async def check_login_status(self, page):
        """
        Check if user is logged in using multiple methods
        IMPORTANT: Must check for QR code FIRST - if QR code exists, NOT logged in
        """
        try:
            # FIRST: Check if QR code is visible - if yes, definitely NOT logged in
            try:
                qr_status = await page.evaluate('''() => {
                    const canvas = document.querySelector('canvas');
                    if (!canvas) return { hasCanvas: false, visible: false };
                    
                    const style = window.getComputedStyle(canvas);
                    const rect = canvas.getBoundingClientRect();
                    
                    return {
                        hasCanvas: true,
                        visible: style.display !== 'none' && 
                                style.visibility !== 'hidden' && 
                                style.opacity !== '0' &&
                                rect.width > 0 && 
                                rect.height > 0
                    };
                }''')
                
                if qr_status.get('hasCanvas') and qr_status.get('visible'):
                    # QR code is visible, definitely not logged in
                    return False
            except:
                pass
            
            # Also check for QR code text/instructions
            try:
                qr_text_check = await page.evaluate('''() => {
                    const bodyText = document.body.innerText || '';
                    const hasQrText = bodyText.includes('Use WhatsApp on your phone') ||
                                     bodyText.includes('Scan this code') ||
                                     bodyText.includes('QR code');
                    return hasQrText;
                }''')
                if qr_text_check:
                    return False
            except:
                pass
            
            # Method 1: Check URL - if we're not on the main page, likely logged in
            current_url = page.url
            if 'web.whatsapp.com' in current_url and '#' in current_url:
                # Has hash in URL, likely a chat or conversation page
                # But verify with selectors to be sure
                pass
            
            # Method 2: Check for STRONG login indicators with better visibility check
            strong_login_check = await page.evaluate('''() => {
                const chatList = document.querySelector('[data-testid="chat-list"]');
                const paneSide = document.querySelector('#pane-side');
                const chatItems = document.querySelectorAll('[data-testid="chat"]');
                
                let strongCount = 0;
                
                // Check chat list
                if (chatList) {
                    const style = window.getComputedStyle(chatList);
                    if (style.display !== 'none' && style.visibility !== 'hidden') {
                        strongCount++;
                    }
                }
                
                // Check side panel
                if (paneSide) {
                    const style = window.getComputedStyle(paneSide);
                    if (style.display !== 'none' && style.visibility !== 'hidden') {
                        strongCount++;
                    }
                }
                
                // Check chat items (at least one visible chat)
                if (chatItems.length > 0) {
                    let hasVisibleChat = false;
                    for (let item of chatItems) {
                        const style = window.getComputedStyle(item);
                        if (style.display !== 'none' && style.visibility !== 'hidden') {
                            hasVisibleChat = true;
                            break;
                        }
                    }
                    if (hasVisibleChat) strongCount++;
                }
                
                // Also check for search box (indicates logged in interface)
                const searchBox = document.querySelector('[data-testid="chat-list-search"]');
                const hasSearchBox = searchBox && window.getComputedStyle(searchBox).display !== 'none';
                
                return {
                    strongCount: strongCount,
                    hasSearchBox: hasSearchBox,
                    hasChatList: chatList !== null,
                    hasPaneSide: paneSide !== null
                };
            }''')
            
            # Require at least 2 STRONG indicators to confirm login
            if strong_login_check and strong_login_check.get('strongCount', 0) >= 2:
                # Double-check: verify no QR code
                try:
                    qr_verify = await page.evaluate('''() => {
                        const canvas = document.querySelector('canvas');
                        if (!canvas) return false;
                        const style = window.getComputedStyle(canvas);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    }''')
                    if qr_verify:
                        return False  # QR code still visible, not logged in
                except:
                    pass
                return True
            
            # Alternative: Check for search box + at least one login indicator
            if strong_login_check and strong_login_check.get('hasSearchBox') and strong_login_check.get('strongCount', 0) >= 1:
                return True
            
            # Method 3: Final verification - check for login page elements that should NOT exist
            try:
                login_page_elements = await page.evaluate('''() => {
                    const bodyText = document.body.innerText || '';
                    const hasQrInstructions = bodyText.includes('Use WhatsApp on your phone') ||
                                             bodyText.includes('Scan this code') ||
                                             bodyText.includes('QR code');
                    const chatList = document.querySelector('[data-testid="chat-list"]');
                    const paneSide = document.querySelector('#pane-side');
                    
                    const hasChatList = chatList !== null;
                    const hasPaneSide = paneSide !== null;
                    
                    // Check if chat elements are actually visible
                    const chatListVisible = chatList ? window.getComputedStyle(chatList).display !== 'none' : false;
                    const paneSideVisible = paneSide ? window.getComputedStyle(paneSide).display !== 'none' : false;
                    
                    return {
                        hasQrInstructions: hasQrInstructions,
                        hasChatList: hasChatList,
                        hasPaneSide: hasPaneSide,
                        chatListVisible: chatListVisible,
                        paneSideVisible: paneSideVisible
                    };
                }''')
                
                # If QR instructions exist, definitely not logged in
                if login_page_elements.get('hasQrInstructions'):
                    return False
                
                # If chat list or pane side is visible and no QR instructions, logged in
                if (login_page_elements.get('chatListVisible') or login_page_elements.get('paneSideVisible')) and not login_page_elements.get('hasQrInstructions'):
                    # Final check: make sure no QR canvas visible
                    try:
                        canvas = await page.query_selector('canvas')
                        if canvas:
                            canvas_visible = await canvas.is_visible()
                            if canvas_visible:
                                return False  # Canvas still visible
                    except:
                        pass
                    return True
            except:
                pass
            
            # Default: NOT logged in (be conservative)
            return False
            
        except Exception as e:
            # If there's an error checking, assume not logged in
            print(f"⚠ Error checking login status: {e}")
            return False
    
    async def handle_qr_auth(self, page, session_name, headless=False):
        """
        Handle QR code authentication with terminal display
        """
        try:
            # Wait for QR code to appear
            print(f"\n📱 Waiting for QR code for session: {session_name}...")
            
            # Wait for page to fully load and check for QR code
            await asyncio.sleep(3)
            
            # First check: Is QR code canvas visible?
            try:
                canvas = await page.query_selector('canvas')
                if canvas:
                    canvas_visible = await canvas.is_visible()
                    if not canvas_visible:
                        # Canvas exists but not visible - might be logged in
                        # Double check with more thorough check
                        await asyncio.sleep(2)
                        is_logged_in = await self.check_login_status(page)
                        if is_logged_in:
                            print(f"✓ Session {session_name} already authenticated!")
                            return
                else:
                    # No canvas - might already be logged in, but verify carefully
                    await asyncio.sleep(2)
                    is_logged_in = await self.check_login_status(page)
                    if is_logged_in:
                        print(f"✓ Session {session_name} already authenticated!")
                        return
            except:
                pass
            
            # Wait for QR code canvas to appear (if not already visible)
            try:
                await page.wait_for_selector('canvas', timeout=10000)
            except:
                # QR code didn't appear - check if actually logged in
                await asyncio.sleep(2)
                is_logged_in = await self.check_login_status(page)
                if is_logged_in:
                    print(f"✓ Session {session_name} already authenticated!")
                    return
                else:
                    print(f"⚠ QR code not found, but also not logged in. Please wait...")
            
            # Wait a bit for QR code to render
            await asyncio.sleep(2)
            
            # Try to get QR code data
            try:
                # Get QR code data URL from canvas
                qr_data_url = await page.evaluate('''
                    () => {
                        const canvas = document.querySelector('canvas');
                        if (canvas) {
                            return canvas.toDataURL();
                        }
                        return null;
                    }
                ''')
                
                if qr_data_url:
                    # Extract base64 data
                    qr_base64 = qr_data_url.split(',')[1] if ',' in qr_data_url else qr_data_url
                    
                    # Save QR code to file for SSH/headless use
                    qr_image_path = self.sessions_dir / f"{session_name}_qr.png"
                    with open(qr_image_path, 'wb') as f:
                        f.write(base64.b64decode(qr_base64))
                    
                    print(f"\n{'='*50}")
                    print(f"QR Code detected for session: {session_name}")
                    print(f"{'='*50}")
                    
                    if headless:
                        print("📱 QR Code saved to file (headless/SSH mode)")
                        print(f"   File: {qr_image_path.absolute()}")
                        print("   Please download this file and scan with WhatsApp mobile app")
                        print(f"\n   To download from SSH server:")
                        print(f"   - Use SCP: scp user@server:{qr_image_path.absolute()} .")
                        print(f"   - Or use SFTP/FTP client")
                        print(f"{'='*50}\n")
                        
                        # Also display ASCII QR code in terminal if possible
                        try:
                            # Try to decode QR code from WhatsApp page
                            # WhatsApp QR contains connection URL
                            qr_text = await page.evaluate('''
                                () => {
                                    // Try to find QR code data in page
                                    const qrDiv = document.querySelector('[data-ref]');
                                    return qrDiv ? qrDiv.getAttribute('data-ref') : null;
                                }
                            ''')
                            
                            if qr_text:
                                qr = qrcode.QRCode()
                                qr.add_data(qr_text)
                                qr.make(fit=True)
                                print("Terminal QR Code (ASCII):")
                                qr.print_ascii(invert=True)
                                print()
                            else:
                                # Fallback: display info about QR file
                                print("Note: Terminal QR code not available.")
                                print("      Please download the PNG file to scan.")
                        except Exception as qr_ascii_error:
                            print("Note: Terminal QR display not available.")
                            print("      Please download the PNG file to scan.")
                    
                    else:
                        print("📱 Please scan the QR code in the browser window")
                        print(f"   (Also saved to: {qr_image_path.absolute()})")
                        print(f"{'='*50}\n")
                
            except Exception as qr_error:
                print(f"⚠ Could not extract QR code: {qr_error}")
                if not headless:
                    print("📱 Please check the browser window and scan manually")
                else:
                    print("📱 Please check browser or use VNC/X11 forwarding")
            
            print("Waiting for authentication...")
            print("💡 Tip: QR code changes every ~20 seconds. If it expires, refresh will happen automatically.")
            
            # Poll for login status with better feedback and page refresh
            max_attempts = 180  # 180 * 2 seconds = 6 minutes
            attempt = 0
            last_qr_refresh = 0
            last_qr_extract = 0
            qr_refresh_interval = 15  # Refresh page every 15 checks (~30 seconds) to get new QR if needed
            qr_extract_interval = 10  # Extract new QR every 10 checks (~20 seconds) without full page refresh
            verification_message_shown = False  # Track if we've shown the verification message
            
            while attempt < max_attempts:
                attempt += 1
                
                # Extract new QR code periodically without page refresh (QR changes every ~20 seconds)
                if attempt > 1 and (attempt - last_qr_extract) >= qr_extract_interval:
                    try:
                        # Check if QR code canvas is still visible (not logged in yet)
                        canvas = await page.query_selector('canvas')
                        if canvas:
                            is_qr_visible = await canvas.is_visible()
                            if is_qr_visible:
                                # QR code visible, extract new QR code
                                try:
                                    qr_data_url = await page.evaluate('''
                                        () => {
                                            const canvas = document.querySelector('canvas');
                                            if (canvas) {
                                                return canvas.toDataURL();
                                            }
                                            return null;
                                        }
                                    ''')
                                    
                                    if qr_data_url:
                                        qr_base64 = qr_data_url.split(',')[1] if ',' in qr_data_url else qr_data_url
                                        qr_image_path = self.sessions_dir / f"{session_name}_qr.png"
                                        with open(qr_image_path, 'wb') as f:
                                            f.write(base64.b64decode(qr_base64))
                                        
                                        print(f"\n{'='*50}")
                                        print(f"📱 NEW QR CODE GENERATED (session: {session_name})")
                                        print(f"{'='*50}")
                                        
                                        if headless:
                                            print(f"📱 New QR code saved: {qr_image_path.absolute()}")
                                            
                                            # Display new QR code ASCII in terminal
                                            try:
                                                qr_text = await page.evaluate('''
                                                    () => {
                                                        const qrDiv = document.querySelector('[data-ref]');
                                                        return qrDiv ? qrDiv.getAttribute('data-ref') : null;
                                                    }
                                                ''')
                                                
                                                if qr_text:
                                                    qr = qrcode.QRCode()
                                                    qr.add_data(qr_text)
                                                    qr.make(fit=True)
                                                    print("\n📱 New Terminal QR Code (ASCII):")
                                                    qr.print_ascii(invert=True)
                                                    print()
                                            except:
                                                print("   (ASCII QR code unavailable - please use PNG file)")
                                        else:
                                            print(f"📱 New QR code displayed in browser (also saved to: {qr_image_path.absolute()})")
                                            # Also show ASCII for convenience
                                            try:
                                                qr_text = await page.evaluate('''
                                                    () => {
                                                        const qrDiv = document.querySelector('[data-ref]');
                                                        return qrDiv ? qrDiv.getAttribute('data-ref') : null;
                                                    }
                                                ''')
                                                if qr_text:
                                                    qr = qrcode.QRCode()
                                                    qr.add_data(qr_text)
                                                    qr.make(fit=True)
                                                    print("\n📱 New Terminal QR Code (ASCII):")
                                                    qr.print_ascii(invert=True)
                                                    print()
                                            except:
                                                pass
                                        
                                        print(f"{'='*50}\n")
                                        last_qr_extract = attempt
                                except:
                                    pass
                    except:
                        pass
                
                # Refresh page periodically to get updated QR code or detect login state changes
                if attempt > 1 and (attempt - last_qr_refresh) >= qr_refresh_interval:
                    try:
                        print("🔄 Refreshing page to check authentication status...")
                        await page.reload(wait_until='networkidle')
                        await asyncio.sleep(3)  # Wait for page to load
                        last_qr_refresh = attempt
                        last_qr_extract = attempt  # Reset QR extract counter after page refresh
                    except Exception as e:
                        print(f"⚠ Error refreshing page: {e}")
                
                # Check if logged in with multiple verification methods
                is_logged_in = await self.check_login_status(page)
                
                # Additional verification: check if QR code disappeared and chat list appeared
                # Only check if we haven't detected login yet
                if not is_logged_in:
                    try:
                        # Check if QR canvas is gone and chat elements appeared
                        qr_check = await page.evaluate('''() => {
                            const canvas = document.querySelector('canvas');
                            const chatList = document.querySelector('[data-testid="chat-list"]');
                            const paneSide = document.querySelector('#pane-side');
                            
                            if (!canvas) {
                                // No canvas, check if chat is visible
                                const hasChatVisible = (chatList && window.getComputedStyle(chatList).display !== 'none') ||
                                                     (paneSide && window.getComputedStyle(paneSide).display !== 'none');
                                return { qrVisible: false, hasChat: hasChatVisible, noCanvas: true };
                            }
                            
                            const style = window.getComputedStyle(canvas);
                            const qrVisible = style.display !== 'none' && 
                                            style.visibility !== 'hidden' && 
                                            style.opacity !== '0';
                            const hasChat = (chatList && window.getComputedStyle(chatList).display !== 'none') ||
                                          (paneSide && window.getComputedStyle(paneSide).display !== 'none');
                            
                            return {
                                qrVisible: qrVisible,
                                hasChat: hasChat,
                                noCanvas: false
                            };
                        }''')
                        
                        if qr_check and not qr_check.get('qrVisible') and qr_check.get('hasChat'):
                            # QR gone and chat present - verify login immediately
                            if not verification_message_shown:  # Only show message once
                                print("🔍 QR code disappeared and chat list detected - verifying login...")
                                verification_message_shown = True
                            
                            await asyncio.sleep(2)  # Give it a moment for page to fully load
                            
                            # Do final verification - use more thorough check
                            is_logged_in = await self.check_login_status(page)
                            
                            if is_logged_in:
                                # Success! Exit verification
                                break
                            else:
                                # Not logged in yet, but QR is gone - might be in transition
                                # Wait a bit more and check again (only once more per detection)
                                await asyncio.sleep(3)
                                is_logged_in = await self.check_login_status(page)
                                if is_logged_in:
                                    break
                                # If still not logged in after this, wait for next check
                                # (Don't immediately check again to avoid loop)
                                await asyncio.sleep(2)
                    except Exception as verify_error:
                        # Don't spam error messages
                        pass
                
                # If we detected login, exit the loop
                if is_logged_in:
                    print(f"\n✓ Session {session_name} authenticated successfully!")
                    # Clean up QR file
                    qr_file = self.sessions_dir / f"{session_name}_qr.png"
                    if qr_file.exists():
                        try:
                            qr_file.unlink()
                        except:
                            pass
                    # Wait a bit more to ensure everything is loaded
                    await asyncio.sleep(2)
                    return
                
                # Provide feedback every 10 seconds
                if attempt % 5 == 0:
                    elapsed = attempt * 2
                    print(f"⏳ Still waiting for authentication... ({elapsed} seconds)")
                    if headless and attempt == 5:
                        qr_file = self.sessions_dir / f"{session_name}_qr.png"
                        if qr_file.exists():
                            print(f"   QR Code file: {qr_file.absolute()}")
                    if elapsed >= 60:
                        print("💡 Reminder: Make sure you've scanned the QR code with your WhatsApp mobile app")
                        print("   If QR code expired, page will auto-refresh soon...")
                
                await asyncio.sleep(2)  # Check every 2 seconds
            
            # Timeout
            print(f"\n⚠ Authentication timeout after {max_attempts * 2} seconds")
            print("Please make sure you've scanned the QR code and try again.")
            raise TimeoutError("Authentication timeout")
            
        except TimeoutError:
            raise
        except Exception as e:
            print(f"⚠ QR authentication error: {e}")
            # Final attempt with longer wait
            print("📱 Making final attempt to detect login...")
            await asyncio.sleep(5)
            if await self.check_login_status(page):
                print(f"✓ Session {session_name} authenticated!")
                return
            raise
    
    async def load_all_sessions(self):
        """
        Load all saved sessions on startup
        """
        session_dirs = [d for d in self.sessions_dir.iterdir() if d.is_dir()]
        
        print(f"Found {len(session_dirs)} saved sessions")
        
        for session_dir in session_dirs:
            session_name = session_dir.name
            try:
                await self.create_session(session_name, headless=True)
                print(f"✓ Loaded session: {session_name}")
            except Exception as e:
                print(f"✗ Failed to load session {session_name}: {e}")
    
    async def monitor_session_health(self, session_name):
        """
        Monitor session health and auto-recover if needed
        """
        while session_name in self.active_sessions:
            session = self.active_sessions[session_name]
            page = session['page']
            
            try:
                # Check if session is still active
                await page.evaluate('() => document.querySelector("[data-testid=\\"chat-list\\"]")')
                
                # Calculate health score
                messages = session['messages_sent']
                age = (datetime.now() - session['created_at']).total_seconds() / 3600  # hours
                
                health = 100
                health -= min(messages / 10, 50)  # Reduce by message count
                health -= min(age * 2, 30)  # Reduce by age
                
                session['health_score'] = max(health, 10)
                
                # Auto-rotate if health is too low
                if health < 20:
                    print(f"⚠ Session {session_name} health low ({health:.1f}%), consider rotation")
                
            except Exception as e:
                print(f"✗ Session {session_name} disconnected: {e}")
                # Attempt recovery
                try:
                    await self.recover_session(session_name)
                except:
                    print(f"✗ Failed to recover session {session_name}")
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def recover_session(self, session_name):
        """Attempt to recover a disconnected session"""
        if session_name in self.active_sessions:
            session = self.active_sessions[session_name]
            try:
                page = session['page']
                await page.reload()
                await page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
                print(f"✓ Session {session_name} recovered")
            except:
                print(f"✗ Could not recover session {session_name}")
    
    def get_best_session(self):
        """
        Get the best available session for sending
        """
        if not self.active_sessions:
            raise Exception("No active sessions available")
        
        # Sort by health score
        sorted_sessions = sorted(
            self.active_sessions.items(),
            key=lambda x: x[1]['health_score'],
            reverse=True
        )
        
        return sorted_sessions[0][1]
    
    async def distribute_load(self, phone_numbers, session_names=None, strategy='round-robin'):
        """
        Distribute phone numbers across sessions for parallel sending
        
        Args:
            phone_numbers: List of phone numbers to send
            session_names: Optional list of specific session names to use. If None, use all active sessions.
            strategy: Distribution strategy - 'round-robin', 'random', or 'weighted'
        
        Returns:
            Dictionary mapping session names to their assigned phone numbers
        """
        # Filter sessions if specific ones requested
        if session_names:
            available_sessions = {name: self.active_sessions[name] for name in session_names 
                                 if name in self.active_sessions}
            if not available_sessions:
                raise Exception(f"None of the requested sessions found: {session_names}")
        else:
            available_sessions = self.active_sessions.copy()
        
        active_count = len(available_sessions)
        if active_count == 0:
            raise Exception("No active sessions")
        
        # Split numbers based on strategy
        if strategy == 'random':
            chunks = [[] for _ in range(active_count)]
            session_list = list(available_sessions.keys())
            for number in phone_numbers:
                random_index = random.randint(0, active_count - 1)
                chunks[random_index].append(number)
        elif strategy == 'weighted':
            # Weight by health score (higher health = more messages)
            chunks = [[] for _ in range(active_count)]
            session_list = list(available_sessions.keys())
            weights = [available_sessions[name]['health_score'] for name in session_list]
            total_weight = sum(weights)
            
            for number in phone_numbers:
                r = random.uniform(0, total_weight)
                upto = 0
                selected_index = 0
                for i, weight in enumerate(weights):
                    if upto + weight >= r:
                        selected_index = i
                        break
                    upto += weight
                chunks[selected_index].append(number)
        else:  # round-robin (default)
            chunks = [[] for _ in range(active_count)]
            for i, number in enumerate(phone_numbers):
                chunks[i % active_count].append(number)
        
        distribution = {}
        session_list = list(available_sessions.keys())
        for i, session_name in enumerate(session_list):
            distribution[session_name] = {
                'session': available_sessions[session_name],
                'numbers': chunks[i]
            }
            
            # Start health monitoring for sessions that will be used
            try:
                loop = asyncio.get_running_loop()
                if session_name not in [t.get_name() for t in asyncio.all_tasks(loop)]:
                    loop.create_task(self.monitor_session_health(session_name))
            except:
                pass
        
        return distribution
    
    async def close_session(self, session_name):
        """Close a specific session"""
        if session_name in self.active_sessions:
            session = self.active_sessions[session_name]
            try:
                # Close context (browser is part of persistent context)
                if session.get('context'):
                    context = session['context']
                    # Close all pages first
                    pages = context.pages
                    for page in pages:
                        try:
                            await page.close()
                        except:
                            pass
                    # Then close context
                    try:
                        await context.close()
                    except:
                        pass
            except Exception as e:
                print(f"⚠ Error closing session {session_name}: {e}")
            finally:
                if session_name in self.active_sessions:
                    del self.active_sessions[session_name]
                    print(f"✓ Session {session_name} closed")
    
    async def delete_session_data(self, session_name):
        """Permanently delete session data from disk"""
        context_dir = self.sessions_dir / session_name
        
        if not context_dir.exists():
            return False
        
        # Close session if active
        if session_name in self.active_sessions:
            await self.close_session(session_name)
            await asyncio.sleep(0.5)
        
        # Delete directory and all its contents
        import shutil
        try:
            shutil.rmtree(context_dir)
            
            # Also delete QR file if exists
            qr_file = self.sessions_dir / f"{session_name}_qr.png"
            if qr_file.exists():
                try:
                    qr_file.unlink()
                except:
                    pass
            
            return True
        except Exception as e:
            print(f"⚠ Error deleting session data: {e}")
            return False
    
    async def close_all(self):
        """Close all sessions"""
        # Close all sessions first
        for session_name in list(self.active_sessions.keys()):
            try:
                await self.close_session(session_name)
            except:
                pass
        
        # Give time for cleanup
        await asyncio.sleep(0.5)
        
        # Stop playwright
        if self.playwright:
            try:
                await self.playwright.stop()
                # Give time for subprocess cleanup
                await asyncio.sleep(0.5)
            except Exception as e:
                # Ignore errors during shutdown
                pass
        
        # Clear playwright reference
        self.playwright = None

