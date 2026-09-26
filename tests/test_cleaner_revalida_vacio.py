"""El Cleaner revalida que la carpeta siga vacia justo antes de quitarla.

SPEC (Risks): "Emptiness check re-validated immediately before removal". Medido el 2026-09-26 al auditar
esa afirmacion: en modo recycle (el por defecto) una carpeta a la que llego un archivo real DESPUES del
escaneo se enviaba a la papelera con el archivo dentro, porque `send2trash` no mira el contenido.
"""

import os
import sys
import types

import pytest

from config import Settings
from core import Cleaner, ScanResult


def _cleaner(modo, papelera):
    ajustes = Settings()
    ajustes.data["delete_mode"] = modo
    errores = []
    cleaner = Cleaner(ajustes, on_error=lambda resultado, error: errores.append(str(error)))
    falso = types.ModuleType("send2trash")
    setattr(falso, "send2trash", lambda ruta: papelera.append(ruta))
    sys.modules["send2trash"] = falso
    return cleaner, errores


@pytest.fixture(autouse=True)
def _restaurar_send2trash():
    previo = sys.modules.get("send2trash")
    yield
    if previo is None:
        sys.modules.pop("send2trash", None)
    else:
        sys.modules["send2trash"] = previo


@pytest.mark.parametrize("modo", ["recycle", "permanent"])
def test_un_archivo_real_llegado_despues_del_escaneo_impide_quitar_la_carpeta(tmp_path, modo):
    carpeta = tmp_path / "vacia"
    carpeta.mkdir()
    (carpeta / "basura.tmp").write_bytes(b"")  # ignorable: cero bytes
    (carpeta / "real.txt").write_text("datos importantes", encoding="utf-8")  # llego despues del escaneo
    papelera = []
    cleaner, errores = _cleaner(modo, papelera)

    liberado = cleaner._delete_one(ScanResult(path=str(carpeta), status="empty", depth=0), modo)

    assert liberado is None
    assert papelera == [], "se envio a la papelera una carpeta que ya tenia un archivo real"
    assert (carpeta / "real.txt").read_text(encoding="utf-8") == "datos importantes"
    assert errores and "no longer empty" in errores[0]


def test_una_carpeta_solo_con_basura_ignorable_si_se_quita_en_recycle(tmp_path):
    carpeta = tmp_path / "solo_basura"
    carpeta.mkdir()
    (carpeta / "basura.tmp").write_bytes(b"")
    papelera = []
    cleaner, errores = _cleaner("recycle", papelera)

    liberado = cleaner._delete_one(ScanResult(path=str(carpeta), status="empty", depth=0), "recycle")

    assert liberado == 0
    assert papelera == [str(carpeta)]
    assert errores == []
    assert os.listdir(carpeta) == [], "la basura ignorable se purga antes de quitarla"


def test_una_carpeta_solo_con_basura_ignorable_si_se_quita_en_permanent(tmp_path):
    carpeta = tmp_path / "solo_basura"
    carpeta.mkdir()
    (carpeta / "basura.tmp").write_bytes(b"")
    papelera = []
    cleaner, errores = _cleaner("permanent", papelera)

    liberado = cleaner._delete_one(ScanResult(path=str(carpeta), status="empty", depth=0), "permanent")

    assert liberado == 0
    assert not carpeta.exists()
    assert errores == [] and papelera == []


def test_en_simulacion_no_se_revalida_ni_se_toca_nada(tmp_path):
    carpeta = tmp_path / "vacia"
    carpeta.mkdir()
    (carpeta / "real.txt").write_text("x", encoding="utf-8")
    papelera = []
    cleaner, errores = _cleaner("simulate", papelera)

    assert cleaner._delete_one(ScanResult(path=str(carpeta), status="empty", depth=0), "simulate") == 0
    assert (carpeta / "real.txt").exists() and papelera == [] and errores == []
