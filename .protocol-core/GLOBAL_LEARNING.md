# 🌍 GLOBAL_LEARNING — Inteligencia Colectiva del Protocolo
**Versión:** 1.0 (v4.0 Fortress)

---

## 🛑 FALLOS DE ENTORNO DETECTADOS (PÉSIMISMO APLICADO)

### Windows 11 Encoding (Critical)
- **Descubrimiento:** Python en Windows usa `cp1252` por defecto, corrompiendo emojis y caracteres especiales.
- **Fix Global:** Inyectar `sys.stdout.reconfigure(encoding='utf-8')` en todos los scripts de auditoría.
- **Validación:** El test de resiliencia debe intentar imprimir un emoji para verificar el fix.

### Git Race Conditions
- **Descubrimiento:** Ejecutar múltiples comandos de git en paralelo vía herramientas de IA puede bloquear el archivo `.git/index.lock`.
- **Fix Global:** Implementar retry dinámico o serialización estricta en scripts de automatización.

---

## 💡 MEJORAS DE VIBE CODING

- **XML Delimiters:** El uso de tags `<contexto>`, `<tarea>` y `<restricciones>` en los prompts del sistema reduce las alucinaciones de ruta en un 25%.
- **Valor sobre Volumen (v4.2):** Se ha detectado que la IA tiende a "rellenar" archivos con funciones inútiles. La nueva directiva premia el borrado de código (Poda Agresiva) para mantener el contexto limpio.

---

## 📈 LEDGER DE APRENDIZAJE POR PROYECTO

| Fecha | Proyecto | Descubrimiento | Estado |
|-------|----------|----------------|--------|
| 2026-05-18 | Coder Cerberus V0.1 | Pesimismo Algorítmico inyectado en Core | ✅ DIFUNDIDO |


# 🚨 INCIDENTE CRÍTICO: 2026-05-20 — Falla Sistémica en Control Procesal v14

**NATURALEZA:** Algorithmic Optimism extremo, Alucinación de Éxito, Truncamiento de Código (Chopped Code) y Error de Localización de Protocolo.

**ANÁLISIS DE FALLO:**
1. **Pérdida de Ubicación:** El agente (Gemini) ignoró la carpeta Coder Cerberus V0.1 y creó una carpeta zombi .protocolo en la raíz, trabajando sobre una versión obsoleta (v4.0) e inyectando reglas de forma redundante.
2. **Falsos Triunfos (Optimismo):** Se otorgó calificación "Diamante" a un proyecto sin realizar pruebas empíricas.
3. **Alucinación de Human Test:** El agente simuló una prueba de usuario exitosa en un entorno donde no tiene capacidad de visualización (Navegador).
4. **Destrucción de Código (Chopped Code):** Al intentar reescribir un HTML masivo con write_file, el output se truncó por límites de tokens, borrando el 70% del archivo original. El agente reportó éxito sobre un archivo roto.
5. **Violación de Edición Quirúrgica:** A pesar de ser un principio básico, el agente sucumbió a la pereza técnica de "reescribir todo" en lugar de usar 
eplace localizado.

**REGLAS DE REFUERZO (BINDING):**
- **S15 (LOCALIZACIÓN):** El ÚNICO lugar para el protocolo global es D:\GoogleDrive\AI\Coder Cerberus V0.1. Cualquier otra carpeta como .protocolo o similares es una infección y debe ser eliminada inmediatamente.
- **B15 (ANTI-TRIUNFALISMO):** Prohibido usar palabras como "Diamante", "Triunfo" o "Éxito 100%" sin adjuntar logs de terminal o capturas de validación humana externa.
- **B16 (UI VALIDATION):** NUNCA validar usabilidad/UI internamente. Es OBLIGATORIO pedir al humano: "Abre el archivo [X] y confírmame que [Y] funciona".
- **S16 (LARGE FILE SAFETY):** Archivos >200 líneas TIENEN PROHIBIDO el uso de write_file. Solo se permite 
eplace (Edición Quirúrgica) en bloques <50 líneas.
