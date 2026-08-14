"""Sanitizador de respuestas.

«Ninguna herramienta documental devuelve el contenido del fichero» deja de ser
una convención que sostiene la disciplina de quien escribe cada tool y pasa a
ser un invariante que el código impide violar.

Adaptado de mcp/contracts.py::sanitize_response del esqueleto de Codex.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel

# Conceptos de clave prohibidos en cualquier respuesta documental.
CLAVES_PROHIBIDAS = re.compile(
    r"(?i)(contenido|content|texto|text|valor|value|extracto|excerpt|snippet|"
    r"fragmento|span|posicion|position|offset|contexto|context|mapping|"
    r"equivalencia_valores|traceback|stack|raw|payload|cuerpo|body)"
)

# Claves admitidas pese a contener una subcadena prohibida por casualidad.
EXCEPCIONES = frozenset(
    {
        "texto_anonimizado",          # es la carga útil legítima de anonimizar_texto
        "tabla_de_equivalencias",     # es una RUTA, no los valores
        "total_datos_personales",
        "total_datos_sustituidos",
    }
)

LONGITUD_MAXIMA_CADENA = 4096


class FugaDetectada(RuntimeError):
    """El sanitizador ha bloqueado una respuesta antes de que saliera."""


def sanitizar(resultado: BaseModel, *, permitir_texto: bool = False) -> dict[str, Any]:
    """Reconstruye la respuesta desde su modelo público y la audita.

    `permitir_texto` solo lo usa `anonimizar_texto`, cuya salida es, por
    definición, texto ya anonimizado que el usuario pegó él mismo en el chat.
    """
    datos = resultado.model_dump(mode="json", exclude_none=True)
    _auditar(datos, permitir_texto=permitir_texto)
    return datos


def _auditar(nodo: Any, *, permitir_texto: bool, ruta: str = "") -> None:
    if isinstance(nodo, dict):
        for clave, valor in nodo.items():
            _revisar_clave(str(clave), permitir_texto=permitir_texto, ruta=ruta)
            _auditar(valor, permitir_texto=permitir_texto, ruta=f"{ruta}.{clave}")
    elif isinstance(nodo, (list, tuple)):
        for indice, elemento in enumerate(nodo):
            _auditar(elemento, permitir_texto=permitir_texto, ruta=f"{ruta}[{indice}]")
    elif isinstance(nodo, str):
        _revisar_cadena(nodo, permitir_texto=permitir_texto, ruta=ruta)


def _revisar_clave(clave: str, *, permitir_texto: bool, ruta: str) -> None:
    if clave in EXCEPCIONES:
        if clave == "texto_anonimizado" and not permitir_texto:
            raise FugaDetectada(f"clave de contenido no permitida en {ruta or 'raíz'}")
        return
    if CLAVES_PROHIBIDAS.search(clave):
        raise FugaDetectada(f"clave prohibida «{clave}» en {ruta or 'raíz'}")


def _revisar_cadena(valor: str, *, permitir_texto: bool, ruta: str) -> None:
    if permitir_texto:
        return
    if len(valor) > LONGITUD_MAXIMA_CADENA:
        raise FugaDetectada(f"cadena demasiado larga en {ruta}")
    if "\n" in valor and not ruta.endswith(("advertencia", "aviso_reversibilidad",
                                            "procesamiento", "mensaje")):
        raise FugaDetectada(f"salto de línea inesperado en {ruta}")
