# 🚀 Ciclo 5 — Plan de Acción

**Fecha Inicio:** 2026-06-02 (Post-Ciclo 4)  
**Duración Estimada:** 2-3 semanas  
**Versión:** CoderCerberus v0.5  
**Objetivo:** Resolver bloqueadores Ciclo 4 + modernization projects

---

## 📊 Herencia Ciclo 4

**Status:** 85% completo (37/41 tasks)  
**Bloqueadores:** 2
- ⚠️ P0-1: GitHub repos (manual) — 15 min
- ⚠️ P1-2: Frankenstein LFS — 30 min (BFG)

**Ventajas:**
- ✅ Todos los 17 proyectos con v0.5 compliance
- ✅ Test suite expandido (18 tests D8 coverage)
- ✅ Scripts portables validados
- ✅ Audits finales ejecutados

---

## 🎯 Ciclo 5 P0 (Bloqueadores — Día 1)

### P0-1: Crear Repos GitHub
**Status:** ⏳ MANUAL  
**Tiempo:** 15 minutos  
**Instrucciones:** SETUP_MISSING_GITHUB_REPOS.md

**Paso 1: Calculadora de sueldos**
```bash
# Opción A: GitHub UI
# https://github.com/new
# Nombre: calculadora-sueldos
# Descripción: Suite de calculadoras de gestión de nómina...

# Opción B: CLI
gh repo create calculadora-sueldos --public \
  --description "Suite de calculadoras de gestión de nómina"
```

**Paso 2: Maletin Homeopatia**
```bash
gh repo create maletin-homeopatia --public \
  --description "Sistema de organización de remedios homeopáticos"
```

**Paso 3: Verify**
```bash
cd /d/AI/Calculadora\ de\ sueldos && git remote -v
cd /d/AI/Maletin\ Homeopatia && git remote -v
```

---

### P0-2: Resolver Frankenstein LFS (DT-F1)
**Status:** ⚠️ BLOQUEADOR  
**Tiempo:** 30 minutos (con validación)  
**Documentación:** CICLO_4_FRANKENSTEIN_LFS_BLOCKER.md

**Opción Recomendada: BFG Repo-Cleaner**

```bash
# 1. Instalar BFG (si no existe)
choco install bfg || brew install bfg

# 2. Backup remote
cd /d/AI/Frankenstein
git fetch --all
git fetch origin

# 3. Cleanup con BFG
git reflog expire --expire=now --all
git gc --prune=now
bfg --strip-blobs-bigger-than 100M
git reflog expire --expire=now --all
git gc --prune=now

# 4. Force push
git push -u origin master --force --no-verify

# 5. Validar
git log --oneline | head -5
```

**Risk Assessment:**
- ⚠️ Destructiva (reescribe commits)
- ✅ Preserva histórico relativo
- ✅ Permite push exitoso

---

## 📋 Ciclo 5 P1 (Importantes)

### P1-1: Cuenza_2025 Modernization Roadmap
**Status:** 📅 Pendiente  
**Proyecto:** Legacy ASP.NET (VB.NET) → .NET 6+ migration  
**Tiempo:** 3-4 horas  
**Owner:** Futuro (investigación + planificación)

**Scope:**
```
1. Auditar codebase VB.NET actual
2. Inventariar librerías y dependencias
3. Evaluar riesgos migración
4. Planificar roadmap .NET 6+
5. Documentar milestones
6. Crear tickets para Ciclo 6+
```

**Resultado:** Documento CUENZA_2025_MODERNIZATION.md

---

### P1-2: Sistemas_Estocasticos Validación Adicional
**Status:** 📅 Investigación continua  
**Proyecto:** Framework matemático (QuantEdge Algorithm)  
**Tiempo:** Variable (8-16 horas)  
**Owner:** Futuro

**Scope:**
```
1. Ejecutar Monte Carlo 200k+ runs (vs 100k actual)
2. Validar convergencia estadística
3. Análisis de sensibilidad parámetros
4. Documentar resultados
5. Actualizar cobertura de tests
```

**Resultado:** Documento SISTEMAS_ESTOCASTICOS_VALIDATION_REPORT.md

---

