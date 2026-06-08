# 02 — AUDITORIA EXTERIOR CONTRACT-FIRST

**Estado:** DISENO ACTIVO  
**Piloto inicial:** Control Procesal  
**Regla de privacidad:** salvo instruccion expresa, todo repositorio auditado debe permanecer privado.

---

## 0. Objetivo

Auditar proyectos hacia afuera desde Cerberus sin asumir que el repositorio ya sabe explicarse, probarse o gobernarse.

La base no es "correr herramientas". La base es reconstruir el contrato real del proyecto, compararlo contra su ejecucion observable, mapearlo contra el Golden Standard y producir un veredicto con plan de remediacion.

---

## 1. Principios obligatorios

1. **Contrato primero:** no se audita contra intuiciones; se audita contra contrato declarado o contrato inferido.
2. **Privado por defecto:** ningun repo debe hacerse publico salvo autorizacion expresa.
3. **Evidencia antes que narrativa:** cada hallazgo debe tener archivo, comando, salida, captura, traza o prueba reproducible.
4. **No teatro de seguridad:** una prueba que solo comprueba mocks, snapshots decorativos o existencia superficial se marca como prueba teatral.
5. **Instalacion progresiva:** Cerberus no crea infraestructura invasiva antes de entender el repo.
6. **Aprendizaje controlado:** lo aprendido alimenta Cerberus; solo lo generalizable se propone como candidato para GS.

---

## 2. Fases de auditoria exterior

### Fase 0 — Perfil, privacidad y purga de controles previos

Objetivo: conocer el repo antes de juzgarlo.

Debe validar:

1. Estado Git, rama, remoto y limpieza.
2. Visibilidad del repositorio. Si esta publico sin instruccion expresa, levantar hallazgo de privacidad.
3. Estructura viva vs `deprecated/`, `archive/`, `legacy/`, `old/`, `backup/`.
4. Versiones previas de Cerberus, auditorias antiguas, hooks viejos o controles equivalentes.
5. Controles activos, obsoletos, duplicados o zombie.

Resultado esperado:

```text
repo_profile.json
legacy_controls_inventory.json
privacy_check.md
purge_plan.md
```

Regla: si hay Cerberus viejo u otro control similar en codigo vivo, debe neutralizarse o mandarse a `deprecated/` antes de declarar que el repo esta bajo auditoria actual.

### Fase 1 — Contrato declarado o contrato inferido

Objetivo: definir contra que se audita.

Si el repo tiene contrato declarado, validar:

1. `README.md` completo y coherente.
2. Descripcion de GitHub llena y alineada al README.
3. Alcance, usuarios, entradas, salidas, no-objetivos y riesgos.
4. Comandos reales de instalacion, ejecucion, test y build.
5. Estado del proyecto y limites conocidos.

Si no hay contrato declarado, generar:

```text
CONTRATO_INFERIDO.md
```

El contrato inferido debe marcar hechos, inferencias y supuestos por separado. No puede inventar promesas.

Resultado esperado:

```text
claims.json
commands_detected.json
CONTRATO_INFERIDO.md
github_surface_check.md
```

### Fase 2 — Realidad operativa humano-like

Objetivo: validar que lo que el proyecto promete existe para un humano real.

Aqui se hacen pruebas como usuario:

1. Arranque local desde cero.
2. Flujo principal de UI/UX, si existe UI.
3. Comparacion UI contra backend: lo visible debe corresponder con datos, estados y errores reales.
4. Caminos felices, caminos enojados y estados vacios.
5. Validacion de permisos, entradas invalidas y errores recuperables.

Resultado esperado:

```text
execution_log.txt
ui_backend_trace.md
human_flow_evidence.md
```

### Fase 3 — Matriz contrato -> evidencia

Objetivo: convertir promesas en pruebas o hallazgos.

Cada claim debe clasificarse como:

```text
VERIFIED
PARTIAL
UNTESTED
FALSE
UNKNOWN
NOT_APPLICABLE
```

