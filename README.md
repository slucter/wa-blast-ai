# WhatsApp High-Performance Bot with CLI & API

A high-performance WhatsApp messaging system with CLI and REST API interfaces, optimized for maximum delivery speed while implementing sophisticated anti-ban mechanisms.

## Features

- 🚀 **High Performance**: Send 500-700 messages/hour with optimal settings
- 🛡️ **Anti-Ban Protection**: Advanced anti-detection algorithms
- 📱 **Multi-Session Support**: Parallel sessions for increased throughput
- 💻 **CLI Interface**: Easy-to-use command-line tool
- 🌐 **REST API**: Full-featured FastAPI server
- 🔄 **Session Management**: Persistent sessions with health monitoring
- 📊 **Rate Limiting**: Dynamic delays based on session state
- 🎯 **Message Variation**: Automatic message variations to avoid detection

## Installation

### Prerequisites

- Python 3.8+
- Node.js (for Playwright)
- Chrome/Chromium browser

### Setup

```bash
# Clone repository
git clone <repo-url>
cd waBlast

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install system dependencies (Linux)
# sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
```

## Quick Start

### CLI Usage

```bash
# Add a new WhatsApp session (first time)
python cli/wa_cli.py --action add-session --session-name default

# Send messages using CLI
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --sessions 3 \
  --country-code 62

# List all sessions
python cli/wa_cli.py --action list-sessions

# Check status
python cli/wa_cli.py --action status
```

### API Usage

```bash
# Start API server
uvicorn api.server:app --reload --port 8000

# Send messages via API
curl -X POST http://localhost:8000/send \
  -H "Content-Type: application/json" \
  -d '{
    "numbers": ["628123456789", "628987654321"],
    "message": "Hello, this is a test message",
    "sessions": 3,
    "priority": "high"
  }'

# Check job status
curl http://localhost:8000/job/{job_id}

# List sessions
curl http://localhost:8000/sessions

# Add new session
curl -X POST "http://localhost:8000/session/add?name=session_2"
```

## Configuration

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

## File Structure

```
waBlast/
├── core/
│   ├── anti_ban.py           # Anti-detection algorithms
│   ├── session_manager.py    # Multi-session management
│   ├── optimizer.py          # Speed optimization
│   ├── formatter.py          # Phone number formatting
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
└── logs/                     # Log files
```

## Message Templates

Create message templates in the `templates/` directory:

```
templates/
└── welcome.txt
```

Example template:
```
Hi {name},

Welcome to our service! We're excited to have you on board.

Best regards,
Team
```

## Contact Lists

Create contact lists in the `data/` directory:

```
data/
└── contacts.txt
```

Format (one number per line):
```
08123456789
+62 812 3456 7890
628123456789
```

## API Endpoints

- `POST /send` - Queue messages for sending
- `GET /job/{job_id}` - Get job status
- `GET /sessions` - List all active sessions
- `POST /session/add` - Add new session
- `DELETE /session/{name}` - Remove session
- `GET /health` - Health check

## Safety Features

### Anti-Ban Mechanisms

1. **Dynamic Delays**: Delays increase/decrease based on session state
2. **Message Variations**: Automatic greetings, endings, and Unicode variations
3. **Typing Simulation**: Human-like typing speed
4. **Session Rotation**: Distribute load across multiple sessions
5. **Health Monitoring**: Track session health and auto-recover
6. **Time-Based Adjustments**: Adjust behavior based on time of day

### Best Practices

1. Start with conservative settings (1-2 sessions)
2. Monitor session health continuously
3. Rotate sessions regularly
4. Use message templates with personalization
5. Implement proper error handling
6. Keep sessions warm with periodic activity
7. Use dedicated phone numbers for automation

## Warning Signs of Potential Ban

- Sudden disconnections
- Slow message delivery
- "Message not sent" errors
- Session health dropping rapidly

## Legal & Compliance

⚠️ **IMPORTANT**:

- **User Consent**: Only message users who have explicitly opted in
- **Opt-out Mechanism**: Always include unsubscribe option
- **Privacy Compliance**: Follow GDPR, CCPA, and local privacy laws
- **WhatsApp Terms**: Strictly follow WhatsApp Business API policies
- **Anti-Spam Laws**: Comply with CAN-SPAM, TCPA, and local regulations
- **Message Content**: No misleading, harmful, or illegal content

## Performance Benchmarks

Based on testing:

| Configuration | Delay | Sessions | Speed | Ban Risk |
|--------------|-------|----------|-------|----------|
| Ultra-Safe   | 10-20s | 1        | ~180/hr | <1% |
| **Balanced** | **3-8s** | **3** | **500-700/hr** | **<5%** |
| Aggressive   | 2-5s  | 5        | ~1000/hr | ~15% |
| Maximum      | 1-3s  | 10       | ~2000+/hr | >30% |

**Recommended**: Configuration B (Balanced) for best speed/safety balance.

## Troubleshooting

### Session Not Connecting

1. Check internet connection
2. Ensure Chrome/Chromium is installed
3. Try running with `--headless=false` to see browser
4. Delete session directory and recreate

### Messages Not Sending

1. Check if WhatsApp Web is logged in
2. Verify phone number format
3. Check session health
4. Reduce number of parallel sessions

### High Failure Rate

1. Increase delays in configuration
2. Reduce parallel sessions
3. Check network stability
4. Monitor session health

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational purposes only. Use responsibly and in compliance with WhatsApp's Terms of Service and applicable laws.

## Disclaimer

This tool should only be used for legitimate business communications with proper user consent. Misuse can result in account suspension and legal consequences. The authors are not responsible for any misuse of this software.

