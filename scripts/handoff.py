#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Handoff Script
Automatiza la creación de un paquete de Handoff entre agentes.
"""

import os
import argparse

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()


def main() -> None:
    """
    Generates an automated handoff package based on STATUS.md and command line arguments.

    Inputs: Command line arguments parsed via argparse.
    Outputs: Prints the formatted handoff text to standard output and optionally copies it to the clipboard.
    Contract: Reads STATUS.md if available, extracts a code snippet if specified, and formats a handoff message.
    """
    parser = argparse.ArgumentParser(
        description="Automatiza la creación de un paquete de Handoff entre agentes."
    )
    parser.add_argument(
        "--archivo", "-a", type=str, help="Ruta del archivo relevante para el handoff."
    )
    parser.add_argument(
        "--lineas", "-l", type=str, help="Rango de líneas (ej. 110-160)."
    )
    parser.add_argument(
        "--comando",
        "-c",
        type=str,
        help="Comando exacto de validación (ej. pytest).",
        default="",
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Copia el resultado al portapapeles (requiere pyperclip).",
    )

    args = parser.parse_args()

    # 1. Leer STATUS.md para extraer Proyecto y Estado
    proyecto = "Desconocido"
    estado = "Pendiente"
    if os.path.exists("STATUS.md"):
        with open("STATUS.md", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "CAMPO 1: Proyecto" in line and i + 1 < len(lines):
                    proyecto = lines[i + 1].strip()
                if "CAMPO 2: Estado actual" in line and i + 1 < len(lines):
                    estado = lines[i + 1].strip()

    # 2. Extraer fragmento de código si se proporciona
    codigo_relevante = "[Inserta código relevante aquí]"
    if args.archivo and args.lineas:
        if os.path.exists(args.archivo):
            try:
                start, end = map(int, args.lineas.split("-"))
                with open(args.archivo, "r", encoding="utf-8") as f:
                    file_lines = f.readlines()
                    fragment = "".join(file_lines[start - 1 : end])
                    codigo_relevante = fragment.strip()
            except Exception as e:
                codigo_relevante = f"[Error al leer líneas: {e}]"
        else:
            codigo_relevante = f"[Archivo {args.archivo} no encontrado]"

    # 3. Construir el bloque de Handoff
    handoff_text = f"""PROYECTO: {proyecto}
ESTADO ACTUAL: {estado}

CÓDIGO RELEVANTE ({args.archivo if args.archivo else 'Ninguno'} {args.lineas if args.lineas else ''}):
```
{codigo_relevante}
```

PARA EJECUTAR (VALIDACIÓN):
`{args.comando if args.comando else '[Inserta comando de validación aquí]'}`

CONTEXTO MÍNIMO:
- [Añade notas breves sobre arquitectura o riesgos aquí]
"""

    print("\n=== PAQUETE DE HANDOFF GENERADO ===\n")
    print(handoff_text)
    print("===================================\n")

    # 4. Copiar al portapapeles si se solicita
    if args.clipboard:
        try:
            import pyperclip

            pyperclip.copy(handoff_text)
            print("✅ Handoff copiado al portapapeles exitosamente.")
        except ImportError:
            print(
                "⚠️ El módulo 'pyperclip' no está instalado. Ejecuta: pip install pyperclip"
            )


if __name__ == "__main__":
    main()
