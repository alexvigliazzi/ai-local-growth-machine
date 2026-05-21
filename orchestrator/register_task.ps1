# Register Growth Machine scheduler as a Windows Scheduled Task.
# Run once as Administrator. Task starts at login and restarts if it dies.
#
# Usage:
#   .\register_task.ps1 -ApiToken "your-token" [-RailsApiUrl "https://your-app.onrender.com/api"] [-OllamaModel "llama3.1:8b"]

param(
    [Parameter(Mandatory=$true)]  [string]$ApiToken,
    [string]$RailsApiUrl  = "https://ai-local-growth-machine.onrender.com/api",
    [string]$OllamaModel  = "gemma3:1b-it-qat",
    [string]$TaskName     = "GrowthMachineScheduler"
)

$scriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe  = (Get-Command python).Source
$schedulerScript = Join-Path $scriptDir "scheduler.py"
$logFile    = Join-Path $scriptDir "scheduler.log"

if (-not (Test-Path $schedulerScript)) {
    Write-Error "scheduler.py not found at: $schedulerScript"
    exit 1
}

# Build the action — python scheduler.py with env vars injected via wrapper
$wrapperScript = Join-Path $scriptDir "_task_wrapper.ps1"
@"
`$env:API_TOKEN    = "$ApiToken"
`$env:RAILS_API_URL = "$RailsApiUrl"
`$env:OLLAMA_MODEL = "$OllamaModel"
`$env:SCHEDULER_LOG = "$logFile"
& "$pythonExe" "$schedulerScript"
"@ | Set-Content $wrapperScript -Encoding UTF8

$action  = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -File `"$wrapperScript`""

# Trigger: at logon + repeat if not already running
$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew

# Remove existing task if present
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Output "Removed existing task: $TaskName"
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Growth Machine: weekly report + outreach scheduler" `
    -RunLevel Limited | Out-Null

Write-Output "Task registered: $TaskName"
Write-Output "  Runs at: login"
Write-Output "  Reports: every Sunday 09:00"
Write-Output "  Outreach: every Monday 08:00"
Write-Output "  Log: $logFile"
Write-Output ""
Write-Output "To start now: Start-ScheduledTask -TaskName '$TaskName'"
Write-Output "To remove:    Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
