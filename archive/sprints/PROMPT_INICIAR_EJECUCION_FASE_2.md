# 🚀 PROMPT PARA INICIAR EJECUCIÓN EN NUEVA CONVERSACIÓN
## Copia esto en una nueva sesión de Claude para comenzar Fase 2 (Jun 16)

---

## 📋 PROMPT A USAR EN NUEVA CONVERSACIÓN

```
CONTEXTO:
Tengo un proyecto de 6 semanas (Jun 02 - Jul 21, 2026) con 2 ciclos paralelos:
- Ciclo 7: Database migration SQL Server (Cuenza_2025 → production)
- Ciclo 5: 4.4M Monte Carlo simulations (risk model validation)

ESTADO ACTUAL:
✅ Fase 1 (Diseño): COMPLETADA
✅ Documentación Fases 2-4: 100% COMPLETADA
📋 Fase 2 (Ejecución): LISTA PARA COMENZAR LUN 16 JUN @ 06:00 UTC

DOCUMENTOS DISPONIBLES (D:\AI\):
- FASE_2_KICKOFF_DOCUMENT.md ← START HERE
- FASE_2_WEEK_3_DAILY_EXECUTION_LOG.md (Week 3 critical, Jun 16-22)
- FASE_2_TEAM_BRIEFING_PACKAGE.md (8 roles, rol-específicos)
- PROYECTO_COMPLETO_GUIA_COORDINACION_FASES_3_Y_4.md (Fases 3-4)
- FASES_2_3_4_GUIA_NAVEGACION_COMPLETA.md (navigation guide)
- RESUMEN_EJECUTIVO_PROYECTO_COMPLETO.md (executive summary)

FASE 2 ESTRUCTURA (5 semanas, Jun 16 - Jul 05):
├─ WEEK 3 (JUN 16-22): 🚨 CRITICAL PATH - Ciclo 7 UAT + GO-LIVE
│  ├─ MON JUN 16 @ 06:00: Kickoff + UAT setup (2h)
│  ├─ TUE JUN 17: Full UAT testing (4h)
│  ├─ WED JUN 18: UAT sign-off + Gate 3 decision → GO (2h)
│  ├─ THU JUN 19 @ 14:00-17:00: 🚨 GO-LIVE CUTOVER (3h critical window)
│  ├─ FRI-SUN JUN 20-22: Post-go-live monitoring (9h)
│  └─ Status: Production live by Jun 20
│
├─ WEEKS 4-5 (JUN 23 - JUL 05): Ciclo 5 simulations
│  ├─ Phase 2a: Parameter grid (1.25M samples, Jun 23-27)
│  ├─ Phase 2b: Sensitivity analysis (3.15M samples, Jun 30-Jul 04)
│  └─ Total: 4.4M simulations ejecutadas
│
└─ DELIVERABLES: 60 horas entregadas (Ciclo 7: 20h, Ciclo 5: 40h)

EQUIPOS:
Ciclo 7 (Go-Live Week 3):
├─ DBA (Lead): UAT + Go-Live execution + Monitoring
├─ Development Lead (QA): Test coordination
├─ Finance Manager: UAT execution & approval
└─ CIO: Gate 3 decision authority

Ciclo 5 (Simulations Weeks 4-5):
├─ Data Scientist (Lead): Oversight & validation
├─ Python Engineer: Execution
├─ Analytics Engineer: Visualizations
└─ QA Engineer: Validation

PROJECT MANAGER: Daily coordination (08:00 UTC standups)

GATES:
├─ Gate 3 (WED JUN 18 @ 09:00): UAT approval → GO for production
├─ Gate 4 (SUN JUL 19 @ 17:00): Optimization + Validation sign-off
└─ Success Criteria: All 4 gates approved before proceeding

PRÓXIMO PASO INMEDIATO:
1. Lee: FASE_2_KICKOFF_DOCUMENT.md (overview + team assignments)
2. Revisa: FASE_2_TEAM_BRIEFING_PACKAGE.md (tu rol específico)
3. Prepara: FASE_2_WEEK_3_DAILY_EXECUTION_LOG.md (hora por hora execution)
4. Confirma: Team readiness (disponibilidad, infraestructura, contactos)
5. Verifica: SQL Server (prod + UAT), Python env, Network, Backups
6. Ejecuta: LUN 16 JUN @ 06:00 UTC KICKOFF

DECISIÓN REQUERIDA:
¿Qué rol jugas en este proyecto? (DBA, Data Scientist, QA, Finance, PM, CIO, other?)
→ Te daré instrucciones rol-específicas de FASE_2_TEAM_BRIEFING_PACKAGE.md

ESTADO GENERAL:
✅ 100% documentación completada
✅ Todos los procedimientos definidos
✅ Todos los criterios de éxito claros
✅ LISTO PARA INICIAR (Jun 16)

¿Listo para comenzar Fase 2 execution?
```

