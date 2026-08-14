"""Detección por reglas. Sin inteligencia artificial y sin llamadas externas.

Dos responsabilidades:

1. Marcar las ZONAS PROTEGIDAS —importes, fechas, citas legales, órganos
   judiciales, números de procedimiento—. Nada que caiga dentro se sustituye.
2. Detectar los identificadores que se validan con su dígito de control y los
   datos de contacto y económicos que tienen una forma estable.
"""

from __future__ import annotations

import re
from typing import Iterable

from .modelo import Entidad
from .validadores import VALIDADORES

# ---------------------------------------------------------------------------
# Zonas protegidas: el fondo del asunto no se toca
# ---------------------------------------------------------------------------

_MESES = (
    "enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    "septiembre|setiembre|octubre|noviembre|diciembre"
)

PATRONES_PROTEGIDOS: dict[str, re.Pattern[str]] = {
    # Importes y cuantías
    "importe": re.compile(
        r"\d{1,3}(?:[.\s]\d{3})*(?:,\d{1,2})?\s?(?:€|euros?|EUR)\b", re.IGNORECASE
    ),
    "porcentaje": re.compile(r"\d{1,3}(?:,\d+)?\s?%"),
    # Fechas
    "fecha_larga": re.compile(
        rf"\b\d{{1,2}}\s+de\s+(?:{_MESES})\s+de\s+\d{{4}}\b", re.IGNORECASE
    ),
    "fecha_corta": re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
    "anio": re.compile(r"\b(?:año|ejercicio)\s+\d{4}\b", re.IGNORECASE),
    # Citas legales
    "articulo": re.compile(
        r"\b(?:art[íi]culos?|arts?\.|art\.)\s*\d+(?:\.\d+)*(?:\s*(?:bis|ter|quáter|quater))?"
        r"(?:\s*(?:,|y|a)\s*\d+(?:\.\d+)*)*",
        re.IGNORECASE,
    ),
    "norma": re.compile(
        r"\b(?:Ley\s+Org[áa]nica|Ley|Real\s+Decreto(?:-ley)?|Decreto|Reglamento|"
        r"Orden|Directiva|Reglamento\s+\(UE\))\s+(?:n[.º°]?\s*)?\d+/\d{4}",
        re.IGNORECASE,
    ),
    "codigo": re.compile(
        r"\b(?:C[óo]digo\s+(?:Civil|Penal|de\s+Comercio|de\s+Trabajo)|"
        r"LEC|LECrim|LJCA|LPACAP|LRJSP|ET|RGPD|LOPDGDD|TRLGDCU|CE)\b"
    ),
    # Órganos judiciales y administrativos
    "organo": re.compile(
        r"\b(?:Tribunal\s+(?:Supremo|Constitucional|Superior\s+de\s+Justicia|de\s+Justicia\s+de\s+la\s+Uni[óo]n\s+Europea)|"
        r"Audiencia\s+(?:Nacional|Provincial)|"
        r"Juzgado\s+de\s+[^.,;\n]{0,60}?n[.º°]?\s*\d+(?:\s+de\s+[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+)?|"
        r"Juzgado\s+de\s+lo\s+[A-Za-záéíóúñ]+(?:\s+n[.º°]?\s*\d+)?|"
        r"Agencia\s+Espa[ñn]ola\s+de\s+Protecci[óo]n\s+de\s+Datos|AEPD)\b"
    ),
    # Identificadores de procedimiento
    "procedimiento": re.compile(
        r"\b(?:procedimiento|autos|juicio|ejecuci[óo]n|recurso|expediente|rollo|"
        r"diligencias|ejecutoria)\s+(?:ordinario\s+|verbal\s+|monitorio\s+|cambiario\s+)?"
        r"(?:n[.º°]?\s*)?\d+[/-]\d{2,4}",
        re.IGNORECASE,
    ),
    "ecli_roj": re.compile(r"\b(?:ECLI:[A-Z]{2}:[A-Z0-9]+:\d{4}:\S+|ROJ:\s*\S+)"),
}


