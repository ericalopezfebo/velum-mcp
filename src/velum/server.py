"""VELUM by Abogado Virtual — servidor MCP.

Legal Document Anonymization & Privacy MCP.

Principio de diseño, y es el que justifica la herramienta: ninguna tool que
trabaje sobre un fichero devuelve su contenido. Devuelve rutas, recuentos y
etiquetas. El expediente no entra en la conversación.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from . import __version__
from .acta import (
    AVISO_ARTICULO_4_5,
    DESCARGO,
    construir_acta,
    escribir_acta,
    escribir_equivalencias,
)
from .documentos import (
    EXTENSIONES_SOPORTADAS,
    FormatoNoSoportado,
    abrir,
    guardar,
    hash_fichero,
    listar_carpeta,
    ruta_de_salida,
)
from .modelo import CATEGORIAS, CATEGORIAS_POR_DEFECTO, TIPOS
from .motor import Anonimizador, revisar as revisar_bloques
from . import perfiles
from .seguridad import (
    LIMITES,
    CodigoError,
    ErrorSeguro,
    RaicesAutorizadas,
    sanitizar,
    validar_firma,
    validar_tamano,
)

# El SDK renombró FastMCP a MCPServer en la versión 2. Se admiten ambas.
try:
    from mcp.server.mcpserver import MCPServer as _Servidor  # SDK >= 2.0
except ImportError:  # pragma: no cover
    try:
        from mcp.server.fastmcp import FastMCP as _Servidor  # SDK 1.x
    except ImportError as error:
        raise SystemExit(
            "Falta el SDK de MCP. Instale las dependencias:  pip install -e ."
        ) from error


mcp = _Servidor(
    "velum",
    version=__version__,
    instructions=(
        "VELUM by Abogado Virtual quita los datos personales de documentos jurídicos "
        "en el propio ordenador del usuario, sin IA y sin llamadas externas.\n\n"
        "REGLA DE USO OBLIGATORIA: cuando el usuario pida anonimizar o revisar uno o "
        "varios documentos, NO abras ni leas el fichero por tu cuenta con ninguna otra "
        "herramienta. Pasa la ruta a las tools de VELUM y limítate a informar del "
        "resultado. No copies, no cites, no resumas ni reproduzcas el contenido de un "
        "documento antes de anonimizarlo: es material sujeto al RGPD y al secreto "
        "profesional.\n\n"
        "Las tools que trabajan sobre ficheros nunca devuelven su contenido: devuelven "
        "rutas, recuentos y etiquetas."
    ),
)


# ---------------------------------------------------------------------------
# Esquemas de salida
# ---------------------------------------------------------------------------

class Estado(BaseModel):
    herramienta: str
    version: str
    procesamiento: str
    entorno: str
    formatos_admitidos: list[str]
    jurisdiccion: str
    carpetas_autorizadas: list[str]
    categorias_disponibles: dict[str, str]
    modos_disponibles: list[str]
    dependencias: dict[str, bool]
    advertencia: str


class Recuento(BaseModel):
    tipo: str
    descripcion: str
    categoria: str
    apariciones: int
    entidades_distintas: int


class Informe(BaseModel):
    """Qué datos hay. Nunca sus valores."""

    fichero: str | None = None
    total_datos_personales: int
    entidades_distintas: int
    por_tipo: list[Recuento]
    por_categoria: dict[str, int]
    articulo_9_rgpd: bool
    menciones_articulo_9: int = 0
    datos_de_menores: bool = False
    advertencia: str = DESCARGO
    # Nota: antes había aquí un campo `contenido_reproducido: bool = False`.
    # Se retiró porque una declaración del propio servidor no prueba nada: el
    # invariante lo impone ahora el sanitizador de salida, que además bloqueó
    # este mismo campo por llevar la palabra «contenido» en el nombre.


class TextoAnonimizado(BaseModel):
    texto_anonimizado: str
    total_datos_sustituidos: int
    por_tipo: dict[str, int]
    etiquetas_asignadas: list[str]
    articulo_9_rgpd: bool
    posibles_residuos: int
    advertencia: str = DESCARGO


class DocumentoAnonimizado(BaseModel):
    fichero_origen: str
    fichero_anonimizado: str
    acta: str
    tabla_de_equivalencias: str | None
    hash_sha256_origen: str
    modo: str
    total_datos_sustituidos: int
    por_tipo: dict[str, int]
    articulo_9_rgpd: bool
    datos_de_menores: bool
    posibles_residuos: int
    aviso_reversibilidad: str | None = None
    advertencia: str = DESCARGO


class ResultadoCarpeta(BaseModel):
    carpeta: str
    procesados: int
    omitidos: int
    documentos: list[DocumentoAnonimizado]
    ficheros_omitidos: list[str]
    total_datos_sustituidos: int
    advertencia: str = DESCARGO


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

Modo = Literal["token", "seudonimo", "redaccion", "hash"]

_RAICES: RaicesAutorizadas | None = None


def raices() -> RaicesAutorizadas:
    """Raíces autorizadas, cargadas una sola vez desde VELUM_RAICES."""
    global _RAICES
    if _RAICES is None:
        _RAICES = RaicesAutorizadas.desde_entorno()
    return _RAICES


def _abrir_seguro(ruta_aportada: str):
    """Resuelve, comprueba y abre. Cuatro controles antes de leer un byte."""
    perfiles.instalar()
    camino = raices().resolver_entrada(ruta_aportada, extensiones=EXTENSIONES_SOPORTADAS)
    validar_tamano(camino, LIMITES)
    validar_firma(camino)
    return camino, abrir(camino)


def _devolver(resultado, *, permitir_texto: bool = False):
    """Pasa la respuesta por el sanitizador antes de que salga del servidor.

    Si algo llevara contenido del documento, aquí se levanta `FugaDetectada` y
    la respuesta no llega a emitirse. Es el último control, y es obligatorio
    aunque el código anterior asegure que su resultado es seguro.
    """
    sanitizar(resultado, permitir_texto=permitir_texto)
    return resultado


def _normalizar_categorias(categorias: list[str] | None) -> set[str] | None:
    if not categorias:
        return None
    desconocidas = [c for c in categorias if c not in CATEGORIAS]
    if desconocidas:
        raise ValueError(
            f"Categorías no reconocidas: {', '.join(desconocidas)}. "
            f"Válidas: {', '.join(CATEGORIAS)}"
        )
    return set(categorias)


def _informe(resultado, fichero: str | None) -> Informe:
    por_tipo = []
    for tipo, apariciones in resultado.recuento_por_tipo().items():
        distintas = len({
            e.etiqueta for e in resultado.entidades if e.tipo == tipo and e.etiqueta
        })
        por_tipo.append(
            Recuento(
                tipo=tipo,
                descripcion=TIPOS[tipo].descripcion,
                categoria=TIPOS[tipo].categoria,
                apariciones=apariciones,
                entidades_distintas=distintas or apariciones,
            )
        )
    return Informe(
        fichero=fichero,
        total_datos_personales=resultado.total,
        entidades_distintas=len(resultado.registro.valores),
        por_tipo=por_tipo,
        por_categoria=resultado.recuento_por_categoria(),
        articulo_9_rgpd=resultado.hay_articulo_9,
        menciones_articulo_9=resultado.menciones_articulo_9,
        datos_de_menores=resultado.hay_menores,
    )


def _anonimizar_fichero(
    ruta: Path,
    modo: str,
    categorias: set[str] | None,
    conservar_fechas: bool,
    carpeta_salida: Path | None,
    generar_equivalencias: bool,
) -> DocumentoAnonimizado:
    from .nombres import contar_menciones_articulo_9

    ruta, documento = _abrir_seguro(str(ruta))
    huella = hash_fichero(ruta)
    menciones = sum(contar_menciones_articulo_9(t) for t in documento.bloques)

    anonimizador = Anonimizador(
        modo=modo, categorias=categorias, conservar_fechas=conservar_fechas
    )
    entidades = anonimizador.detectar(documento.bloques)
    anonimizador.etiquetar(entidades)
    sustituciones = anonimizador.sustituciones_por_bloque(entidades)

    documento.bloques = [
        Anonimizador.aplicar_a_texto(texto, sustituciones.get(indice, []))
        for indice, texto in enumerate(documento.bloques)
    ]
    residuos = anonimizador._revisar(documento.bloques)

    from .motor import Resultado

    resultado = Resultado(
        bloques=documento.bloques,
        entidades=entidades,
        registro=anonimizador.registro,
        residuos=residuos,
        menciones_articulo_9=menciones,
    )

    destino = raices().reservar_salida(
        ruta_de_salida(ruta, carpeta_salida), extension=ruta.suffix.lower()
    )
    guardar(documento, destino, sustituciones)

    acta = construir_acta(
        resultado,
        fichero_origen=str(ruta),
        hash_origen=huella,
        fichero_salida=str(destino),
        modo=modo,
        categorias=sorted(categorias) if categorias else list(CATEGORIAS_POR_DEFECTO),
        conservar_fechas=conservar_fechas,
        version=__version__,
    )
    ruta_acta = escribir_acta(acta, destino.with_name(f"{destino.stem}_acta.json"))

    ruta_equivalencias = None
    if generar_equivalencias and resultado.registro.valores:
        ruta_equivalencias = escribir_equivalencias(
            resultado, destino.with_name(f"{destino.stem}_equivalencias.xlsx")
        )

    return DocumentoAnonimizado(
        fichero_origen=str(ruta),
        fichero_anonimizado=str(destino),
        acta=str(ruta_acta),
        tabla_de_equivalencias=str(ruta_equivalencias) if ruta_equivalencias else None,
        hash_sha256_origen=huella,
        modo=modo,
        total_datos_sustituidos=resultado.total,
        por_tipo=resultado.recuento_por_tipo(),
        articulo_9_rgpd=resultado.hay_articulo_9,
        datos_de_menores=resultado.hay_menores,
        posibles_residuos=len(residuos),
        aviso_reversibilidad=AVISO_ARTICULO_4_5 if ruta_equivalencias else None,
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False, "idempotentHint": True}
)
def estado() -> Estado:
    """Comprueba la conexión y explica dónde y cómo se procesan los documentos.

    Úsala cuando el usuario pregunte si VELUM está disponible, qué formatos
    admite o qué garantías de privacidad ofrece.
    """
    dependencias = {}
    for modulo in ("docx", "openpyxl"):
        try:
            __import__(modulo)
            dependencias[modulo] = True
        except ImportError:
            dependencias[modulo] = False

    try:
        autorizadas = list(raices().entradas)
    except (ValueError, OSError):
        autorizadas = []

    return Estado(
        herramienta="VELUM by Abogado Virtual — Legal Document Anonymization & Privacy MCP",
        version=__version__,
        procesamiento=(
            "Íntegramente local. La detección se hace con reglas, dígitos de control y "
            "léxico jurídico. No hay modelo de lenguaje, no hay llamadas de red y no se "
            "conserva ninguna copia: el documento no sale de este equipo. Solo se abren "
            "ficheros situados dentro de las carpetas autorizadas."
        ),
        entorno=f"{platform.system()} {platform.release()} · Python {platform.python_version()}",
        formatos_admitidos=sorted(EXTENSIONES_SOPORTADAS),
        jurisdiccion=perfiles.instalar(),
        carpetas_autorizadas=autorizadas,
        categorias_disponibles=dict(CATEGORIAS),
        modos_disponibles=["token", "seudonimo", "redaccion", "hash"],
        dependencias=dependencias,
        advertencia=DESCARGO,
    )


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False, "idempotentHint": True}
)
def revisar_texto(
    texto: Annotated[str, Field(description="Texto jurídico a examinar.")],
    categorias: Annotated[
        list[str] | None,
        Field(description="Categorías a examinar. Vacío = todas."),
    ] = None,
) -> Informe:
    """Dice QUÉ datos personales contiene un texto, sin modificarlo y sin repetir sus valores.

    Devuelve el recuento por tipo y avisa si hay datos del artículo 9 del RGPD
    o de personas menores de edad.
    """
    resultado = revisar_bloques(texto.split("\n"), _normalizar_categorias(categorias))
    return _informe(resultado, fichero=None)


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False, "idempotentHint": True}
)
def revisar_documento(
    ruta: Annotated[str, Field(description="Ruta absoluta del fichero .docx, .txt o .md.")],
    categorias: Annotated[list[str] | None, Field(description="Categorías a examinar.")] = None,
) -> Informe:
    """Dice qué datos personales hay en un documento SIN devolver su contenido.

    Úsala cuando el usuario pregunte «qué hay dentro» de un expediente. El
    fichero se abre aquí, en el propio ordenador, y a la conversación solo
    llegan recuentos y tipos: ni una línea del documento.
    """
    camino, documento = _abrir_seguro(ruta)
    resultado = revisar_bloques(documento.bloques, _normalizar_categorias(categorias))
    return _devolver(_informe(resultado, fichero=str(camino)))


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False, "idempotentHint": True}
)
def revisar_carpeta(
    ruta: Annotated[str, Field(description="Ruta absoluta de la carpeta.")],
    recursivo: Annotated[bool, Field(description="Incluir subcarpetas.")] = True,
    categorias: Annotated[list[str] | None, Field(description="Categorías a examinar.")] = None,
) -> list[Informe]:
    """Recuento de datos personales de cada documento de una carpeta, sin leer ninguno.

    Devuelve un informe por fichero: cuántos datos y de qué tipo. Nunca el
    contenido.
    """
    carpeta = raices().resolver_carpeta(ruta)
    compatibles, incompatibles = listar_carpeta(carpeta, recursivo)
    seleccionadas = _normalizar_categorias(categorias)

    informes: list[Informe] = []
    for camino in compatibles[: LIMITES.documentos_maximos_carpeta]:
        try:
            _, documento = _abrir_seguro(str(camino))
        except (FormatoNoSoportado, ErrorSeguro, OSError):
            continue
        resultado = revisar_bloques(documento.bloques, seleccionadas)
        informes.append(_devolver(_informe(resultado, fichero=str(camino))))

    for camino in incompatibles:
        informes.append(
            Informe(
                fichero=str(camino),
                total_datos_personales=0,
                entidades_distintas=0,
                por_tipo=[],
                por_categoria={},
                articulo_9_rgpd=False,
                datos_de_menores=False,
                advertencia=(
                    f"Formato no admitido en esta versión ({camino.suffix}). "
                    "No se ha abierto ni examinado."
                ),
            )
        )
    return informes


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False}
)
def anonimizar_texto(
    texto: Annotated[str, Field(description="El texto a anonimizar.")],
    modo: Annotated[
        Modo,
        Field(description="token = [ACTOR_1]; seudonimo = nombres falsos; "
                          "redaccion = tachado; hash = etiqueta con huella estable."),
    ] = "token",
    conservar_fechas: Annotated[
        bool,
        Field(description="Por defecto sí: en un escrito jurídico las fechas son el hilo del relato."),
    ] = True,
    categorias: Annotated[
        list[str] | None,
        Field(description="Categorías a sustituir. Vacío = todas."),
    ] = None,
) -> TextoAnonimizado:
    """Sustituye los datos personales de un texto pegado o dictado en el chat.

    AVISO que debes trasladar al usuario si te pasa un expediente entero: por
    esta vía el texto ya ha pasado por la conversación. Para que el documento
    no salga de su ordenador, dile que use anonimizar_documento con la ruta del
    fichero.
    """
    perfiles.instalar()
    anonimizador = Anonimizador(
        modo=modo,
        categorias=_normalizar_categorias(categorias),
        conservar_fechas=conservar_fechas,
    )
    resultado = anonimizador.procesar(texto.split("\n"))

    return _devolver(TextoAnonimizado(
        texto_anonimizado="\n".join(resultado.bloques),
        total_datos_sustituidos=resultado.total,
        por_tipo=resultado.recuento_por_tipo(),
        etiquetas_asignadas=sorted(resultado.registro.valores),
        articulo_9_rgpd=resultado.hay_articulo_9,
        posibles_residuos=len(resultado.residuos),
    ), permitir_texto=True)


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False}
)
def anonimizar_documento(
    ruta: Annotated[str, Field(description="Ruta absoluta del fichero .docx, .txt o .md.")],
    modo: Annotated[Modo, Field(description="Modo de sustitución.")] = "token",
    conservar_fechas: Annotated[bool, Field(description="Conservar las fechas.")] = True,
    categorias: Annotated[
        list[str] | None,
        Field(description="Categorías a sustituir: identificadores, contacto, economicos, "
                          "bienes, nombres, empresas, sensibles. Vacío = todas."),
    ] = None,
    carpeta_salida: Annotated[
        str | None,
        Field(description="Dónde dejar el resultado. Por defecto, junto al original."),
    ] = None,
    generar_equivalencias: Annotated[
        bool,
        Field(description="Generar la tabla reversible. Si se conserva, el tratamiento "
                          "es seudonimización (art. 4.5 RGPD)."),
    ] = True,
) -> DocumentoAnonimizado:
    """Anonimiza un documento en el propio ordenador y devuelve rutas, no contenido.

    El original no se modifica: se escribe un fichero nuevo con el sufijo
    `_anonimizado`, más el acta con la huella SHA-256 y, si se pide, la tabla
    de equivalencias.

    NO abras el fichero por tu cuenta antes ni después de llamar a esta tool.
    """
    return _devolver(_anonimizar_fichero(
        Path(ruta).expanduser(),
        modo=modo,
        categorias=_normalizar_categorias(categorias),
        conservar_fechas=conservar_fechas,
        carpeta_salida=Path(carpeta_salida).expanduser() if carpeta_salida else None,
        generar_equivalencias=generar_equivalencias,
    ))


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False}
)
def anonimizar_carpeta(
    ruta: Annotated[str, Field(description="Ruta absoluta de la carpeta con los expedientes.")],
    modo: Annotated[Modo, Field(description="Modo de sustitución.")] = "token",
    recursivo: Annotated[bool, Field(description="Incluir subcarpetas.")] = True,
    conservar_fechas: Annotated[bool, Field(description="Conservar las fechas.")] = True,
    categorias: Annotated[list[str] | None, Field(description="Categorías a sustituir.")] = None,
    carpeta_salida: Annotated[
        str | None,
        Field(description="Carpeta de destino. Por defecto, junto a cada original."),
    ] = None,
    generar_equivalencias: Annotated[bool, Field(description="Generar tabla reversible.")] = True,
) -> ResultadoCarpeta:
    """Anonimiza todos los documentos compatibles de una carpeta.

    Cada expediente conserva su propio acta y su propia tabla de equivalencias.
    Los ficheros de formato no admitido se enumeran sin abrirlos.
    """
    carpeta = raices().resolver_carpeta(ruta)
    compatibles, incompatibles = listar_carpeta(carpeta, recursivo)
    seleccionadas = _normalizar_categorias(categorias)
    destino = Path(carpeta_salida).expanduser() if carpeta_salida else None

    documentos: list[DocumentoAnonimizado] = []
    omitidos: list[str] = [str(c) for c in incompatibles]

    for camino in compatibles[: LIMITES.documentos_maximos_carpeta]:
        try:
            documentos.append(
                _anonimizar_fichero(
                    camino,
                    modo=modo,
                    categorias=seleccionadas,
                    conservar_fechas=conservar_fechas,
                    carpeta_salida=destino,
                    generar_equivalencias=generar_equivalencias,
                )
            )
        except (FormatoNoSoportado, ErrorSeguro, OSError) as error:
            codigo = getattr(error, "codigo", CodigoError.ERROR_INTERNO)
            omitidos.append(f"{camino} — {codigo.value}")

    return _devolver(ResultadoCarpeta(
        carpeta=str(Path(ruta).expanduser()),
        procesados=len(documentos),
        omitidos=len(omitidos),
        documentos=documentos,
        ficheros_omitidos=omitidos,
        total_datos_sustituidos=sum(d.total_datos_sustituidos for d in documentos),
    ))


def main() -> None:
    """Arranca el servidor sobre stdio."""
    try:
        mcp.run()
    except KeyboardInterrupt:  # pragma: no cover
        sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
