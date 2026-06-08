# 🚀 CICLO 4 — Plan de Remediación

**Fecha Inicio:** 2026-06-02  
**Duración Estimada:** 1-2 semanas  
**Versión:** CoderCerberus v0.5  
**Objetivo:** Resolver deuda técnica de Ciclo 3 + preparar Ciclo 5

---

## 📋 Tareas Prioritarias (P0 — Bloqueadores)

### P0-1: Crear repos GitHub faltantes
**Status:** ⏳ Pendiente  
**Descripción:** Crear 2 repos en GitHub para proyectos sin remote  
**Archivos Afectados:**
- Calculadora de sueldos (ya tiene commit local)
- Maletin Homeopatia (ya tiene commit local)

**Instrucciones:** Ver `SETUP_MISSING_GITHUB_REPOS.md`

**Esfuerzo:** 15 minutos  
**Bloqueador:** No — pueden hacerse en paralelo a P0-2/P0-3

---

### P0-2: Agregar .gitignore para .protocol-core
**Status:** ⏳ Pendiente  
**Descripción:** Eliminar archivos Zombi esperados (symlinks Cerberus) de git tracking  
**Archivos Afectados:** Todos los proyectos satélites (11/11)

**Plan:**
```bash
# Para cada proyecto satélite:
# 1. Leer .gitignore actual
# 2. Agregar líneas:
.protocol-core/
.protocol-eval/
*.swp
*.swo

# 3. Hacer git rm --cached para symlinks
git rm --cached .protocol-core -r --force 2>/dev/null || true
git add .gitignore
git commit -m "Add .protocol-core to gitignore (symlinks)"
git push
```

**Proyectos:**
1. Aequitas_OS
2. Quenza
3. Frankenstein
4. Calculadora de sueldos
5. Declutter
6. Imagen_Corporativa_Aequitas
7. RED-Python
8. Maletin Homeopatia
9. Cuenza_2025
10. Sistemas_Estocasticos_Ruleta

**Esfuerzo:** 30 minutos (1-2 min por repo)  
**Bloqueador:** Resuelve D1 INTEGRIDAD en audits

---

### P0-3: Crear settings.template.json faltante
**Status:** ⏳ Pendiente  
**Descripción:** Agregar archivo de permisos faltante en 4 proyectos  
**Archivos Afectados:**
- Calculadora de sueldos/.claude/settings.template.json
- Imagen_Corporativa_Aequitas/.claude/settings.template.json
- Maletin Homeopatia/.claude/settings.template.json
- Cuenza_2025/.claude/settings.template.json

**Contenido Template:**
```json
{
  "version": "0.5",
  "permissions": {
    "read": ["**/*.md", "**/*.txt", "**/*.json"],
    "write": ["SPEC.md", "AGENT.md", "PLAN.md", "HISTORIAL.md"],
    "execute": ["scripts/run_*.py"],
    "dangerous": []
  },
  "settings": {
    "model": "claude-haiku",
    "max_tokens": 4000,
    "temperature": 0.7
  }
}
```

**Esfuerzo:** 20 minutos (1-2 min por archivo)  
**Bloqueador:** Resuelve Permission audit FAILED en audits

---

## 📊 Tareas Medianas (P1 — Importantes)

### P1-1: Tests para scripts portables
**Status:** ⏳ Pendiente  
**Descripción:** Agregar test coverage para scripts sin adversarial coverage (D8 FAIL)

**Scripts a Testear:**
- run_security_audit_12d.py
- sync_binding.py
- verify_chaos_robustness.py
- run_compliance_tests.py
- global_sync_safe.py
- permission_auditor.py

**Patrón Test:**
```python
# tests/test_audit_scripts.py
import pytest
from scripts.run_security_audit_12d import DeepForensicAuditor

def test_audit_initialization():
    auditor = DeepForensicAuditor("/tmp/test_project")
    assert auditor.project_path == "/tmp/test_project"
    assert auditor.is_cerberus == False  # External project detection

def test_audit_execution_external_project(tmp_path):
    auditor = DeepForensicAuditor(str(tmp_path))
    # Should NOT crash even without protocol_engine
    results = auditor.run()
    assert results is not None

def test_audit_with_dangerous_permissions(tmp_path):
    # Create file with dangerous permissions
    test_file = tmp_path / "test.py"
    test_file.write_text("import os; os.system('rm -rf /')")
    auditor = DeepForensicAuditor(str(tmp_path))
    results = auditor.run()
    # Should detect dangerous patterns
    assert any("dangerous" in str(r) for r in results)
```