### P1-3: Cerberus Cleanup (Archivos Temporales)
**Status:** 📅 Mantenimiento  
**Tiempo:** 30 minutos  
**Scope:**
```
✓ Remover archivos temporales de audits
✓ Limpiar logs de tests
✓ Archivar reports antiguos
✓ Actualizar .gitignore (si necesario)
```

---

## 🔄 Ciclo 5 P2 (Nice-to-Have)

### P2-1: Refactor Scripts (Reducir shell=True)
**Status:** 📅 Security Hardening  
**Problema:** B602 subprocess_popen_with_shell_equals_true  
**Tiempo:** 4-6 horas  
**Impacto:** Reduce riesgo command injection

**Plan:**
```python
# ANTES (shell=True)
subprocess.Popen('ls -la | grep tmp', shell=True)

# DESPUÉS (shell=False)
proc = subprocess.Popen(['ls', '-la'], stdout=subprocess.PIPE)
grep = subprocess.Popen(['grep', 'tmp'], stdin=proc.stdout)
```

---

### P2-2: Integrar Tests en CI/CD
**Status:** 📅 Automatización  
**Tiempo:** 2-3 horas  
**Scope:**
```
1. Crear GitHub Actions workflow
2. Ejecutar tests en push
3. Validar bandit en PRs
4. Reportar status en commits
```

---

### P2-3: Actualizar Documentación Ciclo 5
**Status:** 📅 Post-Sprint  
**Tiempo:** 1 hora  
**Archivos:**
```
+ CICLO_5_PROGRESS.md
+ CICLO_5_COMPLETION_REPORT.md
~ HISTORIAL.md (agregar entries)
~ README.md (si necesario)
```

---

## 📅 Schedule Propuesto

```
DÍA 1 (2026-06-03):
  ⏳ P0-1: GitHub repos (15 min) — MANUAL
  ⏳ P0-2: Frankenstein LFS (30 min) — BFG cleanup
  ✅ Audits finales + validación (30 min)

DÍA 2-3 (2026-06-04/05):
  ⏳ P1-1: Cuenza_2025 roadmap (3-4h)
  ⏳ P1-2: Sistemas_Estocasticos (investigación)
  ⏳ P1-3: Cerberus cleanup (30 min)

DÍA 4 (2026-06-06):
  ⏳ P2-1 opcional: Script refactoring (4-6h)
  ⏳ P2-2 opcional: CI/CD setup (2-3h)

DÍA 5 (2026-06-07):
  ✅ Ciclo 5 completado
  📅 Ciclo 6 planning
```

**Total Estimado:** 6-8 horas (1 día de trabajo)

---

## ✅ Definición de Hecho (Ciclo 5)

- [ ] 2 repos GitHub creados (P0-1)
- [ ] Frankenstein LFS resuelto (P0-2)
- [ ] Cuenza_2025 roadmap documentado (P1-1)
- [ ] Sistemas_Estocasticos validación reportada (P1-2)
- [ ] Cerberus cleanup completado (P1-3)
- [ ] 11/11 proyectos auditados (final)
- [ ] Reporte Ciclo 5 generado
- [ ] Transición a Ciclo 6

---

## 🔗 Documentación de Referencia

- `CICLO_4_COMPLETION_REPORT.md` — Estado actual
- `CICLO_4_FRANKENSTEIN_LFS_BLOCKER.md` — Análisis LFS
- `SETUP_MISSING_GITHUB_REPOS.md` — Instrucciones P0-1
- `PLAN_CICLO_4.md` — Plan anterior
- `HISTORIAL.md` — Audit trail

---

## ⚙️ Decision Point (Ciclo 5)

**¿Qué hacer primero?**

- **A:** Resolver bloqueadores (P0-1/P0-2) — Recomendado
- **B:** Ejecutar modernization projects (P1-1/P1-2) — Parallelizable
- **C:** Ambos en paralelo — Más rápido, menos secuencial

**Recomendación:** A (bloqueadores) en Día 1, luego B (parallelizable) en Día 2-3.

---

**Ciclo 5 Ready to Start.** 🚀

*Plan: 2026-06-02 | CoderCerberus v0.5 | Transición Post-Ciclo 4*
