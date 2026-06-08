# Human Flow Evidence - Control_Procesal Fase 2

**Fecha:** 2026-06-06  
**Flujo:** abrir app local con backend vivo

## Pasos Reproducibles

1. Desde un estado sin servidor, solicitar `GET http://127.0.0.1:5050/ping`.
2. Confirmar que falla por conexion rechazada.
3. Levantar `scripts\servidor_pdf.py` desde `D:\AI\Control_Procesal`.
4. Confirmar `/ping` con `200` y version `3.2`.
5. Confirmar `/storage/get` con 86 registros y 28 expedientes unicos.
6. Confirmar `/expedientes` con 28 expedientes y respuesta rapida.
7. Abrir `file:///D:/AI/Control_Procesal/ControlProcesal_POE_v14.html`.
8. Esperar 8 segundos.
9. Observar pantalla.

## Resultado Observado

La pantalla carga visualmente, pero no representa los datos reales:

- Sigue mostrando `Conectando...`.
- Muestra `0` expedientes.
- Muestra tabla vacia.
- No muestra lista lateral de expedientes.

## Evidencia Visual

- `phase2_ui_screenshot_wait8s.png`

## Caminos Enojados

1. **Servidor ausente:** `/ping` falla por conexion rechazada. La UI deberia mostrar error claro y accion recuperable.
2. **PDF inexistente:** `/pdf/cargar/__missing__` responde `404`; backend maneja el error de forma recuperable.
3. **Race de inicializacion:** backend vivo, pero UI visible queda vacia por orden asincrono probable.

## Clasificacion

- Arranque backend: `VERIFIED`.
- Endpoints principales: `VERIFIED`.
- `/expedientes` timeout historico: `NOT_REPRODUCED_THIS_RUN`.
- UI/UX principal contra backend: `FALSE`.
- Flujo humano completo: `FAILED`.

## Remediacion Recomendada Para La Siguiente Parte

1. Esperar `await verificarServidor()` antes de `await cargarData()`.
2. Unificar el estado de `ControlProcesal_POE_v14.html` y `scripts/app.js`, o retirar el script externo si es ruta zombie.
3. Agregar prueba Playwright/funcional que falle si backend tiene expedientes y UI muestra `0`.
4. Agregar prueba de estado vacio real separada de estado "backend no cargado".