def zonas_protegidas(texto: str) -> list[tuple[int, int]]:
    """Devuelve los tramos de texto que nunca deben sustituirse."""
    zonas: list[tuple[int, int]] = []
    for patron in PATRONES_PROTEGIDOS.values():
        zonas.extend((m.start(), m.end()) for m in patron.finditer(texto))
    return _fusionar(zonas)


def _fusionar(tramos: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not tramos:
        return []
    tramos = sorted(tramos)
    fusionados = [tramos[0]]
    for inicio, fin in tramos[1:]:
        ultimo_inicio, ultimo_fin = fusionados[-1]
        if inicio <= ultimo_fin:
            fusionados[-1] = (ultimo_inicio, max(ultimo_fin, fin))
        else:
            fusionados.append((inicio, fin))
    return fusionados


def dentro_de(inicio: int, fin: int, zonas: Iterable[tuple[int, int]]) -> bool:
    return any(inicio < zona_fin and fin > zona_inicio for zona_inicio, zona_fin in zonas)


# ---------------------------------------------------------------------------
# Identificadores, contacto y datos económicos
# ---------------------------------------------------------------------------

_VIAS = (
    r"calle|c/|avda\.?|avenida|plaza|pza\.?|paseo|p\.?[ºo°]\.?|carretera|ctra\.?|"
    r"camino|travesía|travesia|ronda|glorieta|urbanizaci[óo]n|urb\.?|polígono|poligono|"
    r"barrio|vía|via|rambla|carrer|passeig|avinguda|rúa|rua|praza"
)

# «n.º 47», «núm. 47», «nº 47» o simplemente «47».
_ORDINAL = r"[.ºoª°]{0,3}"
_NUMERO_VIA = rf"(?:n\s?{_ORDINAL}|n[úu]m\.?|n[úu]mero)?\s*\d{{1,4}}\s?[a-zA-Z]?"

# «3.º B», «bajo», «esc. 2», «pta. 4».
_PISO = (
    rf"(?:\d{{1,3}}(?!\d)\s?{_ORDINAL}\s*[a-zA-Z]?|bajo|entresuelo|[áa]tico|"
    rf"esc\.?\s*\w+|pta\.?\s*\w+|puerta\s*\w+|piso\s*\w+|izq\w*\.?|dcha?\w*\.?)"
)

_NOMBRE_VIA = r"(?:[A-ZÁÉÍÓÚÑa-záéíóúñ0-9'’\-]+\s+){1,6}?"

PATRONES: dict[str, re.Pattern[str]] = {
    "DNI": re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}\s?-?\s?[A-Za-z]\b"),
    "NIE": re.compile(r"\b[XYZxyz]\s?-?\s?\d{7}\s?-?\s?[A-Za-z]\b"),
    "CIF": re.compile(r"\b[ABCDEFGHJNPQRSUVWabcdefghjnpqrsuvw]\s?-?\s?\d{7}\s?-?\s?[0-9A-Ja-j]\b"),
    "IBAN": re.compile(r"\b[A-Z]{2}\d{2}(?:[ -]?[0-9A-Z]{4}){2,7}(?:[ -]?[0-9A-Z]{1,4})?\b"),
    "TARJETA": re.compile(r"\b(?:\d{4}[ -]?){3}\d{1,4}\b"),
    "NSS": re.compile(r"\b\d{2}[ /-]?\d{8}[ /-]?\d{2}\b"),
    "CATASTRO": re.compile(r"\b\d{7}[A-Z]{2}\d{4}[A-Z]\d{4}[A-Z]{2}\b"),
    "MATRICULA": re.compile(r"\b\d{4}\s?-?\s?[BCDFGHJKLMNPRSTVWXYZ]{3}\b"),
    "PASAPORTE": re.compile(r"\b(?:pasaporte\s+(?:n[.º°]?\s*)?)([A-Z]{2,3}\s?\d{6})\b", re.IGNORECASE),
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]{2,}\b"),
    "TELEFONO": re.compile(
        r"(?:(?<=\D)|^)(?:\+34[ -]?|0034[ -]?)?[6789]\d{2}[ .-]?\d{2}[ .-]?\d{2}[ .-]?\d{2}(?=\D|$)"
    ),
    "DIRECCION": re.compile(
        rf"\b(?:{_VIAS})\s+{_NOMBRE_VIA}{_NUMERO_VIA}"
        rf"(?:\s*,\s*{_PISO})*"
        rf"(?:\s*,?\s*\d{{5}})?"
        rf"(?:\s*,?\s*(?:de\s+)?[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+(?:\s+de\s+[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+)?)?",
        re.IGNORECASE,
    ),
}

