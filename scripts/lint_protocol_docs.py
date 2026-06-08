#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lint_protocol_docs.py — Wiki-Lint semántico (PI-021 / Karpathy LLM Wiki pattern)

Detecta contradicciones, referencias rotas y afirmaciones inconsistentes entre
los documentos de protocolo de Cerberus. Complementa sync_binding.py (que verifica
checksums) con verificación semántica de contenido.

Checks:
  L1 — Referencias a archivos inexistentes en docs de protocolo
  L2 — Versiones inconsistentes declaradas entre documentos
  L3 — Mandatos mencionados en PROTOCOL_SYSTEM pero ausentes en CLAUDE.md binding
  L4 — Afirmaciones de estado contradictorias (ACTIVE vs deprecated, etc.)
  L5 — Confidence tag audit: afirmaciones sin VERIFIED/INFERRED/ASSUMED en SPEC.md

Exit 0: sin hallazgos. Exit 1: hallazgos críticos.
"""
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger("lint_protocol_docs")
logging.basicConfig(level=logging.INFO, format="%(message)s")

_ROOT = Path(__file__).resolve().parent.parent

PROTOCOL_DOCS = [
    _ROOT / "SPEC.md",
    _ROOT / "AGENT.md",
    _ROOT / "PROTOCOL_SYSTEM.md",
    _ROOT / "PROTOCOL_BEHAVIOR.md",
]

CLAUDE_MD = _ROOT / ".claude" / "CLAUDE.md"
VERSION_PATTERN = re.compile(r"v(\d+\.\d+)", re.IGNORECASE)
FILE_REF_PATTERN = re.compile(r"`([^`]+\.(py|md|yaml|json|toml))`")


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def check_L1_broken_refs(docs: dict[str, str]) -> list[str]:
    """L1: Referencias a archivos inexistentes.

    Busca en root Y en scripts/ y tests/. Ignora patrones glob (*.yaml),
    rutas de ejemplo y referencias con 'deprecated/' (son intencionales).
    """
    findings = []
    for doc_name, content in docs.items():
        for match in FILE_REF_PATTERN.finditer(content):
            ref = match.group(1)
            # Ignorar: patrones glob, URLs, rutas de ejemplo, deprecated, líneas de contexto archivo
            line_ctx = content[max(0, match.start()-200):match.start()+50]
            if ("*" in ref or ref.startswith("http") or
                    "nombre_viejo" in ref or "deprecated/" in ref or
                    ref.startswith(".protocol/evidence") or
                    "archivado" in line_ctx.lower() or "purga_v002" in line_ctx or
                    "DEPRECADO" in line_ctx or "BIBLIOTECA" in ref or
                    "intent" in line_ctx.lower() or  # evidencia histórica "intentó"
                    "P7.1" in line_ctx or "VC-118" in line_ctx or
                    "stale" in line_ctx.lower() or
                    "si el usuario aprueba" in line_ctx.lower() or  # referencia conceptual
                    "aprueba un" in line_ctx.lower()):
                continue
            # Buscar en root, scripts/, tests/, docs/
            candidates = [
                _ROOT / ref,
                _ROOT / "scripts" / ref,
                _ROOT / "tests" / ref,
                _ROOT / "scripts" / Path(ref).name,
            ]
            if not any(c.exists() for c in candidates):
                findings.append(f"L1 {doc_name}: referencia rota → `{ref}`")
    return findings


_DOC_VERSION_RE = re.compile(
    r"(?:Versión:|Version:|Binding válido|v0\.\d)\s*[:\s]*(v?\d+\.\d+)",
    re.IGNORECASE,
)


def check_L2_version_consistency(docs: dict[str, str]) -> list[str]:
    """L2: Versiones del PROTOCOLO inconsistentes entre documentos.

    Solo considera declaraciones explícitas de versión del protocolo
    (Versión: vX.Y, CoderCerberus vX.Y, Binding válido X.Y) —
    no versiones de scripts individuales dentro del contenido.
    """
    versions: dict[str, list[str]] = {}
    for doc_name, content in docs.items():
        found = list(set(_DOC_VERSION_RE.findall(content)))
        if found:
            versions[doc_name] = found
    if len(versions) < 2:
        return []
    all_versions = {v.lstrip("v") for vlist in versions.values() for v in vlist}
    majors = {v.split(".")[0] for v in all_versions}
    if len(majors) <= 1:
        return []
    return [f"L2 versión de protocolo inconsistente entre docs: {versions}"]


def check_L3_mandate_coverage(protocol_content: str, claude_content: str) -> list[str]:
    """L3: Mandatos S-xx en PROTOCOL_SYSTEM no reflejados en binding CLAUDE.md."""
    if not protocol_content or not claude_content:
        return []
    mandates = re.findall(r"\*\*(S\d+)[:\s]", protocol_content)
    findings = []
    for m in set(mandates):
        if m not in claude_content:
            findings.append(f"L3 mandato {m} en PROTOCOL_SYSTEM.md no aparece en CLAUDE.md binding")
    return findings


def check_L4_contradictions(docs: dict[str, str]) -> list[str]:
    """L4: Afirmaciones de estado contradictorias (ACTIVE vs deprecated en mismo archivo)."""
    findings = []
    for doc_name, content in docs.items():
        if "ACTIVE" in content and "deprecated" in content.lower():
            # Buscar si el mismo token aparece como active Y deprecated
            active_items = re.findall(r"(\w[\w_/.-]+)[^\n]*ACTIVE", content)
            deprecated_items = re.findall(r"(\w[\w_/.-]+)[^\n]*(?:deprecated|DEPRECATED)", content)
            conflicts = set(active_items) & set(deprecated_items)
            for item in conflicts:
                findings.append(f"L4 {doc_name}: '{item}' aparece como ACTIVE y deprecated")
    return findings


def check_L5_confidence_tags(spec_content: str) -> list[str]:
    """L5: Afirmaciones de estado en SPEC.md sin confidence tag (PI-020).

    Busca líneas con verbos de estado fuertes ('es', 'está', 'tiene', 'cubre')
    sin VERIFIED/INFERRED/ASSUMED. Solo reporta si hay más de 10 afirmaciones sin tag
    para evitar ruido — SPEC.md existente no tiene tags aún (deuda técnica aceptada).
    """
    if not spec_content:
        return []
    state_verbs = re.compile(
        r"^\s*[-*]?\s*.{5,80}(está|is |covers|cubre|tiene|ACTIVE|APPROVED)",
        re.MULTILINE | re.IGNORECASE,
    )
    tagged = re.compile(r"VERIFIED|INFERRED|ASSUMED", re.IGNORECASE)
    untagged = [
        ln for ln in state_verbs.findall(spec_content)
        if not tagged.search(ln)
    ]
    if len(untagged) > 10:
        return [
            f"L5 SPEC.md: {len(untagged)} afirmaciones de estado sin confidence tag "
            f"(PI-020). Considerar añadir VERIFIED/INFERRED/ASSUMED progresivamente."
        ]
    return []


def run_lint() -> int:
    try:
        docs = {p.name: _read(p) for p in PROTOCOL_DOCS}
        claude_content = _read(CLAUDE_MD)
    except OSError as exc:
        logger.error("[Wiki-Lint] Error leyendo documentos de protocolo: %s", exc)
        return 1

    findings: list[str] = []
    try:
        findings.extend(check_L1_broken_refs(docs))
        findings.extend(check_L2_version_consistency(docs))
        findings.extend(check_L3_mandate_coverage(
            docs.get("PROTOCOL_SYSTEM.md", ""), claude_content
        ))
        findings.extend(check_L4_contradictions(docs))
        findings.extend(check_L5_confidence_tags(docs.get("SPEC.md", "")))
    except Exception as exc:
        logger.error("[Wiki-Lint] Fallo inesperado en check: %s", exc)
        return 1

    if not findings:
        logger.info("[Wiki-Lint] ✅ Sin hallazgos semánticos en documentos de protocolo.")
        return 0

    logger.warning("[Wiki-Lint] Hallazgos semánticos detectados:")
    for f in findings:
        logger.warning("  ⚠ %s", f)
    logger.info("[Wiki-Lint] Total: %d hallazgo(s). Revisar antes de commit.", len(findings))
    # L5 es advisory (no bloquea), L1-L4 son críticos
    critical = [f for f in findings if not f.startswith("L5")]
    return 1 if critical else 0


if __name__ == "__main__":
    sys.exit(run_lint())
