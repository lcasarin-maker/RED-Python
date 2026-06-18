"""Bootstrap RED-Python so the canonical Cerberus core wins import resolution.

If `.protocol-core/` is present, it is inserted ahead of the repo root so
imports like `scripts.core_utils` and `protocol_engine.*` resolve to the
canonical core copy instead of local vendored mirrors.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_protocol_core() -> None:
    repo_root = Path(__file__).resolve().parent
    protocol_core = repo_root / ".protocol-core"
    if not protocol_core.is_dir():
        return

    protocol_core_str = str(protocol_core)
    if protocol_core_str in sys.path:
        sys.path.remove(protocol_core_str)
    sys.path.insert(0, protocol_core_str)


_bootstrap_protocol_core()
