# install_hooks.ps1 — Instala git hooks del protocolo en Windows (P6.4)
# Ejecutar UNA sola vez después de clonar o en setup inicial.
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

# Install pre-commit hook
$PreCommitSrc = Join-Path $HooksSrc "pre-commit"
$PreCommitDst = Join-Path $GitHooksDir "pre-commit"

if (Test-Path $PreCommitSrc) {
    Copy-Item -Path $PreCommitSrc -Destination $PreCommitDst -Force
    Write-Host "OK  pre-commit hook instalado" -ForegroundColor Green
} else {
    Write-Host "ERROR: scripts/hooks/pre-commit no encontrado" -ForegroundColor Red
    exit 1
}

# Validate Python + pytest available
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "AVISO: python no encontrado en PATH — el hook puede fallar" -ForegroundColor Yellow
} else {
    Write-Host "OK  Python: $($python.Source)" -ForegroundColor Green
}

# GF-2: only invoke python for pytest check if it was found in PATH.
# Without this guard, $ErrorActionPreference = "Stop" causes a hard crash on CommandNotFoundException.
if ($python) {
    $pytest = & python -m pytest --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "AVISO: pytest no disponible — instalar con: pip install pytest" -ForegroundColor Yellow
    } else {
        Write-Host "OK  $pytest" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Git hooks instalados. Proximos commits seran validados automaticamente." -ForegroundColor Cyan
Write-Host "Si la validacion falla: git commit sera BLOQUEADO hasta corregir el error." -ForegroundColor Cyan
