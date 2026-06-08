# TK-046: Sub-Agentes — Por Qué NO Es Automatizable

**Decisión de Arquitectura:** Sub-agentes requieren juicio estratégico y NO pueden automatizarse.

---

## El Problema

**Escenario:** Usuario necesita exploración profunda que consume 50K+ tokens.

❌ **Opción 1: Automatizar (NO FUNCIONA)**
```
IF exploración_grande THEN spawn_subagent
```
**Problema:** ¿Cuándo es "grande"? ¿Siempre delegamos? ¿Nunca?
- Overhead de sub-agente: inicialización, contexto, síntesis
- A veces la exploración aporta insights que el usuario necesita ver
- Decisión es **contextual, no métrica**

✅ **Opción 2: Manual (CORRECTO)**
```
Usuario: "Investiga X"
Claude: "Esta investigación es grande. ¿Quieres sub-agente?"
Usuario: SÍ → spawn | NO → exploración directa
```

---

## Por Qué No Se Puede Automatizar

### 1. **Decisión Estratégica, No Táctica**

| Aspecto | Automatizable | No Automatizable |
|---|---|---|
| Thinking mode | ✅ (técnica) | — |
| Model routing | ✅ (complejidad) | — |
| Tool truncation | ✅ (bytes) | — |
| **Sub-agentes** | ❌ | ✅ (contexto) |

Sub-agentes no son "técnica de ahorro de tokens" — son **decisión de workflow**.

### 2. **Contexto es Opaco**

Preguntas que solo el usuario puede responder:
- ¿Necesitas ver el proceso de investigación?
- ¿Basta con un resumen final?
- ¿La exploración podría generar insights?
- ¿Es crítica para la decisión?

**Ejemplo 1:**
```
Usuario: "Investiga si nuestra API es segura"
Claude (automático): spawn subagent
Problema: Usuario quería ver los hallazgos de seguridad, no solo "Resultado: segura"
```

**Ejemplo 2:**
```
Usuario: "Dame un resumen de trends en ML"
Claude (automático): exploración directa
Problema: 60K tokens gastados cuando sub-agente habría bastado
```

### 3. **Overhead Vs Ahorro**

```
Sub-agente tiene COSTO:
- Inicialización de contexto
- Síntesis de resultados
- Context-switching

Sub-agente tiene BENEFICIO:
- Aislamiento de tokens (no arrastra a chat principal)
- Paralelización posible
- Limpieza de contexto

Equilibrio es CONTEXTUAL, no automático.
```

### 4. **Conflicto con Autonomía**

Si automatizamos:
```
Claude SIEMPRE delega exploración grande
→ Usuario pierde visibilidad
→ Perdemos oportunidad de insights
→ Claude actúa sin permiso
```

Esto viola:
- **B8: Anti-Deriva** (decisiones secundarias sin aprobación)
- **B1: Doctrina Fallo** (asumir que funcionará sin validar)

---

## Cuándo Usar Sub-Agentes (Manual)

✅ **USAR sub-agente si:**
- Exploración > 30K tokens estimados
- Usuario solo necesita resumen final
- Investigación es paralela a tarea principal
- Necesitas aislar contexto para paralelización

❌ **NO USAR si:**
- Usuario dijo explícitamente "investiga conmigo"
- Exploración podría descubrir cambios de plan
- < 10K tokens estimados (overhead no vale la pena)
- Decisión depende de cómo se llega al resultado

---

## Implementación: Sugerencia Manual

**Mejor práctica: Claude sugiere, usuario decide**

```python
# Pseudo-código
if exploration_size > 30000:
    print("⚠️ Esta investigación es grande (30K+ tokens).")
    print("Opciones:")
    print("  1. Usar sub-agente (resumen final)")
    print("  2. Exploración directa (veo todo el proceso)")
    # Usuario elige
```

**No código automático, sino UX clara.**

---

## Conclusion

| Fase | TK | Automatización | Motivo |
|---|---|---|---|
| 1 | 044-050 | ✅ 5/5 | Tácticas (tokens, modelos, output) |
| 2 | 048 | ✅ 1/1 | Detectar plan (patrón claro) |
| **Manual** | **046** | ❌ 0/1 | **Decisión estratégica (contexto)** |

**TK-046 está CERRADO como MANUAL.**

No es falta de implementación — es decisión arquitectónica correcta.

---

**Documentado:** 2026-06-02 | **Status:** MANUAL (by design)
