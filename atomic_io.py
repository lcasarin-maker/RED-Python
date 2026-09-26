"""Escritura atomica de archivos de texto: el destino queda intacto o queda completo, nunca a medias.

`open(path, "w")` trunca el destino ANTES de escribir: si el proceso muere, si el disco se llena o si
`escribir` lanza a mitad, el archivo que habia (un export, `red_config.json`) queda vacio o cortado.
Aqui se escribe a un temporal en el mismo directorio, se sincroniza a disco y se reemplaza el destino
con `os.replace`, que es atomico dentro del mismo volumen.
"""

import contextlib
import os
import stat
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import TextIO

_MODO_NUEVO = 0o644


def write_atomic(
    path: str | os.PathLike[str],
    escribir: Callable[[TextIO], object],
    *,
    newline: str | None = None,
    encoding: str = "utf-8",
) -> None:
    """Escribe `path` llamando `escribir(archivo)`; si algo falla, el destino no se toca."""
    destino = Path(path)
    modo = stat.S_IMODE(destino.stat().st_mode) if destino.exists() else _MODO_NUEVO
    fd, temporal = tempfile.mkstemp(dir=destino.parent, prefix=f".{destino.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline=newline, encoding=encoding) as archivo:
            escribir(archivo)
            archivo.flush()
            os.fsync(archivo.fileno())
        os.chmod(temporal, modo)
        os.replace(temporal, destino)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporal)
        raise
