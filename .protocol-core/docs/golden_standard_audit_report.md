# Golden Standard Compliance Audit Report
**CoderCerberus V0.02 | Date: 2026-05-28 | Total Audited Items: 281**

This document is generated automatically by `scripts/generate_golden_audit.py` to map every Golden Standard point to its specific mitigation action and validating test in CoderCerberus.

## Summary of Compliance

| Category | Audited Items | Prevented / Remediated | Audited / Not Applicable | Clean Status |
|---|---|---|---|---|
| **Testing & Evaluation** | 114 | 26 | 88 | 100% |
| **Vibe Coding** | 122 | 8 | 114 | 100% |
| **Tokenomics & Context** | 45 | 4 | 41 | 100% |
| **Total** | 281 | 38 | 243 | 100% |

---

## Full Audit Details

### Testing & Evaluation (114 items)

| ID | Flaw Title | Status | Action Taken / Prevention Method | Validating Test / Guard |
|---|---|---|---|---|
| `VT-001` | Hardcoded return | **PREVENTED** | Prevented by D7 (Completeness) and D8 (Test Coverage) in audit_10d.py using AST analysis of function bodies to reject empty stubs or stub docstrings. | `audit_d2_completeness` |
| `VT-002` | Stub permanente | **PREVENTED** | Prevented by D7 (Completeness) and D8 (Test Coverage) in audit_10d.py using AST analysis of function bodies to reject empty stubs or stub docstrings. | `audit_d2_completeness` |
| `VT-003` | Respuesta por dato exacto | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-004` | Copiar esperado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-005` | Assert trivial | **PREVENTED** | Checked by D9 (Test Purity) using AST TestTheaterVisitor to flag assert True, assertTrue(True), assertEqual(x, x), and tests without active asserts. | `audit_d9_test_purity` |
| `VT-006` | Test sin assert | **PREVENTED** | Checked by D9 (Test Purity) using AST TestTheaterVisitor to flag assert True, assertTrue(True), assertEqual(x, x), and tests without active asserts. | `audit_d9_test_purity` |
| `VT-007` | Presencia no corrección | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-008` | Mensaje no resultado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-009` | Tautología | **PREVENTED** | Checked by D9 (Test Purity) using AST TestTheaterVisitor to flag assert True, assertTrue(True), assertEqual(x, x), and tests without active asserts. | `audit_d9_test_purity` |
| `VT-010` | Test de implementación | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-011` | Esperado incorrecto | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-012` | Cobertura sin asserts | **PREVENTED** | Checked by D9 (Test Purity) using AST TestTheaterVisitor to flag assert True, assertTrue(True), assertEqual(x, x), and tests without active asserts. | `audit_d9_test_purity` |
| `VT-013` | Tests por porcentaje | **PREVENTED** | Checked by D9 (Test Purity) using AST TestTheaterVisitor to flag assert True, assertTrue(True), assertEqual(x, x), and tests without active asserts. | `audit_d9_test_purity` |
| `VT-014` | Test circular | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-015` | Test demasiado amplio | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-016` | Aserción textual teatral | **PREVENTED** | Checked by D9 (Test Purity) using AST TestTheaterVisitor to flag assert True, assertTrue(True), assertEqual(x, x), and tests without active asserts. | `audit_d9_test_purity` |
| `VT-017` | Evidencia hardcodeada | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-018` | String matching frágil | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-019` | Hash de error válido | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-020` | Cien por ciento como objetivo | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-021` | Regresión sin centinela | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-022` | Teatralidad del Verde y Aserciones Tautológicas | **PREVENTED** | Checked by D9 (Test Purity) using AST TestTheaterVisitor to flag assert True, assertTrue(True), assertEqual(x, x), and tests without active asserts. | `audit_d9_test_purity` |
| `VT-023` | Mock complaciente | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-024` | Fake incompleto | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-025` | Stub de red | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-026` | Base simplificada | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-027` | Reloj fijo | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-028` | Aleatoriedad controlada | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-029` | Sistema de archivos falso | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-030` | Monkey patch amable | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-031` | Comando stub | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-032` | Mock scan parcial | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-033` | Wrapper como remediación | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-034` | Placeholder aprobado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-035` | xfail permanente | **PREVENTED** | Checked by D9 Test Purity which rejects permanent xfail or skip markers unless annotated with removal criteria or reasons. | `audit_d9_test_purity` |
| `VT-036` | Skip permanente | **PREVENTED** | Checked by D9 Test Purity which rejects permanent xfail or skip markers unless annotated with removal criteria or reasons. | `audit_d9_test_purity` |
| `VT-037` | Condición imposible | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-038` | Dependencia de orden | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-039` | Dependencia temporal | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-040` | Excepción absorbida | **PREVENTED** | Enforced by D5 (Angry Path) AST TryBlockVisitor flagging empty try-except blocks or silent pass/continue statements. | `audit_d5_angry_path` |
| `VT-041` | Error output ignorado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-042` | Log de éxito falso | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-043` | Exit exitoso incondicional | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-044` | Retorno ignorado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-045` | Happy path único | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-046` | Dato mágico | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-047` | Dataset pequeño | **PREVENTED** | Prevented by tests/test_volume_calendar.py containing dataset stress tests and edge date boundaries. | `test_volume_calendar` |
| `VT-048` | No vacío/nulo/cero | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-049` | No caracteres especiales | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-050` | No fechas límite | **PREVENTED** | Prevented by tests/test_volume_calendar.py containing dataset stress tests and edge date boundaries. | `test_volume_calendar` |
| `VT-051` | CI informativo | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-052` | Ignore errors | **PREVENTED** | Enforced by D5 (Angry Path) AST TryBlockVisitor flagging empty try-except blocks or silent pass/continue statements. | `audit_d5_angry_path` |
| `VT-053` | Tests fuera de rama activa | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-054` | Tests opcionales | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-055` | Notificación no atendida | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-056` | Test post-bug complaciente | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-057` | Skip luego | **PREVENTED** | Checked by D9 Test Purity which rejects permanent xfail or skip markers unless annotated with removal criteria or reasons. | `audit_d9_test_purity` |
| `VT-058` | Feature flag divergente | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-059` | Variable altera validación | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-060` | Setup limpia demasiado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-061` | UI por delta | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-062` | Archivo lleno muerto | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-063` | Interfaz documentada falsa | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-064` | Tests rotos invisibles | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-065` | Captura global rota | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-066` | Tests huérfanos | **PREVENTED** | Discovery gaps prevented by rigor_maestro executing full pytest tests/ dynamically, verified in test_infrastructure.py. | `test_infrastructure_checks` |
| `VT-067` | Falso negativo por docstring | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-068` | Backups como deprecated | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-069` | Nombre engañoso | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-070` | Validación de setup ausente | **REMEDIATED** | Checked by setup_validate.py which runs comprehensive pre-flight verification of Python, git hooks, write access, encoding, and the project registry. | `test_setup_validation` |
| `VT-071` | Handoff no reanudable | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-072` | Rollback documental | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-073` | Compatibilidad no evaluada | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-074` | Observabilidad no testeada | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-075` | Discovery Incompleto de Pruebas | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-076` | Dependencia de sistema | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-077` | Timeout engañoso | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-078` | Máquina local única | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-079` | Sandbox no perforado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-080` | Acoplamiento de Dirección Física | **REMEDIATED** | Enforced by D9 absolute path scanners. In code, resolved via dynamic str(Path(__file__).resolve().parent.parent) path bootstrapping. | `audit_d9_test_purity` |
| `VT-081` | Autor prueba su implementación | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-082` | Review sin tests | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-083` | Expected codificado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-084` | Approval hardcodeado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-085` | Golden file complaciente | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-086` | Expected failure normalizado | **PREVENTED** | Checked by D9 Test Purity which rejects permanent xfail or skip markers unless annotated with removal criteria or reasons. | `audit_d9_test_purity` |
| `VT-087` | Warning tolerado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-088` | Tolerancia de errores | **PREVENTED** | Enforced by D5 (Angry Path) AST TryBlockVisitor flagging empty try-except blocks or silent pass/continue statements. | `audit_d5_angry_path` |
| `VT-089` | Wrapper de conveniencia | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-090` | Placeholder testeado | **PREVENTED** | Prevented by D7 (Completeness) and D8 (Test Coverage) in audit_10d.py using AST analysis of function bodies to reject empty stubs or stub docstrings. | `audit_d2_completeness` |
| `VT-091` | Dominio documentado no implementado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-092` | Sección como cumplimiento | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-093` | Docstrings como calidad | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-094` | Manejo por palabra clave | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-095` | Tests del protocolo, no del sujeto | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-096` | Evidencia obsoleta | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-097` | Chaos teatral | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-098` | Reporte passed mentiroso | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-099` | Versión zombi | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-100` | Permisos no adversariales | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-101` | Ruteo no validado | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-102` | Approved list codificada | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-103` | Expected codificado en evaluador | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-104` | Warnings fuera del score | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-105` | Sin test de existencia de hooks | **REMEDIATED** | Validated by tests/test_infrastructure.py:test_pre_commit_hook_exists_and_executable, ensuring hooks are physically present and active. | `test_pre_commit_hook_exists_and_executable` |
| `VT-106` | Exclusión no revalidada | **REMEDIATED** | Checked by setup_validate.py which runs comprehensive pre-flight verification of Python, git hooks, write access, encoding, and the project registry. | `test_setup_validation` |
| `VT-107` | Stack incompleto silencioso | **REMEDIATED** | Checked by setup_validate.py which runs comprehensive pre-flight verification of Python, git hooks, write access, encoding, and the project registry. | `test_setup_validation` |
| `VT-108` | Nombre desconectado del dominio | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-109` | Teatro de Frameworks e Intermediarios Redundantes (Testing Bridge Theater) | **PREVENTED** | Testing Bridge Theater is bypassed; static audits and tests run as direct shell pipelines returning native exit codes. | `test_infrastructure_checks` |
| `VT-110` | Fragmentación de Directorios Ocultos (Dot-Directory Fragmentation) | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-111` | Deferred Without Registration (Diferido Sin Registro) | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-112` | Deriva de Dependencia Fantasma (Ghost Dependency Drift) | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-113` | Ausencia de Falsabilidad Mutacional (Lack of Test Mutation Validation) | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |
| `VT-114` | Deriva de Sincronización Multirepositorio (Multi-Repository Sync Drift) | **AUDITED** | Audited by DeepForensicAuditor D8 and D9 behavioral and static test validations. | `audit_d8_test_coverage` |

