# 03 — EVOLUCIÓN Y EJECUTABILIDAD DEL GOLDEN STANDARD EXTERNO

## 0. Objetivo

Verificar que el Golden Standard externo esté correctamente regulado, actualizado, trazable y consumible por Coder Cerberus.

No basta con documentar reglas.

Cada regla debe ser:

1. Detectable.
2. Falsable.
3. Medible.
4. Automatizable.
5. Bloqueable o clasificable.
6. Trazable a evidencia.
7. Traducible a riesgo operativo.

---

## 1. Fuentes obligatorias

Abre y lee físicamente:

```text
D:\AI\VibeCoding_GoldenStandard\golden_standard.yaml
```

El archivo `golden_standard.yaml` del repo externo es la única fuente de verdad unificada para la gobernanza del protocolo. La carpeta local `Golden_Standard/` en Cerberus fue **eliminada físicamente**. No existe copia local ni snapshot. GS vive exclusivamente en `D:\AI\VibeCoding_GoldenStandard`.

## 1B. Contrato de consumo GS -> Cerberus

Todo `DOC_ONLY` del GS debe consumirse con la siguiente lógica:

- `DOC_ONLY` + `downstream_verification: required` -> `consumer_guard_expected`
- `DOC_ONLY` + `downstream_verification: none` -> `advisory_only`

En ningún caso `DOC_ONLY` equivale automáticamente a `test_exempt`.

Después de resincronizar `.protocol/metadata/golden_standard_audit.json` desde GS, ejecutar:

```text
python scripts/normalize_golden_audit_consumer_contract.py
```

Este normalizador preserva reglas nuevas como contrato de consumidor y convierte mecanismos no verificables físicamente en `DOC_ONLY` honesto con `downstream_verification`, evitando que Cerberus confunda strings o comandos externos con pruebas reales.

---

## 2. Fase 2 — Golden Standard Sweep

Contrasta el proyecto contra el catálogo canónico actual y el legado histórico:

1. Catálogo canónico actual: leer dinámicamente desde `golden_standard.yaml`; la validación de 2026-06-05 detectó `PI-001` a `PI-034`
2. Referencia histórica de testing: `VT-001` a `VT-115`
3. Referencia histórica de completitud/comportamiento: `VC-001` a `VC-126`
4. Referencia histórica de tokenomics: `TK-001` a `TK-046`

---

## 3. IDs de atención prioritaria

Presta especial atención a:

```text
PI-003 Tokenomics y coste visible
PI-008 Batch de autorizaciones y preguntas
PI-013 Vigilancia en vivo
PI-015 Ratchet de circularidad
PI-016 Honestidad DOC_ONLY
PI-017 Anti-cobertura many-to-one
PI-018 Ingesta canónica satélite
VT-109 Testing Bridge Theater
VT-110 Fragmentación de Directorios Ocultos
VC-115 Ejecución dinámica de expresiones
VC-116 Instalación automática silenciosa
VC-118 Teatro de Compatibilidad Zombie
VC-119 Pánico de Bloqueo y Parcheo Rápido
```

## 3B. Qué debe traer Cerberus de vuelta

Traer a Cerberus solo lo que pueda convertirse en:

- guard de consumidor;
- lint de protocolo;
- auditoría de consumo;
- regla de preflight;
- evidencia trazable;
- backlog explícito.

No traer nombres comerciales, no traer copias literales de catálogo, no traer mutaciones del GS.

---

## 4. Auditoría de ejecutabilidad del Golden Standard

Para cada regla o ID:

1. ¿Es detectable?
2. ¿Es falsable?
3. ¿Es automatizable?
4. ¿Es medible?
5. ¿Es bloqueable?
6. ¿Tiene acción esperada?
7. ¿Tiene evidencia esperada?
8. ¿Tiene severidad?
9. ¿Tiene traducción de riesgo?
10. ¿Tiene ruta de enforcement?

Si no cumple, clasifica como:

`RULE THEATER`

## 4B. Resultado esperado para consumo

Cada regla GS debe terminar en una de estas salidas de Cerberus:

- `advisory_only`
- `consumer_guard_expected`
- `consumer_guard_absent_but_tracked`

---

## 5. Auditoría MD vs YAML

Verifica entre las bibliotecas `.md` y `golden_standard.yaml`:

1. Cobertura completa.
2. Trazabilidad.
3. No pérdida semántica.
4. No contradicciones.
5. No reglas huérfanas.
6. No IDs huérfanos.
7. No duplicados.
8. No drift documental.
9. No diferencias de severidad.
10. No diferencias de acción esperada.
11. No diferencias de enforcement.
12. No diferencias de categoría.
13. No reglas en `.md` ausentes del YAML.
14. No reglas en YAML ausentes de `.md` salvo que estén justificadas como índice técnico.

---

## 6. Evaluación de Tokenomics y ahorro de tokens

Analiza el codebase contra los principios de ahorro e higiene de tokens:

`PI-003`, `PI-008`, `PI-013`, `TK-001` a `TK-041`

Debes comprobar empíricamente:

