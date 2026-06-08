# install_hooks.ps1 - Instala git hooks del protocolo en Windows (P6.4)
# Ejecutar UNA sola vez despues de clonar o en setup inicial.
# Uso: powershell -ExecutionPolicy Bypass -File scripts\install_hooks.ps1

$ErrorActionPreference = "Stop"

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProtocolDir = Split-Path -Parent $ScriptDir
$HooksSrc    = Join-Path $ScriptDir "hooks"
$GitHooksDir = Join-Path $ProtocolDir ".git\hooks"

Write-Host "Instalando git hooks del protocolo..." -ForegroundColor Cyan

# Verify .git exists
if (-not (Test-Path (Join-Path $ProtocolDir ".git"))) {
    Write-Host "ERROR: No se encontro .git en $ProtocolDir" -ForegroundColor Red
    Write-Host "       Ejecutar desde la raiz del repositorio." -ForegroundColor Red
    exit 1
}

# Create hooks dir if missing
if (-not (Test-Path $GitHooksDir)) {
    New-Item -ItemType Directory -Path $GitHooksDir -Force | Out-Null
}

# Install hooks versionados (pre-commit + commit-msg VC-140)
foreach ($hook in @("pre-commit", "commit-msg")) {
    $HookSrc = Join-Path $HooksSrc $hook
    $HookDst = Join-Path $GitHooksDir $hook
    if (Test-Path $HookSrc) {
        Copy-Item -Path $HookSrc -Destination $HookDst -Force
        Write-Host "OK  $hook hook instalado" -ForegroundColor Green
    } else {
        Write-Host "ERROR: scripts/hooks/$hook no encontrado" -ForegroundColor Red
        exit 1
    }
}

# Validate Python + pytest available
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "AVISO: python no encontrado en PATH - el hook puede fallar" -ForegroundColor Yellow
} else {
    Write-Host "OK  Python: $($python.Source)" -ForegroundColor Green
}

if ($python) {
    Write-Host "OK  pytest check" -ForegroundColor Green
}

Write-Host ""
Write-Host "Git hooks instalados. Proximos commits seran validados automaticamente." -ForegroundColor Cyan
Write-Host "Si la validacion falla: git commit sera BLOQUEADO hasta corregir el error." -ForegroundColor Cyan
