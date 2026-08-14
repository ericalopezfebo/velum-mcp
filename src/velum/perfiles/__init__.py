"""Perfiles jurisdiccionales.

Un perfil amplía los detectores y el léxico base con lo propio de una
jurisdicción. Nunca los sustituye: un escrito puertorriqueño puede citar
jurisprudencia local, federal y española en el mismo párrafo.

Detectar no es proteger. Las referencias legales que un perfil aporta
—TSPR, DPR, KLAN, números de caso— se detectan para PRESERVARLAS.
"""

from __future__ import annotations

import os

JURISDICCIONES = ("ESPANA", "PUERTO_RICO")
VARIABLE_ENTORNO = "VELUM_JURISDICCION"
POR_DEFECTO = "ESPANA"

_instalada: str | None = None


def jurisdiccion_configurada() -> str:
    valor = os.environ.get(VARIABLE_ENTORNO, POR_DEFECTO).strip().upper()
    return valor if valor in JURISDICCIONES else POR_DEFECTO


def instalar(jurisdiccion: str | None = None) -> str:
    """Instala el perfil indicado. Idempotente."""
    global _instalada
    elegida = (jurisdiccion or jurisdiccion_configurada()).upper()
    if elegida not in JURISDICCIONES:
        elegida = POR_DEFECTO
    if elegida == _instalada:
        return elegida
    if elegida == "PUERTO_RICO":
        from . import puerto_rico

        puerto_rico.instalar()
    _instalada = elegida
    return elegida


def instalada() -> str:
    return _instalada or POR_DEFECTO
