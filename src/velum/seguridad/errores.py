"""Códigos de error cerrados.

Un mensaje de error derivado de una excepción puede contener la ruta del
fichero, el nombre del cliente o un fragmento del documento. Aquí no se
devuelve texto derivado de nada: se devuelve un código de una lista cerrada y
una plantilla escrita de antemano.
"""

from __future__ import annotations

from enum import Enum


class CodigoError(str, Enum):
    SOLICITUD_INVALIDA = "INVALID_REQUEST"
    RUTA_NO_AUTORIZADA = "PATH_NOT_AUTHORIZED"
    FORMATO_NO_ADMITIDO = "UNSUPPORTED_FORMAT"
    FICHERO_DEMASIADO_GRANDE = "FILE_TOO_LARGE"
    DOCUMENTO_MALFORMADO = "MALFORMED_DOCUMENT"
    SALIDA_YA_EXISTE = "OUTPUT_EXISTS"
    LIMITE_EXCEDIDO = "PROCESSING_LIMIT_EXCEEDED"
    ERROR_INTERNO = "INTERNAL_ERROR"


MENSAJES: dict[CodigoError, str] = {
    CodigoError.SOLICITUD_INVALIDA: (
        "La solicitud no es válida. Revise el modo, las categorías y la ruta."
    ),
    CodigoError.RUTA_NO_AUTORIZADA: (
        "La ruta queda fuera de las carpetas autorizadas. Configure VELUM_RAICES "
        "o mueva el documento a una carpeta autorizada."
    ),
    CodigoError.FORMATO_NO_ADMITIDO: (
        "Formato no admitido. Esta versión procesa .docx, .txt y .md."
    ),
    CodigoError.FICHERO_DEMASIADO_GRANDE: (
        "El fichero supera el tamaño máximo admitido."
    ),
    CodigoError.DOCUMENTO_MALFORMADO: (
        "El documento no se corresponde con su extensión o está dañado."
    ),
    CodigoError.SALIDA_YA_EXISTE: "Ya existe un fichero de salida con ese nombre.",
    CodigoError.LIMITE_EXCEDIDO: "Se ha superado un límite de procesamiento.",
    CodigoError.ERROR_INTERNO: (
        "Error interno. Consulte el registro local con el identificador de operación."
    ),
}


class ErrorSeguro(Exception):
    """Excepción cuyo mensaje procede de una plantilla, nunca de la entrada."""

    def __init__(self, codigo: CodigoError) -> None:
        super().__init__(MENSAJES[codigo])
        self.codigo = codigo

    @property
    def mensaje(self) -> str:
        return MENSAJES[self.codigo]
