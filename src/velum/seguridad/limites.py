"""Límites de recursos y validación de firma de fichero.

Adaptado de security/limits.py y security/signatures.py del esqueleto de Codex.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errores import CodigoError, ErrorSeguro


@dataclass(frozen=True)
class Limites:
    tamano_maximo_bytes: int = 64 * 1024 * 1024      # 64 MB
    documentos_maximos_carpeta: int = 1_000
    bloques_maximos: int = 200_000


LIMITES = Limites()


FIRMAS: dict[str, tuple[bytes, ...]] = {
    ".docx": (b"PK\x03\x04",),
    ".pdf": (b"%PDF-",),
}


def validar_tamano(ruta: Path, limites: Limites = LIMITES) -> None:
    try:
        tamano = ruta.stat().st_size
    except OSError as error:
        raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA) from error
    if tamano < 0 or tamano > limites.tamano_maximo_bytes:
        raise ErrorSeguro(CodigoError.FICHERO_DEMASIADO_GRANDE)


def validar_firma(ruta: Path) -> None:
    """Comprueba que el contenido coincide con la extensión.

    Un .docx que no empieza por PK no es un DOCX, aunque se llame así. Los
    formatos de texto no tienen firma y se aceptan sin esta comprobación.
    """
    esperadas = FIRMAS.get(ruta.suffix.lower())
    if esperadas is None:
        return
    try:
        with ruta.open("rb") as flujo:
            prefijo = flujo.read(8)
    except OSError as error:
        raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA) from error
    if not any(prefijo.startswith(firma) for firma in esperadas):
        raise ErrorSeguro(CodigoError.DOCUMENTO_MALFORMADO)
