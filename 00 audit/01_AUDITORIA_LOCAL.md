# 01 — AUDITORÍA LOCAL CODER CERBERUS

## 0. Objetivo

Auditar integralmente el proyecto local para determinar:

1. Qué partes son código vivo y operativo.
2. Qué partes son deprecated u obsoletas.
3. Qué scripts son activos, auxiliares, manuales, huérfanos o peligrosos.
4. Si el sistema cumple con la intención de gobernanza autónoma.
5. Si existen duplicidades, regresiones, stubs o éxito simulado.
6. Si el diseño actual es arquitectónicamente adecuado para lo que pretende resolver.

---

## 1. Proyecto local

Audita físicamente:

`D:\AI\Cerberus`

> ⚠️ Ruta anterior `D:\GoogleDrive\AI\Cerberus` es obsoleta. Actualizada 2026-06-05.

> ⚠️ No incluir `D:\AI\VibeCoding_GoldenStandard` en esta fase. GS es repo separado; su doctrina y la interfaz Cerberus↔GS viven en `D:\AI\VibeCoding_GoldenStandard\CERBERUS_CONTRACT.md`, no en este paquete.

No trabajes por memoria ni por documentación aislada.

---

## 2. Fase 0 — Alineación local y mapa del sistema

### Objetivo

Construir el mapa empírico del sistema antes de emitir juicios o modificar código.

### Instrucciones

1. Inspecciona la estructura completa del proyecto.
2. Identifica código vivo.
3. Identifica código deprecated.
4. Identifica scripts auxiliares.
5. Identifica runners.
6. Identifica hooks.
7. Identifica tests.
8. Identifica carpetas ocultas.
9. Identifica archivos de protocolo.
10. Extrae las dimensiones reales de evaluación que el sistema ya pretende aplicar.
11. Detecta discrepancias entre lo declarado y lo ejecutable.
12. Genera mapa inicial de topología.

### Restricción

No modifiques código en esta fase.

### Entregable

```text
[FASE 0 — MAPA DEL SISTEMA]

[HECHO] Código vivo:
[HECHO] Código deprecated:
[HECHO] Scripts:
[HECHO] Hooks:
[HECHO] Tests:
[HECHO] Carpetas ocultas:
[HECHO] Archivos de protocolo:
[INFERENCIA] Topología real:
[INFERENCIA] Discrepancias detectadas:
```

### Alcance excluido

- No leer ni reinterpretar GS como si fuera parte de Cerberus.
- No comparar esta fase contra `Wiki/` del GS salvo para validar consumo explícito según el contrato `VibeCoding_GoldenStandard\CERBERUS_CONTRACT.md`.

---

## 3. Fase 1 — Auditoría adversarial local 12D

Audita el proyecto contra las siguientes dimensiones:

1. D1 Integridad y pureza estructural.
2. D2 Completitud del control plane.
3. D3 Claridad, estilo y complejidad.
4. D4 Anti-spaghetti, aislamiento e imports.
5. D5 Angry Path y robustez de excepciones.
6. D6 Anti-theater y anti-slop.
7. D7 Seguridad de datos y confinamiento.
8. D8 Cobertura adversarial.
9. D9 Pureza de tests y falsabilidad.
10. D10 Tokenomics e higiene de contexto.
11. D11 SCA Trivy.
12. D12 Satellite Drift (Adopción de Release).

---

## 4. Dimensiones obligatorias

### D1 — Integridad y pureza estructural

Detecta:

- archivos zombies no declarados en whitelist;
- shims;
- wrappers;
- compatibilidad zombie;
- fallbacks de existencia;
- duplicidades estructurales;
- archivos fuera de ubicación lógica;
- violaciones al mandato Reemplazar = Eliminar + Crear.

---

### D2 — Completitud del control plane

Detecta:

- archivos obligatorios ausentes;
- configuraciones incompletas;
- runners desconectados;
- hooks ausentes;
- evidencia no generada;
- reglas no enlazadas.

**Checklist adicional — Entradas DOC_ONLY del Golden Standard:**

Para cada entrada en `golden_standard_audit.json` con `validating_mechanism: DOC_ONLY`:
- [ ] Si `downstream_verification: required` → ¿existe un guard físico, binding a guard existente, o consumer gap documentado?
- [ ] Si `downstream_verification: none` → ¿está indexada y es buscable vía `knowledge_loader`?
- [ ] ¿El campo `downstream_verification` se preserva en la ingesta (no se pierde al cargar)?

Un DOC_ONLY con `required` sin guard ni gap registrado = falla D2.

