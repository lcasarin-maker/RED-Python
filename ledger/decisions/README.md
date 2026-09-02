# `ledger/decisions/`

Decisiones durables, una por archivo, con **el motivo y que descarta cada una**. Lo descartado es
la mitad que se pierde siempre y la que mas se echa de menos despues.

El CUERPO no tiene esquema, y esa abstencion tiene su cero medido: **0 documentos del acervo
cosechado de Atlas definen las secciones internas de un ADR**. Solo hay convencion de nombre
(`NNNN-slug.md`, cuatro digitos). Inventar un esquema para el cuerpo seria inventar.

Lo tipado es el INDICE, `ledger/decisions.jsonl`, que es **generado** por
`gates/index_decisions.py`. Una tabla escrita a mano que resume otros archivos es una segunda
fuente de verdad: en Atlas ya divergio -- 41 archivos contra 1 fila en el SPEC contra 3 narradas.
