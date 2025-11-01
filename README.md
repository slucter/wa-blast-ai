# WhatsApp High-Performance Bot with CLI & API

A high-performance WhatsApp messaging system with CLI and REST API interfaces, optimized for maximum delivery speed while implementing sophisticated anti-ban mechanisms.

## ✨ Features

- 🚀 **High Performance**: Send 500-700 messages/hour with optimal settings
- 🛡️ **Anti-Ban Protection**: Advanced anti-detection algorithms
- 📱 **Multi-Session Support**: Parallel sessions for increased throughput with flexible session selection
- 💻 **CLI Interface**: Easy-to-use command-line tool with comprehensive options
- 🌐 **REST API**: Full-featured FastAPI server
- 🔄 **Session Management**: Persistent sessions with health monitoring and auto-recovery
- 📊 **Rate Limiting**: Dynamic delays based on session state
- 🎯 **Message Variation**: Automatic message variations to avoid detection
- 🎨 **Message Personalization**: Auto-greeting, name bolding, address inclusion
- 🔄 **Auto QR Refresh**: Automatic QR code refresh every ~20 seconds
- 📝 **Template Support**: Multi-bubble messages, line breaks, and placeholders

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [Session Management](#session-management)
- [Message Templates](#message-templates)
- [Contact Lists](#contact-lists)
- [API Usage](#api-usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Playwright (automatically installed)
- Chrome/Chromium browser (automatically installed)

### Quick Install

#### Windows (PowerShell):
```powershell
.\install.ps1
```

#### Linux/macOS (Bash):
```bash
chmod +x install.sh
./install.sh
```

### Manual Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install Playwright system dependencies (Linux only)
playwright install-deps chromium

# Create necessary directories
mkdir -p sessions logs data templates
```

## 🎯 Quick Start

### 1. Add Your First Session

```bash
# Add session with GUI (browser window will open)
python cli/wa_cli.py --action add-session --session-name my_session

# Add session in headless mode (for SSH/VPS)
python cli/wa_cli.py --action add-session --session-name my_session --headless
```

**Note**: In headless mode, QR code will be saved to `sessions/{session_name}_qr.png`. Download and scan with your WhatsApp mobile app.

### 2. Send Your First Message

```bash
# Send to single number
python cli/wa_cli.py --action send \
  --phone "08123456789" \
  --message "Hello, this is a test!"

# Send to multiple contacts from file
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --personalize
```

## 📖 CLI Usage

### Session Management

```bash
# List all sessions
python cli/wa_cli.py --action list-sessions

# Add new session
python cli/wa_cli.py --action add-session --session-name session_2

# Add session with force (delete existing if any)
python cli/wa_cli.py --action add-session --session-name session_2 --force

# Delete session
python cli/wa_cli.py --action delete-session --session-name session_2

# Check status
python cli/wa_cli.py --action status
```

### Sending Messages

#### Basic Send

```bash
# Send to single number
python cli/wa_cli.py --action send \
  --phone "08123456789" \
  --message "Hello!"

# Send to multiple contacts
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt
```

#### Session Selection

```bash
# Use specific session(s)
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --use-sessions "session1,session2"

# Use first N sessions
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --sessions 3

# Use all available sessions
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --sessions 0
```

#### Distribution Strategies

```bash
# Round-robin (default) - evenly distribute numbers
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --session-strategy round-robin

# Random - randomly assign numbers to sessions
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --session-strategy random

# Weighted - assign based on session health score
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --session-strategy weighted
```

#### With Personalization

```bash
# Enable personalization (greeting + name + address)
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --personalize
```

**Personalization Features:**
- Auto-greeting based on time (Selamat pagi/siang/sore/malam)
- Bold contact name
- Optional address inclusion

### CLI Options

| Option | Description | Example |
|--------|-------------|---------|
| `--action` | Action to perform | `send`, `add-session`, `list-sessions`, `delete-session`, `status` |
| `--phone` | Single phone number | `"08123456789"` |
| `--numbers` | Path to contacts file | `data/contacts.txt` |
| `--message` | Direct message text | `"Hello!"` |
| `--template` | Path to template file | `templates/message.txt` |
| `--sessions` | Number of sessions (0 = all) | `3` or `0` |
| `--use-sessions` | Specific session names | `"session1,session2"` |
| `--session-strategy` | Distribution strategy | `round-robin`, `random`, `weighted` |
| `--session-name` | Session name for add/delete | `"my_session"` |
| `--headless` | Run browser in headless mode | (flag) |
| `--force` | Force create new session | (flag) |
| `--country-code` | Default country code | `62` |
| `--personalize` | Enable personalization | (flag) |

## 🔐 Session Management

### Adding Sessions

```bash
# With GUI (recommended for first time)
python cli/wa_cli.py --action add-session --session-name session_1

# Headless mode (for SSH/VPS)
python cli/wa_cli.py --action add-session --session-name session_1 --headless

# Force create (delete existing and create new)
python cli/wa_cli.py --action add-session --session-name session_1 --force
```

**Headless Mode (SSH/VPS):**
1. QR code will be saved to `sessions/{session_name}_qr.png`
2. Download the QR code file using SCP/SFTP
3. Scan with your WhatsApp mobile app
4. Session will be automatically detected when authenticated

**QR Code Auto-Refresh:**
- QR code automatically refreshes every ~20 seconds
- New QR code is displayed in terminal and saved to file
- No manual refresh needed

### Managing Sessions

```bash
# List all sessions
python cli/wa_cli.py --action list-sessions

# Delete a session (removes all session data)
python cli/wa_cli.py --action delete-session --session-name session_1
```

## 📝 Message Templates

### Basic Template

Create a template file in `templates/` directory:

```txt
# templates/welcome.txt
Hi {name},

Welcome to our service! We're excited to have you on board.

Best regards,
Team
```

### Multi-Bubble Messages

Empty lines in template create separate chat bubbles:

```txt
# templates/product_offer.txt
Hi {name}! Check out our latest product.

[Empty line = new bubble]

Special offer: 50% off for the first 100 customers!
```

### Line Breaks in Same Bubble

Use `\n` for line breaks within the same bubble:

```txt
# templates/details.txt
Product Details:
\n
Name: {product_name}
Price: {price}
Stock: {stock}
```

### Using Templates

```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/welcome.txt
```

## 📋 Contact Lists

### Format 1: Simple (Number Only)

```txt
# data/contacts.txt
08123456789
+62 812 3456 7890
628123456789
```

### Format 2: With Name and Address (for Personalization)

```txt
# data/contacts_personalized.txt
08123456789|John Doe|Jl. Sudirman No. 123
08123456790|Jane Smith|Jl. Thamrin No. 456
08123456791|Bob Johnson|
```

**Format**: `nomor|nama|alamat`
- Name is optional (can be empty: `nomor||alamat`)
- Address is optional (can be empty: `nomor|nama|` or `nomor|nama`)

### With Personalization

When using `--personalize` flag:

```
Message format:
Selamat siang *nama*.

Alamat : alamat

*pesan nya
```

**Example output:**
```
Selamat siang *John Doe*.

Alamat : Jl. Sudirman No. 123

Check out our latest product!
```

## 🌐 API Usage

### Start API Server

```bash
uvicorn api.server:app --reload --port 8000
```

### API Endpoints

#### Send Messages

```bash
curl -X POST http://localhost:8000/send \
  -H "Content-Type: application/json" \
  -d '{
    "numbers": ["628123456789", "628987654321"],
    "message": "Hello, this is a test message",
    "sessions": 3,
    "priority": "high"
  }'
```

#### List Sessions

```bash
curl http://localhost:8000/sessions
```

#### Add Session

```bash
curl -X POST "http://localhost:8000/session/add?name=session_2"
```

#### Check Job Status

```bash
curl http://localhost:8000/job/{job_id}
```

#### Health Check

```bash
curl http://localhost:8000/health
```

See API documentation at `http://localhost:8000/docs` (Swagger UI).

## ⚙️ Configuration

### Optimal Settings

The system uses optimal settings discovered through testing:

- **Configuration B (Recommended)**: Balanced speed/safety
  - Delays: 3-8 seconds dynamic
  - Sessions: 3 parallel
  - Speed: ~500-700 messages/hour
  - Ban Risk: <5%

Settings can be customized in `config/optimal_settings.yaml`.

### Delay Strategy

- First 10 messages: 8-15 seconds
- Messages 11-50: 5-12 seconds
- Messages 51-200: 3-8 seconds
- Messages 200+: 2-5 seconds
- Break every 50 messages: 30-60 seconds

## 📁 File Structure

```
waBlast/
├── core/
│   ├── anti_ban.py           # Anti-detection algorithms
│   ├── session_manager.py    # Multi-session management
│   ├── optimizer.py          # Speed optimization
│   ├── formatter.py          # Phone number formatting
│   ├── personalizer.py       # Message personalization
│   └── validator.py          # Input validation
├── cli/
│   └── wa_cli.py             # CLI interface
├── api/
│   ├── server.py             # FastAPI server
│   ├── routes/               # API routes
│   └── middleware/           # API middleware
├── config/
│   └── optimal_settings.yaml # Configuration
├── templates/                # Message templates
├── data/                     # Contact lists
├── sessions/                 # Session storage
├── logs/                     # Log files
├── guide_md/                 # Additional documentation
│   ├── TEMPLATE_GUIDE.md
│   ├── PERSONALIZATION_GUIDE.md
│   ├── SSH_SETUP.md
│   └── QUICK_START.md
└── README.md                 # This file
```

## 🛡️ Safety Features

### Anti-Ban Mechanisms

1. **Dynamic Delays**: Delays increase/decrease based on session state
2. **Message Variations**: Automatic greetings, endings, and Unicode variations
3. **Typing Simulation**: Human-like typing speed
4. **Session Rotation**: Distribute load across multiple sessions
5. **Health Monitoring**: Track session health and auto-recover
6. **Time-Based Adjustments**: Adjust behavior based on time of day

### Best Practices

1. ✅ Start with conservative settings (1-2 sessions)
2. ✅ Monitor session health continuously
3. ✅ Rotate sessions regularly
4. ✅ Use message templates with personalization
5. ✅ Implement proper error handling
6. ✅ Keep sessions warm with periodic activity
7. ✅ Use dedicated phone numbers for automation
8. ✅ Use multiple sessions for better distribution
9. ✅ Delete and recreate sessions periodically

### Warning Signs of Potential Ban

- ⚠️ Sudden disconnections
- ⚠️ Slow message delivery
- ⚠️ "Message not sent" errors
- ⚠️ Session health dropping rapidly

## 📊 Performance Benchmarks

Based on testing:

| Configuration | Delay | Sessions | Speed | Ban Risk |
|--------------|-------|----------|-------|----------|
| Ultra-Safe   | 10-20s | 1        | ~180/hr | <1% |
| **Balanced** | **3-8s** | **3** | **500-700/hr** | **<5%** |
| Aggressive   | 2-5s  | 5        | ~1000/hr | ~15% |
| Maximum      | 1-3s  | 10       | ~2000+/hr | >30% |

**Recommended**: Configuration B (Balanced) for best speed/safety balance.

## 🔧 Troubleshooting

### Session Not Connecting

1. Check internet connection
2. Ensure Playwright browsers are installed: `playwright install chromium`
3. Try running with `--headless=false` to see browser
4. Delete session directory and recreate with `--force` flag

### QR Code Not Showing (Headless Mode)

1. Check if QR file is created: `sessions/{session_name}_qr.png`
2. Download the QR code file using SCP/SFTP
3. QR code auto-refreshes every ~20 seconds
4. Wait for "NEW QR CODE GENERATED" message

### Messages Not Sending

1. Check if WhatsApp Web is logged in (verify session status)
2. Verify phone number format
3. Check session health
4. Reduce number of parallel sessions
5. Try with single session first

### High Failure Rate

1. Increase delays in configuration
2. Reduce parallel sessions
3. Check network stability
4. Monitor session health
5. Try different session strategy (weighted instead of round-robin)

### Loop "verifying login" After QR Scan

- This is normal during transition
- Bot will automatically detect successful login
- Wait a few seconds for detection to complete

## 📚 Additional Documentation

### Quick Start & Guides

- **[Getting Started Guide](docs/GETTING_STARTED.md)**: Step-by-step guide from installation to first message
- **[Command Reference](docs/COMMAND_REFERENCE.md)**: Complete reference for all CLI commands and options

### Advanced Guides

- **[Template Guide](guide_md/TEMPLATE_GUIDE.md)**: Detailed guide on creating message templates
- **[Personalization Guide](guide_md/PERSONALIZATION_GUIDE.md)**: How to use message personalization
- **[SSH Setup Guide](guide_md/SSH_SETUP.md)**: Setting up in SSH/VPS environments
- **[Quick Start Guide](guide_md/QUICK_START.md)**: Quick start examples

## ⚖️ Legal & Compliance

⚠️ **IMPORTANT**:

- **User Consent**: Only message users who have explicitly opted in
- **Opt-out Mechanism**: Always include unsubscribe option
- **Privacy Compliance**: Follow GDPR, CCPA, and local privacy laws
- **WhatsApp Terms**: Strictly follow WhatsApp Business API policies
- **Anti-Spam Laws**: Comply with CAN-SPAM, TCPA, and local regulations
- **Message Content**: No misleading, harmful, or illegal content

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is for educational purposes only. Use responsibly and in compliance with WhatsApp's Terms of Service and applicable laws.

## ⚠️ Disclaimer

This tool should only be used for legitimate business communications with proper user consent. Misuse can result in account suspension and legal consequences. The authors are not responsible for any misuse of this software.
