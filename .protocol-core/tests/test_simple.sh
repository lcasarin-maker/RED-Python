#!/bin/bash

echo "==============================================="
echo "VALIDACION DE REGLAS - TEST SIMPLE"
echo "==============================================="
echo

# REGLA 3: STATUS.md
echo "[TEST] REGLA #3: STATUS.md con 7 campos"
if grep -q "CAMPO 1" STATUS.md && grep -q "CAMPO 7" STATUS.md; then
  echo "PASS: STATUS.md completo"
else
  echo "FAIL: STATUS.md incompleto"
fi
echo

# REGLA 12: Commits
echo "[TEST] REGLA #12: Commits existen"
if git log --oneline -1 > /dev/null 2>&1; then
  echo "PASS: $(git log --oneline -1)"
else
  echo "FAIL: No hay commits"
fi
echo

# REGLA 13: Tests existen
echo "[TEST] REGLA #13: TDD Inverso"
if [ -f "test_protocolo_reglas.py" ]; then
  echo "PASS: Test suite presente"
else
  echo "FAIL: Test suite NO existe"
fi
echo

# REGLA 14: Archivos principales
echo "[TEST] REGLA #14: Archivos principales"
missing=0
for f in NIVEL_1_INTEGRIDAD.md NIVEL_3_VALIDACION.md NIVEL_4_GUARDIAS.md; do
  if [ ! -f "$f" ]; then
    echo "FAIL: $f FALTA"
    ((missing++))
  fi
done
if [ $missing -eq 0 ]; then
  echo "PASS: Todos archivos presentes"
fi
echo

# REGLA 15: GitHub remote
echo "[TEST] REGLA #15: GitHub remote"
remote=$(git remote -v 2>&1)
if echo "$remote" | grep -q github; then
  echo "PASS: Remote GitHub configurado"
  echo "$remote"
else
  echo "FAIL/BLOCKED: NO hay remote GitHub"
  echo "Current remotes: $remote"
fi
echo

# REGLA 16: Trazabilidad
echo "[TEST] REGLA #16: Archivos de trazabilidad"
if [ -f "../CHANGELOG_ECOSYSTEM.md" ]; then
  echo "PASS: CHANGELOG_ECOSYSTEM.md existe"
else
  echo "FAIL: CHANGELOG_ECOSYSTEM.md FALTA"
fi
echo

# REGLA 17: Rollback testing
echo "[TEST] REGLA #17: Referencias a rollback"
if grep -r "rollback\|reverse" . --include="*.md" > /dev/null 2>&1; then
  echo "PASS: Rollback mencionado en documentacion"
else
  echo "FAIL: No hay referencias a rollback"
fi
echo

# REGLA 19: Alternativas
echo "[TEST] REGLA #19: Alternativas documentadas"
if grep -i "alternativa\|opcion" ../CHANGELOG_ECOSYSTEM.md > /dev/null 2>&1; then
  echo "PASS: Alternativas en CHANGELOG"
else
  echo "FAIL: No hay alternativas documentadas"
fi
echo

echo "==============================================="
echo "BLOQUEADORES CRITICOS:"
echo "==============================================="
echo "[BLOCKER] REGLA #15: GitHub remote configurado"
if git remote -v 2>&1 | grep -q github; then
  echo "  Status: OK"
else
  echo "  Status: BLOQUEADO - NECESITA TOKEN + CONFIGURACION"
fi
echo
