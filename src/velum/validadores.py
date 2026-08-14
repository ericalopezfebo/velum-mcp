"""Validadores con dígito de control.

Ningún identificador se sustituye por parecerse a un DNI: se sustituye porque
su dígito o letra de control cuadra. Si no cuadra, no es ese dato y no se toca.
"""

from __future__ import annotations

import re

_LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"
_PREFIJO_NIE = {"X": "0", "Y": "1", "Z": "2"}

# Letras de organización que obligan a letra de control en el NIF/CIF.
_CIF_SOLO_LETRA = set("PQRSNW")
_CIF_SOLO_NUMERO = set("ABEH")
_CIF_LETRAS_CONTROL = "JABCDEFGHI"

_VALORES_IBAN = {c: str(i + 10) for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}


def _solo_alfanumerico(valor: str) -> str:
    return re.sub(r"[^0-9A-Za-z]", "", valor).upper()


def dni_valido(valor: str) -> bool:
    limpio = _solo_alfanumerico(valor)
    if not re.fullmatch(r"\d{8}[A-Z]", limpio):
        return False
    return _LETRAS_DNI[int(limpio[:8]) % 23] == limpio[8]


def nie_valido(valor: str) -> bool:
    limpio = _solo_alfanumerico(valor)
    if not re.fullmatch(r"[XYZ]\d{7}[A-Z]", limpio):
        return False
    numero = _PREFIJO_NIE[limpio[0]] + limpio[1:8]
    return _LETRAS_DNI[int(numero) % 23] == limpio[8]


def cif_valido(valor: str) -> bool:
    """NIF de persona jurídica (antiguo CIF)."""
    limpio = _solo_alfanumerico(valor)
    if not re.fullmatch(r"[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]", limpio):
        return False

    inicial, cuerpo, control = limpio[0], limpio[1:8], limpio[8]

    suma_pares = sum(int(d) for d in cuerpo[1::2])
    suma_impares = 0
    for digito in cuerpo[0::2]:
        doble = int(digito) * 2
        suma_impares += doble // 10 + doble % 10

    resto = (suma_pares + suma_impares) % 10
    digito_control = (10 - resto) % 10
    letra_control = _CIF_LETRAS_CONTROL[digito_control]

    if inicial in _CIF_SOLO_LETRA:
        return control == letra_control
    if inicial in _CIF_SOLO_NUMERO:
        return control == str(digito_control)
    return control in (str(digito_control), letra_control)


def iban_valido(valor: str) -> bool:
    limpio = _solo_alfanumerico(valor)
    if not re.fullmatch(r"[A-Z]{2}\d{2}[0-9A-Z]{10,30}", limpio):
        return False
    reordenado = limpio[4:] + limpio[:4]
    numerico = "".join(_VALORES_IBAN.get(c, c) for c in reordenado)
    try:
        return int(numerico) % 97 == 1
    except ValueError:
        return False


def luhn_valido(valor: str) -> bool:
    digitos = re.sub(r"\D", "", valor)
    if not 13 <= len(digitos) <= 19:
        return False
    suma = 0
    for indice, caracter in enumerate(reversed(digitos)):
        digito = int(caracter)
        if indice % 2 == 1:
            digito *= 2
            if digito > 9:
                digito -= 9
        suma += digito
    return suma % 10 == 0


def nss_valido(valor: str) -> bool:
    """Número de afiliación a la Seguridad Social: 2 + 8 + 2 con control mod 97."""
    digitos = re.sub(r"\D", "", valor)
    if len(digitos) != 12:
        return False
    provincia, numero, control = digitos[:2], digitos[2:10], digitos[10:]
    if provincia == "00" or int(provincia) > 66:
        return False
    base = int(provincia + numero)
    if int(numero) < 10_000_000:
        base = int(numero) + int(provincia) * 10_000_000
    return base % 97 == int(control)


def referencia_catastral_valida(valor: str) -> bool:
    """Comprobación estructural: 20 caracteres alfanuméricos en el formato oficial."""
    limpio = _solo_alfanumerico(valor)
    if len(limpio) != 20:
        return False
    return bool(
        re.fullmatch(r"\d{7}[A-Z]{2}\d{4}[A-Z]\d{4}[A-Z]{2}", limpio)
        or re.fullmatch(r"[0-9A-Z]{14}\d{4}[A-Z]{2}", limpio)
    )


def matricula_valida(valor: str) -> bool:
    limpio = _solo_alfanumerico(valor)
    if re.fullmatch(r"\d{4}[BCDFGHJKLMNPRSTVWXYZ]{3}", limpio):
        return True
    return bool(re.fullmatch(r"[A-Z]{1,2}\d{4}[A-Z]{1,2}", limpio))


VALIDADORES = {
    "DNI": dni_valido,
    "NIE": nie_valido,
    "CIF": cif_valido,
    "IBAN": iban_valido,
    "TARJETA": luhn_valido,
    "NSS": nss_valido,
    "CATASTRO": referencia_catastral_valida,
    "MATRICULA": matricula_valida,
}
