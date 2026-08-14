"""Genera icon.png (512×512) para el bundle .mcpb.

Un documento con dos líneas tachadas: la idea de VELUM en una sola imagen, y
legible a 16 píxeles. Ejecutar con:

    uv run --with pillow python tools/generar_icono.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

LADO = 512
FONDO = (15, 20, 32, 255)        # tinta muy oscura
PAPEL = (243, 240, 235, 255)     # papel cálido
TACHADO = (15, 20, 32, 255)      # las barras son del color del fondo
LINEA = (176, 172, 165, 255)     # texto no redactado
ACENTO = (198, 164, 92, 255)     # oro apagado


def main() -> None:
    e = 4  # supermuestreo
    lienzo = Image.new("RGBA", (LADO * e, LADO * e), (0, 0, 0, 0))
    d = ImageDraw.Draw(lienzo)

    # Fondo: cuadrado redondeado, esquinas transparentes.
    d.rounded_rectangle((0, 0, LADO * e - 1, LADO * e - 1), radius=112 * e, fill=FONDO)

    # Hoja de papel.
    px0, py0, px1, py1 = 128 * e, 96 * e, 384 * e, 416 * e
    d.rounded_rectangle((px0, py0, px1, py1), radius=16 * e, fill=PAPEL)

    # Líneas del documento: unas normales, otras tachadas.
    margen = 30 * e
    x0, x1 = px0 + margen, px1 - margen
    alto = 20 * e
    hueco = 32 * e
    y = py0 + 46 * e

    plan = [
        ("linea", 1.00),
        ("tachado", 0.86),
        ("linea", 0.72),
        ("tachado", 0.94),
        ("linea", 0.58),
    ]

    for clase, proporcion in plan:
        ancho = int((x1 - x0) * proporcion)
        color = TACHADO if clase == "tachado" else LINEA
        d.rounded_rectangle((x0, y, x0 + ancho, y + alto), radius=6 * e, fill=color)
        y += hueco + alto

    # Filo inferior en oro: la marca del acta.
    d.rounded_rectangle(
        (x0, py1 - 42 * e, x0 + int((x1 - x0) * 0.34), py1 - 30 * e),
        radius=6 * e,
        fill=ACENTO,
    )

    icono = lienzo.resize((LADO, LADO), Image.LANCZOS)
    destino = Path(__file__).resolve().parents[1] / "icon.png"
    icono.save(destino, "PNG")
    print(f"icono escrito en {destino} ({icono.size[0]}x{icono.size[1]})")


if __name__ == "__main__":
    main()
