# 🛡️ Coder Cerberus V0.1 — Inmunidad Total contra Vibe-Coding

[![Version](https://img.shields.io/badge/version-v0.02-blueviolet.svg?style=flat-square)](VERSION.txt)
[![Build](https://img.shields.io/badge/audit--10d-APPROVED-success.svg?style=flat-square)](scripts/audit_10d.py)
[![Tests](https://img.shields.io/badge/tests-333%20PASSED-success.svg?style=flat-square)](#)
[![OS](https://img.shields.io/badge/OS-Windows--CrossPlatform-blue.svg?style=flat-square)](#)
[![Python](https://img.shields.io/badge/python-3.13+-yellow.svg?style=flat-square)](#)

> **Coder Cerberus** es un marco de desarrollo defensivo y un motor de auditoría de confianza cero diseñado para erradicar fallos silenciosos, stubs y malas prácticas de agentes de IA (como Claude y Gemini) en tiempo real. Actúa como un guardián de pre-commit inmutable que valida y sincroniza el protocolo operacional en toda la Fortaleza del programador.

---

## 🧭 ¿Qué es Coder Cerberus?

Cuando se trabaja con agentes de codificación autónomos, es común sufrir el fenómeno del *"Vibe Coding"*: la IA genera stubs vacíos, implementa bloques `try-catch` silenciosos que ocultan errores, introduce complejidad spaghetti con operadores lógicos excesivos, o altera estados críticos sin sincronizar.

**Cerberus destruye este problema de raíz.** Establece una contención física y lógica estricta a través de un analizador forense multidimensional y Git Hooks inmutables que aseguran que el código de la Fortaleza de desarrollo cumpla con el estándar de calidad absoluta.

---

## 🎨 Los 10 Dominios de Auditoría (Forense 10D)

El guardián `audit_10d.py` de Cerberus analiza estáticamente todos los recursos del core y de los sub-proyectos basándose en **10 pilares rigurosos**:

| Dominio | Métrica de Rigor | Acción del Guardián |
| :--- | :--- | :--- |
| **D1: Integridad** | Whitelist Forense estricta | Bloquea y elimina archivos "Zombi" no declarados en `SPEC.md`. |
| **D2: Completitud** | Cero stubs y marcas pendientes | Erradica placeholders vacíos (`pass`, `...`, `NotImplementedError`, y stubs de JS). |
| **D3: Claridad** | AST Call Graph & Conectividad | Detecta código muerto (funciones huérfanas) y exige documentación en el docstring de los archivos. |
| **D4: Anti-Spaghetti** | Lógica y complejidad ciclomática | Bloquea líneas con complejidad ciclomática excesiva o densidad descontrolada de operadores lógicos. |
| **D5: Angry Path** | Resiliencia y manejo de errores | Fuerza a que cada `try-except` contenga obligatoriamente 4 elementos: LOG, USUARIO, ESTADO y ACCIÓN. |
| **D6: Anti-Slop** | Higiene y estándares modernos | Prohíbe tipados débiles (`any`/`Any`), declaraciones obsoletas (`var`) y malas prácticas estilísticas. |
| **D7: Seguridad de Datos** | Blindaje y auditoría estática | Detecta credenciales expuestas, uso de comandos destructivos (`git reset --hard`) y prohíbe inyecciones o `eval()` inseguros. |
| **D8: Test Coverage** | Validación de regresión | Garantiza la presencia de suite de tests y bloquea la entrega si hay fallos o regresiones. |
| **D9: Test Purity** | Pureza estructural de pruebas | Prohíbe aserciones de teatro (`assert True`), mocks no válidos, feature flags en tests y rutas absolutas en el código. |
| **D10: Tokenomics** | Eficiencia y límites del contexto | Controla el tamaño de manifiestos clave (`AGENT.md`, `STATUS.md`, `SPEC.md`) y asegura la compresión y optimización de tokens. |

---

## 🏁 Dynamic Golden Standard Compliance

Cerberus cuenta con una base de datos inmutable de **278 vicios de vibe coding, testing y tokenomics** extraída directamente de las tres bibliotecas de la Golden Standard.

Nuestra suite de tests dinámicos (`tests/test_golden_standard_compliance.py`) analiza reflectivamente el repositorio para asegurar:
1. **0% Gaps**: Cada vicio se mapea a una mitigación real en `.protocol/metadata/golden_standard_audit.json`.
2. **Pruebas Físicas**: Cada mapeo apunta a un test pytest o un guardián estático que existe físicamente en el código y previene regresiones.

---

## 📦 Arquitectura de la Fortaleza

El ecosistema Cerberus está compuesto por:
1. **Módulo de Autoridad (`SPEC.md` & `AGENT.md`)**: El cerebro del sistema que define los archivos permitidos, metas y reglas de confinamiento.
2. **Scripts Core (El Músculo)**:
   * [`scripts/audit_10d.py`](scripts/audit_10d.py): El auditor forense automatizado multi-lenguaje de 10 dominios.
   * [`scripts/rigor_maestro.py`](scripts/rigor_maestro.py): El orquestador que ejecuta la suite de resiliencia y el Chaos Monkey.
   * [`scripts/sync_binding.py`](scripts/sync_binding.py): El unificador central que propaga checksums, versionamiento y archivos de protocolo a los 16 proyectos satélites.
3. **Git Hooks de Contención**: Bloquean cualquier intento de `git commit` o `git push` si no se aprueba el estándar al 100%.
4. **Mapa funcional vivo**: [`docs/MAPA_FUNCIONAL_CERBERUS.md`](docs/MAPA_FUNCIONAL_CERBERUS.md) explica como se conectan la autoridad, la ejecucion, la sincronizacion y la memoria operativa.

---

## 🚀 Guía de Instalación Rápida (Para tus Proyectos)

Para blindar un proyecto con el estándar Cerberus y forzar a que las IAs ejecuten la suite de rigor antes de hacer commits locales:

### 1. Clonar e Inicializar
```bash
git clone https://github.com/lcasarin-maker/protocolo-agentes.git
cd CoderCerberus
```

### 2. Proteger un Proyecto
Copia los recursos del protocolo y del gatekeeper a la raíz del proyecto destino:

```bash
# Copiar manifiestos y directivas de seguridad
cp AGENT.md PROTOCOL_SYSTEM.md PROTOCOL_BEHAVIOR.md SPEC.md /ruta/a/tu/proyecto/
cp -r .claude/ /ruta/a/tu/proyecto/

# Copiar scripts core de validación
cp -r scripts/ /ruta/a/tu/proyecto/
```

### 3. Activar los Git Hooks
```bash
# Copiar e instalar el Hook de Pre-commit
cp scripts/hooks/pre-commit /ruta/a/tu/proyecto/.git/hooks/pre-commit
chmod +x /ruta/a/tu/proyecto/.git/hooks/pre-commit
```

---

## 🛠️ Comandos de Uso Frecuente

### Ejecutar Auditoría Local (10 Dominios)
```powershell
python scripts/audit_10d.py
```

### Ejecutar Suite Completa (Rigor Maestro)
```powershell
python scripts/rigor_maestro.py
```

### Sincronización y Propagación del Protocolo
Sincroniza y propaga checksums y actualizaciones a todos los repositorios registrados en la Fortaleza:
```powershell
python scripts/sync_binding.py --sync
```

### Consultar Conocimiento del Golden Standard
Muestra el resumen de la base de conocimiento y los `PI-*` integrados:
```powershell
python scripts/protocol_cli.py knowledge
```

### Versionado Semántico y Propagación
Incrementa de forma segura la versión del proyecto y propaga dinámicamente el cambio a todos los manifiestos, hooks y estados para evitar desincronizaciones (evitando el drift S17/B26):
```powershell
# Incrementa parche (ej. 1.2.3 -> 1.2.4)
python scripts/bump_version.py patch

# Incrementa versión menor (ej. 0.02 -> 0.3)
python scripts/bump_version.py minor

# Crea un tag de git y lo sube al repositorio remoto
python scripts/bump_version.py patch --tag
```

---

## 💎 Filosofía Operativa
1. **Cerebro-Músculo**: `SPEC.md` dicta la realidad; los hooks automáticos ejecutan la validación técnica.
2. **Angry Path Dominance**: Asumimos que el flujo principal de ejecución es el fallo; el éxito es simplemente el residuo de un error no encontrado.
3. **Invariancia**: La seguridad y la robustez son prioritarias y nunca se relajan para acelerar la entrega.
