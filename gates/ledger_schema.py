#!/usr/bin/env python3
"""Valida el esquema tipado de `ledger/entries/*.md` y regenera `ledger/index.jsonl`.

Por qué existe: el defecto de fondo del repo es guardar datos en prosa y leerlos con regex
(DGX-411, seis errores de medición en una tarde). Este gate es la mitad que lo impide: cada
campo del que un gate depende tiene tipo y dominio CERRADO, y lo que no está en el dominio
no pasa. La prosa vive debajo del frontmatter y ningún gate la mira.

Reporta con los ceros puestos y distingue `could_not_run` de `failed`: un archivo que no se
pudo leer NO es un archivo válido ni uno inválido, y colapsarlos haría que un instrumento
caído fuera indistinguible de un sujeto sano.

Uso:
    python gates/ledger_schema.py            # valida y regenera el índice
    python gates/ledger_schema.py --check    # valida sin escribir (para pre-commit)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "ledger" / "entries"
INDEX = ROOT / "ledger" / "index.jsonl"

# El `id` NO lleva restricción de FORMA, y eso lo decidió una medición del 2026-09-01: de los
# 182 ids reales de `tasks/done/` de este repo, **177 fallaban** el patrón que la primera versión
# del diseño imponía (`DEBT-ruff-rag-entity-graph-py-157-5-c901-buil-838a98d9` y compañía).
# Renombrarlos rompería las citas desde código, tests y dictámenes — la misma razón por la que
# DGX-416 conservó los 276 ids cerrados en vez de migrarlos. Un identificador se restringe por
# UNICIDAD y ESTABILIDAD, que es lo que un gate puede comprobar sin destruir referencias; su
# forma es cosmética, y el patrón estaba describiendo un corpus imaginario.
ID_RE = re.compile(r"^\S+$")
FAMILY_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
EXPECT = {"exit_zero", "exit_nonzero", "empty_stdout"}
KIND = {"debt", "bug", "risk", "task"}
STATUS = {"open", "active", "blocked", "done", "void"}
SEVERITY = {"P0", "P1", "P2", "P3"}
ORIGIN = {"detected", "asserted"}
SCOPE = {"repo", "fleet", "kit"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Campos siempre obligatorios. `blast_radius` NO está: su poder distintivo vive en el 0.86%
# de las fichas de la flota (21 de 2,452), así que exigirlo en el 99% restante es impuesto.
REQUIRED = ("id", "kind", "title", "status", "severity", "origin", "satd_family",
            "close_check", "created")
CAMPOS_ESTRUCTURADOS = {"close_check", "evidence", "detector", "block_reason", "owns"}
# Version del contrato, sellada en CADA linea del indice. La pidio la sesion Simplecode y su
# argumento es el que la justifica: sin ella, un lector con otro contrato lee campos AUSENTES
# como valores vacios, y eso convierte un `could_not_run` en un cero. Un cero es una medicion;
# un campo que no se supo leer no lo es.
SCHEMA_VERSION = 1


def parse(path: Path) -> tuple[dict | None, str | None]:
    """Devuelve (frontmatter, None) o (None, motivo_de_could_not_run)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"ilegible: {exc}"
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, "sin frontmatter en la primera línea"
    out: dict = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if not m:
            continue
        clave, raw = m.group(1), m.group(2).strip()
        # Se parsea JSON en los campos que el ESQUEMA declara estructurados, nunca por la FORMA
        # del valor. Medido el 2026-09-01 en office2office: 343 fichas dieron `could_not_run`
        # porque su `title` empieza con "[BUG | ...]" y el parser dedujo "empieza con corchete,
        # luego es JSON". Deducir el tipo de un dato de su apariencia es DGX-411 otra vez, esta
        # vez dentro del gate que existe para impedirlo.
        if clave in CAMPOS_ESTRUCTURADOS:
            try:
                out[clave] = json.loads(raw)
            except json.JSONDecodeError:
                return None, f"campo {clave} deberia ser JSON y no lo es: {raw[:60]!r}"
        else:
            out[clave] = raw
    return out, None