**Esfuerzo:** 4-6 horas (1 script ~30-45 min con test suite)  
**Bloqueador:** Resuelve D8 COBERTURA ADVERSARIAL en 9/11 proyectos

---

### P1-2: Resolver Frankenstein LFS
**Status:** ⏳ Pendiente  
**Descripción:** Git Large File Storage setup o .gitignore node_modules

**Opción A: Git LFS (preferido)**
```bash
cd /d/AI/Frankenstein
git lfs install
git lfs track "implementacion/fase-g/portal/node_modules/**/*.node"
git add .gitattributes
git commit -m "Setup Git LFS for node_modules"
git push
```

**Opción B: .gitignore (rápido)**
```bash
cd /d/AI/Frankenstein
# Agregar a .gitignore:
node_modules/
dist/
build/

git rm --cached -r implementacion/fase-g/portal/node_modules/
git add .gitignore
git commit -m "Remove node_modules from tracking"
git push
```

**Recomendación:** Opción B (node_modules no debe estar en git)

**Esfuerzo:** 10 minutos  
**Bloqueador:** Permite push exitoso de Frankenstein

---

### P1-3: Bandit HIGH+ Review
**Status:** ⏳ Pendiente  
**Descripción:** Revisar y remediar 5 hallazgos HIGH en bandit security audit

**Proyectos con Hallazgos:**
- Aequitas_OS (1 HIGH)
- Quenza (1 HIGH)
- Frankenstein (1 HIGH)
- Calculadora de sueldos (1 HIGH)
- Declutter (1 HIGH)

**Plan:**
1. Ejecutar bandit específico: `bandit -r . -ll`
2. Documentar hallazgos por proyecto
3. Clasificar como: False Positive / Deliberado / Requiere Fix
4. Remediar genuinos

**Esfuerzo:** 1-2 horas  
**Bloqueador:** No (bajo riesgo)

---

## 🎯 Tareas Futuras (P2 — Nice to Have)

### P2-1: Cuenza_2025 Modernización Roadmap
**Status:** 📅 Sprint 2+  
**Descripción:** Documentar migration path VB.NET → .NET 6+ + PostgreSQL  
**Esfuerzo:** 3-4 horas  
**Owner:** Futuro

### P2-2: Sistemas_Estocasticos Validación Adicional
**Status:** 📅 Investigación continua  
**Descripción:** Monte Carlo 200k+ runs para mayor confianza  
**Esfuerzo:** Variable  
**Owner:** Futuro

### P2-3: Cerberus Cleanup (archivos temporales)
**Status:** 📅 Mantenimiento  
**Descripción:** Remover audit temporales, logs de test  
**Esfuerzo:** 30 minutos  
**Owner:** Futuro

---

## 📅 Schedule Propuesto

```
DÍA 1 (2026-06-02/03):
  ✅ P0-1: Repos GitHub (15 min) — HECHO HOY
  ⏳ P0-2: .gitignore (.protocol-core) — 30 min
  ⏳ P0-3: settings.template.json — 20 min
  
DÍA 2-3 (2026-06-04/05):
  ⏳ P1-1: Test scripts (4-6h) — Parallelizable
  ⏳ P1-2: Frankenstein LFS — 10 min
  
DÍA 4 (2026-06-06):
  ⏳ P1-3: Bandit review — 1-2h
  ⏳ Final audits + reporte

DÍA 5 (2026-06-07):
  ✅ Ciclo 4 completado
  📅 Ciclo 5 planning
```

**Total Estimado:** 10-12 horas (1-2 días de trabajo)

---

## ✅ Definición de Hecho (Ciclo 4)

- [ ] 11 proyectos con .gitignore actualizado (sin zombis)
- [ ] 4 proyectos con settings.template.json
- [ ] 2 repos GitHub creados + pushed
- [ ] 6 scripts con test coverage (D8 PASS)
- [ ] Frankenstein con push exitoso
- [ ] 5 HIGH bandit issues revisados
- [ ] Audits finales ejecutados (11/11 proyectos)
- [ ] Reporte Ciclo 4 generado

---

## 🔗 Documentación de Referencia

- `CICLO_3_COMPLETION_REPORT.md` — Status Ciclo 3
- `CICLO_3_DEUDA_TECNICA.md` — Inventario completo
- `SETUP_MISSING_GITHUB_REPOS.md` — Instrucciones repos
- `HISTORIAL.md` — Audit trail

---

**Ciclo 4 — Listo para iniciar.** 🚀

*Plan: 2026-06-02 | CoderCerberus v0.5*
