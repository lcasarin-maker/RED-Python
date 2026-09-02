# `ledger/evidence/<ID>/`

Salidas LITERALES de las corridas que cierran una ficha. Tres archivos por ficha cerrada:

    pass.txt   el `close_check` produciendo el veredicto que `expect` declara
    fail.txt   el MISMO comando produciendo el veredicto CONTRARIO
    e2e.txt    el gate end-to-end del repo

**El de FALLO es el que suele faltar, y es el unico que da sentido a los otros dos.** Sin el, la
comprobacion no ha demostrado que pueda salir negativa, y una verificacion que no puede salir
negativa no es una verificacion. Medido en la flota el 2026-09-01: de 2,104 fichas cerradas,
**32 (1.5%)** nombraban un control negativo y mostraban ambos codigos de salida.

Nadie escribe aqui a mano: lo escriben los gates al cerrar.
