# UI Backend Trace - Control_Procesal Fase 2

**Fecha:** 2026-06-06  
**Modo:** Validacion humano-like con backend real  
**Repo auditado:** `D:\AI\Control_Procesal`

## Contrato Probado

Claims relevantes de Fase 1:

- `CP-C001`: UI local de control procesal.
- `CP-C002`: servidor local Python en `127.0.0.1:5050`.
- `CP-C003`: persistencia en `storage_poe.json`.
- `CP-C005`: endpoints locales salud/storage/PDF/expedientes.
- `CP-C008`: deuda critica historica en `/expedientes`.

## Backend Real

El servidor no estaba activo al inicio. Tras levantar `scripts\servidor_pdf.py`, `/ping` respondio:

```json
{"ok": true, "version": "3.2"}
```

Mediciones:

| Endpoint | Estado | Tiempo | Resultado |
|---|---:|---:|---|
| `/ping` | 200 | 0.003679s | version `3.2` |
| `/storage/get` | 200 | 0.1250s | 86 registros, 28 expedientes unicos |
| `/expedientes` | 200 | 0.1298s | 28 expedientes |
| `/pdf/cargar/__missing__` | 404 | 0.006440s | error recuperable para PDF inexistente |

## UI Visible

Evidencia:

- `phase2_ui_screenshot.png`
- `phase2_ui_screenshot_wait8s.png`
- HAR generado e inspeccionado durante la corrida, no versionado porque contenia payload completo de `storage_poe.json`.

Observacion visual despues de 8 segundos:

- Header: `POE Consultores · Control Procesal`.
- Estado superior derecho: `Conectando...`.
- Contadores: `Urgentes=0`, `Normales=0`, `Informativos=0`, `Expedientes=0`.
- Lista lateral de expedientes: vacia.
- Tabla principal: solo encabezados, sin filas.

## Comparacion UI vs Backend

| Superficie | Realidad backend | Realidad UI | Resultado |
|---|---:|---:|---|
| Expedientes unicos | 28 | 0 visibles | `FALSE` para usuario |
| Storage registros | 86 | 0 visibles | `FALSE` para usuario |
| Estado conexion | `/ping` 200 | `Conectando...` | `FALSE` para usuario |
| `/expedientes` timeout historico | no reproducido; ~0.13s | no consumido visiblemente | `PARTIAL` |

## Causa Probable

El HTML ejecuta:

```js
verificarServidor();
cargarData();
```

`verificarServidor()` es asincrona y no se espera antes de `cargarData()`. Por tanto, `cargarData()`
puede correr mientras `servidorOk` todavia es `false`, saltarse `/storage/get`, caer a storage local
vacio y renderizar 0 expedientes.

Ademas, `scripts/app.js` tambien inicializa un cliente que llama `/ping` y `/storage/get`, pero usa un
estado separado (`StorageManager`) que no alimenta la UI inline principal. El HAR contiene trafico a
storage, pero la pantalla no se actualiza.

## Veredicto Fase 2 Inicial

**Fase 2 FALLA en UI/backend parity.**

El backend local funciona y la deuda historica de timeout en `/expedientes` no se reprodujo en esta
corrida. Sin embargo, el usuario humano ve una UI vacia/desconectada aunque el backend tiene datos.
Esto es fallo funcional, no teatro menor.

## Remediacion Posterior

Ver `phase2_remediation_result.md`.

Tras corregir el error de sintaxis `const dualTable` y el bootstrap asincrono, la captura
`phase2_fix_ui_screenshot_verified.png` muestra estado `Sincronizado`, `28` expedientes y lista
lateral poblada.