1. Higiene de contexto.
2. Si se leen archivos `.md` mayores a 100 líneas sin rangos.
3. Si hay fugas masivas de tokens de entrada.
4. Si la extracción inteligente de fragmentos está activa.
5. Si el sistema soporta insensibilidad a mayúsculas/minúsculas para evitar llamadas RAG muertas.
6. Si las salidas respetan modo compacto operativo.
7. Si hay lectura repetitiva de documentos sin caché o índice.
8. Si hay exceso narrativo en diagnósticos técnicos.
9. Si los reportes distinguen entre evidencia mínima y detalle extendido.

## 6B. Lectura de primera ejecución

- No reutilizar decisiones antiguas como si estuvieran vigentes por defecto.
- No asumir que una regla queda operable solo por existir en Markdown.
- No marcar `DOC_ONLY` como “sin acción” si el consumidor necesita guard.

---

## 7. Fase 5 — Síntesis e integración del Golden Standard

Actualiza conceptualmente el Golden Standard sin insertar:

- nombres comerciales;
- comandos de instalación;
- dependencias específicas;
- rutas de terceros;
- instrucciones atadas a un lenguaje específico.

### Reglas

1. Si la lógica no existe, genera nuevo bloque agnóstico.
2. Si existe parcialmente, complementa solo con heurística nueva.
3. Si ya existe, descarta por redundancia.
4. No dupliques conceptos.
5. No mezcles herramienta con principio.
6. Cada nuevo bloque debe ser ejecutable o convertible en regla ejecutable.
7. Cada bloque debe tener criterio de falsabilidad.
8. Cada bloque debe tener ruta de enforcement.
9. Cada bloque debe tener acción esperada.
10. Cada bloque debe mapearse a una dimensión Cerberus.

---

## 8. Formato de bloque propuesto

```markdown
### [ID PROPUESTO] — [Nombre del vicio o principio]

**Categoría:** [Testing / Vibe Coding / Tokenomics / Seguridad / Gobernanza / Arquitectura]

**Dimensión Cerberus:** [D1-D12]

**Defecto regulado:**
[Descripción agnóstica]

**Riesgo operativo:**
[Consecuencia para estabilidad, seguridad o gobernanza]

**Regla ejecutable:**
[Condición verificable por código, hook, runner o scanner]

**Criterio de falsabilidad:**
[Cómo probar que la regla sí detecta el defecto]

**Ruta de enforcement:**
[Scanner / Hook / Runner / Pipeline / Agente / Skill / Manual Backlog]

**Evidencia esperada:**
[Archivo, log o reporte que debe generarse]

**Acción esperada:**
[BLOCK / WARN / BACKLOG / AUTO-REPAIR]
```

---

## 9. Fase 6 — Plan técnico de integración en Coder Cerberus

Diseña la estrategia para que las nuevas reglas del Golden Standard sean ejecutables.

Incluye:

1. Archivos a modificar.
2. Pipelines a actualizar.
3. Hooks a fortalecer.
4. Runners a crear o corregir.
5. Validaciones que deben bloquear con `exit 1`.
6. Evidencia que debe generarse.
7. Riesgos de implementación.
8. Tests de falsabilidad.
9. Refactorizaciones arquitectónicas recomendadas.
10. Componentes que deberían eliminarse.
11. Componentes que deberían fusionarse.
12. Cambios de persistencia recomendados.
13. Cambios de patrón arquitectónico recomendados.
14. Cambios de topología agente / skill / librería / pipeline.
15. Reglas que deben quedar solo en backlog por no ser ejecutables todavía.

No basta con decir “actualizar documentación”.

Cada principio debe tener ruta de ejecución.

## 9B. Aprendizajes adicionales a consolidar antes de S5

Antes de continuar con la siguiente fase operativa, el Golden Standard debe reflejar explícitamente estos aprendizajes agnósticos ya validados por el proyecto:

1. Agrupar autorizaciones y preguntas previsibles en una sola pasada.
2. Convertir warnings conocidos y hallazgos no bloqueantes en errores reales hasta remediarlos.
3. Tratar `results/` y otros artefactos históricos como referencia, no como fuente activa.
4. Preferir nombres descriptivos y topologías simples.
5. Mantener exclusiones, skips y xfails en mínimo real con justificación verificable.
6. Favorecer vigilancia en tiempo real antes que revisión post-mortem.
7. Mantener el Golden Standard vivo con aprendizaje continuo de proyectos satélite.

---

## 10. Entregable Golden Standard

```markdown
## Escrutinio Cruzado del Golden Standard

- **Vicios de Testing Detectados:**
- **Vicios de Vibe Coding Detectados:**
- **Fugas de Tokenomics Detectadas:**
- **Reglas Declarativas No Ejecutables:**
- **Diferencias entre MD y YAML:**
- **RULE THEATER Detectado:**

## Diferencias MD vs YAML

| ID | Fuente MD | Estado YAML | Diferencia | Riesgo | Acción |
|---|---|---|---|---|---|

## Bloques Propuestos para Golden Standard

### Archivo: [nombre]

```markdown
[bloques exactos]
```

## Estrategia de Integración Ejecutable

| Regla | Archivo / Runner / Hook | Acción | Falsabilidad | Resultado esperado |
|---|---|---|---|---|
```
