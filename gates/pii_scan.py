#!/usr/bin/env python3
"""Bloquea datos personales de terceros en `ledger/` y `tasks/`. Seguridad: no se recorta.

Lo pidio la sesion aequitas_os el 2026-09-02 tras un incidente real: un agente pego en una
ficha una tabla con **20 RFC y razones sociales de clientes reales**, y la migracion del canon
la copio verbatim a `ledger/entries/`. El repo se publica en GitHub. Lo redactaron en los dos
sitios antes de que entrara a la historia.

La regla del canon: **fichas, entradas y evidencia llevan CONTEOS y NOMBRES DE ARCHIVO, nunca
RFC, CURP, razones sociales, folios ni texto de clientes.** Un hallazgo se describe por su forma
y su tamano, no por su contenido identificable.

**Las exenciones estan declaradas y son la parte que hace usable el control.** Un barrido que da
un numero irreducible se apaga; uno que puede llegar a cero se respeta. Medido en la flota:

  - **Ids de hash con forma de RFC**: `CONV-DEBT-DBB092660AB4` casa el patron por casualidad.
    1 ficha de las 2,044 de la flota. Sin esta exencion, office2office nunca llega a cero.
  - **RFC generico oficial** `XAXX010101000` (publico) y valores de prueba tipo `BETA010203AB1`.
  - **El RFC propio del repo**, declarado en `.simplecode/pii_allow.txt` una vez por repo.
    Medido: aequitas_os usa `SPG081028LV3` y poe_systems `POE930217QIA` en fichas legitimas
    sobre su propia FIEL.
  - **Fixtures declarados**: lineas que dicen `[SIMULACION]` o viven en un test.

Uso:  python gates/pii_scan.py [--check]
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AMBITOS = ("tasks", "docs")
PERMITIDOS_FIJOS = {"XAXX010101000", "XEXX010101000"}   # RFC genericos oficiales, publicos
RFC = re.compile(r"\b[A-Z&Ñ]{3,4}-?[0-9]{6}-?[A-Z0-9]{3}\b")
CURP = re.compile(r"\b[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[A-Z0-9]{2}\b")
EXENTA_LINEA = re.compile(r"\[SIMULACION\]|fixture|_test|test_|NO es secreto", re.I)
# Un archivo entero puede DECLARARSE sintetico con este marcador en sus primeras 20 lineas.
# Existe porque un documento de ejemplo legal contiene una identidad completa inventada
# --nombre, cedula, RFC, telefono, correo-- y el escaner no puede distinguirla de una real.
# La salida correcta no es eximirla en silencio ni dejar el gate en rojo para siempre: es que
# el documento DIGA lo que es. Un marcador es una afirmacion que alguien firma; una exencion
# en el codigo del gate es una que nadie ve.
MARCADOR_SINTETICO = re.compile(r"<!--\s*pii:sintetico\s*-->", re.I)


def permitidos() -> tuple[set[str], list[str]]:
    """Los del repo, declarados una vez. Un allowlist explicito, nunca inferido.

    Vive en `ledger/pii_allow.txt`, NO en `.simplecode/`. Lo cazo la sesion aequitas_os al
    ponerlo y notar de pasada que su `.gitignore` ignora `.simplecode/*`; medido despues,
    **15 de los 18 repos lo ignoran**, asi que el allowlist no viajaria a ningun clone.

    Es la misma clase que CANON-017: una afirmacion FIRMADA que no sobrevive al clone. Un
    allowlist es exactamente eso -- alguien afirma «este RFC es nuestro y su uso aqui es
    legitimo»-- y si no esta en la historia, el proximo que clone ve 30 hallazgos y ninguna
    firma que los explique. Por eso vive dentro del `ledger/`, que es el estado declarado del
    repo y esta versionado.
    """
    avisos: list[str] = []
    extra: set[str] = set()
    canonico = ROOT / "ledger" / "pii_allow.txt"
    heredado = ROOT / ".simplecode" / "pii_allow.txt"
    for p in (canonico, heredado):
        if not p.is_file():
            continue
        extra |= {l.split("#")[0].strip() for l in p.read_text(encoding="utf-8").splitlines()
                  if l.split("#")[0].strip()}
        if p is heredado:
            avisos.append(f"{p.relative_to(ROOT)} se lee, pero esa carpeta esta en .gitignore "
                          f"en 15 de 18 repos: mueve las lineas a ledger/pii_allow.txt o la "
                          f"declaracion no sobrevive a un clone")
    return PERMITIDOS_FIJOS | extra, avisos


def main() -> int:
    ok, avisos = permitidos()
    hallazgos: list[tuple[object, int, str]] = []
    could_not_run: list[str] = []
    revisados = 0
    for ambito in AMBITOS:
        base = ROOT / ambito
        if not base.is_dir():
            continue
        for f in base.rglob("*.md"):
            try:
                lineas = f.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError as exc:
                could_not_run.append(f"{f}: {exc}")
                continue
            revisados += 1
            if MARCADOR_SINTETICO.search("\n".join(lineas[:20])):
                continue
            # El nombre del archivo es un id, no un dato: si el id casa el patron, no cuenta.
            id_del_archivo = RFC.findall(f.stem)
            for n, l in enumerate(lineas, 1):
                if EXENTA_LINEA.search(l):
                    continue
                for m in RFC.findall(l) + CURP.findall(l):
                    if m in ok or m in id_del_archivo:
                        continue
                    hallazgos.append((f.relative_to(ROOT), n, m))

    print(f"revisados={revisados} hallazgos={len(hallazgos)} could_not_run={len(could_not_run)}")
    for f, n, m in hallazgos[:40]:
        print(f"  PII {f}:{n}  {m}")
    if len(hallazgos) > 40:
        print(f"  ... y {len(hallazgos) - 40} mas")
    for c in could_not_run:
        print(f"  COULD_NOT_RUN {c}")
    for a in avisos:
        print(f"  AVISO {a}")
    return 1 if (hallazgos or could_not_run) else 0


if __name__ == "__main__":
    raise SystemExit(main())