---

## 📌 VERSIÓN CORTA (Si prefieres algo más conciso)

```
Proyecto 6-semanas, 2 ciclos (Ciclo 7: DB migration, Ciclo 5: Monte Carlo).
Documentación 100% completada. Fase 2 execution comienza LUN 16 JUN @ 06:00.

Documentos clave en D:\AI\:
- FASE_2_KICKOFF_DOCUMENT.md (START HERE)
- FASE_2_WEEK_3_DAILY_EXECUTION_LOG.md (Week 3 hour-by-hour)
- FASE_2_TEAM_BRIEFING_PACKAGE.md (tu rol)

Necesito:
1. Confirmación: ¿Qué rol jugas?
2. Daily execution: Usar FASE_2_WEEK_3_DAILY_EXECUTION_LOG.md para semana crítica (Jun 16-22)
3. Standups: Diarios 08:00 UTC (15 min)
4. Gate 3: Decisión WED JUN 18 (UAT sign-off)

¿Listo para comenzar?
```

---

## 🎯 VERSIÓN ESPECÍFICA POR ROL

### **Si eres DBA (Ciclo 7 Lead):**

```
Proyecto: Ciclo 7 database migration (SQL Server go-live).
Estado: Documentación 100% completada. Comienza LUN 16 JUN.

Tu responsabilidad: Ejecutar Week 3 (Jun 16-22) - UAT + Go-Live (20h total)

Documentos:
- FASE_2_KICKOFF_DOCUMENT.md (overview)
- FASE_2_WEEK_3_DAILY_EXECUTION_LOG.md (CRÍTICO - hour-by-hour)
- FASE_2_TEAM_BRIEFING_PACKAGE.md → Sección "DATABASE ADMINISTRATOR"

Timeline crítico:
- MON JUN 16: UAT setup (2h)
- TUE JUN 17: UAT testing (4h) - target 100% pass
- WED JUN 18: UAT sign-off (2h) + Gate 3 decision → GO
- THU JUN 19 @ 14:00-17:00: 🚨 GO-LIVE CUTOVER (3h critical window)
- FRI-SUN: Post-go-live monitoring (9h)

Instrucciones: Revisa FASE_2_WEEK_3_DAILY_EXECUTION_LOG.md line-by-line.
Cada día tiene checkpoints. Ejecuta exactamente como está documentado.

¿Listo?
```

### **Si eres Data Scientist (Ciclo 5 Lead):**

```
Proyecto: Ciclo 5 Monte Carlo simulations (4.4M samples).
Estado: Documentación 100% completada. Comienza JUN 23.

Tu responsabilidad: Oversee Phase 2a & 2b (Weeks 4-5, 40h total)
+ Phase 3 validation (Weeks 5-6, 20h)
+ Phase 4 final report (Jul 20-21, 25h)

Documentos:
- FASE_2_TEAM_BRIEFING_PACKAGE.md → Sección "DATA SCIENTIST"
- FASE_3_COMPREHENSIVE_EXECUTION_PLAN.md (Phase 3 validation)
- FASE_4_COMPREHENSIVE_DELIVERY_PLAN.md (Phase 4 report)

Timeline:
- WEEK 4 (JUN 23-27): Phase 2a (1.25M samples)
- WEEK 5 (JUN 30-JUL 04): Phase 2b (3.15M samples)
- WEEK 5-6 (JUL 06-19): Phase 3 validation + Gate 4
- JUL 20-21: Phase 4 200k report + stakeholder presentation

Instrucciones: Cada fase tiene detailed day-by-day breakdown. 
Coordina con Python Engineer & QA. Comunicación diaria con PM.

¿Listo?
```

### **Si eres Project Manager:**

