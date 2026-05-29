# GLOBAL_LEARNING.md — Inteligencia Colectiva del Protocolo
**Versión:** 1.1 | **Rescatado de:** deprecated/docs/GLOBAL_LEARNING.md | **Actualizado:** 2026-05-24

---

## FALLOS DE ENTORNO DETECTADOS

### Windows 11 Encoding (Critico)
- **Descubrimiento:** Python en Windows usa `cp1252` por defecto, corrompiendo emojis y caracteres especiales en archivos UTF-8.
- **Fix global:** Inyectar `sys.stdout.reconfigure(encoding='utf-8')` al inicio de todos los scripts de auditoría.
- **Validacion:** El test de resiliencia debe intentar imprimir un emoji para verificar el fix.
- **Afecta:** Todos los scripts en `scripts/`.

### Git Race Conditions
- **Descubrimiento:** Ejecutar multiples comandos git en paralelo via herramientas de IA puede bloquear `.git/index.lock`.
- **Fix global:** Serializar comandos git en scripts de automatizacion. No correr git en paralelo.
- **Patron seguro:**
  ```python
  import subprocess, time
  def git_safe(cmd, retries=3):
      for i in range(retries):
          r = subprocess.run(cmd, capture_output=True)
          if r.returncode == 0: return r
          time.sleep(1)
      raise RuntimeError(f"git command failed: {cmd}")
  ```

---

## MEJORAS DE VIBE CODING

- **XML Delimiters:** El uso de tags `<contexto>`, `<tarea>` y `<restricciones>` en los prompts reduce alucinaciones de ruta en ~25%.
- **Valor sobre Volumen:** La IA tiende a rellenar archivos con funciones inutiles. Directiva: premiar borrado de codigo (Poda Agresiva) para mantener contexto limpio.

---

## INCIDENTE CRITICO: 2026-05-20 — Falla Sistemica en Control Procesal v14

**Naturaleza:** Algorithmic Optimism extremo, Alucinacion de Exito, Chopped Code, Error de Localizacion.

**Analisis:**
1. **Perdida de Ubicacion:** Gemini ignoro `Cerberus/` y creo carpeta zombi `.protocolo` en la raiz, trabajando sobre version obsoleta v4.0.
2. **Falsos Triunfos:** Se otorgo calificacion "Diamante" sin pruebas empiricas.
3. **Alucinacion de Human Test:** Simulo prueba de usuario en entorno sin capacidad de visualizacion.
4. **Chopped Code:** Al reescribir HTML masivo con write_file, output truncado por limites de tokens. Borro 70% del archivo. Reporto exito sobre archivo roto.
5. **Violacion de Edicion Quirurgica:** Reescribio todo en lugar de usar replace localizado.

**Reglas derivadas (BINDING):**
- **S15 (LOCALIZACION):** El UNICO lugar para protocolo global es `D:\GoogleDrive\AI\Cerberus`. Cualquier carpeta `.protocolo` externa es infeccion — eliminar inmediatamente.
- **B15 (ANTI-TRIUNFALISMO):** Prohibido "Diamante", "Triunfo", "Exito 100%" sin adjuntar logs de terminal o capturas externas.
- **B16 (UI VALIDATION):** NUNCA validar UI internamente. Obligatorio pedir al humano: "Abre [X] y confirmame que [Y] funciona".
- **S16 (LARGE FILE SAFETY):** Archivos >200 lineas: PROHIBIDO write_file. Solo replace en bloques <50 lineas.

---

## LEDGER DE APRENDIZAJE

| Fecha | Proyecto | Descubrimiento | Estado |
|-------|----------|----------------|--------|
| 2026-05-18 | Coder Cerberus V0.1 | Pesimismo Algoritmico inyectado en Core | DIFUNDIDO |
| 2026-05-20 | Control Procesal v14 | Incidente Chopped Code + Alucinacion UI | BINDING S15/B15/B16/S16 |
| 2026-05-24 | Cerberus deprecated audit | 10 fallos concretos en scripts core | Ver FALLOS_CONOCIDOS.md |

---

**Protocolo de actualizacion:** Cuando ocurre un incidente nuevo, agregar entrada al Ledger + derivar regla con codigo S/B. Nunca borrar entradas previas.
