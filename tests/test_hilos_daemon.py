"""Los hilos de escaneo y limpieza son daemon: cerrar la ventana no queda esperando un recorrido en curso.

SPEC (System Patterns): "Daemon Threads: Scanning and cleaning operations run in background threads to keep the UI responsive."
"""

import threading

from config import Settings
from core import Cleaner, Scanner


def test_el_hilo_del_escaner_es_daemon(tmp_path):
    escaner = Scanner(Settings())
    escaner.scan([str(tmp_path)])
    hilo = escaner._thread
    assert isinstance(hilo, threading.Thread)
    assert hilo.daemon is True
    hilo.join(timeout=5)


def test_el_hilo_del_limpiador_es_daemon():
    limpiador = Cleaner(Settings())
    limpiador.delete([])
    hilo = limpiador._thread
    assert isinstance(hilo, threading.Thread)
    assert hilo.daemon is True
    hilo.join(timeout=5)
