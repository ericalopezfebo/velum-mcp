"""Perfil de Estados Unidos.

Lo que se comprueba aquí no es solo que los datos personales desaparezcan, sino
que **el aparato de citación sobreviva**. Un escrito federal sin sus citas no
sirve para nada, y anonimizar «Bell Atlantic Corp. v. Twombly» sería un fallo
peor que no anonimizar nada.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

ESCRITO = (
    "Plaintiff Michael Anthony Rodriguez, SSN 123-45-6789, residing at 1234 Main "
    "Street, Suite 500, Springfield, IL 62701, telephone (312) 555-0147, email "
    "m.rodriguez@example.com, brings this action against Delta Holdings, LLC, "
    "EIN 36-4171930, in the United States District Court for the Northern District "
    "of Illinois, Case No. 1:24-cv-01234-ABC. Plaintiff invokes 42 U.S.C. Sec. 1983 "
    "and Fed. R. Civ. P. 12(b)(6), citing Bell Atlantic Corp. v. Twombly, 550 U.S. "
    "544 (2007) and 490 F.3d 143. Damages of $34,500.00 are sought. Counsel for "
    "Plaintiff is Sarah Elizabeth Cohen, Esq. Routing number 021000021."
)

DATOS_PERSONALES = (
    "Michael Anthony Rodriguez",
    "123-45-6789",
    "1234 Main Street",
    "555-0147",
    "m.rodriguez@example.com",
    "36-4171930",
    "Sarah Elizabeth Cohen",
    "021000021",
)

DEBE_SOBREVIVIR = (
    "42 U.S.C. Sec. 1983",
    "Fed. R. Civ. P. 12(b)(6)",
    "Bell Atlantic Corp. v. Twombly",
    "550 U.S. 544",
    "490 F.3d 143",
    "United States District Court",
    "Case No. 1:24-cv-01234-ABC",
    "$34,500.00",
)


def anonimizar(texto: str, jurisdiccion: str = "ESTADOS_UNIDOS") -> str:
    from velum import perfiles
    from velum.motor import Anonimizador

    perfiles.instalar(jurisdiccion)
    return "\n".join(Anonimizador().procesar(texto.split("\n")).bloques)


def test_los_datos_personales_desaparecen():
    salida = anonimizar(ESCRITO)
    for dato in DATOS_PERSONALES:
        assert dato not in salida, f"sin sustituir: {dato}"


def test_las_citas_sobreviven():
    salida = anonimizar(ESCRITO)
    for cita in DEBE_SOBREVIVIR:
        assert cita in salida, f"se ha destruido: {cita}"


def test_papeles_procesales():
    salida = anonimizar(ESCRITO)
    assert "[ACTOR_1]" in salida, "el demandante no se etiquetó como ACTOR"
    assert "[LETRADO_1]" in salida, "el abogado no se etiquetó como LETRADO"


def test_validador_aba():
    from velum.validadores import aba_valido

    assert aba_valido("021000021")      # JPMorgan Chase, dígito de control correcto
    assert aba_valido("011000015")      # Reserva Federal de Boston
    assert not aba_valido("021000022")  # un dígito cambiado
    assert not aba_valido("000000000")


def test_validador_ein():
    from velum.validadores import ein_valido

    assert ein_valido("36-4171930")
    assert not ein_valido("00-1234567")   # prefijo de campus inexistente
    assert not ein_valido("36-0000000")


def test_ssn_rechaza_bloques_no_emitidos():
    salida = anonimizar("The numbers 000-12-3456, 666-12-3456 and 900-12-3456 are not SSNs.")
    for falso in ("000-12-3456", "666-12-3456", "900-12-3456"):
        assert falso in salida, f"se sustituyó un SSN imposible: {falso}"


def test_puerto_rico_apila_sobre_estados_unidos():
    """Un escrito puertorriqueño cita los dos sistemas en el mismo párrafo."""
    texto = (
        "El Sr. Luis A. Rivera Colón, SSN 123-45-6789, presentó su reclamación al "
        "amparo de 42 U.S.C. Sec. 1983 y de la Regla 10.2 de Procedimiento Civil, "
        "citando 2024 TSPR 41 y Bell Atlantic Corp. v. Twombly, 550 U.S. 544, ante "
        "el Tribunal de Primera Instancia en el recurso KLAN2024-00456."
    )
    salida = anonimizar(texto, "PUERTO_RICO")

    for dato in ("Rivera Colón", "123-45-6789"):
        assert dato not in salida, f"sin sustituir: {dato}"
    for cita in ("42 U.S.C. Sec. 1983", "Regla 10.2", "2024 TSPR 41",
                 "Bell Atlantic Corp. v. Twombly", "KLAN2024-00456"):
        assert cita in salida, f"se ha destruido: {cita}"


def test_espana_sigue_intacta():
    """Añadir jurisdicciones no puede degradar la de partida."""
    texto = (
        "Que D. Juan Antonio Pérez Molina, con DNI 45.892.113-Y, interpone demanda "
        "frente a Inversiones Delta Sur, S.L., CIF B-87456323, por 34.500 € "
        "el 12 de marzo de 2024. Artículos 1101 y 1124 del Código Civil."
    )
    salida = anonimizar(texto, "ESPANA")
    for dato in ("Juan Antonio Pérez Molina", "45.892.113-Y", "B-87456323"):
        assert dato not in salida, f"sin sustituir: {dato}"
    for intacto in ("34.500 €", "12 de marzo de 2024", "1101 y 1124", "Código Civil"):
        assert intacto in salida, f"se ha destruido: {intacto}"
