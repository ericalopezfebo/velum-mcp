"""Tipos compartidos y catálogo de categorías."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Tipo:
    """Un tipo de dato personal detectable."""

    codigo: str
    etiqueta: str          # raíz del marcador: [DNI_1], [ACTOR_1]...
    categoria: str
    descripcion: str
    articulo_9: bool = False


TIPOS: dict[str, Tipo] = {
    # --- Identificadores oficiales -------------------------------------
    "DNI": Tipo("DNI", "DNI", "identificadores", "Documento nacional de identidad"),
    "NIE": Tipo("NIE", "NIE", "identificadores", "Número de identidad de extranjero"),
    "CIF": Tipo("CIF", "CIF", "identificadores", "NIF de persona jurídica"),
    "PASAPORTE": Tipo("PASAPORTE", "PASAPORTE", "identificadores", "Número de pasaporte"),
    "NSS": Tipo("NSS", "NSS", "identificadores", "Número de la Seguridad Social"),
    "SSN": Tipo("SSN", "SSN", "identificadores", "Social Security Number (EE. UU. / P. R.)"),
    "LICENCIA": Tipo("LICENCIA", "LICENCIA", "identificadores", "Licencia de conducir"),
    "EIN": Tipo("EIN", "EIN", "identificadores", "Employer Identification Number (EE. UU.)"),
    "MEDICARE": Tipo("MEDICARE", "MEDICARE", "identificadores", "Medicare Beneficiary Identifier"),
    "EXPEDIENTE_MEDICO": Tipo(
        "EXPEDIENTE_MEDICO", "EXPEDIENTE_MEDICO", "sensibles",
        "Número de historia clínica", articulo_9=True,
    ),
    "ABA": Tipo("ABA", "ABA", "economicos", "Número de ruta bancaria (EE. UU.)"),
    # --- Contacto -------------------------------------------------------
    "EMAIL": Tipo("EMAIL", "EMAIL", "contacto", "Dirección de correo electrónico"),
    "TELEFONO": Tipo("TELEFONO", "TELEFONO", "contacto", "Número de teléfono"),
    "DIRECCION": Tipo("DIRECCION", "DIRECCION", "contacto", "Dirección postal"),
    # --- Económicos -----------------------------------------------------
    "IBAN": Tipo("IBAN", "IBAN", "economicos", "Cuenta bancaria"),
    "TARJETA": Tipo("TARJETA", "TARJETA", "economicos", "Tarjeta de pago"),
    # --- Bienes ---------------------------------------------------------
    "MATRICULA": Tipo("MATRICULA", "MATRICULA", "bienes", "Matrícula de vehículo"),
    "CATASTRO": Tipo("CATASTRO", "CATASTRO", "bienes", "Referencia catastral"),
    # --- Personas y organizaciones --------------------------------------
    "PERSONA": Tipo("PERSONA", "PERSONA", "nombres", "Persona física"),
    "ACTOR": Tipo("ACTOR", "ACTOR", "nombres", "Parte demandante"),
    "DEMANDADO": Tipo("DEMANDADO", "DEMANDADO", "nombres", "Parte demandada"),
    "LETRADO": Tipo("LETRADO", "LETRADO", "nombres", "Profesional interviniente"),
    "PERITO": Tipo("PERITO", "PERITO", "nombres", "Perito interviniente"),
    "TESTIGO": Tipo("TESTIGO", "TESTIGO", "nombres", "Testigo"),
    "MENOR": Tipo("MENOR", "MENOR", "nombres", "Persona menor de edad", articulo_9=True),
    "EMPRESA": Tipo("EMPRESA", "EMPRESA", "empresas", "Persona jurídica"),
    # --- Artículo 9 RGPD -------------------------------------------------
    "SALUD": Tipo("SALUD", "DATO_SALUD", "sensibles", "Dato de salud", articulo_9=True),
    "IDEOLOGIA": Tipo("IDEOLOGIA", "DATO_IDEOLOGIA", "sensibles", "Ideología, religión o afiliación", articulo_9=True),
    "PENAL": Tipo("PENAL", "DATO_PENAL", "sensibles", "Antecedentes o condenas penales", articulo_9=True),
}

CATEGORIAS = {
    "identificadores": "Identificadores oficiales (DNI, NIE, CIF, pasaporte, NSS)",
    "contacto": "Contacto y domicilio (correo, teléfono, dirección postal)",
    "economicos": "Datos económicos (IBAN, tarjetas)",
    "bienes": "Bienes (matrículas, referencias catastrales)",
    "nombres": "Nombres de personas físicas",
    "empresas": "Denominaciones sociales",
    "sensibles": "Datos del artículo 9 del RGPD",
}

CATEGORIAS_POR_DEFECTO = tuple(CATEGORIAS)


@dataclass
class Entidad:
    """Una aparición concreta de un dato personal dentro de un bloque de texto."""

    tipo: str
    inicio: int
    fin: int
    valor: str
    bloque: int = 0
    confianza: float = 1.0
    clave: str | None = None      # clave de coreferencia
    etiqueta: str | None = None   # marcador final asignado

    @property
    def longitud(self) -> int:
        return self.fin - self.inicio


@dataclass
class Registro:
    """Correspondencia entre valores originales y marcadores asignados."""

    asignaciones: dict[str, str] = field(default_factory=dict)   # clave -> etiqueta
    valores: dict[str, list[str]] = field(default_factory=dict)  # etiqueta -> valores vistos
    contadores: dict[str, int] = field(default_factory=dict)
    tipos: dict[str, str] = field(default_factory=dict)          # etiqueta -> tipo

    def etiqueta_para(self, tipo: str, clave: str, generador: Callable[[str, int], str]) -> str:
        if clave in self.asignaciones:
            return self.asignaciones[clave]
        raiz = TIPOS[tipo].etiqueta
        numero = self.contadores.get(raiz, 0) + 1
        self.contadores[raiz] = numero
        etiqueta = generador(tipo, numero)
        self.asignaciones[clave] = etiqueta
        self.tipos[etiqueta] = tipo
        return etiqueta

    def anotar(self, etiqueta: str, valor: str) -> None:
        vistos = self.valores.setdefault(etiqueta, [])
        if valor not in vistos:
            vistos.append(valor)
