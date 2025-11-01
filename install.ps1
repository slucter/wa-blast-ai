# Installation script for WhatsApp Bot (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "WhatsApp Bot Installation Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Python version compatibility
$versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
if ($versionMatch) {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
        Write-Host "⚠️  Warning: Python 3.8+ is recommended" -ForegroundColor Yellow
    }
}

# Install Python dependencies
Write-Host ""
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
try {
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Error: Failed to install Python dependencies" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: Failed to install Python dependencies" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Install Playwright browsers
Write-Host ""
Write-Host "🌐 Installing Playwright browsers..." -ForegroundColor Yellow
try {
    python -m playwright install chromium
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Playwright browsers installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Error: Failed to install Playwright browsers" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: Failed to install Playwright browsers" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host ""
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$directories = @("sessions", "logs", "data", "templates", "guide_md")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}
Write-Host "✓ Directories created" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Add your first WhatsApp session:" -ForegroundColor Cyan
Write-Host "   python cli/wa_cli.py --action add-session --session-name my_session" -ForegroundColor White
Write-Host ""
Write-Host "   For SSH/VPS (headless mode):" -ForegroundColor Cyan
Write-Host "   python cli/wa_cli.py --action add-session --session-name my_session --headless" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  Send your first message:" -ForegroundColor Cyan
Write-Host "   python cli/wa_cli.py --action send --phone `"08123456789`" --message `"Hello!`"" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣  Or start the API server:" -ForegroundColor Cyan
Write-Host "   uvicorn api.server:app --reload --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "📚 For more information, see README.md" -ForegroundColor Yellow
Write-Host ""

