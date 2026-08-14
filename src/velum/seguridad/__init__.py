"""Frontera de seguridad de VELUM.

Cuatro controles, cada uno independiente del anterior:

- `rutas`    — solo se abre lo que está dentro de una raíz autorizada.
- `limites`  — tamaño de fichero y firma coherente con la extensión.
- `errores`  — códigos cerrados; ningún mensaje deriva de la entrada.
- `salida`   — sanitizador que impide que una respuesta lleve contenido.
"""

from .errores import MENSAJES, CodigoError, ErrorSeguro
from .limites import LIMITES, Limites, validar_firma, validar_tamano
from .rutas import RaicesAutorizadas
from .salida import FugaDetectada, sanitizar

__all__ = [
    "LIMITES",
    "MENSAJES",
    "CodigoError",
    "ErrorSeguro",
    "FugaDetectada",
    "Limites",
    "RaicesAutorizadas",
    "sanitizar",
    "validar_firma",
    "validar_tamano",
]
