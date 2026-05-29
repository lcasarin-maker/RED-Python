# PowerShell wrapper to run import verification and tests with UTF-8 handling
# Save as run_audit_fixed.ps1 in the project root

# Step 1: Verify imports (force UTF-8 for the process)
Write-Host "Ejecutando verificación de imports..."
python -X utf8 -m scripts.check_imports
if ($LASTEXITCODE -ne 0) {
    Write-Error "La verificación de imports falló. Abortando ejecución de pruebas."
    exit $LASTEXITCODE
}

# Step 2: Ejecutar pruebas con captura UTF-8
Write-Host "Importaciones correctas. Ejecutando pytest..."
# Ensure Python uses UTF-8 for output (helps on Windows) and disables pytest capture issues
$env:PYTHONUTF8 = "1"
$env:PYTEST_ADDOPTS = "-s"  # disable internal capture
pytest -q
if ($LASTEXITCODE -ne 0) {
    Write-Error "Algunas pruebas fallaron. Revisa el reporte anterior."
    exit $LASTEXITCODE
}
Write-Host "Auditoría completada con éxito."
