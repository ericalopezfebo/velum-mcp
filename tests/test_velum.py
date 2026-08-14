"""Comprobaciones sobre el fragmento de demanda de referencia."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from velum.motor import Anonimizador, revisar  # noqa: E402
from velum.validadores import cif_valido, dni_valido, iban_valido, nie_valido  # noqa: E402

FRAGMENTO = (
    "Que D. Juan Antonio Pérez Molina, mayor de edad, con DNI 45.892.113-Y y "
    "domicilio en la calle Serrano n.º 47, 3.º B, 28001 Madrid, interpone demanda "
    "de reclamación de cantidad frente a Inversiones Delta Sur, S.L., con CIF "
    "B-87456323, por la transferencia de 34.500 € ordenada el 12 de marzo de 2024 "
    "a la cuenta ES91 2100 0418 4502 0005 1332, sin que a fecha de hoy se haya "
    "prestado el servicio contratado. Resultan de aplicación los artículos 1101 y "
    "1124 del Código Civil."
)

INTACTO = ("34.500 €", "12 de marzo de 2024", "artículos 1101 y 1124", "Código Civil")


def anonimizar(texto: str, **kwargs) -> str:
    return "\n".join(Anonimizador(**kwargs).procesar(texto.split("\n")).bloques)


def test_validadores_con_digito_de_control():
    assert dni_valido("45.892.113-Y")
    assert not dni_valido("45.892.113-X")
    assert nie_valido("X1234567L")
    assert cif_valido("B-87456323")
    assert iban_valido("ES91 2100 0418 4502 0005 1332")
    assert not iban_valido("ES91 2100 0418 4502 0005 1333")


def test_el_fondo_del_asunto_no_se_toca():
    salida = anonimizar(FRAGMENTO)
    for trozo in INTACTO:
        assert trozo in salida, f"se ha perdido: {trozo}"


def test_los_identificadores_se_sustituyen():
    salida = anonimizar(FRAGMENTO)
    for dato in ("45.892.113-Y", "B-87456323", "ES91 2100 0418 4502 0005 1332",
                 "Juan Antonio Pérez Molina", "Serrano"):
        assert dato not in salida, f"ha quedado sin sustituir: {dato}"


def test_etiquetas_esperadas():
    salida = anonimizar(FRAGMENTO)
    for etiqueta in ("[ACTOR_1]", "[DNI_1]", "[DIRECCION_1]", "[EMPRESA_1]",
                     "[CIF_1]", "[IBAN_1]"):
        assert etiqueta in salida, f"falta la etiqueta {etiqueta}"


def test_coreferencia_persona():
    texto = (
        "D. Juan Antonio Pérez Molina compareció. Posteriormente, el Sr. Pérez "
        "ratificó su escrito."
    )
    salida = anonimizar(texto)
    assert salida.count("[ACTOR_1]") + salida.count("[PERSONA_1]") == 2


def test_apellido_ambiguo_no_se_toca():
    texto = (
        "D. Juan Antonio Pérez Molina y D.ª Marta Pérez Lorenzo comparecieron. "
        "El Sr. Pérez guardó silencio."
    )
    salida = anonimizar(texto)
    assert "el Sr. Pérez".lower() in salida.lower()


def test_revisar_no_modifica_el_texto():
    resultado = revisar(FRAGMENTO.split("\n"))
    assert "\n".join(resultado.bloques) == FRAGMENTO
    assert resultado.total >= 5


def test_modo_redaccion_y_seudonimo():
    tachado = anonimizar(FRAGMENTO, modo="redaccion")
    assert "█" in tachado and "45.892.113-Y" not in tachado

    seudonimo = anonimizar(FRAGMENTO, modo="seudonimo")
    assert "Juan Antonio Pérez Molina" not in seudonimo
    assert "34.500 €" in seudonimo


def test_categorias_selectivas():
    solo_identificadores = anonimizar(FRAGMENTO, categorias={"identificadores"})
    assert "[DNI_1]" in solo_identificadores
    assert "Juan Antonio Pérez Molina" in solo_identificadores


def test_no_confunde_numero_de_articulo_con_telefono():
    texto = "Conforme al artículo 611234567 no procede."
    assert "[TELEFONO_1]" not in anonimizar(texto)


if __name__ == "__main__":
    fallos = 0
    for nombre, funcion in sorted(globals().items()):
        if not nombre.startswith("test_"):
            continue
        try:
            funcion()
            print(f"  ok   {nombre}")
        except AssertionError as error:
            fallos += 1
            print(f"  FALLA {nombre}: {error}")
    print()
    print("Salida del fragmento de referencia:\n")
    print(anonimizar(FRAGMENTO))
    sys.exit(1 if fallos else 0)