---

### D3 — Claridad, estilo y complejidad

Detecta:

- funciones excesivamente complejas;
- anidamientos excesivos;
- comentarios inútiles;
- variables redundantes;
- slop técnico;
- salidas verbosas sin valor operativo;
- ausencia de traducción ejecutiva.

---

### D4 — Anti-spaghetti y aislamiento

Detecta:

- dependencias circulares;
- imports rotos;
- acoplamiento excesivo;
- ausencia de bio-containment en fronteras de I/O;
- lógica transversal dispersa;
- mezcla indebida entre reglas, ejecución, presentación y evidencia.

---

### D5 — Angry Path y robustez

Toda cláusula de excepción debe verificar los cuatro elementos obligatorios:

1. `LOG`
2. `USUARIO` traducido
3. `ESTADO` o garantía de consistencia
4. `ACCIÓN`

Detecta:

- `try/except` silenciosos;
- excepciones genéricas;
- errores tragados;
- fallback complaciente;
- recuperación que oculta corrupción de estado.

---

### D6 — Anti-theater de producción

Detecta:

- emojis en código de producción;
- prints teatrales;
- stubs vacíos;
- retorno incondicional de `True`;
- validaciones cosméticas;
- “success” sin evidencia;
- mensajes verdes sin prueba real.

---

### D7 — Seguridad de datos y confinamiento

Detecta:

- secretos hardcodeados;
- uso inseguro de `eval()`;
- uso inseguro de `exec()`;
- uso inseguro de `shell=True`;
- rutas absolutas locales del desarrollador;
- exposición de archivos sensibles;
- instalación automática silenciosa;
- dependencias no autorizadas.

---

### D8 — Cobertura adversarial

Detecta:

- scripts core sin pruebas asociadas;
- flujos críticos sin test negativo;
- ausencia de pruebas de fallo;
- ausencia de fixtures maliciosos;
- ausencia de casos de regresión.

---

### D9 — Pureza de tests y falsabilidad

Detecta:

- `assert True`;
- aserciones triviales;
- `xfail` permanente sin criterio de remoción;
- feature flags en tests;
- mocking de dependencias internas del mismo repositorio;
- tests que validan el mock y no el sujeto;
- tests que pasan si el código crítico no se ejecuta;
- pruebas nombradas fuera del patrón real de descubrimiento.

---

### D10 — Tokenomics e higiene de contexto

Detecta:

1. Lectura de archivos `.md` mayores a 100 líneas sin rangos.
2. Fugas masivas de tokens de entrada.
3. RAG muerto por sensibilidad a mayúsculas/minúsculas.
4. Extracción inteligente de fragmentos ausente.
5. Salidas que no respetan modo compacto operativo.
6. Lectura repetida de contexto ya disponible.
7. Narrativa excesiva en reportes de consola.

---

### D11 — SCA Trivy

Detecta:

- Dependencias externas con vulnerabilidades críticas (CVEs).
- Secretos, contraseñas, tokens expuestos en la base de datos de dependencias.
- Desalineamiento de dependencias y brechas de SBOM.

---

### D12 — Satellite Drift (Adopción de Release)

Detecta:

- Desincronización de versión de protocolo entre el Core del proyecto y los repositorios satélites.
- Fallas de adopción o falta del archivo `VERSION.txt` en el prefijo `.protocol-core/` de satélites activos.

---

## 5. Formato obligatorio de hallazgo 12D

Cada hallazgo debe contener:

```text
[HECHO]
Archivo:
Línea o patrón:
Dimensión afectada:
Riesgo traducido:
Corrección propuesta:
Test de falsabilidad:
```

---

## 6. Fase 3 — Auditoría de autonomía Set and Forget

### Objetivo

Verificar si el sistema puede operar sin intervención manual de Luis.

### Evalúa

1. Hooks de pre-commit.
2. Runners locales.
3. Validaciones automáticas.
4. Evidencia generada en `.protocol/evidence/`.
5. Auto-repair o rollback.
6. Diagnóstico traducido a lenguaje operativo.
7. Bloqueo físico ante violaciones graves.
8. Ausencia de pasos que dependan de memoria humana.
9. Ejecución silenciosa de fondo.
10. Reparación de un solo click cuando auto-repair no sea seguro.

### Veredicto

Usa únicamente:

```text
EXCELENTE
FRÁGIL
INACEPTABLE
```

---

## 7. Fase 3.5 — Auditoría de Adecuación Arquitectónica

### Objetivo

Determinar si cada componente del proyecto está implementado mediante el mecanismo técnicamente más apropiado para el problema que pretende resolver.

