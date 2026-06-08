# install_cerberus.ps1 — Instala y aprovisiona Cerberus de forma nativa en Windows (B2 / TK-004)
# Uso: powershell -ExecutionPolicy Bypass -File scripts\install_cerberus.ps1

$ErrorActionPreference = "Continue"

# Directorios de trabajo
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProtocolDir = Split-Path -Parent $ScriptDir
$HooksSrc    = Join-Path $ScriptDir "hooks"
$GitHooksDir = Join-Path $ProtocolDir ".git\hooks"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   🛡️  INSTALADOR NATIVO DE CODER CERBERUS PARA WINDOWS" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar .git
if (-not (Test-Path (Join-Path $ProtocolDir ".git"))) {
    Write-Host "❌ ERROR: No se encontro el directorio .git en $ProtocolDir" -ForegroundColor Red
    Write-Host "          Por favor, ejecute este instalador desde la raiz del repositorio." -ForegroundColor Red
    exit 1
}

# 2. Verificar Python >= 3.10
Write-Host "[1/4] Verificando Python >= 3.10..." -ForegroundColor Cyan
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ ERROR: Python no esta instalado o no se encuentra en el PATH." -ForegroundColor Red
    exit 1
}

# Ejecutar validación interna de versión con un script mínimo para mayor robustez
$pyVersionCheck = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
$major, $minor = $pyVersionCheck.Split('.')
if ([int]$major -lt 3 -or ([int]$major -eq 3 -and [int]$minor -lt 10)) {
    Write-Host "❌ ERROR: Python $pyVersionCheck detectado. Cerberus requiere Python >= 3.10." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python $pyVersionCheck detectado en: $($python.Source)" -ForegroundColor Green

# 3. Instalar dependencias si faltan
Write-Host "[2/4] Verificando dependencias (pyyaml, rich)..." -ForegroundColor Cyan
$hasDeps = & python -c "
try:
    import yaml, rich
    print('OK')
except ImportError:
    print('MISSING')
" 2>&1

if ($hasDeps -eq "MISSING") {
    Write-Host "💡 Faltan dependencias. Instalando desde requirements.txt..." -ForegroundColor Yellow
    & python -m pip install --quiet -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: No se pudieron instalar las dependencias de Python." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Dependencias instaladas correctamente." -ForegroundColor Green
} else {
    Write-Host "✅ Dependencias pyyaml y rich ya estan disponibles." -ForegroundColor Green
}

# 4. Instalar Git Hooks
Write-Host "[3/4] Instalando Git Hooks del protocolo..." -ForegroundColor Cyan
if (-not (Test-Path $GitHooksDir)) {
    New-Item -ItemType Directory -Path $GitHooksDir -Force | Out-Null
}

$hooks = @("pre-commit", "post-commit", "pre-push")
foreach ($hook in $hooks) {
    $src = Join-Path $HooksSrc $hook
    $dst = Join-Path $GitHooksDir $hook
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Force
        Write-Host "   -> Hook '$hook' instalado" -ForegroundColor Gray
    } else {
        Write-Host "❌ ERROR: Hook de origen '$hook' no encontrado en scripts/hooks/" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Git hooks instalados correctamente en .git/hooks/" -ForegroundColor Green

# 5. Ejecutar Smoke Test (run_security_audit_12d.py)
Write-Host "[4/4] Ejecutando Smoke Test (Auditoria de Cerberus)..." -ForegroundColor Cyan
$auditScript = Join-Path $ScriptDir "run_security_audit_12d.py"
if (-not (Test-Path $auditScript)) {
    Write-Host "❌ ERROR: No se encontro el auditor scripts/run_security_audit_12d.py" -ForegroundColor Red
    exit 1
}

# Ejecutar auditoría y capturar salida
$auditResult = & python $auditScript 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host "   ✅ Cerberus operativo y certificado exitosamente!" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ ERROR: Smoke test de auditoria fallido (Exit Code: $exitCode)" -ForegroundColor Red
    Write-Host "Detalles del fallo:" -ForegroundColor Red
    Write-Host $auditResult -ForegroundColor DarkRed
    exit 1
}
