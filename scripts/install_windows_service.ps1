# IgnisBot Windows Service Installer
# This script installs IgnisBot as a Windows service using Task Scheduler
# This allows the bot to run 24/7 even when you're not logged in

$ErrorActionPreference = "Stop"

Write-Host "=== IgnisBot Windows Service Installer ===" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Check if Python is available
try {
    $pythonPath = (Get-Command python).Source
    Write-Host "Python found: $pythonPath" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found in PATH!" -ForegroundColor Red
    Write-Host "Please install Python and add it to your PATH" -ForegroundColor Yellow
    exit 1
}

# Check if required files exist
if (-not (Test-Path (Join-Path $projectRoot "ignis_main.py"))) {
    Write-Host "ERROR: ignis_main.py not found in $projectRoot" -ForegroundColor Red
    exit 1
}

# Create startup script
$startupScript = Join-Path $scriptDir "service_startup.ps1"
$startupScriptContent = @"
# IgnisBot Service Startup Script
# This script is called by Task Scheduler

`$ErrorActionPreference = "Continue"
Set-Location "$projectRoot"

# Start the bot
python ignis_main.py
"@

Set-Content -Path $startupScript -Value $startupScriptContent -Encoding UTF8
Write-Host "Created startup script: $startupScript" -ForegroundColor Green

# Create Task Scheduler task
$taskName = "IgnisBot"
$taskDescription = "IgnisBot Discord Bot - Runs 24/7"

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create action (run PowerShell script)
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$startupScript`"" -WorkingDirectory $projectRoot

# Create trigger (at startup)
$trigger = New-ScheduledTaskTrigger -AtStartup

# Create principal (run as SYSTEM with highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

# Register the task
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description $taskDescription | Out-Null
    Write-Host "Task Scheduler task created successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to create Task Scheduler task: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Installation Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "The bot will now:" -ForegroundColor Cyan
Write-Host "  • Start automatically when Windows boots" -ForegroundColor White
Write-Host "  • Restart automatically if it crashes (up to 3 times)" -ForegroundColor White
Write-Host "  • Run even when you're not logged in" -ForegroundColor White
Write-Host ""
Write-Host "To manage the service:" -ForegroundColor Yellow
Write-Host "  • Start: Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host "  • Stop: Stop-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host "  • Remove: Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false" -ForegroundColor Gray
Write-Host "  • View: Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host ""
Write-Host "To start the bot now, run:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host ""


