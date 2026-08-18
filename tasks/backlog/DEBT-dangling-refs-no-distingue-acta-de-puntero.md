---
id: DEBT-dangling-refs-no-distingue-acta-de-puntero
title: dangling_refs/file_refs bloquea el acta que registra un borrado, no sólo el puntero a lo borrado
status: backlog
created: 2026-08-17
---

## Finding

Al pagar [[DEBT-zero-debt-hardcoded-path-validate-satellite]] (borrar
`deprecated/bootstrap_v0.5/`), el hook pre-commit bloqueó el commit con 3 FAIL
de `dangling_refs`, detector `file_refs`:

```
[dangling_refs] 3 findings (3 FAIL, 0 WARN)
  [FAIL] (file_refs) deprecated/bootstrap_v0.5/record_validation_debt_historical.py -- deleted file ... still referenced by name (in tasks/backlog/DEBT-zero-debt-hardcoded-path-validate-satellite.md)
  [FAIL] (file_refs) deprecated/bootstrap_v0.5/validate_satellite_functional.py -- deleted file ... still referenced by name (in tasks/backlog/DEBT-zero-debt-hardcoded-path-validate-satellite.md)
  [FAIL] (file_refs) docs/VALIDATION_DEBT_SYSTEM.md -- deleted file ... still referenced by name (in tasks/backlog/DEBT-zero-debt-hardcoded-path-validate-satellite.md)
rc=1
```

Los 3 hallazgos apuntan al **acta de cierre de esa misma deuda**: el documento
cuya función es decir qué se borró y por qué.

Escribir *este* documento subió la cuenta de 3 a **6** — 3 archivos borrados ×
2 actas que los nombran — porque una tarea que documenta el defecto tiene que
citar los hallazgos, y citarlos significa escribir las rutas:

```
$ python3 $G/verification/dangling_refs.py --repo-root .
[dangling_refs] 6 findings (6 FAIL, 0 WARN)
  ... (in tasks/backlog/DEBT-dangling-refs-no-distingue-acta-de-puntero.md)   x3
  ... (in tasks/backlog/DEBT-zero-debt-hardcoded-path-validate-satellite.md)  x3
rc=1
```

El detector cuenta como referencia colgante el acta que lo reporta a él.

## Por qué el detector tiene razón a medias

`file_refs` (`goodcode/verification/dangling_refs.py:176-201`) compara las
borradas *staged* contra `git grep -F <basename>` del árbol. No puede
distinguir dos cosas opuestas:

- **puntero vivo** — «corre `validate_satellite_functional.py`». Miente. Debe fallar.
- **acta** — «`validate_satellite_functional.py` se borró el 2026-08-17 porque
  moría en el import». Es verdad sobre el pasado. No debe fallar.

Sus autores ya reconocieron exactamente esta distinción y la resolvieron por
prefijo de ruta (`dangling_refs.py:99-109`):

```python
# `deprecated/` y `archive/` enteros, no sólo historial_backups: un acta de
# purga NOMBRA lo que purgó, y ésa es su función.
_EXEMPT_PREFIXES = ("deprecated/", "archive/")
```

Un acta de cierre bajo `tasks/` es la misma clase de documento y no está
exenta. La exención se escribió mirando `deprecated/`; `tasks/` quedó fuera.

## Por qué no se arregló editando la prosa

Dos de los tres hallazgos salen de texto que **ya existía antes de esta
sesión** — el `title:` del frontmatter y la salida literal de `zero_debt` que
la tarea guardó como evidencia:

```
$ git show HEAD:tasks/backlog/DEBT-zero-debt-hardcoded-path-validate-satellite.md | grep -n 'validate_satellite_functional\.py'
3:title: zero_debt bloquea deprecated/bootstrap_v0.5/validate_satellite_functional.py — hardcoded_path
18:  - deprecated/bootstrap_v0.5/validate_satellite_functional.py (1 findings)
```

Poner el gate en verde por esta vía exige redactar el título de una tarea y la
salida literal de una herramienta guardada como prueba. Eso es falsificar la
evidencia para satisfacer al instrumento, no arreglar nada.

Tampoco se partió en dos commits (borrado primero, acta después) para que
`--diff-filter=DR` no vea nada: llega al mismo estado final que el gate acaba
de rechazar, esquivando el detector por orden de commits en vez de por
argumento.

## Cómo se cerró el commit

`git commit --no-verify`, que el propio hook anuncia como la salida deliberada.
El bypass es de un solo commit y no desactivó nada.

**Corrección medida — el bypass NO quedó auditado.** Al escribir esto afirmé que
`bypass_ledger.py` lo registraría en `.evidence/hook_receipts.jsonl`. Lo deduje
del docstring de esa herramienta sin verificar que corriera aquí. No corre:

```
$ ls -la .evidence
ls: no se puede acceder a '.evidence': No existe el archivo o el directorio
```

`bypass_ledger` tampoco aparece entre los órganos que el hook pre-commit de este
repo lista al ejecutarse (`staged_scan`, `zero_debt`, `clean_worktree`,
`secret_scan`, `dangling_refs`, `dependency_guard`, `finding_backlog`,
`restore_hooks`). Y el 2026-08-17, mientras esta sesión corría, otra sesión lo
retiró a `goodcode/archive/organos-retirados/bypass_ledger.py`.

El único registro del bypass es el cuerpo del commit `4ca51d9` y este documento.
Eso es peor que un ledger: no es consultable por herramienta.

Un `dangling_refs` corrido **después** del commit devuelve `0 findings`: el
detector sólo mira borrados *staged*, así que el bloqueo es de un commit, no
un estado permanente. Que quede en cero en régimen no borra que fallara en el
único momento en que tenía algo que juzgar.

## Qué haría falta

En `goodcode`, no aquí. Una de dos:

1. Añadir a `_EXEMPT_PREFIXES` los directorios de actas de cierre (`tasks/` o,
   más estrecho, sólo los documentos con `status: pagada-*`), con el mismo
   argumento escrito para `deprecated/`.
2. Dar a `file_refs` un marcador explícito (como el `[PROSE-ONLY]` que ya usa
   el detector de reglas) para que una mención pueda declararse acta.

La opción 2 es más precisa y más cara; la 1 repite un criterio ya aceptado.

## Acceptance

- [ ] Un commit que borre un archivo y en el mismo commit registre el acta que
      lo nombra pasa `dangling_refs` sin `--no-verify`.
- [ ] La exención no deja pasar un puntero vivo: un documento fuera de un acta
      que cite el archivo borrado sigue dando FAIL.