# Patrones añadidos por un perfil jurisdiccional. Se recorren junto a PATRONES,
# en una lista y no en el diccionario, para que un perfil pueda aportar una
# segunda expresión para un tipo ya existente (p. ej. otra forma de DIRECCION)
# sin destruir la peninsular.
PATRONES_EXTRA: list[tuple[str, re.Pattern[str]]] = []

# Tipos cuyo hallazgo se descarta si el dígito de control no cuadra.
_REQUIEREN_CONTROL = {
    "DNI", "NIE", "CIF", "IBAN", "TARJETA", "NSS", "CATASTRO", "MATRICULA",
    "ABA", "EIN",
}

# Máscara del Social Security Number. Un teléfono nunca se escribe así.
_MASCARA_SSN = re.compile(r"\d{3}-\d{2}-\d{4}")

# Palabras que, delante de una cifra, indican que no es un teléfono.
_ANTES_NO_TELEFONO = re.compile(
    r"(?:art[íi]culos?|arts?\.|n[.º°]|n[úu]m\.?|ref\.?|expediente|folio|p[áa]g\.?|"
    r"CP|c[óo]digo\s+postal)\s*$",
    re.IGNORECASE,
)


def detectar_reglas(texto: str, bloque: int = 0, categorias: set[str] | None = None) -> list[Entidad]:
    """Detecta con reglas y valida con dígito de control cuando procede."""
    from .modelo import TIPOS

    protegidas = zonas_protegidas(texto)
    encontradas: list[Entidad] = []

    for codigo, patron in list(PATRONES.items()) + PATRONES_EXTRA:
        if categorias is not None and TIPOS[codigo].categoria not in categorias:
            continue

        for coincidencia in patron.finditer(texto):
            grupo = 1 if patron.groups else 0
            inicio, fin = coincidencia.span(grupo)
            valor = coincidencia.group(grupo).strip()

            if not valor or dentro_de(inicio, fin, protegidas):
                continue

            if codigo in _REQUIEREN_CONTROL and not VALIDADORES[codigo](valor):
                continue

            if codigo == "TELEFONO":
                if _ANTES_NO_TELEFONO.search(texto[max(0, inicio - 24):inicio]):
                    continue
                # 666-12-3456 tiene la máscara de un SSN, no de un teléfono. Si
                # el validador de SSN ya lo descartó por pertenecer a un bloque
                # nunca emitido, tampoco es un número de teléfono español: es
                # una cifra que no se puede identificar, y no se toca.
                if _MASCARA_SSN.fullmatch(valor):
                    continue

            if codigo in {"DIRECCION", "LICENCIA"}:
                valor = valor.rstrip(" ,.;:")
                fin = inicio + len(valor)
                if codigo == "DIRECCION" and len(valor) < 8:
                    continue

            encontradas.append(
                Entidad(tipo=codigo, inicio=inicio, fin=fin, valor=valor, bloque=bloque)
            )

    return encontradas