### Vibe Coding (122 items)

| ID | Flaw Title | Status | Action Taken / Prevention Method | Validating Test / Guard |
|---|---|---|---|---|
| `VC-001` | Incompetencia no asumida | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-002` | Complacencia generativa | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-003` | Triunfalismo sin prueba | **PREVENTED** | Mitigated by EvidenceLogger recording structured, physical JSON logs to .protocol/evidence/ to capture actual test execution outcomes. | `test_evidence_logger` |
| `VC-004` | Demo como calidad | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-005` | Prototipo convertido en deuda | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-006` | Estética como integridad | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-007` | Auditoría no humana del core | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-008` | Optimismo operativo | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-009` | Autoauditoría contaminada | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-010` | Fallo no convertido en doctrina | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-011` | Human test falso | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-012` | Se ve bien como métrica | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-013` | Calificación máxima gratuita | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-014` | Falso positivo de auditoría | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-015` | Agente como ingeniero autónomo | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-016` | Código incomprensible | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-017` | Triunfalismo Conversacional Estocástico | **PREVENTED** | Mitigated by EvidenceLogger recording structured, physical JSON logs to .protocol/evidence/ to capture actual test execution outcomes. | `test_evidence_logger` |
| `VC-018` | Fix ciego | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-019` | Síntoma parcheado | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-020` | Bug no reproducido | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-021` | Cierre prematuro | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-022` | Velocidad sobre precisión | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-023` | Productividad ilusoria | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-024` | Construcción sin validación | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-025` | Especificación vaga | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-026` | Suposiciones excesivas | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-027` | Plan no externalizado | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-028` | Paso sin validación | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-029` | Alcance no quirúrgico | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-030` | State drift | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-031` | Reescritura completa | **PREVENTED** | Surgical edit tools (replace_file_content) are used to prevent complete file rewrites and state drift. | `test_cerberus_core` |
| `VC-032` | Sidequest | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-033` | Presión de cierre | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-034` | Decisiones sin porqué | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-035` | Aclaraciones perdidas | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-036` | Sin dry run | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-037` | Regeneración ciega | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-038` | Victoria prematura | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-039` | Deuda invisible | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-040` | Mantenibilidad no auditada | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-041` | Deriva operativa | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-042` | Loops de corrección | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-043` | Parches sobre parches | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-044` | Producción sin dueño técnico | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-045` | Handoff ambiguo | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-046` | Rescate pre-deprecación omitido | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-047` | Estado no vinculante | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-048` | Memoria monolítica | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-049` | Audiencias mezcladas | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-050` | Actualización no dirigida | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-051` | Saturación contextual | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-052` | Context rot | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-053` | Sin checkpoint previo | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-054` | Estado descentralizado | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-055` | Concurrencia sin cuarentena | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-056` | Integración alucinada | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-057` | Paridad de versión rota | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-058` | Deadlock sin latido | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-059` | Ruteo opaco | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-060` | Merge textual de memoria | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-061` | Stub como arquitectura | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-062` | Deriva de Concurrencia de Estado (Dual-Session Drift) | **PREVENTED** | Mitigated by FASE I Startup checks, pre-commit hooks, and mandatory STATUS.md next steps to align state. | `test_behavioral_compliance` |
| `VC-063` | Documentación mentirosa | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-064` | Caja negra arquitectónica | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-065` | Esquema tardío | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-066` | Ceguera espacial | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-067` | Políticas implícitas | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-068` | Conflictos normativos | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-069` | Dependencias no mapeadas | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-070` | Manipulación shell ciega | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-071` | Módulo sin biocontainment | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-072` | Blind chunking | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-073` | Código crítico troceado | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-074` | I/O sin validación | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-075` | Integraciones no verificadas | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-076` | Tipado laxo | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-077` | Ambigüedad semántica de tipo | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-078` | Placeholder permanente | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-079` | Core dependiente de inestables | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-080` | Copy-paste acrítico | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-081` | Secuestro documental | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-082` | Dependencias sin gate | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-083` | Archivo zombie tolerado | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-084` | Compatibilidad regresiva ignorada | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-085` | Observabilidad ornamental | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-086` | Wrapper evasivo | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-087` | Warning normalizado | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-088` | Error tolerado por política | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-089` | Reconocimiento omitido | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-090` | Memoria no cargada | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-091` | Archivo no encontrado perezoso | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-092` | Auditoría parcial llamada total | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-093` | Seguridad optimista | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-094` | Seguridad mezclada | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-095` | Acceso directo a producción | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-096` | Código sin tests | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-097` | Tests tardíos | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-098` | Happy path exclusivo | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-099` | Sin caos | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-100` | No funcional ignorado | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-101` | Config optimista | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-102` | Debug pobre | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-103` | UI sin uso real | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-104` | Infraestructura ignorada | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-105` | Omisión de componentes | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-106` | Setup fantasma | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-107` | Matriz de permisos implícita | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-108` | Frontera de seguridad por convención | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-109` | Ruta literal ambiental | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-110` | Cuota como sorpresa | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-111` | Exclusión sin auditoría previa | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-112` | Propagación sin verificación de adopción | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-113` | Nomenclatura congelada | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-114` | Hallazgo sin plan de remediación | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-115` | Ejecución dinámica de expresiones externas | **REMEDIATED** | Replaced eval-based rules with a pre-registered SAFE_CHECKS dispatch table in rules_engine.py to prevent remote code execution. | `test_rule_security` |
| `VC-116` | Instalación automática de dependencias no verificadas | **REMEDIATED** | Disabled automatic subprocess pip installs in auto_repair.py, forcing manual package guidance. | `test_auto_repair_no_pip` |
| `VC-117` | Escritura destructiva no atómica de estado crítico | **REMEDIATED** | Implemented transactional atomic writing using tempfile + Path.replace() in close_pending.py. | `test_atomic_write` |
| `VC-118` | Teatro de Compatibilidad Zombie | **PREVENTED** | Prevented by D1 _audit_d1_zombie_compat scanning active scripts for zombie compatibility shim patterns. | `audit_d1_integrity` |
| `VC-119` | Pánico de Bloqueo y Parcheo Sintáctico Rápido (Lock Panic Shortcut) | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-120` | Reasoning Lock-In & AI Runaway loops (Chain-Pattern Interrupts) | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-121` | Redundancias Críticas y Patrones Repetitivos de AI Slop | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |
| `VC-122` | Contaminación de Cadena de Suministro por Ejecuciones Silenciosas | **AUDITED** | Enforced by CoderCerberus 4-Phase operating loop, preflight compliance, and git pre-commit hooks. | `test_behavioral_compliance` |

