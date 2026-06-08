#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX ENCODING: Valida y arregla problemas de encoding UTF-8
- Detecta: BOM, CRLF, soft hyphens, encoding inválido
- Arregla: Convierte a UTF-8 LF sin BOM
"""

import sys
import codecs
from pathlib import Path
from argparse import ArgumentParser


def validate_encoding(filepath):
    """Valida que archivo sea UTF-8 válido."""
    try:
        with open(filepath, "rb") as f:
            content = f.read()

        issues = []

        # Detectar BOM
        if content.startswith(codecs.BOM_UTF8):
            issues.append("BOM (UTF-8 signature)")

        # Detectar CRLF
        if b"\r\n" in content:
            issues.append("CRLF (line endings Windows)")

        # Detectar soft hyphens
        if b"\xad" in content:
            issues.append("Soft hyphens (\xad)")

        # Validar UTF-8
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as e:
            issues.append(f"Encoding inválido: {str(e)[:50]}")

        return issues
    except Exception as e:
        return [f"Error al leer: {str(e)[:50]}"]


def fix_encoding(filepath):
    """Arregla problemas de encoding."""
    try:
        # Leer contenido binario
        with open(filepath, "rb") as f:
            content = f.read()

        # Remover BOM si existe
        if content.startswith(codecs.BOM_UTF8):
            content = content[len(codecs.BOM_UTF8) :]

        # Convertir a string
        text = content.decode("utf-8", errors="ignore")

        # Remover soft hyphens
        text = text.replace("\xad", "")

        # Convertir CRLF a LF
        text = text.replace("\r\n", "\n")

        # Guardar con UTF-8 LF sin BOM
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

        return True
    except Exception as e:
        print(f"❌ Error al arreglar: {str(e)[:50]}", file=sys.stderr)
        return False


def main():
    parser = ArgumentParser(description="Valida y arregla encoding UTF-8")
    parser.add_argument("filepath", help="Archivo a validar/arreglar")
    parser.add_argument(
        "--fix", action="store_true", help="Arreglar problemas detectados"
    )
    args = parser.parse_args()

    filepath = Path(args.filepath)
    if not filepath.exists():
        print(f"❌ Archivo no existe: {filepath}", file=sys.stderr)
        return 1

    issues = validate_encoding(filepath)

    if not issues:
        print(f"[OK] {filepath.name}: Encoding válido (UTF-8 LF sin BOM)")
        return 0

    print(f"[WARN]  {filepath.name}: Issues detectados:")
    for issue in issues:
        print(f"   • {issue}")

    if args.fix:
        if fix_encoding(filepath):
            print(f"[OK] Arreglado: {filepath.name}")
            return 0
        else:
            return 1
    else:
        print("Run with --fix para arreglar")
        return 1


if __name__ == "__main__":
    sys.exit(main())
