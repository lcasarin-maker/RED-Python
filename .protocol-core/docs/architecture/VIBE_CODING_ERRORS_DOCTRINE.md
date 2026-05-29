# Protocolo Consolidado de Riesgos y Controles para Vibe Coding

---

# I. Doctrina Base y Modelo Mental

## 1. Desconfianza Fundamental hacia la IA

1. Asumir Incompetencia Inherente
   Todo código generado por IA debe tratarse como patrones sin razonamiento real.

2. Mentalidad del “Pasante Incompetente”
   La IA es un operador sobreconfiado que tenderá a complacer, alucinar y ocultar incertidumbre.

3. Auditoría Anti-Slop / Anti-Gaslighting
   Nunca aceptar afirmaciones de éxito sin validación empírica.

4. Asumir que “Funciona” es una Trampa
   Un demo funcional no implica calidad arquitectónica.

5. Trampa del “Solo es un Prototipo”
   Los prototipos improvisados se convierten en deuda técnica permanente.

6. Escepticismo Superficial
   Una UI bonita no prueba integridad lógica.

7. Asumir que la Documentación Miente
   README, comentarios y markdown pueden estar desactualizados.
   La fuente de verdad es:

   * código ejecutándose
   * comportamiento real
   * configuración efectiva
   * logs y tests

---

## 2. Primacía del Entendimiento Humano

8. Auditoría Manual Obligatoria
   La arquitectura core y lógica crítica requieren revisión humana.

9. Auditoría Línea por Línea Obligatoria
   Si el humano no leyó el código, está acumulando deuda técnica.

10. Prohibición de Caja Negra
    Toda decisión arquitectónica debe explicarse.

11. Razón Forzada
    Prohibido pegar errores y aplicar fixes ciegamente.

12. Verificación de Causa Raíz
    Prohibido parchear síntomas.

13. Reproducir antes de Remediar
    Todo bug requiere caso reproducible antes de modificar código.

14. Finalización en Cadena
    Una tarea no termina si reveló fallos secundarios.

---

## 3. Calidad sobre Velocidad

15. Priorizar Precisión sobre Velocidad

16. Escepticismo Gerencial
    El “10x productivity” oculta costos de debugging y refactorización.

17. Validar Temprano, Construir Poco
    Primero validar mínima funcionalidad real.

18. Política de Pesimismo Operativo
    Asumir siempre degradación, regresiones y errores ocultos.

---

## 4. Disciplina de Prompting y Especificación

19. CICO Estricto
    Specs imprecisos producen software riesgoso.

20. Definir Esquema antes que Lógica
    Primero entidades y relaciones.

21. Regla de Ceguera Espacial (UI)
    La estructura visual debe declararse explícitamente antes de implementar.

22. Extracción de Políticas Obligatoria
    El agente debe listar las reglas arquitectónicas aplicadas antes de modificar código.

23. Resolución de Conflictos First-Class
    El agente debe detectar contradicciones entre reglas globales y locales.

24. Política de Detención por Ambigüedad
    Si se requieren más de dos suposiciones no verificadas, detenerse.

---

# II. Arquitectura, Reconocimiento y Planeación

## 1. Reconocimiento Obligatorio

25. Fase de Reconocimiento Mandataria
    Prohibido modificar código antes de entender el repositorio.

26. Lectura Inicial Forzosa
    El agente debe cargar memoria y contexto antes de actuar.

27. Context Collapse Check
    Antes de refactorizar, generar mapa de dependencias.

28. “Archivo no encontrado” es fallo de esfuerzo
    Agotar búsqueda estructural antes de concluir inexistencia.

29. Auditoría Completa Significa Auditoría Completa
    Si se solicita auditoría total:

* incluye frontend
* HTML
* scripts de arranque
* build
* infraestructura
* rutas críticas
* UX real

---

## 2. Planeación y Control

30. Externalización de Planes
    Todo trabajo debe existir en PLAN.md o equivalente.

31. Validación de Paso
    Cada etapa debe demostrar éxito antes de continuar.

32. Enforcement de Estado Vinculante
    MEMORY.md y estados declarados deben coincidir con el sistema real.

33. Autoauditoría con Reset de Memoria
    Validar estado final desde contexto fresco.

34. Evolución Metacognitiva
    Cada fallo debe convertirse en doctrina permanente.

---

## 3. Control de Alcance

35. Límite Quirúrgico de Alcance
    Cambios pequeños y testeables.