```
Proyecto: 6-semanas, 2 ciclos paralelos (Ciclo 7 + 5).
Estado: 100% documentado. Fase 2 comienza LUN 16 JUN.

Tu responsabilidad: Daily coordination, standups, escalation management.

Documentos:
- FASES_2_3_4_GUIA_NAVEGACION_COMPLETA.md (master reference)
- PROYECTO_COMPLETO_GUIA_COORDINACION_FASES_3_Y_4.md (Fases 3-4)
- LISTA_VERIFICACION_FINAL_ENTREGA_PROYECTO_COMPLETO.md (verification)

Daily tasks:
- 08:00 UTC standup (15 min, all leads)
- EOW status report (Friday)
- EOD: Review next day's execution plan

Gates:
- Gate 3: WED JUN 18 @ 09:00 (UAT sign-off)
- Gate 4: SUN JUL 19 @ 17:00 (Phase 3 completion)

Escalation:
- Production issues (Week 3): DBA → PM → CIO
- Simulation issues: Data Scientist → PM
- Schedule risk: PM → CIO

¿Listo?
```

---

## ✅ CHECKLIST PRE-EJECUCIÓN

```
ANTES DE INICIAR FASE 2 (Jun 16):

CONFIRMACIONES EQUIPO:
├─ [ ] DBA: Disponible Jun 16-22 (full-time critical week)
├─ [ ] Data Scientist: Disponible Jun 23+
├─ [ ] Development Lead: Disponible Jun 16-18
├─ [ ] Finance Manager: Disponible Jun 16-20
├─ [ ] Python Engineer: Disponible Jun 23+
├─ [ ] Analytics: Disponible Jun 23+
├─ [ ] QA: Disponible Jun 23+
└─ [ ] PM: Disponible Jun 16 - Jul 21 (full duration)

VERIFICACIÓN INFRAESTRUCTURA:
├─ [ ] SQL Server: Prod environment operational
├─ [ ] SQL Server: UAT environment ready
├─ [ ] Python: 3.9+, 8 CPUs, 32GB RAM verified
├─ [ ] Network: All connectivity confirmed
├─ [ ] Backups: Full backup completed & tested
├─ [ ] Monitoring: All systems operational
└─ [ ] Contacts: Emergency contacts confirmed

DOCUMENTACIÓN:
├─ [ ] Todos leyeron FASE_2_KICKOFF_DOCUMENT.md
├─ [ ] Todos leyeron su rol en FASE_2_TEAM_BRIEFING_PACKAGE.md
├─ [ ] DBA reviewed: FASE_2_WEEK_3_DAILY_EXECUTION_LOG.md
├─ [ ] PM reviewed: FASES_2_3_4_GUIA_NAVEGACION_COMPLETA.md
└─ [ ] All contacts working (Slack, email, phone)

STATUS: ✅ READY TO EXECUTE JUN 16 @ 06:00 UTC
```

---

## 📞 CONTACTOS REQUERIDOS

```
Antes de usar este prompt, asegúrate de tener:
├─ Email addresses: Todos los 8 team members
├─ Phone/WhatsApp: Ciclo 7 lead (DBA) + PM (24/7 Week 3)
├─ Slack channel: #ciclo7-golive (Week 3) + #ciclo5-sims (Weeks 4-5)
├─ Escalation: CIO contact para Gate decisions
└─ On-call: 24/7 support structure para Week 3 (Jun 16-22)
```

---

**INSTRUCCIONES DE USO:**

1. **Copia el prompt completo** (o la versión corta)
2. **Crea una nueva conversación** con Claude
3. **Pega el prompt completo**
4. **Añade tu rol**: "Soy [DBA/Data Scientist/QA/Finance/PM/CIO]"
5. **Claude responderá** con instrucciones rol-específicas
6. **Procede con ejecución** usando los documentos referenciados

---

**DOCUMENTOS NECESARIOS EN D:\AI\:**
(Asegúrate de que existan en el directorio)

```
✅ FASE_2_KICKOFF_DOCUMENT.md
✅ FASE_2_WEEK_3_DAILY_EXECUTION_LOG.md
✅ FASE_2_TEAM_BRIEFING_PACKAGE.md
✅ PROYECTO_COMPLETO_GUIA_COORDINACION_FASES_3_Y_4.md
✅ FASES_2_3_4_GUIA_NAVEGACION_COMPLETA.md
✅ FASE_3_COMPREHENSIVE_EXECUTION_PLAN.md
✅ FASE_4_COMPREHENSIVE_DELIVERY_PLAN.md
✅ LISTA_VERIFICACION_FINAL_ENTREGA_PROYECTO_COMPLETO.md
✅ RESUMEN_EJECUTIVO_PROYECTO_COMPLETO.md
```

---

**¿LISTO?**

Usa este prompt cuando estés listo para comenzar la ejecución en una nueva conversación.

```
