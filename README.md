# 🛡️ Coder Cerberus v0.3 — Guardián de Calidad del Código

[![Version](https://img.shields.io/badge/version-v0.3-blueviolet.svg?style=flat-square)](PLAN.md)
[![Audit](https://img.shields.io/badge/audit--12d-APPROVED-success.svg?style=flat-square)](scripts/run_security_audit_12d.py)
[![Tests](https://img.shields.io/badge/tests-386%20PASSED-success.svg?style=flat-square)](#)
[![MCP](https://img.shields.io/badge/MCP-compatible-brightgreen.svg?style=flat-square)](#integraciones)
[![Python](https://img.shields.io/badge/python-3.13+-yellow.svg?style=flat-square)](#)

---

## ¿Qué es Cerberus?

**Cerberus es el blindaje defensivo del código** — no orquesta agentes (eso hacen LangGraph, CrewAI), sino que **valida y protege** todo lo que otros sistemas generan.

Funciona como un guardián automático que revisa todo el código antes de cada cambio. Piensa en él como un revisor que:

- ✅ **Valida que el código funciona correctamente** — detecta errores silenciosos y codigo abandonado
- ✅ **Garantiza documentación y claridad** — obliga a explicar qué hace cada cosa
- ✅ **Previene costumbres malas** — bloquea patrones que causan problemas después
- ✅ **Mantiene todo sincronizado** — los cambios se propagan automáticamente a todos los sub-proyectos
- ✅ **Controla el gasto** — vigila cuántos tokens de IA se gastan en cada operación

Cerberus funciona automáticamente: cada vez que intentas guardar cambios, ejecuta 12 tipos de verificación (llamados "dominios") que aseguran que todo esté bien antes de permitir que el cambio se guarde.

---

## Lo que Cerberus valida

| Validación | ¿Qué revisa? |
|------------|-------------|
| **Integridad** | Que no haya archivos "fantasma" sin declarar en el sistema |
| **Completitud** | Que el código esté terminado (no tenga placeholders vacíos) |
| **Claridad** | Que el código sea legible y esté documentado |
| **Lógica simple** | Que la lógica sea directa (no demasiado enredada) |
| **Manejo de errores** | Que cada error se maneje con registro y contexto |
| **Higiene** | Que no haya código viejo, imports innecesarios o malas prácticas |
| **Seguridad** | Que no haya contraseñas, secretos ni operaciones peligrosas |
| **Tests funcionales** | Que los tests existan y pasen |
| **Tests auténticos** | Que los tests realmente prueben el código (no sean falsos) |
| **Tokenomics** | Que se controle el gasto de recursos (tokens de IA) |
| **Seguridad externa** | Que no haya librerías con vulnerabilidades conocidas |
| **Sincronización** | Que todos los sub-proyectos estén alineados |

---

## 🔗 Integraciones (Complementario a otros sistemas)

| Sistema | ¿Qué hace? | ¿Cómo se complementan? |
|---------|-----------|----------------------|
| **LangGraph** | Orquesta flujos de agentes | Cerberus valida el código que LangGraph genera |
| **CrewAI** | Coordina equipos de agentes | Cerberus audita las decisiones y código del equipo |
| **MCP** | Protocolo estándar para herramientas | Cerberus protege las conexiones MCP contra errores silenciosos |
| **Tu código actual** | Lo que escribes tú | Cerberus lo verifica automáticamente |

**La clave:** Cerberus no compite con estos sistemas, los **protege**. Mientras ellos orquestan y coordinan, Cerberus es el sistema inmunológico que evita que algo malo llegue a producción.

---

## Cómo se usa

### Verificación automática (diaria)
```bash
python scripts/run_security_audit_12d.py .
```
Esto ejecuta todas las verificaciones y muestra:
- ✅ **APPROVED** — todo está bien, puedes guardar tus cambios
- ❌ **REJECTED** — hay problemas, y te muestra dónde están para que los arregles

### Sincronizar sub-proyectos
```bash
python scripts/protocol_cli propagate --apply
```
Asegura que 17 sub-proyectos tengan los mismos estándares que el core.

---

## Estado actual

- **Versión:** v0.3 (Sprint 5-11 completados)
- **Tests:** 386 pasando, 0 fallando
- **Auditoría:** APPROVED (todas las 12 verificaciones pasan)
- **Cobertura de problemas:** 278 tipos de errores detectados y bloqueados
- **Sprints cerrados:** 0-11 (arquitectura, naming, documentación, auditoría final)

---

## Aprendizajes integrados (Sprints 5-11)

| Sprint | Aprendizaje | Implementado |
|--------|-------------|--------------|
| **5** | No permitir hallazgos que no causen bloqueo (WARN→BLOCK) | ✅ Recomendaciones solo con FAILs |
| **7** | Nombres de script claros y descriptivos | ✅ 23 scripts renombrados (verb_noun) |
| **8** | Estructura simple, sin carpetas innecesarias | ✅ Aplanamiento ejecutado |
| **9** | Golden Standard como única fuente de verdad | ✅ PI-015..018 formalizadas |
| **10** | Vigilancia de costos en tiempo real | ✅ 36 repos externos auditados |
| **11** | Auditoría completa y veredicto final | ✅ Guides refrescadas, plan viejo retirado |

---

## Documentación importante

- **[PLAN.md](PLAN.md)** — Qué sprints están hechos y cuáles quedan (para supervisión)
- **[Golden Standard repo](https://github.com/lcasarin-maker/VibeCoding_GoldenStandard)** — Fuente normativa externa separada del core de Cerberus
- **[HISTORIAL.md](HISTORIAL.md)** — El registro de todo lo que se ha hecho (auditoría histórica)
- **[scripts/run_security_audit_12d.py](scripts/run_security_audit_12d.py)** — El guardián (aquí está la inteligencia)

---

## Para empezar

1. **Clona este repo** y entra en la carpeta
2. **Ejecuta la auditoría inicial:**
   ```bash
   python scripts/run_security_audit_12d.py .
   ```
3. **Si ves APPROVED**, todo está listo. Si ves REJECTED, lee los mensajes — te dicen exactamente qué arreglar.
4. **Cada vez que hagas cambios**, el sistema los verifica automáticamente (mediante Git hooks).

---

## Preguntas frecuentes

**¿Cerberus bloquea mi trabajo?**
No. Solo bloquea cosas que después van a causar problemas (código incompleto, errores silenciosos, etc.). Es una protección, no una restricción.

**¿Qué pasa si una verificación es muy estricta?**
Se puede documentar como una excepción válida en [REGLAS.md](docs/REGLAS.md), pero con causa clara.

**¿Puedo deshabilitar Cerberus?**
Técnicamente sí, pero no se recomienda. Está diseñado para proteger el proyecto. Si algo no tiene sentido, mejor abre un issue para discutirlo.

---

---

## 🌍 Ecosistema & Compatibilidad

- ✅ Compatible con **MCP** (Model Context Protocol) — el estándar emergente para herramientas de IA
- ✅ Funciona con **LangGraph**, **CrewAI** y otros orquestadores
- ✅ Multi-plataforma: Windows, Linux, macOS
- ✅ Python 3.13+

---

**Última actualización:** 2026-05-31 (Sprints 5-11 finalizados)
**Mantenedor:** Luis Casarin
**Repositorio:** [lcasarin-maker/protocolo-agentes](https://github.com/lcasarin-maker/protocolo-agentes)

