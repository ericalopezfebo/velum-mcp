"""Punto de entrada del bundle .mcpb.

Claude Desktop ejecuta `uv run --directory <bundle> src/server.py`. Este fichero
solo resuelve la ruta del paquete y arranca el servidor: toda la lógica vive en
`src/velum/`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from velum.server import main  # noqa: E402

if __name__ == "__main__":
    main()
