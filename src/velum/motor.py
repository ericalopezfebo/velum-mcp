"""Motor de anonimización.

Orden de trabajo, y el orden importa:

  1. Se marcan las zonas protegidas (importes, fechas, citas, órganos).
  2. Se detecta con reglas y dígito de control.
  3. Se detectan nombres, empresas y datos del artículo 9 con léxico y contexto.
  4. Se une cada persona consigo misma en todo el documento.
  5. Se resuelven solapamientos: gana el hallazgo más largo y más fiable.
  6. Se sustituye sobre el texto original, de derecha a izquierda.
  7. Se relee el resultado por si algo se ha escapado.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from .detectores import detectar_reglas
from .modelo import TIPOS, Entidad, Registro
from .nombres import (
    ContextoNombres,
    contar_menciones_articulo_9,
    detectar_articulo_9,
    detectar_formas_cortas,
    detectar_nombres,
)
from .lexico import SEUDONIMOS_EMPRESA, SEUDONIMOS_PERSONA

MODOS = ("token", "seudonimo", "redaccion", "hash")


@dataclass
class Resultado:
    bloques: list[str]
    entidades: list[Entidad]
    registro: Registro
    residuos: list[Entidad] = field(default_factory=list)
    menciones_articulo_9: int = 0
    """Menciones a categoría especial que solo se avisan, no se sustituyen."""

    @property
    def total(self) -> int:
        return len(self.entidades)

    def recuento_por_tipo(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for entidad in self.entidades:
            conteo[entidad.tipo] = conteo.get(entidad.tipo, 0) + 1
        return dict(sorted(conteo.items(), key=lambda par: -par[1]))

    def recuento_por_categoria(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for entidad in self.entidades:
            categoria = TIPOS[entidad.tipo].categoria
            conteo[categoria] = conteo.get(categoria, 0) + 1
        return dict(sorted(conteo.items(), key=lambda par: -par[1]))

    @property
    def hay_articulo_9(self) -> bool:
        return (
            any(TIPOS[e.tipo].articulo_9 for e in self.entidades)
            or self.menciones_articulo_9 > 0
        )

    @property
    def hay_menores(self) -> bool:
        return any(e.tipo == "MENOR" for e in self.entidades)

    def equivalencias(self) -> list[dict[str, str]]:
        filas = []
        for etiqueta, valores in self.registro.valores.items():
            filas.append(
                {
                    "etiqueta": etiqueta,
                    "tipo": self.registro.tipos.get(etiqueta, ""),
                    "categoria": TIPOS[self.registro.tipos[etiqueta]].categoria
                    if etiqueta in self.registro.tipos
                    else "",
                    "valores_originales": " | ".join(valores),
                    "apariciones": str(
                        sum(1 for e in self.entidades if e.etiqueta == etiqueta)
                    ),
                }
            )
        return sorted(filas, key=lambda f: (f["categoria"], f["etiqueta"]))


class Anonimizador:
    """Anonimiza una lista de bloques de texto manteniendo la coherencia global."""

    def __init__(
        self,
        modo: str = "token",
        categorias: set[str] | None = None,
        conservar_fechas: bool = True,
        semilla: str = "velum",
    ) -> None:
        if modo not in MODOS:
            raise ValueError(f"Modo desconocido: {modo}. Válidos: {', '.join(MODOS)}")
        self.modo = modo
        self.categorias = categorias
        self.conservar_fechas = conservar_fechas
        self.semilla = semilla
        self.registro = Registro()
        self.contexto = ContextoNombres()

    # -- Detección ---------------------------------------------------------

    def detectar(self, bloques: list[str]) -> list[Entidad]:
        hallazgos: list[Entidad] = []

        for indice, texto in enumerate(bloques):
            hallazgos.extend(detectar_reglas(texto, indice, self.categorias))
            hallazgos.extend(detectar_nombres(texto, self.contexto, indice, self.categorias))
            hallazgos.extend(detectar_articulo_9(texto, indice, self.categorias))

        # Segunda pasada: las formas cortas necesitan conocer ya a todas las personas.
        for indice, texto in enumerate(bloques):
            hallazgos.extend(detectar_formas_cortas(texto, self.contexto, indice, self.categorias))

        return self._resolver_solapamientos(hallazgos)

    @staticmethod
    def _resolver_solapamientos(entidades: list[Entidad]) -> list[Entidad]:
        ordenadas = sorted(
            entidades, key=lambda e: (e.bloque, e.inicio, -e.longitud, -e.confianza)
        )
        aceptadas: list[Entidad] = []
        ultimo_fin: dict[int, int] = {}
        for entidad in ordenadas:
            if entidad.inicio < ultimo_fin.get(entidad.bloque, -1):
                continue
            aceptadas.append(entidad)
            ultimo_fin[entidad.bloque] = entidad.fin
        return aceptadas

    # -- Etiquetado --------------------------------------------------------

    def _clave(self, entidad: Entidad) -> str:
        if entidad.clave:
            return entidad.clave
        normalizado = "".join(ch for ch in entidad.valor.upper() if ch.isalnum())
        return f"{entidad.tipo}:{normalizado}"

    def _generar_etiqueta(self, tipo: str, numero: int) -> str:
        raiz = TIPOS[tipo].etiqueta
        if self.modo == "seudonimo":
            if tipo == "EMPRESA":
                return SEUDONIMOS_EMPRESA[(numero - 1) % len(SEUDONIMOS_EMPRESA)]
            if TIPOS[tipo].categoria == "nombres":
                return SEUDONIMOS_PERSONA[(numero - 1) % len(SEUDONIMOS_PERSONA)]
            return f"[{raiz}_{numero}]"
        if self.modo == "hash":
            return f"[{raiz}_{numero}]"
        return f"[{raiz}_{numero}]"

    def _marcador(self, entidad: Entidad, etiqueta: str) -> str:
        if self.modo == "redaccion":
            return "█" * max(4, min(len(entidad.valor), 40))
        if self.modo == "hash":
            digesto = hashlib.sha256(
                (self.semilla + "::" + entidad.valor.upper()).encode("utf-8")
            ).hexdigest()[:10]
            return f"[{TIPOS[entidad.tipo].etiqueta}_{digesto}]"
        return etiqueta

    def etiquetar(self, entidades: list[Entidad]) -> None:
        for entidad in entidades:
            clave = self._clave(entidad)
            etiqueta = self.registro.etiqueta_para(entidad.tipo, clave, self._generar_etiqueta)
            entidad.etiqueta = etiqueta
            self.registro.anotar(etiqueta, entidad.valor)

    # -- Sustitución -------------------------------------------------------

    def sustituciones_por_bloque(
        self, entidades: list[Entidad]
    ) -> dict[int, list[tuple[int, int, str]]]:
        por_bloque: dict[int, list[tuple[int, int, str]]] = {}
        for entidad in entidades:
            marcador = self._marcador(entidad, entidad.etiqueta or "")
            por_bloque.setdefault(entidad.bloque, []).append(
                (entidad.inicio, entidad.fin, marcador)
            )
        for lista in por_bloque.values():
            lista.sort()
        return por_bloque

    @staticmethod
    def aplicar_a_texto(texto: str, sustituciones: list[tuple[int, int, str]]) -> str:
        resultado = texto
        for inicio, fin, marcador in sorted(sustituciones, reverse=True):
            resultado = resultado[:inicio] + marcador + resultado[fin:]
        return resultado

    # -- Orquestación ------------------------------------------------------

    def procesar(self, bloques: list[str]) -> Resultado:
        menciones = sum(contar_menciones_articulo_9(texto) for texto in bloques)

        entidades = self.detectar(bloques)
        self.etiquetar(entidades)
        sustituciones = self.sustituciones_por_bloque(entidades)

        salida = [
            self.aplicar_a_texto(texto, sustituciones.get(indice, []))
            for indice, texto in enumerate(bloques)
        ]

        residuos = self._revisar(salida)
        return Resultado(bloques=salida, entidades=entidades,
                         registro=self.registro, residuos=residuos,
                         menciones_articulo_9=menciones)

    def _revisar(self, bloques: list[str]) -> list[Entidad]:
        """Control de calidad: el documento ya anonimizado vuelve a los detectores."""
        pendientes: list[Entidad] = []
        contexto = ContextoNombres()
        for indice, texto in enumerate(bloques):
            pendientes.extend(detectar_reglas(texto, indice, self.categorias))
            pendientes.extend(detectar_nombres(texto, contexto, indice, self.categorias))
        return self._resolver_solapamientos(pendientes)


def revisar(
    bloques: list[str], categorias: set[str] | None = None
) -> Resultado:
    """Solo detecta: no modifica el texto ni devuelve valores."""
    anonimizador = Anonimizador(categorias=categorias)
    entidades = anonimizador.detectar(bloques)
    anonimizador.etiquetar(entidades)
    return Resultado(
        bloques=bloques,
        entidades=entidades,
        registro=anonimizador.registro,
        menciones_articulo_9=sum(contar_menciones_articulo_9(t) for t in bloques),
    )
