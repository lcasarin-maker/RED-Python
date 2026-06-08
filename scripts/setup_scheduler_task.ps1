# setup_scheduler_task.ps1 — Windows Task Scheduler Setup for Cerberus
# Run this script as Administrator to register the background task.

$TaskName = "CerberusAutoMaestro"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$MonitorScript = Join-Path $ScriptDir "monitor_projects.py"

# 1. Verify Administrative Privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "Este script requiere permisos de Administrador para registrar tareas del sistema."
    Write-Host "Re-ejecutando con elevación..."
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "=================================================================="
Write-Host "🤖 Configurando Tarea Programada de Cerberus Auto-Maestro"
Write-Host "=================================================================="

# 2. Locate Python executable (prefer pythonw.exe to run without popping console windows)
$PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) {
    # Fallback search in Registry/Path
    $PythonPath = where.exe python.exe | Select-Object -First 1
}

if (-not $PythonPath) {
    Write-Error "No se encontró la instalación de Python. Por favor agrégala al PATH."
    exit 1
}

# Resolve pythonw.exe in same directory
$PythonwPath = Join-Path (Split-Path $PythonPath -Parent) "pythonw.exe"
if (-not (Test-Path $PythonwPath)) {
    # Fallback to python.exe if pythonw.exe doesn't exist
    $PythonwPath = $PythonPath
}

Write-Host "Python: $PythonwPath"
Write-Host "Script: $MonitorScript"
Write-Host "Directorio de Trabajo: $ProjectDir"

# 3. Create Scheduled Task Principal, Action, Trigger, and Settings
$Action = New-ScheduledTaskAction -Execute $PythonwPath -Argument "`"$MonitorScript`" --fix --background" -WorkingDirectory $ProjectDir
$Trigger = New-ScheduledTaskTrigger -AtLogOn -RandomDelay (New-TimeSpan -Minutes 2)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Add repetition of every 4 hours indefinitely
# We modify the trigger in PowerShell to repeat
$Trigger.Repetition = (New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 4) -RepetitionDuration ([TimeSpan]::MaxValue)).Repetition

# 4. Unregister existing task if it exists
Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false

# 5. Register Task
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Monitoreo y auto-remediación determinista en background para el ecosistema Cerberus." -ErrorAction Stop
    Write-Host "`n✅ Tarea '$TaskName' registrada exitosamente en el Programador de Tareas."
    Write-Host "La tarea se ejecutará cada 4 horas y en cada inicio de sesión de forma silenciosa."
} catch {
    Write-Error "Fallo al registrar la tarea programada: $_"
    exit 1
}

Write-Host "=================================================================="
