# Installation script for WhatsApp Bot (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "WhatsApp Bot Installation Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Green

# Install Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install Playwright browsers
Write-Host ""
Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
playwright install chromium

# Create necessary directories
Write-Host ""
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path sessions, logs, data, templates | Out-Null

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Add a WhatsApp session:"
Write-Host "   python cli/wa_cli.py --action add-session"
Write-Host ""
Write-Host "2. Start sending messages:"
Write-Host "   python cli/wa_cli.py --action send --numbers data/contacts.txt --message 'Hello'"
Write-Host ""
Write-Host "3. Or start the API server:"
Write-Host "   uvicorn api.server:app --reload --port 8000"
Write-Host ""

