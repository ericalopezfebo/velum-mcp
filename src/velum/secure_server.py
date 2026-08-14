"""Secure launcher for VELUM.

This launcher applies the conservative external-sharing policy before the MCP
server starts. Equivalence tables are disabled by default because they make an
otherwise tokenized document reversible. They can only be enabled explicitly
for a local workflow with VELUM_ALLOW_EQUIVALENCE=1.
"""
from __future__ import annotations

import os

from . import server


_original_anonimizar_fichero = server._anonimizar_fichero


def _safe_anonimizar_fichero(*args, **kwargs):
    """Never create a reversible mapping unless explicitly opted in locally."""
    if os.environ.get("VELUM_ALLOW_EQUIVALENCE") != "1":
        kwargs["generar_equivalencias"] = False
    return _original_anonimizar_fichero(*args, **kwargs)


server._anonimizar_fichero = _safe_anonimizar_fichero


def main() -> None:
    server.main()


if __name__ == "__main__":  # pragma: no cover
    main()