### Tokenomics & Context (45 items)

| ID | Flaw Title | Status | Action Taken / Prevention Method | Validating Test / Guard |
|---|---|---|---|---|
| `TK-001` | Checkpoint ausente | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-002` | Memoria de chat como fuente principal | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-003` | Cambio de proyecto sin cierre | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-004` | Setup reexplicado | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-005` | Handoff prose-heavy | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-006` | Merge manual de historial | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-007` | Fuente de verdad duplicada | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-008` | Segregación Epistemológica de la Memoria | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-009` | Poda semántica | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-010` | Recuperación contextual | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-011` | Delimitadores estructurados | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-012` | Exploration tax | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-013` | Tool schemas inflados | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-014` | Lectura completa por defecto | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-015` | Archivo completo para duda puntual | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-016` | Prompt gigante multiobjetivo | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-017` | Permisos narrados | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-018` | Backlog mezclado con objetivo | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-019` | Esqueleto Jerárquico de Dependencias | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-020` | Restricción de salida | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-021` | Prefilling | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-022` | Optimización de ejemplos | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-023` | Logs crudos | **REMEDIATED** | D10 enforces that all major background loop and orchestrator scripts import and wrap execution inside OutputCompressor. | `audit_d10_tokenomics` |
| `TK-024` | Resumen sin densidad | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-025` | Salida de auditoría verbosa | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-026` | Observabilidad ruidosa | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-027` | Compresión Léxica de Diagnósticos | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-028` | Caching de contexto estable | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-029` | Procesamiento batch | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-030` | Cascada de capacidades | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-031` | Compactación de contexto | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-032` | Cache cliff | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-033` | Sin headroom | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-034` | Costo de reversión invisible | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-035` | Pensar con herramienta de ejecución | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-036` | Respuesta sin modo | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-037` | Monitoreo manual olvidable | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-038` | Relectura de estado completo | **REMEDIATED** | D10 manifest size gate validates that AGENT.md <= 150 lines, STATUS.md <= 200 lines, and SPEC.md <= 500 lines. | `audit_d10_tokenomics` |
| `TK-039` | Herramientas externas no integradas | **REMEDIATED** | D10 check extracts and verifies that all python scripts referenced in TOKEN_BUDGET.md or AGENT.md exist on disk. | `audit_d10_tokenomics` |
| `TK-040` | Ahorro prometido no medido | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-041` | Cuotas invisibles | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-042` | Manifiestos sin restricción de tamaño | **REMEDIATED** | D10 manifest size gate validates that AGENT.md <= 150 lines, STATUS.md <= 200 lines, and SPEC.md <= 500 lines. | `audit_d10_tokenomics` |
| `TK-F01` | Reprocesamiento de contexto estable | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-F02` | Poda contextual primitiva | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |
| `TK-F03` | Salida verbal excesiva | **AUDITED** | Monitored by the token_tracker and token_manager modules to track and compress context size. | `test_d10_tokenomics` |

## Project Insights

These entries are preserved as project-agnostic knowledge extracted from external references and now consumed by Cerberus.

| ID | Insight |
|---|---|
| `PI-001` | Deptry – reconciliación de imports contra dependencias declaradas para detectar faltantes, no usadas, transitivas, dev mal ubicadas y stdlib declaradas como dependencias. |
| `PI-002` | pytest-good-assertions – densidad diagnóstica de aserciones y fallos: cuando un test falla, el mensaje debe explicar la discrepancia con claridad accionable. |
| `PI-003` | Tokencost – metering previo de tokens y conversión a USD para hacer visible el gasto antes de ejecutar una llamada LLM. |
| `PI-004` | Trivy – escaneo multi-superficie (imágenes, filesystem, git, VMs, Kubernetes) para CVEs, secretos, misconfiguraciones, SBOM y licencias. |
| `PI-005` | Litellm – gateway agnóstico de proveedor con routing, fallback, cost tracking, guardrails, logging y load balancing. |
| `PI-006` | Cerberus – compuerta entre intención y ejecución que impone disciplina de contexto, observabilidad, redacción y control de estado. |

## Project Insight Recommendations by Domain

These actions are the operational bridge between the project insights and the Cerberus audit domains.

| Domain | Insight | Project | Action |
|---|---|---|---|
| `D1` | `PI-001` | deptry | Compare imports against declared dependencies and fail on missing, unused, transitive or misplaced packages. |
| `D1` | `PI-004` | trivy | Scan repos, images and filesystems for secrets, CVEs, misconfigurations and SBOM gaps before release. |
| `D10` | `PI-003` | tokencost | Measure prompt and completion cost before calling LLMs so token usage is visible and budgetable. |
| `D10` | `PI-005` | litellm | Use provider routing and cost tracking together to pick the cheapest viable model path. |
| `D10` | `PI-006` | cerberus | Preserve compact state, checkpoints and summaries to keep context budgets under control. |
| `D2` | `PI-001` | deptry | Treat missing or stale dependency declarations as completeness debt and block delivery until reconciled. |
| `D2` | `PI-006` | cerberus | Keep the operational contract complete by storing state, evidence and checkpoints outside the chat. |
| `D3` | `PI-002` | pytest-good-assertions | Require failure messages that explain the mismatch clearly enough to debug without guesswork. |
| `D3` | `PI-006` | cerberus | Use explicit state and evidence fields so the system tells a clear causal story instead of relying on memory. |
| `D4` | `PI-005` | litellm | Centralize provider routing and fallbacks so the code does not grow provider-specific branching spaghetti. |
| `D5` | `PI-006` | cerberus | Turn failure handling into a structured protocol with next steps, evidence and a visible recovery path. |
| `D5` | `PI-002` | pytest-good-assertions | Make failing assertions explain what to do next so the angry path is actionable, not noisy. |
| `D6` | `PI-006` | cerberus | Enforce clean boundaries, compact state and explicit handoffs to avoid slop and context drift. |
| `D7` | `PI-004` | trivy | Use security scanning as a mandatory gate for secrets, vulnerabilities and IaC misconfigurations. |
| `D8` | `PI-002` | pytest-good-assertions | Keep tests high-signal: assertions should discriminate behavior, not merely confirm presence. |
| `D8` | `PI-001` | deptry | Prevent dependency drift from destabilizing the test suite by validating imports before running coverage gates. |
| `D9` | `PI-002` | pytest-good-assertions | Preserve assertion quality so tests fail with precise, inspectable output instead of theater. |
