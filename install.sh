#!/bin/bash
# Installation script for WhatsApp Bot

echo "=========================================="
echo "WhatsApp Bot Installation Script"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check version compatibility (3.8+)
major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)
if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 8 ]); then
    echo "⚠️  Warning: Python 3.8+ is recommended"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
if python3 -m pip install -r requirements.txt; then
    echo "✓ Python dependencies installed"
else
    echo "❌ Error: Failed to install Python dependencies"
    exit 1
fi

# Install Playwright browsers
echo ""
echo "🌐 Installing Playwright browsers..."
if python3 -m playwright install chromium; then
    echo "✓ Playwright browsers installed"
else
    echo "❌ Error: Failed to install Playwright browsers"
    exit 1
fi

# Install Playwright system dependencies (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo ""
    echo "🔧 Installing Playwright system dependencies..."
    if python3 -m playwright install-deps chromium; then
        echo "✓ Playwright system dependencies installed"
    else
        echo "⚠️  Warning: Failed to install system dependencies (may need sudo)"
        echo "You can try: sudo $(which python3) -m playwright install-deps chromium"
    fi
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p sessions logs data templates guide_md
echo "✓ Directories created"

echo ""
echo "=========================================="
echo "✅ Installation complete!"
echo "=========================================="
echo ""
echo "📖 Next steps:"
echo ""
echo "1️⃣  Add your first WhatsApp session:"
echo "   python3 cli/wa_cli.py --action add-session --session-name my_session"
echo ""
echo "   For SSH/VPS (headless mode):"
echo "   python3 cli/wa_cli.py --action add-session --session-name my_session --headless"
echo ""
echo "2️⃣  Send your first message:"
echo "   python3 cli/wa_cli.py --action send \\"
echo "     --phone \"08123456789\" \\"
echo "     --message \"Hello!\""
echo ""
echo "3️⃣  Or start the API server:"
echo "   uvicorn api.server:app --reload --port 8000"
echo ""
echo "📚 For more information, see README.md"
echo ""