Resultado esperado:

```text
claim_matrix.csv
evidence_index.json
```

### Fase 4 — Mapeo contra Golden Standard

Objetivo: saber que reglas GS aplican y cuales faltan como consumer guards.

Cada regla GS relevante debe terminar en una de estas salidas:

```text
covered_by_test
covered_by_guard
advisory_only
missing_required_guard
not_applicable_with_reason
```

Resultado esperado:

```text
gs_mapping.json
gs_gaps.md
```

### Fase 5 — Pruebas adversariales

Objetivo: intentar romper el proyecto desde sus fronteras reales.

Debe incluir:

1. Entradas malformadas.
2. Estados incompletos.
3. Dependencias ausentes.
4. Configuracion incorrecta.
5. Permisos insuficientes.
6. Datos inconsistentes.
7. Pruebas de falso positivo en tests existentes.

Resultado esperado:

```text
adversarial_findings.md
theater_findings.md
```

### Fase 6 — Veredicto + plan de remediacion

Objetivo: no terminar en diagnostico esteril ni cerrar con hallazgos abiertos.

Debe producir:

1. Veredicto operativo.
2. Riesgos bloqueantes.
3. Hallazgos ordenados por severidad.
4. Plan de remediacion por fases.
5. Pruebas que deben agregarse o corregirse.
6. Criterio de salida para declarar el repo sano.
7. Evidencia de revalidacion posterior a la remediacion.

Regla de cierre: la auditoria no se considera terminada con el primer `verdict.md`. Si existen hallazgos, el cierre solo es valido cuando las correcciones se aplican y se revalidan sobre la misma baseline activa. Un "approved" sin recheck post-fix es preliminar, no cierre.

Resultado esperado:

```text
verdict.md
repair_plan.md
```

---

## 3. Infraestructura por nivel

Cerberus no debe instalarse igual en todos los repos.

```text
Nivel 0 — Auditoria externa sin instalar nada
Nivel 1 — Adaptador minimo: cerberus.audit.yaml
Nivel 2 — Hooks, watcher o CI solo despues de entender contrato y riesgos
```

Regla: si el repo aun no tiene contrato claro, no se instala enforcement pesado.

---

## 4. Aprendizaje hacia Cerberus y GS

Cada auditoria exterior debe alimentar una bandeja de aprendizaje en Cerberus:

```text
.protocol/inbox/external_learnings/<repo>_<yyyy-mm-dd>.json
```

Flujo:

1. Registrar hallazgo estructurado.
2. Normalizar y deduplicar en Cerberus.
3. Clasificar como caso local, patron Cerberus o candidato GS.
4. Proponer cambios a GS solo si el aprendizaje es generalizable.
5. Tras cambios en GS, sincronizar Cerberus hacia adentro y recalcular impacto en repos auditados.

GS no se modifica automaticamente desde un hallazgo exterior.

---

## 5. Vigilancia en tiempo real

Cuando el repo pase de auditoria a operacion, Cerberus puede vigilar:

1. Pre-commit local.
2. CI.
3. Watcher de archivos criticos.
4. Ledger de evidencia.
5. Re-auditoria por drift de contrato, GS o dependencias.

Esto requiere aprobacion por repo y no debe asumirse como default invasivo.

---

## 6. Piloto Control Procesal

Control Procesal no es muestra generica. Es el primer piloto real para validar la metodologia.

Antes de tocar codigo del piloto:

1. Ejecutar Fase 0.
2. Confirmar privacidad.
3. Identificar o inferir contrato.
4. Definir si solo se audita desde fuera o si se agrega adaptador minimo.

---

## 7. Preguntas abiertas antes de implementar runner

1. Esquema final de `cerberus.audit.yaml`.
2. Ruta exacta de artefactos por repo auditado.
3. Comandos permitidos por stack.
4. Criterios de severidad compartidos entre repos.
5. Formato de sincronizacion con GS candidates.

