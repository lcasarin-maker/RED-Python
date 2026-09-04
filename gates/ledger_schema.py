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
from typing import cast

ROOT = Path(__file__).resolve().parent.parent
# UNA sola casa: `tasks/`. El `ledger/` se colapso aqui el 2026-09-02 por instruccion de Luis
# --*«suena estupido tener duplicado, son puntos de falla»*-- y el dato le daba la razon:
# `tasks/` YA separaba abierto de cerrado por carpeta y el kit YA lo leia asi, mientras el
# ledger duplicaba 2,133 fichas sin anadir esa separacion. Costo de haberlo duplicado: el
# migrador piso un cierre en Atlas, 18 en simplecode y 54 lineas de prosa en office2office.
#
# Las carpetas son el estado: backlog|active|blocked = ABIERTO, done = CERRADO, archive = void.
ABIERTAS = ("backlog", "active", "blocked", "review")
CERRADAS = ("done",)
ANULADAS = ("archive",)
ENTRIES = ROOT / "tasks"
INDEX = ROOT / "tasks" / "index.jsonl"

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
# DOS estados, no cinco. Luis, 2026-09-02: *«las tasks estan en open o done, solo 2 estados»*.
# Los otros tres se inventaron y no se usaban: medido al consolidar, `active` y `blocked` tenian
# CERO fichas en los 18 repos y `review` tenia una. `void` existia solo para las 1,947 de
# cosecha del harvester, que se borraron el mismo dia. Tres estados para 1 ficha real.
STATUS = {"open", "done", "done_unverified"}
SEVERITY = {"P0", "P1", "P2", "P3"}
ORIGIN = {"detected", "asserted"}
SCOPE = {"repo", "fleet", "kit"}
# Estado del que la ficha viene, cuando el contrato la reabrio. Opcional: su AUSENCIA significa
# «nunca estuvo cerrada», que es informacion tanto como su presencia.
PRIOR = {"done"}
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

# Fecha en que el contrato de cierre empezo a exigir `evidence`. Una ficha nacida en/despues de
# ella pudo producir su tríada desde el primer dia, asi que NO puede declararse
# `done_unverified`: sin esta linea el tercer estado deja de ser una declaracion honesta sobre
# el pasado y pasa a ser una salida disponible para cualquier deuda nueva, que es amnistia con
# otro nombre. Medido antes de cablearla: las 789 fichas que hoy lo usan (office2office) fueron
# creadas ANTES, asi que la guarda rompe cero y solo cierra el futuro.
CONTRATO_EVIDENCE = "2026-09-02"

# Una razon de menos de esto es una etiqueta, no una razon. El numero no es arbitrario: las 789
# que existen hoy tienen todas una razon sustantiva, y la mas corta las supera con holgura, asi
# que el listón describe la practica que ya hay en vez de inventar una.
RAZON_MINIMA = 60

# El titulo: se REPORTA por encima de 100 y solo BLOQUEA por encima de 200.
#
# Medido el 2026-09-03 sobre los 2,313 titulos de la flota: p50=67, p95=88, p99=115,
# max=162, y solo 59 (el 2.5%) pasan de 100. Ninguno de esos 59 hace falsa una sola
# afirmacion, y NADA en el kit consume `title` con restriccion de ancho -- se busco:
# el unico consumidor es `cli_adr._slug`, que es de ADRs y no de fichas.
#
# Hasta hoy los 59 BLOQUEABAN, y en aequitas_os eran las 60 ultimas fichas rojas tras
# reparar 521: un repo entero sin poder commitear por estilo. Un gate debe bloquear lo
# que hace falsa una afirmacion y reportar lo que solo la hace mas fea; es la misma
# forma que `unrecognised_closing_status` en el kit, que reporta y nunca condena.
#
# El 200 no es cosmetico: por encima de eso el campo dejo de ser un titulo y es un
# cuerpo, y eso si dice algo -- que quien la escribio no habia acotado el defecto.
TITULO_REPORTADO = 100
TITULO_MAXIMO = 200


