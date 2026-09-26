"""`write_atomic`: el destino queda completo o queda como estaba, nunca a medias."""

import os
import stat

import pytest

from atomic_io import write_atomic


def test_escribe_el_contenido_completo(tmp_path):
    destino = tmp_path / "salida.txt"
    write_atomic(destino, lambda f: f.write("uno\ndos\n"))
    assert destino.read_text(encoding="utf-8") == "uno\ndos\n"


def test_newline_vacio_no_duplica_los_saltos_del_csv(tmp_path):
    import csv

    destino = tmp_path / "salida.csv"

    def escribir(f):
        csv.writer(f).writerow(["a", "b"])

    write_atomic(destino, escribir, newline="")
    assert destino.read_bytes() == b"a,b\r\n"


def test_si_escribir_falla_a_medias_el_original_queda_intacto(tmp_path):
    destino = tmp_path / "config.json"
    destino.write_text("original", encoding="utf-8")

    def escribe_y_revienta(f):
        f.write("a medias")
        raise RuntimeError("disco lleno")

    with pytest.raises(RuntimeError, match="disco lleno"):
        write_atomic(destino, escribe_y_revienta)

    assert destino.read_text(encoding="utf-8") == "original"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["config.json"], "quedo un temporal huerfano"


def test_si_escribir_falla_no_se_crea_el_destino(tmp_path):
    destino = tmp_path / "nuevo.txt"

    def revienta(f):
        f.write("x")
        raise RuntimeError("falla")

    with pytest.raises(RuntimeError, match="falla"):
        write_atomic(destino, revienta)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.skipif(os.name == "nt", reason="los bits de modo POSIX no aplican en Windows")
def test_conserva_el_modo_del_archivo_existente(tmp_path):
    destino = tmp_path / "script.sh"
    destino.write_text("viejo", encoding="utf-8")
    destino.chmod(0o755)
    write_atomic(destino, lambda f: f.write("nuevo"))
    assert stat.S_IMODE(destino.stat().st_mode) == 0o755
    assert destino.read_text(encoding="utf-8") == "nuevo"


def test_un_directorio_inexistente_falla_sin_dejar_nada(tmp_path):
    with pytest.raises(FileNotFoundError, match="no_existe"):
        write_atomic(tmp_path / "no_existe" / "a.txt", lambda f: f.write("x"))
