# `ledger/entries/`

Una ficha por archivo: frontmatter tipado + prosa que **ningun gate lee**. Aqui vive TODO el
estado del repo -- deuda, bugs, riesgos y tareas son la misma entidad con un campo `kind`.

**Dos reglas que esta carpeta existe para hacer cumplir, las dos con su medicion:**

1. **El `status` lo declara el CAMPO, nunca la ruta.** Medido en la flota: **605 desacuerdos de
   2,742** entre carpeta y campo -- RePic tiene 33 fichas en `backlog/` que dicen
   `status: closed`. Un contador que deduce el estado de la ruta da un cero tranquilizador en un
   repo lleno de deuda viva.
2. **El `id` se compara por IGUALDAD, jamas normalizado ni validado por forma.** Medido: de los
   182 ids reales de `tasks/done/` de Atlas, **177 fallaban** un patron de forma. Normalizarlos
   rompe la deduplicacion entre arboles y las citas desde codigo, tests y dictamenes.

Contrato completo: `Atlas/docs/LEDGER_CONTRACT.md`.