def validate(fm: dict) -> list[str]:
    """Lista de violaciones. Vacía = la ficha pasa."""
    bad: list[str] = []
    # `void` no lleva `close_check`: una ficha anulada resulto NO ser deuda, y pedirle como se
    # comprobaria su resolucion es pedir la comprobacion de algo que no existe. Lo que si le
    # exige el esquema es `void_reason`, mas abajo.
    obligatorios = tuple(k for k in REQUIRED
                         if not (k == "close_check" and fm.get("status") == "void"))
    for k in obligatorios:
        if k not in fm:
            bad.append(f"falta campo obligatorio `{k}`")
    if "id" in fm and not ID_RE.match(str(fm["id"])):
        bad.append(f"id fuera de patrón: {fm['id']!r}")
    for field, domain in (("kind", KIND), ("status", STATUS),
                          ("severity", SEVERITY), ("origin", ORIGIN)):
        if field in fm and fm[field] not in domain:
            bad.append(f"{field} fuera de dominio: {fm[field]!r} no está en {sorted(domain)}")
    if "satd_family" in fm and not FAMILY_RE.match(str(fm["satd_family"])):
        bad.append(f"satd_family fuera de patrón: {fm['satd_family']!r}")
    if "title" in fm and len(str(fm["title"])) > 100:
        bad.append(f"title de {len(str(fm['title']))} chars, máximo 100")
    if "created" in fm and not DATE_RE.match(str(fm["created"])):
        bad.append(f"created no es ISO-8601: {fm['created']!r}")
    cc = fm.get("close_check")
    if cc is not None and fm.get("status") != "void":
        if not isinstance(cc, dict):
            bad.append("close_check no es objeto")
        else:
            if not str(cc.get("cmd", "")).strip():
                bad.append("close_check.cmd vacío: quien no puede enunciar cómo se sabría "
                           "que está resuelta, no entendió el defecto todavía")
            if cc.get("expect") not in EXPECT:
                bad.append(f"close_check.expect fuera de dominio: {cc.get('expect')!r}")
    if fm.get("scope") is not None and fm["scope"] not in SCOPE:
        bad.append(f"scope fuera de dominio: {fm['scope']!r}")
    # Condicionales
    if fm.get("status") == "active" and not fm.get("owns"):
        bad.append("status=active exige `owns` (convención OWNS cableada en el esquema)")
    if fm.get("status") == "blocked" and not fm.get("block_reason"):
        bad.append("status=blocked exige `block_reason`")
    if fm.get("status") == "done":
        if not fm.get("evidence"):
            bad.append("status=done exige `evidence`")
        elif not all(fm["evidence"].get(k) for k in ("pass", "fail", "e2e")):
            bad.append("evidence incompleta: el contrato exige pass, fail Y e2e — una "
                       "verificación que no puede salir negativa no es una verificación")
        if not fm.get("closed_at"):
            bad.append("status=done exige `closed_at`")
    if fm.get("status") == "void" and not fm.get("void_reason"):
        bad.append("status=void exige `void_reason`: nada se borra, pero anular sin motivo "
                   "es indistinguible de barrer bajo la alfombra")
    if fm.get("origin") == "detected" and not fm.get("detector"):
        bad.append("origin=detected exige `detector`")
    return bad


def main() -> int:
    check_only = "--check" in sys.argv
    if not ENTRIES.is_dir():
        print(f"could_not_run: {ENTRIES} no existe")
        return 1
    # `README.md` documenta la carpeta, no es una ficha. Se excluye por NOMBRE y no por
    # "no tiene frontmatter": un archivo sin frontmatter que SI pretende ser ficha tiene que
    # seguir saliendo como could_not_run, o el gate se volveria ciego justo a lo que busca.
    paths = sorted(p for p in ENTRIES.glob("*.md") if p.name != "README.md")
    ok, failed, could_not_run = [], [], []
    seen: dict[str, str] = {}
    for p in paths:
        fm, motivo = parse(p)
        if motivo:
            could_not_run.append((p.name, motivo))
            continue
        bad = validate(fm)
        ident = str(fm.get("id", ""))
        if ident in seen:
            bad.append(f"id duplicado, ya usado por {seen[ident]}")
        else:
            seen[ident] = p.name
        (failed if bad else ok).append((p.name, bad, fm))

    print(f"checked={len(paths)} passed={len(ok)} failed={len(failed)} "
          f"could_not_run={len(could_not_run)}")
    for name, motivo in could_not_run:
        print(f"  COULD_NOT_RUN {name}: {motivo}")
    for name, bad, _ in failed:
        print(f"  FAIL {name}")
        for b in bad:
            print(f"        - {b}")

    # El índice se escribe SIEMPRE con lo que se pudo leer, y el código de salida lleva el
    # veredicto aparte. Antes sólo se escribía si nada fallaba, y eso acoplaba dos cosas
    # distintas: medido el 2026-09-01, 14 repos con fichas inválidas se quedaban sin índice
    # para siempre, así que `owns_collision` —que lo lee— no podía correr en ninguno. Un gate
    # que impide correr a otro gate por deuda ajena es un gate mal puesto.
    if not check_only:
        INDEX.write_text(
            "".join(json.dumps({**fm, "schema_version": SCHEMA_VERSION},
                               ensure_ascii=False, sort_keys=True) + "\n"
                    for _, _, fm in sorted(ok, key=lambda t: t[2].get("id", ""))),
            encoding="utf-8")
        omitidas = len(failed) + len(could_not_run)
        print(f"índice regenerado: {INDEX.relative_to(ROOT)} ({len(ok)} líneas"
              + (f", {omitidas} omitidas por inválidas o ilegibles)" if omitidas else ")"))

    # Un reporte con could_not_run > 0 NO es un reporte limpio, por muchas filas que pasen.
    return 1 if (failed or could_not_run) else 0


if __name__ == "__main__":
    raise SystemExit(main())
