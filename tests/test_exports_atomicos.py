"""Los exports y el guardado de configuracion no pisan el archivo previo si fallan a medias.

Antes cada uno hacia `open(path, "w")`: trunca el destino ANTES de escribir, asi que un fallo
a mitad (un resultado que revienta al formatearse, el disco lleno) dejaba el export o
`red_config.json` vacio o cortado. Ahora pasan por `atomic_io.write_atomic`.
"""

import json

import pytest

import red
from config import Settings
from core import ScanResult


class _ResultadoQueReviente:
    """Un resultado cuyo `status` lanza al formatearse: falla A MITAD de la escritura."""

    path = "/a"
    depth = 0

    @property
    def status(self):
        raise RuntimeError("resultado corrupto")


@pytest.mark.parametrize("nombre", ["previo.txt", "previo.csv"])
def test_un_export_que_falla_a_medias_conserva_el_archivo_previo(tmp_path, capsys, nombre):
    destino = tmp_path / nombre
    destino.write_text("export anterior\n", encoding="utf-8")
    buenos = ScanResult(path="/ok", status="empty", depth=1)

    red._export_results([buenos, _ResultadoQueReviente()], str(destino))

    assert "Export error: resultado corrupto" in capsys.readouterr().out
    assert destino.read_text(encoding="utf-8") == "export anterior\n"
    assert [p.name for p in tmp_path.iterdir()] == [nombre], "quedo un temporal huerfano"


def test_un_export_csv_correcto_reemplaza_el_previo(tmp_path):
    destino = tmp_path / "salida.csv"
    destino.write_text("viejo\n", encoding="utf-8")

    red._export_results([ScanResult(path="/a", status="empty", depth=2)], str(destino))

    assert destino.read_text(encoding="utf-8").splitlines() == ["Path,Status,Depth", "/a,empty,2"]


def test_guardar_la_configuracion_que_falla_conserva_la_previa(tmp_path, monkeypatch):
    ajustes = Settings()
    ajustes.config_path = tmp_path / "red_config.json"
    ajustes.config_path.write_text(json.dumps({"max_depth": 7}), encoding="utf-8")

    def revienta(*_args, **_kwargs):
        raise OSError("disco lleno")

    monkeypatch.setattr("config.json.dump", revienta)
    with pytest.raises(OSError, match="disco lleno"):
        ajustes.save()

    assert json.loads(ajustes.config_path.read_text(encoding="utf-8")) == {"max_depth": 7}
    assert [p.name for p in tmp_path.iterdir()] == ["red_config.json"]


def test_guardar_la_configuracion_escribe_json_completo(tmp_path):
    ajustes = Settings()
    ajustes.config_path = tmp_path / "sub" / "red_config.json"
    ajustes.data["max_depth"] = 3

    ajustes.save()

    assert json.loads(ajustes.config_path.read_text(encoding="utf-8"))["max_depth"] == 3
