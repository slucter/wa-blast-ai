"""
WhatsApp High-Performance CLI
"""
import click
import asyncio
import yaml
from pathlib import Path
import sys
import os
import tempfile
import shutil
import warnings

# Set event loop policy for Windows before importing Playwright
if sys.platform == 'win32':
    # Python 3.8+ on Windows: use WindowsDefaultEventLoopPolicy
    # which defaults to ProactorEventLoop (supports subprocess)
    if hasattr(asyncio, 'WindowsDefaultEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsDefaultEventLoopPolicy())
    # Suppress ResourceWarning from asyncio subprocess cleanup on Windows
    warnings.filterwarnings('ignore', category=ResourceWarning, message='.*unclosed.*')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.session_manager import SessionManager
from core.optimizer import SpeedOptimizer
from core.formatter import PhoneFormatter
from core.validator import Validator
from core.anti_ban import AntiBanEngine
from core.personalizer import MessagePersonalizer


def estimate_time(total_numbers, sessions):
    """
    Estimate completion time based on optimal settings
    """
    numbers_per_session = total_numbers / sessions if sessions > 0 else total_numbers
    
    # Average delays from optimal settings
    if numbers_per_session <= 50:
        avg_delay = 8
    elif numbers_per_session <= 200:
        avg_delay = 5
    else:
        avg_delay = 3
    
    total_seconds = numbers_per_session * avg_delay
    breaks = (numbers_per_session // 50) * 45  # Break time
    total_seconds += breaks
    
    minutes = int(total_seconds / 60)
    return f"~{minutes} minutes"


async def send_messages(numbers_file, message, template_file, session_count, country_code='62', personalize=False, use_sessions=None, session_strategy='round-robin'):
    """
    Main sending function with optimal settings
    """
    personalizer = MessagePersonalizer()
    
    # Load contacts (support format: nomor|nama|alamat or just nomor)
    contacts = []
    with open(numbers_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '|' in line:
                # Format: nomor|nama|alamat
                contact = personalizer.parse_contact_line(line)
                if contact:
                    contacts.append(contact)
            else:
                # Format: nomor saja
                contacts.append({
                    'number': line,
                    'name': None,
                    'address': None
                })
    
    if not contacts:
        click.echo("Error: No valid contacts found in file")
        return
    
    # Extract numbers for distribution
    numbers = [c['number'] for c in contacts]
    
    # Load message
    messages_list = []  # List of messages (each will be separate bubble)
    
    if template_file:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by empty lines (lines with only whitespace)
        # Empty line = new bubble chat
        # Non-empty line with \n = line breaks within same bubble
        lines = content.split('\n')
        current_bubble = []
        
        for line in lines:
            line_stripped = line.strip()
            
            if not line_stripped:
                # Empty line = finish current bubble and start new one
                if current_bubble:
                    # Join current bubble (handle \n within bubble)
                    bubble_text = '\n'.join(current_bubble)
                    bubble_text = bubble_text.replace('\\n', '\n')  # Convert \n literal to actual newline
                    messages_list.append(bubble_text.strip())
                    current_bubble = []
            else:
                # Non-empty line = part of current bubble
                current_bubble.append(line)
        
        # Don't forget last bubble if file doesn't end with empty line
        if current_bubble:
            bubble_text = '\n'.join(current_bubble)
            bubble_text = bubble_text.replace('\\n', '\n')  # Convert \n literal to actual newline
            messages_list.append(bubble_text.strip())
        
        # If only one message, keep backward compatibility
        if len(messages_list) == 1:
            message = messages_list[0]
            messages_list = None
        elif len(messages_list) == 0:
            click.echo("Error: Template file is empty")
            return
    elif not message:
        click.echo("Error: Message or template file required")
        return
    else:
        # Handle \n in direct message input
        message = message.replace('\\n', '\n')
        messages_list = None
    
    print(f"""
╔════════════════════════════════════╗
║   WhatsApp High-Speed Sender      ║
╠════════════════════════════════════╣
║ Numbers: {len(numbers):<26}║
║ Sessions: {session_count:<25}║
║ Est. Time: {estimate_time(len(numbers), session_count):<22}║
╚════════════════════════════════════╝
""")
    
    # Initialize components
    session_mgr = SessionManager()
    optimizer = SpeedOptimizer(max_parallel=session_count, default_country_code=country_code)
    
    # Load sessions
    try:
        await session_mgr.load_all_sessions()
    except Exception as e:
        click.echo(f"Error loading sessions: {e}")
        click.echo("Creating new session...")
        await session_mgr.create_session("default", headless=False)
    
    # Check if we have active sessions
    if not session_mgr.active_sessions:
        click.echo("No active sessions. Creating new session...")
        await session_mgr.create_session("default", headless=False)
    
    # Parse session selection
    selected_sessions = None
    if use_sessions:
        selected_sessions = [s.strip() for s in use_sessions.split(',')]
        # Validate sessions exist
        missing = [s for s in selected_sessions if s not in session_mgr.active_sessions]
        if missing:
            click.echo(f"Error: Sessions not found: {', '.join(missing)}")
            click.echo(f"Available sessions: {', '.join(session_mgr.active_sessions.keys())}")
            return
        click.echo(f"📱 Using specific sessions: {', '.join(selected_sessions)}")
    elif session_count > 0:
        # Limit to session_count sessions
        available = list(session_mgr.active_sessions.keys())[:session_count]
        selected_sessions = available
        if len(available) < session_count:
            click.echo(f"⚠ Only {len(available)} session(s) available, using all available")
    else:
        # Use all sessions
        selected_sessions = None
        click.echo(f"📱 Using all available sessions: {', '.join(session_mgr.active_sessions.keys())}")
    
    click.echo(f"📊 Distribution strategy: {session_strategy}")
    
    # Create contact mapping
    contact_map = {c['number']: c for c in contacts}
    
    # Distribute load
    try:
        distribution = await session_mgr.distribute_load(numbers, session_names=selected_sessions, strategy=session_strategy)
    except Exception as e:
        click.echo(f"Error distributing load: {e}")
        return
    
    # Send in parallel
    try:
        # If messages_list is set, send multiple bubbles per contact
        if messages_list:
            results = await optimizer.parallel_send_multiple(distribution, messages_list, contact_map=contact_map, personalize=personalize)
        else:
            results = await optimizer.parallel_send(distribution, message, contact_map=contact_map, personalize=personalize)
        
        # Show results
        success = sum(1 for r in results if r.get('status') == 'sent')
        failed = len(results) - success
        
        print(f"""
╔════════════════════════════════════╗
║          SENDING COMPLETE          ║
╠════════════════════════════════════╣
║ Success: {success:<24}║
║ Failed: {failed:<25}║
║ Total: {len(results):<27}║
╚════════════════════════════════════╝
""")
        
    except Exception as e:
        click.echo(f"Error during sending: {e}")
    finally:
        # Clean up
        await session_mgr.close_all()


async def add_new_session(session_name="default", headless=False, force_new=False):
    """Add new WhatsApp session"""
    session_mgr = SessionManager()
    try:
        await session_mgr.create_session(session_name, headless=headless, force_new=force_new)
        click.echo(f"\n✓ Session '{session_name}' created successfully!")
        
        if not headless:
            click.echo("\n" + "="*50)
            click.echo("Browser window is open. Please:")
            click.echo("1. Scan the QR code with your WhatsApp mobile app")
            click.echo("2. Wait for authentication to complete")
            click.echo("3. Press Ctrl+C to close the session")
            click.echo("="*50 + "\n")
            try:
                # Keep the session alive until user interrupts
                while session_name in session_mgr.active_sessions:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                click.echo("\n⚠ Closing session...")
                await session_mgr.close_session(session_name)
        else:
            # In headless mode: if session already authenticated, close immediately
            if session_name in session_mgr.active_sessions:
                # Session is ready and authenticated
                click.echo(f"✓ Session '{session_name}' is ready and saved")
                await session_mgr.close_session(session_name)
                click.echo(f"✓ Session '{session_name}' saved successfully")
            else:
                # Session needs QR scan, but in headless mode we can't wait
                # QR code should have been saved to file
                click.echo(f"⚠ Session '{session_name}' created but needs QR scan")
                click.echo(f"   Please check: sessions/{session_name}_qr.png")
                click.echo(f"   Download and scan the QR code, then session will be ready")
        
        # Clean up playwright properly
        await session_mgr.close_all()
    except KeyboardInterrupt:
        click.echo("\n⚠ Interrupted by user")
        try:
            await session_mgr.close_all()
        except:
            pass
    except Exception as e:
        click.echo(f"✗ Failed to create session: {e}")
        try:
            await session_mgr.close_all()
        except:
            pass
        raise


def list_active_sessions():
    """List all active sessions"""
    sessions_dir = Path("./sessions")
    if not sessions_dir.exists():
        click.echo("No sessions found")
        return
    
    session_dirs = [d for d in sessions_dir.iterdir() if d.is_dir()]
    if not session_dirs:
        click.echo("No sessions found")
        return
    
    click.echo(f"\nFound {len(session_dirs)} sessions:")
    for session_dir in session_dirs:
        click.echo(f"  - {session_dir.name}")


def show_status():
    """Show system status"""
    click.echo("System Status:")
    click.echo("  Sessions: Check with --action list-sessions")
    click.echo("  Configuration: Check config/optimal_settings.yaml")


async def delete_session_async(session_name):
    """Delete a session by name - permanently removes all session data"""
    session_mgr = SessionManager()
    
    # Initialize playwright to access session manager methods
    await session_mgr.initialize_playwright()
    
    # Check if session directory exists
    session_path = session_mgr.sessions_dir / session_name
    
    if not session_path.exists():
        click.echo(f"✗ Session '{session_name}' not found")
        await session_mgr.close_all()
        return
    
    # Delete session data (this will also close active session if any)
    success = await session_mgr.delete_session_data(session_name)
    
    # Close playwright
    if session_mgr.playwright:
        await session_mgr.close_all()
    
    if success:
        click.echo(f"✓ Session '{session_name}' deleted successfully (all data removed)")
        click.echo(f"  You can now create a new session with the same name")
    else:
        click.echo(f"✗ Failed to delete session '{session_name}' completely")


def delete_session(session_name):
    """Delete a session by name (wrapper)"""
    try:
        asyncio.run(delete_session_async(session_name))
    except Exception as e:
        click.echo(f"✗ Error deleting session: {e}")


@click.command()
@click.option('--action', type=click.Choice(['send', 'add-session', 'list-sessions', 'delete-session', 'status']), required=True,
              help='Action to perform')
@click.option('--numbers', type=click.Path(exists=True), help='Path to numbers file')
@click.option('--phone', type=str, help='Single phone number (alternative to --numbers file)')
@click.option('--message', type=str, help='Message text')
@click.option('--template', type=click.Path(exists=True), help='Message template file')
@click.option('--sessions', type=int, default=1, help='Number of sessions to use (0 = use all available sessions)')
@click.option('--session-name', type=str, default='default', help='Session name for add-session')
@click.option('--force', is_flag=True, help='Force create new session (delete existing session folder if exists)')
@click.option('--use-sessions', type=str, help='Comma-separated list of specific session names to use (e.g., "session1,session2")')
@click.option('--session-strategy', type=click.Choice(['round-robin', 'random', 'weighted']), default='round-robin',
              help='Session distribution strategy: round-robin (default), random, or weighted (by health score)')
@click.option('--headless', is_flag=True, help='Run browser in headless mode')
@click.option('--country-code', type=str, default='62', help='Default country code')
@click.option('--personalize', is_flag=True, help='Enable personalization (greeting + name + address)')
def cli(action, numbers, phone, message, template, sessions, session_name, headless, country_code, personalize, use_sessions, session_strategy, force):
    """
    WhatsApp High-Performance CLI
    
    Examples:
    # Send to single number
    python wa_cli.py --action send --phone "08123456789" --message "Hello!"
    
    # Send with file (bulk) - use 3 sessions
    python wa_cli.py --action send --numbers contacts.txt --template template.txt --sessions 3
    
    # Send using specific sessions
    python wa_cli.py --action send --numbers contacts.txt --template template.txt --use-sessions "session1,session2"
    
    # Send with random session distribution
    python wa_cli.py --action send --numbers contacts.txt --template template.txt --session-strategy random
    
    # Send with weighted distribution (by health score)
    python wa_cli.py --action send --numbers contacts.txt --template template.txt --session-strategy weighted
    
    # Use all available sessions
    python wa_cli.py --action send --numbers contacts.txt --template template.txt --sessions 0
    
    # Add new session
    python wa_cli.py --action add-session --session-name session_2
    
    # Force create new session (delete existing if any)
    python wa_cli.py --action add-session --session-name session_2 --force
    
    # List sessions
    python wa_cli.py --action list-sessions
    
    # Delete session
    python wa_cli.py --action delete-session --session-name session_2
    
    # Check status
    python wa_cli.py --action status
    """
    
    if action == 'send':
        # Support both --phone (single) and --numbers (file)
        if not numbers and not phone:
            click.echo("Error: Either --numbers (file) or --phone (single number) is required for send action")
            return
        
        # If phone provided, create temp file with single number
        temp_file_path = None
        if phone:
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
            temp_file.write(phone + '\n')
            temp_file.close()
            numbers = temp_file.name
            temp_file_path = temp_file.name
            click.echo(f"📱 Sending to single number: {phone}")
        
        if not message and not template:
            click.echo("Error: Either --message or --template is required")
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)  # Clean up temp file
            return
        try:
            # Python 3.8+ on Windows defaults to ProactorEventLoop which supports subprocess
            # Just use asyncio.run() which will create the appropriate event loop
            asyncio.run(send_messages(numbers, message, template, sessions, country_code, personalize, use_sessions, session_strategy))
        except KeyboardInterrupt:
            click.echo("\n⚠ Interrupted by user")
        except Exception as e:
            click.echo(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up temp file if created from --phone
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
    elif action == 'add-session':
        try:
            # Use asyncio.run() which respects the event loop policy set above
            asyncio.run(add_new_session(session_name, headless, force_new=force))
            # Give time for subprocess cleanup on Windows
            import sys
            if sys.platform == 'win32':
                import time
                time.sleep(0.5)
        except KeyboardInterrupt:
            click.echo("\n⚠ Interrupted by user")
        except Exception as e:
            click.echo(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Additional cleanup time for Windows
            if sys.platform == 'win32':
                import time
                time.sleep(0.3)
    elif action == 'list-sessions':
        list_active_sessions()
    elif action == 'delete-session':
        if not session_name:
            click.echo("Error: --session-name is required for delete-session action")
            return
        delete_session(session_name)
    elif action == 'status':
        show_status()


if __name__ == '__main__':
    cli()

