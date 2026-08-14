"""Pruebas de la frontera de seguridad.

La promesa de VELUM es que el expediente no sale del ordenador ni entra en la
conversación. Estas pruebas la comprueban; sin ellas, la promesa es un párrafo
del README.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

FRAGMENTO = (
    "Que D. Juan Antonio Pérez Molina, mayor de edad, con DNI 45.892.113-Y y "
    "domicilio en la calle Serrano n.º 47, 3.º B, 28001 Madrid, interpone demanda "
    "frente a Inversiones Delta Sur, S.L., con CIF B-87456323, por 34.500 € "
    "ordenados el 12 de marzo de 2024. Artículos 1101 y 1124 del Código Civil."
)

# Valores que jamás deben aparecer en una respuesta sobre un FICHERO.
CANARIOS = (
    "Juan Antonio Pérez Molina",
    "45.892.113-Y",
    "B-87456323",
    "Serrano",
    "Inversiones Delta Sur",
)


def _preparar(tmp: Path) -> Path:
    tmp.mkdir(parents=True, exist_ok=True)
    fichero = tmp / "demanda.md"
    fichero.write_text(FRAGMENTO, encoding="utf-8")
    os.environ["VELUM_RAICES"] = str(tmp)
    import velum.server as servidor

    servidor._RAICES = None
    return fichero


# --- Raíces autorizadas ----------------------------------------------------

def test_rechaza_ruta_fuera_de_las_raices(tmp_path):
    from velum.seguridad import ErrorSeguro, RaicesAutorizadas

    permitida = tmp_path / "autorizada"
    prohibida = tmp_path / "prohibida"
    permitida.mkdir()
    prohibida.mkdir()
    secreto = prohibida / "expediente.md"
    secreto.write_text(FRAGMENTO, encoding="utf-8")

    raices = RaicesAutorizadas({permitida})
    try:
        raices.resolver_entrada(str(secreto))
    except ErrorSeguro as error:
        assert error.codigo.value == "PATH_NOT_AUTHORIZED"
    else:
        raise AssertionError("se ha abierto un fichero fuera de las raíces autorizadas")


def test_rechaza_ruta_relativa_y_travesia(tmp_path):
    from velum.seguridad import ErrorSeguro, RaicesAutorizadas

    (tmp_path / "ok").mkdir()
    raices = RaicesAutorizadas({tmp_path / "ok"})
    for candidata in ("relativa.md", str(tmp_path / "ok" / ".." / "fuera.md")):
        try:
            raices.resolver_entrada(candidata)
        except ErrorSeguro:
            continue
        raise AssertionError(f"ruta aceptada indebidamente: {candidata}")


def test_firma_incoherente_con_la_extension(tmp_path):
    from velum.seguridad import ErrorSeguro, validar_firma

    falso = tmp_path / "falso.docx"
    falso.write_text("esto no es un docx", encoding="utf-8")
    try:
        validar_firma(falso)
    except ErrorSeguro as error:
        assert error.codigo.value == "MALFORMED_DOCUMENT"
    else:
        raise AssertionError("un .docx sin firma PK ha pasado la validación")


# --- Fuga de contenido -----------------------------------------------------

def test_revisar_documento_no_devuelve_contenido(tmp_path):
    fichero = _preparar(tmp_path / "casos")
    from velum.server import revisar_documento

    salida = revisar_documento(str(fichero)).model_dump_json()
    for canario in CANARIOS:
        assert canario not in salida, f"se ha filtrado «{canario}»"
    assert "DNI" in salida  # el TIPO sí sale; el VALOR no


def test_anonimizar_documento_no_devuelve_contenido(tmp_path):
    fichero = _preparar(tmp_path / "casos2")
    from velum.server import anonimizar_documento

    salida = anonimizar_documento(str(fichero)).model_dump_json()
    for canario in CANARIOS:
        assert canario not in salida, f"se ha filtrado «{canario}»"


def test_el_sanitizador_bloquea_una_clave_de_contenido():
    from pydantic import BaseModel

    from velum.seguridad import FugaDetectada, sanitizar

    class Indebido(BaseModel):
        fichero: str = "/tmp/x.md"
        contenido: str = "Que D. Juan Antonio Pérez Molina..."

    try:
        sanitizar(Indebido())
    except FugaDetectada:
        return
    raise AssertionError("el sanitizador ha dejado pasar una clave de contenido")


def test_anonimizar_texto_si_puede_devolver_texto():
    from velum.server import anonimizar_texto

    resultado = anonimizar_texto(FRAGMENTO)
    assert "[DNI_1]" in resultado.texto_anonimizado
    assert "45.892.113-Y" not in resultado.texto_anonimizado
    assert "34.500 €" in resultado.texto_anonimizado


# --- Perfil de Puerto Rico -------------------------------------------------

def test_perfil_puerto_rico():
    from velum import perfiles
    from velum.motor import Anonimizador

    perfiles.instalar("PUERTO_RICO")
    texto = (
        "El Sr. Luis A. Rivera Colón, SSN 123-45-6789, con dirección en Urb. Villa "
        "Nevárez, Calle 3 #1023, San Juan, PR 00927, y teléfono (787) 555-1234, "
        "invoca la Regla 10.2 de Procedimiento Civil, 2024 TSPR 41 y 205 DPR 1119 "
        "en el recurso KLAN2024-00456."
    )
    salida = "\n".join(Anonimizador().procesar(texto.split("\n")).bloques)

    for dato in ("123-45-6789", "Villa Nevárez", "555-1234", "Rivera Colón"):
        assert dato not in salida, f"sin sustituir: {dato}"
    for cita in ("Regla 10.2", "2024 TSPR 41", "205 DPR 1119", "KLAN2024-00456"):
        assert cita in salida, f"se ha destruido la cita: {cita}"