36. Prevención de State Drift
    Ediciones grandes degradan coherencia global.

37. Prohibición de Reescrituras Completas
    Solo diffs quirúrgicos.

38. No Salirse del Plan
    Prohibido introducir desviaciones no solicitadas.

39. No Corretear al Usuario
    No presionar cierre prematuro de tareas.

---

# III. Gestión de Contexto y Memoria

40. Arquitectura de Memoria Estricta
    Separar:

* núcleo estable
* contexto activo
* patrones del sistema
* historial de decisiones

41. Separación de Audiencias
    Memoria IA ≠ documentación humana.

42. Actualización Dirigida por Eventos

43. Gestión de Saturación / Hard Reset

44. Mitigación de Context Rot

45. Anticipar Decaimiento de Contexto

46. Registro del “Por Qué”

47. Log de Aclaraciones Históricas

---

# IV. Disciplina Operativa y Control de Cambios

## 1. Seguridad Operativa

48. Commit Antes del Prompt

49. Dry Runs Obligatorios

50. Prohibición de Manipulación vía Bash
    No usar hacks de shell cuando existen herramientas estructuradas.

---

## 2. Corrección de Bugs

51. Prohibición de Regeneración Ciega

52. Reproducir → Diagnosticar → Corregir → Verificar

53. Nunca Declarar Victoria Prematuramente

54. Prohibido Reportar Auditoría 100% sin Verificación Real

55. Toda afirmación requiere evidencia:

* tests
* logs
* screenshots
* ejecución real

---

# V. Estado, Modularidad y Concurrencia

56. Estado Descentralizado Prohibido

57. Cuarentena de Concurrencia

58. Aislamiento Modular / Biocontainment

59. Blind Chunking Prohibido
    El chunking debe respetar:

* límites semánticos
* instrucciones delimitadas
* integridad funcional
* dependencias estructurales

60. Nunca Trocear Código Crítico sin Modelo Estructural

---

# VI. Integridad de Datos y Tipado

61. Validación Estricta en Fronteras I/O

62. Validación Obligatoria de APIs y BD

63. Restricción de Tipado Estricto

64. Prohibición de Any

65. Cero Dependencia de Placeholders

---

# VII. Seguridad

66. Desconfianza de Seguridad Mandataria

67. Aislamiento de la Capa de Seguridad

68. Dependencias Estables para el Core

69. Prohibición de Acceso Directo a Producción

---

# VIII. Testing, Validación y Auditoría

## 1. Testing Obligatorio

70. Sin Tests No Hay Código

71. Test-First o Test-Simultaneous

72. Forzar Happy Path y Unhappy Path

73. Chaos Monkey Obligatorio

74. Auditoría de Requisitos No Funcionales

75. Validación Pesimista de Configuración

76. Infraestructura de Depuración Extrema

---

## 2. Human Testing Real

77. Human Test Real Obligatorio
    No basta linting ni compilación.

78. Tests de Usabilidad deben:

* abrir navegador real
* ejecutar flujo real
* interactuar con UI
* validar comportamiento observable

79. “Se ve bien” no equivale a “funciona”

80. Veredicto de Calidad requiere:

* uso real
* navegación real
* interacción real
* inspección de errores reales

81. Prohibido asignar calificaciones máximas sin validación empírica humana.

---

# IX. Reutilización, Deuda Técnica y Mantenibilidad

82. Auditoría Anti Copy-Paste

83. Impuesto de Deuda Técnica

84. Maintainability Audit

85. Secuestro de Documentación
    Código y documentación deben evolucionar juntos.

---

# X. Dependencias, APIs y Fuente de Verdad

86. Verificación de Integraciones Hallucinadas

87. Gatekeeping de Dependencias

88. La Infraestructura Real es la Fuente de Verdad

---

# XI. Fallos Críticos Observados y Contramedidas

## 1. Falsos Positivos de Auditoría

Problema observado:

* Se declaró éxito total con sistema roto o vacío.

Contramedidas:

* Human testing obligatorio.
* Validación funcional real.
* Evidencia obligatoria.
* Prohibición de veredictos triunfalistas sin ejecución verificable.

---

## 2. Blind Chunking Destructivo

Problema observado:

* Segmentación automática rompió integridad funcional.

Contramedidas:

* Chunking semántico.
* Preservación de fronteras funcionales.
* Validación estructural posterior.
* Tests de regresión obligatorios.

---

