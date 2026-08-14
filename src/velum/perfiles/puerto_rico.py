"""Perfil jurídico de Puerto Rico.

El léxico base de VELUM es peninsular. Este perfil añade lo que un escrito
radicado en el Tribunal General de Justicia sí tiene y una demanda madrileña no:
salas apelativas KLAN/KLCE/KLRA, citas TSPR y DPR, números de caso «Civil Núm.»,
y direcciones con urbanización, barrio, sector y apartado postal.

Adaptado de policies/puerto_rico.py y docs/PUERTO_RICO_PROFILE.md de Codex.

Advertencia deliberada: detectar no es proteger. Las referencias legales
—TSPR, DPR, artículos, números de caso— se detectan para PRESERVARLAS, igual
que el importe y la fecha. Son el fondo del asunto, no el dato del cliente.
"""

from __future__ import annotations

import re

# --- Zonas protegidas propias de Puerto Rico -------------------------------

PROTEGIDOS_PR: dict[str, re.Pattern[str]] = {
    # Salas del Tribunal de Apelaciones y del Tribunal Supremo.
    "sala_apelativa": re.compile(
        r"\b(?:KLAN|KLCE|KLRA|KLEB|CC|AC)\s?-?\s?\d{4}\s?-?\s?\d{3,5}\b"
    ),
    # Citas del Tribunal Supremo: 2024 TSPR 41, 205 DPR 1119.
    "cita_tspr": re.compile(r"\b\d{4}\s+TSPR\s+\d{1,4}\b"),
    "cita_dpr": re.compile(r"\b\d{1,3}\s+D\.?P\.?R\.?\s+\d{1,4}\b"),
    "cita_lpra": re.compile(r"\b\d{1,2}\s+L\.?P\.?R\.?A\.?\s+(?:sec\.?|§)\s*[\d\-.]+"),
    # Número de caso: Civil Núm. K AC2019-0123, Caso Núm. SJ2024CV00123.
    "numero_caso_pr": re.compile(
        r"\b(?:Civil|Criminal|Caso|Querella|Apelaci[oó]n|Certiorari)\s+N[uú]m\.?\s*"
        r"[A-Z0-9][A-Z0-9\-]{3,20}",
        re.IGNORECASE,
    ),
    # Reglas de Procedimiento Civil de PR: Regla 10.2, Regla 36.
    "regla_pr": re.compile(
        r"\bRegla\s+\d{1,3}(?:\.\d{1,2})?\s+de\s+(?:Procedimiento\s+Civil|Evidencia)",
        re.IGNORECASE,
    ),
    # Tribunales y foros locales.
    "foro_pr": re.compile(
        r"\b(?:Tribunal\s+de\s+Primera\s+Instancia|Tribunal\s+de\s+Apelaciones|"
        r"Tribunal\s+Supremo\s+de\s+Puerto\s+Rico|Sala\s+(?:Superior|Municipal)\s+de\s+"
        r"[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+|Departamento\s+de\s+Justicia|"
        r"Junta\s+de\s+Libertad\s+Bajo\s+Palabra|Comisi[oó]n\s+Apelativa\s+del\s+"
        r"Servicio\s+P[uú]blico|CASP)\b"
    ),
}

# --- Datos personales propios de Puerto Rico -------------------------------

_VIAS_PR = (
    r"calle|c/|ave\.?|avenida|carr\.?|carretera|urb\.?|urbanizaci[oó]n|barrio|bo\.?|"
    r"sector|parcela|residencial|condominio|cond\.?|apartado|apdo\.?|p\.?\s?o\.?\s?box|"
    r"km\.?|kil[oó]metro|calle\s+marginal|camino"
)

# Un segmento: palabra de vía + hasta cinco componentes + número opcional.
_SEGMENTO_VIA = (
    rf"(?:{_VIAS_PR})\s*[A-ZÁÉÍÓÚÑa-záéíóúñ0-9'’\-\.]+"
    rf"(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ0-9'’\-\.]+){{0,4}}"
    rf"(?:\s*(?:#|n[uú]m\.?|apt\.?|apto\.?)\s*[\d\-]{{1,8}}[A-Za-z]?)?"
)