No basta con que algo funcione.

Debe evaluarse si la solución elegida es:

1. La más simple.
2. La más robusta.
3. La más mantenible.
4. La más falsable.
5. La más alineada con Set and Forget.
6. La de menor complejidad accidental.
7. La de menor costo operativo.

### Método por subsistema

Para cada subsistema identificado:

1. Identificar el problema real que resuelve.
2. Identificar la implementación actual.
3. Evaluar alternativas arquitectónicas viables.
4. Comparar complejidad, mantenibilidad, escalabilidad, falsabilidad y costo operativo.
5. Emitir un veredicto.
6. Determinar si debe conservarse, eliminarse, dividirse, fusionarse o migrarse.

### Preguntas obligatorias

- ¿Este componente debería existir?
- ¿Puede eliminarse por completo?
- ¿Debe fusionarse con otro?
- ¿Debe dividirse?
- ¿Debe convertirse en configuración?
- ¿Debe convertirse en código?
- ¿Debe convertirse en skill?
- ¿Debe convertirse en agente?
- ¿Debe convertirse en librería?
- ¿Debe convertirse en plugin?
- ¿Debe convertirse en pipeline?
- ¿Debe convertirse en regla declarativa?
- ¿JSON sería superior a YAML?
- ¿SQLite sería superior a JSON?
- ¿Índices serían superiores a búsquedas lineales?
- ¿Un motor de reglas sería superior a lógica hardcodeada?
- ¿El almacenamiento actual minimiza complejidad accidental?

### Formato obligatorio

```text
Componente:
Problema que resuelve:
Implementación actual:
Alternativas evaluadas:
Ventajas:
Desventajas:
Veredicto: OPTIMAL / ADECUADO / SUBÓPTIMO / DEFECTUOSO
Nivel de confianza:
Recomendación:
```

---

## 8. Fase 7 — Corrección quirúrgica local

Aplica correcciones únicamente si:

1. Están directamente vinculadas con hallazgos críticos.
2. No generan sidequests.
3. No crean shims.
4. No ocultan fallos.
5. No rompen el principio de Reemplazar = Eliminar + Crear.
6. No introducen compatibilidad zombie.
7. No reducen falsabilidad.

Cada corrección aplicada debe documentarse así:

```text
Archivo:
Cambio:
ID GS vinculado:
Dimensión afectada:
Riesgo mitigado:
Prueba ejecutada:
Resultado:
```

---

## 9. Verificaciones específicas de estructura limpia

### 9.1 Pureza de deprecated

Confirma que `deprecated/` es cuarentena inerte:

- Ningún archivo vivo importa desde `deprecated/`.
- Ningún runner depende de `deprecated/`.
- Ningún hook depende de `deprecated/`.
- Ninguna prueba viva requiere `deprecated/`.
- Ningún fallback usa `deprecated/`.

---

### 9.2 Clasificación de scripts

Clasifica cada script en `scripts/` como:

1. Activo automático.
2. Manual útil.
3. Auxiliar.
4. Cuarentena / Deprecated.
5. Huérfano / Peligroso.

Cualquier script huérfano debe clasificarse, corregirse, aislarse o eliminarse.

---

## 10. Entregable local

```markdown
## Auditoría Local 12D

| Dimensión | Veredicto | Evidencia | Riesgo traducido | Corrección |
|---|---|---|---|---|
| D1 Integridad & S19 | APPROVED / REJECTED | | | |
| D2 Completitud | APPROVED / REJECTED | | | |
| D3 Claridad | APPROVED / REJECTED | | | |
| D4 Anti-spaghetti | APPROVED / REJECTED | | | |
| D5 Angry Path | APPROVED / REJECTED | | | |
| D6 Anti-theater & Anti-slop | APPROVED / REJECTED | | | |
| D7 Seguridad | APPROVED / REJECTED | | | |
| D8 Cobertura | APPROVED / REJECTED | | | |
| D9 Pureza de Tests | APPROVED / REJECTED | | | |
| D10 Tokenomics | APPROVED / REJECTED | | | |
| D11 SCA Trivy | APPROVED / REJECTED | | | |
| D12 Satellite Drift | APPROVED / REJECTED | | | |

## Auditoría de Adecuación Arquitectónica

| Componente | Implementación Actual | Alternativa Recomendada | Veredicto | Impacto |
|---|---|---|---|---|

## Scripts Clasificados

| Script | Clasificación | Evidencia | Riesgo | Acción |
|---|---|---|---|---|
```
