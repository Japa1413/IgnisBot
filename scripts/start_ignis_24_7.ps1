# IgnisBot 24/7 Startup Script
# Run this script to start the bot with 24/7 monitoring

Write-Host "=== IgnisBot 24/7 Startup ===" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Python not found! Please install Python first." -ForegroundColor Red
    exit 1
}

# Check if required files exist
if (-not (Test-Path "ignis_main.py")) {
    Write-Host "ERROR: ignis_main.py not found!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found. Bot may not work correctly." -ForegroundColor Yellow
}

Write-Host "Starting IgnisBot with 24/7 monitoring..." -ForegroundColor Yellow
Write-Host ""

# Start the monitor script
$monitorScript = Join-Path $PSScriptRoot "monitor_24_7.ps1"
if (Test-Path $monitorScript) {
    Write-Host "Launching monitor script..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-File", $monitorScript
    Write-Host ""
    Write-Host "✅ Monitor script started in new window" -ForegroundColor Green
    Write-Host "The bot will automatically restart if it crashes." -ForegroundColor Gray
    Write-Host ""
    Write-Host "To stop the bot, close the monitor window or run:" -ForegroundColor Yellow
    Write-Host "  Get-Process python | Where-Object {`$_.Path -like '*python*'} | Stop-Process" -ForegroundColor Gray
}
else {
    Write-Host "WARNING: Monitor script not found. Starting bot directly..." -ForegroundColor Yellow
    python ignis_main.py
}

