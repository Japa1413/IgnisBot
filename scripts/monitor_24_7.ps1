# IgnisBot 24/7 Monitor Script (PowerShell)
# This script monitors the bot and automatically restarts it if it crashes

$ErrorActionPreference = "Continue"
$script:RestartCount = 0
$script:MaxRestartsPerHour = 5
$script:RestartTimes = @()
$script:BotProcess = $null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    
    # Also write to log file
    $logFile = "logs\monitor.log"
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" | Out-Null
    }
    Add-Content -Path $logFile -Value $logMessage
}

function Test-BotRunning {
    if ($script:BotProcess -and -not $script:BotProcess.HasExited) {
        return $true
    }
    return $false
}

function Start-Bot {
    Write-Log "Starting IgnisBot..." "INFO"
    
    # Check if we can restart (rate limiting)
    $now = Get-Date
    $hourAgo = $now.AddHours(-1)
    $script:RestartTimes = $script:RestartTimes | Where-Object { $_ -gt $hourAgo }
    
    if ($script:RestartTimes.Count -ge $script:MaxRestartsPerHour) {
        Write-Log "Maximum restarts per hour reached ($script:MaxRestartsPerHour). Waiting..." "ERROR"
        Start-Sleep -Seconds 3600  # Wait 1 hour
        $script:RestartTimes = @()
    }
    
    try {
        $script:RestartCount++
        $script:RestartTimes += $now
        
        # Start bot process
        $script:BotProcess = Start-Process -FilePath "python" -ArgumentList "ignis_main.py" -PassThru -NoNewWindow
        
        Write-Log "Bot started (PID: $($script:BotProcess.Id), Restart #$script:RestartCount)" "INFO"
        return $true
    }
    catch {
        Write-Log "Failed to start bot: $_" "ERROR"
        return $false
    }
}

function Stop-Bot {
    if ($script:BotProcess -and -not $script:BotProcess.HasExited) {
        Write-Log "Stopping bot (PID: $($script:BotProcess.Id))..." "INFO"
        try {
            Stop-Process -Id $script:BotProcess.Id -Force -ErrorAction Stop
            Write-Log "Bot stopped successfully" "INFO"
        }
        catch {
            Write-Log "Error stopping bot: $_" "WARNING"
        }
    }
    $script:BotProcess = $null
}

function Wait-ForBotExit {
    param([int]$TimeoutSeconds = 5)
    
    if (-not $script:BotProcess) {
        return $true
    }
    
    $waited = 0
    while (-not $script:BotProcess.HasExited -and $waited -lt $TimeoutSeconds) {
        Start-Sleep -Seconds 1
        $waited++
    }
    
    return $script:BotProcess.HasExited
}

# Main monitoring loop
Write-Log "=== IgnisBot 24/7 Monitor Started ===" "INFO"
Write-Log "Monitoring bot for crashes and auto-restarting..." "INFO"

# Start bot initially
Start-Bot

while ($true) {
    Start-Sleep -Seconds 30  # Check every 30 seconds
    
    if (-not (Test-BotRunning)) {
        Write-Log "Bot process not running! Restarting..." "WARNING"
        
        # Wait a bit before restarting
        Start-Sleep -Seconds 5
        
        # Restart bot
        if (Start-Bot) {
            Write-Log "Bot restarted successfully" "INFO"
        }
        else {
            Write-Log "Failed to restart bot. Will retry in 60 seconds..." "ERROR"
            Start-Sleep -Seconds 60
        }
    }
    else {
        # Bot is running, log status periodically
        $uptime = (Get-Date) - $script:BotProcess.StartTime
        if ($uptime.TotalMinutes % 30 -lt 1) {  # Log every ~30 minutes
            Write-Log "Bot running (Uptime: $([math]::Round($uptime.TotalHours, 2)) hours, PID: $($script:BotProcess.Id))" "INFO"
        }
    }
}