PERSONALES_PR: dict[str, re.Pattern[str]] = {
    # «Urb. Villa Nevárez, Calle 3 #1023, San Juan, PR 00927» es UNA dirección,
    # no cuatro fragmentos. Se compone de segmentos encadenados por comas.
    "DIRECCION": re.compile(
        rf"\b{_SEGMENTO_VIA}(?:\s*,\s*{_SEGMENTO_VIA})*"
        rf"(?:\s*,\s*[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+)?)?"
        rf"(?:\s*,?\s*(?:PR|P\.\s?R\.)\s*\d{{5}}(?:-\d{{4}})?)?",
        re.IGNORECASE,
    ),
    # Seguro Social estadounidense: 123-45-6789.
    "SSN": re.compile(r"(?<!\d)(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}(?!\d)"),
    # Licencia de conducir de PR: 9 dígitos precedidos de la palabra licencia.
    "LICENCIA": re.compile(
        r"\blicencia\s+(?:de\s+conducir\s+)?(?:n[uú]m\.?\s*)?(\d{6,9})\b", re.IGNORECASE
    ),
    # Teléfono con código de área de Puerto Rico.
    "TELEFONO": re.compile(
        r"(?:\+1[\s.-]?)?\(?(?:787|939)\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)"
    ),
}

# ZIP+4. Es señal de localización, no decisión automática de sustitución:
# solo se usa dentro del patrón de dirección, nunca suelto.
CODIGO_POSTAL = re.compile(r"(?<!\d)00[6-9]\d{2}(?:-\d{4})?(?!\d)")

# --- Apellidos frecuentes en Puerto Rico -----------------------------------

APELLIDOS_PR: frozenset[str] = frozenset(
    """
    rivera rodriguez torres colon santiago vazquez ramos gonzalez lopez martinez
    ortiz sanchez perez cruz rosario diaz maldonado figueroa hernandez negron
    burgos berrios cintron nieves melendez soto acevedo padilla ayala vega morales
    quinones fuentes cordero rosa marrero irizarry medina caraballo velazquez
    santos delgado feliciano roman aponte lugo camacho pagan carrasquillo
    hernandez guzman alvarado sepulveda otero cotto avila robles serrano leon
    matos flores mercado bonilla concepcion collazo rolon estrada mojica
    """.split()
)

# Formas societarias de uso corriente en Puerto Rico y Estados Unidos.
FORMAS_SOCIETARIAS_PR: tuple[str, ...] = (
    r"Inc\.?", r"Corp\.?", r"L\.?\s?L\.?\s?C\.?", r"L\.?\s?L\.?\s?P\.?",
    r"P\.?\s?S\.?\s?C\.?", r"C\.?\s?S\.?\s?P\.?", r"Ltd\.?", r"Co\.?",
)


def instalar() -> None:
    """Inyecta el perfil de Puerto Rico en los detectores base.

    Se llama una sola vez al arrancar el servidor cuando la jurisdicción
    configurada es PUERTO_RICO. No sustituye al léxico peninsular: lo amplía,
    porque un expediente puertorriqueño puede citar tanto el Código Civil de
    Puerto Rico como jurisprudencia española o federal.
    """
    from .. import detectores, lexico, nombres

    detectores.PATRONES_PROTEGIDOS.update(PROTEGIDOS_PR)
    for codigo, patron in PERSONALES_PR.items():
        if (codigo, patron) not in detectores.PATRONES_EXTRA:
            detectores.PATRONES_EXTRA.append((codigo, patron))

    lexico.APELLIDOS = frozenset(lexico.APELLIDOS | APELLIDOS_PR)
    if FORMAS_SOCIETARIAS_PR[0] not in lexico.FORMAS_SOCIETARIAS:
        lexico.FORMAS_SOCIETARIAS = lexico.FORMAS_SOCIETARIAS + FORMAS_SOCIETARIAS_PR
    nombres.recompilar()