def parse(path: Path) -> tuple[dict[str, object] | None, str | None]:
    """Devuelve (frontmatter, None) o (None, motivo_de_could_not_run)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"ilegible: {exc}"
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, "sin frontmatter en la primera línea"
    out: dict[str, object] = {}
    for idx in range(1, len(lines)):
        line = lines[idx]
        if line.strip() == "---":
            break
        m = re.match(r"^([a-z0-9_]+):\s*(.*)$", line)
        if not m:
            continue
        clave, raw = m.group(1), m.group(2).strip()
        # Se parsea JSON en los campos que el ESQUEMA declara estructurados, nunca por la FORMA
        # del valor. Medido el 2026-09-01 en office2office: 343 fichas dieron `could_not_run`
        # porque su `title` empieza con "[BUG | ...]" y el parser dedujo "empieza con corchete,
        # luego es JSON". Deducir el tipo de un dato de su apariencia es DGX-411 otra vez, esta
        # vez dentro del gate que existe para impedirlo.
        if clave in CAMPOS_ESTRUCTURADOS:
            if not raw:
                # Bloque YAML indentado, no objeto en linea. Las dos formas son el mismo dato y
                # el contrato pide un OBJETO, no una sintaxis. Lo escribio asi la sesion
                # Simplecode al cerrar 28 fichas, y es mas legible que el JSON en una linea.
                # El gate las reportaba como `could_not_run` --que era lo correcto: no fingio
                # que estuvieran vacias-- pero rechazar una forma valida por no haberla previsto
                # es imponer mi sintaxis sobre su dato.
                bloque: dict[str, str] = {}
                for sig in lines[idx + 1:]:
                    if sig.strip() == "---" or not sig.startswith((" ", "\t")):
                        break
                    m2 = re.match(r"^\s+([a-z0-9_]+):\s*(.*)$", sig)
                    if m2:
                        bloque[m2.group(1)] = m2.group(2).strip().strip('"')
                if bloque:
                    out[clave] = bloque
                    continue
                return None, f"campo {clave} vacio y sin bloque indentado debajo"
            try:
                out[clave] = json.loads(raw)
            except json.JSONDecodeError:
                return None, f"campo {clave} deberia ser JSON y no lo es: {raw[:60]!r}"
        else:
            out[clave] = raw
    return out, None


def _obj(v: object) -> dict[str, object]:
    """Devuelve el objeto como mapa tipado, o vacio. Existe por pyright en modo ESTRICTO:
    dos repos de la flota (Twiner, maletin_homeopatia) lo corren asi, y un `dict` sin
    parametrizar --incluso tras `isinstance`-- es «partially unknown» ahi. Un gate que solo
    tipa bien donde el verificador es laxo no esta tipado: esta sin comprobar."""
    if not isinstance(v, dict):
        return {}
    crudo = cast("dict[object, object]", v)
    return {str(k): val for k, val in crudo.items()}


def validate(fm: dict[str, object]) -> list[str]:
    """Lista de violaciones. Vacía = la ficha pasa."""
    bad: list[str] = []
    # `void` no lleva `close_check`: una ficha anulada resulto NO ser deuda, y pedirle como se
    # comprobaria su resolucion es pedir la comprobacion de algo que no existe. Lo que si le
    # exige el esquema es `void_reason`, mas abajo.
    obligatorios = REQUIRED
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
    if "title" in fm and len(str(fm["title"])) > TITULO_MAXIMO:
        bad.append(f"title de {len(str(fm['title']))} chars, máximo {TITULO_MAXIMO}: "
                   "por encima de eso no es un titulo, es un cuerpo")
    if "created" in fm and not DATE_RE.match(str(fm["created"])):
        bad.append(f"created no es ISO-8601: {fm['created']!r}")
    cc: object = fm.get("close_check")
    if cc is not None:
        ccd = _obj(cc)
        if not ccd:
            bad.append("close_check no es objeto o esta vacio")
        else:
            if not str(ccd.get("cmd") or "").strip():
                bad.append("close_check.cmd vacío: quien no puede enunciar cómo se sabría "
                           "que está resuelta, no entendió el defecto todavía")
            if ccd.get("expect") not in EXPECT:
                bad.append(f"close_check.expect fuera de dominio: {ccd.get('expect')!r}")
    if fm.get("prior_status") is not None and fm["prior_status"] not in PRIOR:
        bad.append(f"prior_status fuera de dominio: {fm['prior_status']!r}")
    if fm.get("scope") is not None and fm["scope"] not in SCOPE:
        bad.append(f"scope fuera de dominio: {fm['scope']!r}")
    # Condicionales
    if fm.get("status") == "active" and not fm.get("owns"):
        bad.append("status=active exige `owns` (convención OWNS cableada en el esquema)")
    if fm.get("status") == "blocked" and not fm.get("block_reason"):
        bad.append("status=blocked exige `block_reason`")
    ev: object = fm.get("evidence")
    if fm.get("status") == "done":
        if not ev:
            bad.append("status=done exige `evidence`")
        elif not all(_obj(ev).get(k) for k in ("pass", "fail", "e2e")):
            bad.append("evidence incompleta: el contrato exige pass, fail Y e2e — una "
                       "verificación que no puede salir negativa no es una verificación")
        if not fm.get("closed_at"):
            bad.append("status=done exige `closed_at`")
    # `done_unverified` (2026-09-02, propuesto por la sesión 020 tras medir 790 fichas de
    # office2office cerradas antes de que este contrato exigiera evidence): cerrada, sin
    # verificación ejecutable, y ESO ES LO QUE DECLARA -- no se le exige lo que no puede dar
    # sin inventarlo. Cero de las 790 puede producir un `fail` real sin fabricarlo, y `fail`
    # es exactamente el campo que la regla del control negativo (CLAUDE.md) existe para
    # proteger: una verificación que no puede salir negativa no es una verificación, así que
    # fabricar ese campo sería peor que no tenerlo. No pasa como `done` (no está probada) ni
    # bloquea como violación (no es un descuido: es honesta sobre su propio límite). Un solo
    # requisito, y es el mismo que ya exige `blocked`: decir POR QUÉ no se puede verificar.
    if fm.get("status") == "done_unverified":
        razon = str(fm.get("unverified_reason") or "").strip()
        if not razon:
            bad.append("status=done_unverified exige `unverified_reason` (por qué no hay evidence)")
        elif len(razon) < RAZON_MINIMA:
            bad.append(f"unverified_reason de {len(razon)} chars: por debajo de {RAZON_MINIMA} es "
                       "una etiqueta y no una razon -- di POR QUE esta ficha no puede producir "
                       "una corrida negativa sin fabricarla")
        creada = str(fm.get("created") or "")
        if DATE_RE.match(creada) and creada >= CONTRATO_EVIDENCE:
            bad.append(f"created={creada} es de {CONTRATO_EVIDENCE} en adelante: una ficha nacida "
                       "bajo el contrato pudo producir `evidence` desde el primer dia, asi que "
                       "no puede declararse `done_unverified`. Ese estado declara un limite "
                       "historico, no es una salida disponible para deuda nueva")
    if fm.get("origin") == "detected" and not fm.get("detector"):
        bad.append("origin=detected exige `detector`")
    return bad


def avisos(fm: dict[str, object]) -> list[str]:
    """Lo que se dice y NO bloquea. Vacia = nada que reportar.

    Existe para que «no bloquea» no signifique «no se ve»: un aviso que no se imprime
    es indistinguible de una comprobacion que no se hizo.
    """
    notas: list[str] = []
    largo = len(str(fm.get("title", "")))
    if TITULO_REPORTADO < largo <= TITULO_MAXIMO:
        notas.append(f"title de {largo} chars, por encima de {TITULO_REPORTADO} recomendado")
    return notas


def main() -> int:
    check_only = "--check" in sys.argv
    if not ENTRIES.is_dir():
        print(f"could_not_run: {ENTRIES} no existe")
        return 1
    # `README.md` documenta la carpeta, no es una ficha. Se excluye por NOMBRE y no por
    # "no tiene frontmatter": un archivo sin frontmatter que SI pretende ser ficha tiene que
    # seguir saliendo como could_not_run, o el gate se volveria ciego justo a lo que busca.
    # Se gobiernan LAS MISMAS carpetas que el kit (`GOVERNED_TASK_DIRS`) mas `review`.
    # `archive/` queda fuera a proposito: son fichas archivadas como ruido --Atlas tiene 1,947
    # en dos lotes cuyo nombre lo declara-- y meterlas daba `could_not_run=1385`, un numero que
    # ahoga la senal real. Que el kit y este gate miren lo mismo evita que un repo este limpio
    # para uno y sucio para el otro, que es el defecto que el canon existe para eliminar.
    OMITIR = {"README.md", "BACKLOG.md", "FORMATO_JOBS.md", "RETIRED.md"}
    GOBERNADAS = ("backlog", "done")   # backlog = open. El kit llama backlog a lo abierto.
    paths = sorted(p for c in GOBERNADAS for p in (ENTRIES / c).glob("*.md")
                   if p.name not in OMITIR)
    ok: list[tuple[str, list[str], dict[str, object]]] = []
    failed: list[tuple[str, list[str], dict[str, object]]] = []
    unverified: list[tuple[str, dict[str, object]]] = []
    avisados: list[tuple[str, str]] = []
    could_not_run: list[tuple[str, str]] = []
    seen: dict[str, str] = {}
    for p in paths:
        fm, motivo = parse(p)
        # Se comprueba `fm is None` y no `motivo`: son la misma condicion para el humano y NO
        # para el verificador de tipos, que no puede saber que van emparejados. Lo reporto la
        # sesion aequitas_os -- dos errores de pyright aqui bloqueaban su pre-push, y el archivo
        # estaba distribuido en los 17 repos, asi que el bloqueo era de la flota entera.
        # Una rama muerta en la practica sigue siendo un error de tipo para quien lee el codigo
        # sin poder ejecutarlo, y ese lector es el gate.
        if fm is None:
            could_not_run.append((p.name, motivo or "sin frontmatter legible"))
            continue
        bad = validate(fm)
        ident = str(fm.get("id", ""))
        if ident in seen:
            bad.append(f"id duplicado, ya usado por {seen[ident]}")
        else:
            seen[ident] = p.name
        for nota in avisos(fm):
            avisados.append((p.name, nota))
        if not bad and fm.get("status") == "done_unverified":
            unverified.append((p.name, fm))
        else:
            (failed if bad else ok).append((p.name, bad, fm))

    print(f"checked={len(paths)} passed={len(ok)} failed={len(failed)} "
          f"unverified={len(unverified)} avisos={len(avisados)} "
          f"could_not_run={len(could_not_run)}")
    for name, nota in avisados:
        print(f"  AVISO {name}: {nota}")
    for name, motivo in could_not_run:
        print(f"  COULD_NOT_RUN {name}: {motivo}")
    for name, bad, _ in failed:
        print(f"  FAIL {name}")
        for b in bad:
            print(f"        - {b}")
    # `unverified` se imprime SIEMPRE, no sólo cuando alguien lo pide: un repo con 790 fichas
    # sin verificar no es un repo limpio, aunque ninguna de las 790 esté violando el contrato
    # que declaran cumplir. Callar el número sería repetir el defecto que esta guarda existe
    # para cerrar -- el `evidence` que se inventaba para que el gate no se quejara.
    for name, _ in unverified:
        print(f"  UNVERIFIED {name}")

    # El indice que este bloque regeneraba se retiro el 2026-09-02: lo generaba este gate y
    # lo leia SOLO `owns_collision`, que se retiro por llevar 0 capturas en 17 repos. Un
    # artefacto generado sin lector es trabajo que hay que mantener a cambio de nada -- el
    # print quedo huerfano referenciando `omitidas`, una variable que la escritura ya
    # retirada calculaba y que aqui nunca se definio (reportUndefinedVariable, pyright).

    # Un reporte con could_not_run > 0 NO es un reporte limpio, por muchas filas que pasen.
    return 1 if (failed or could_not_run) else 0


if __name__ == "__main__":
    raise SystemExit(main())
