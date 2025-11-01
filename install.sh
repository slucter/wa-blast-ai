#!/bin/bash
# Installation script for WhatsApp Bot

echo "=========================================="
echo "WhatsApp Bot Installation Script"
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
playwright install chromium

# Install Playwright system dependencies (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo ""
    echo "Installing Playwright system dependencies..."
    playwright install-deps chromium
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p sessions logs data templates

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Add a WhatsApp session:"
echo "   python cli/wa_cli.py --action add-session"
echo ""
echo "2. Start sending messages:"
echo "   python cli/wa_cli.py --action send --numbers data/contacts.txt --message 'Hello'"
echo ""
echo "3. Or start the API server:"
echo "   uvicorn api.server:app --reload --port 8000"
echo ""

