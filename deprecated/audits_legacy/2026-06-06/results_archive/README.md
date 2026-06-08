# Resultados de Auditoría — Directorio limpio

Este directorio está **vacío y listo para una corrida limpia**.

## Estado

- Corrida previa: no debe asumirse como referencia operativa.
- Próxima corrida: depositar resultado aquí con nombre estándar.
- Si se reinicia la auditoría, tratarla como primera ejecución lógica.

## Convención de nombres

```
results/
└── external_repositories_audit.md   ← resultado de corrida activa
```

## Instrucciones para el agente

- **NO consultar corridas anteriores** salvo pedido explícito del usuario.
- Al completar la auditoría, guardar el resultado en este directorio
- El resultado anterior no es fuente de verdad de la siguiente corrida
