"""Nombres de persona, denominaciones sociales y datos del artículo 9 del RGPD.

Sin modelo de lenguaje. Lo que aquí se usa es lo que un jurista reconoce a
simple vista: el tratamiento que precede al nombre, la forma societaria que lo
cierra, el papel procesal que lo rodea y un léxico de nombres de pila.

Regla de prudencia heredada del planteamiento original: cuando dos personas
comparten apellido, la forma corta («el Sr. Pérez») se deja intacta. Antes no
tocar que sustituir mal.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from .detectores import dentro_de, zonas_protegidas
from . import lexico
from .modelo import Entidad

_MAY = "A-ZÁÉÍÓÚÜÑ"
_MIN = "a-záéíóúüñ"

# Un componente de nombre: «Juan», «Pérez-Molina» o la inicial «J.».
_TOKEN_NOMBRE = rf"(?:[{_MAY}][{_MIN}'’\-]+|[{_MAY}]\.)"
_PARTICULA = r"(?:de\s+la|de\s+los|de\s+las|del|de|y|e|i|van|von|da|dos|do)"

_SECUENCIA_NOMBRE = rf"{_TOKEN_NOMBRE}(?:\s+(?:{_PARTICULA}\s+)?{_TOKEN_NOMBRE}){{0,4}}"

def _compilar_tratamiento() -> re.Pattern[str]:
    return re.compile(rf"(?:{'|'.join(lexico.TRATAMIENTOS)})\s+({_SECUENCIA_NOMBRE})")


def _compilar_nombre_libre() -> re.Pattern[str]:
    return re.compile(rf"\b({_SECUENCIA_NOMBRE})\b")


def _compilar_empresa() -> re.Pattern[str]:
    return re.compile(
        rf"\b((?:[{_MAY}][\w'’\-\.]*|{_PARTICULA})"
        rf"(?:\s+(?:[{_MAY}][\w'’\-\.]*|&|{_PARTICULA})){{0,6}})"
        rf"\s*,?\s+(?:{'|'.join(lexico.FORMAS_SOCIETARIAS)})(?=\W|$)"
    )


def _compilar_forma_corta() -> re.Pattern[str]:
    return re.compile(
        rf"(?:{'|'.join(lexico.TRATAMIENTOS_CORTOS)})\s+"
        rf"({_TOKEN_NOMBRE}(?:\s+(?:{_PARTICULA}\s+)?{_TOKEN_NOMBRE})?)(?=\W|$)"
    )


def _compilar_menciones_art_9() -> re.Pattern[str]:
    return re.compile(
        r"\b(?:" + "|".join(re.escape(m) for m in lexico.MENCIONES_ARTICULO_9) + r")\b",
        re.IGNORECASE,
    )


RE_TRATAMIENTO = _compilar_tratamiento()
RE_NOMBRE_LIBRE = _compilar_nombre_libre()
RE_EMPRESA = _compilar_empresa()
RE_FORMA_CORTA = _compilar_forma_corta()
_RE_MENCIONES_ART_9 = _compilar_menciones_art_9()


def recompilar() -> None:
    """Rehace todos los patrones que dependen del léxico.

    Un perfil jurisdiccional amplía el léxico —tratamientos, formas
    societarias, menciones del artículo 9— después de que este módulo se haya
    importado. Sin esta llamada, las expresiones seguirían siendo las de la
    jurisdicción base.
    """
    global RE_TRATAMIENTO, RE_NOMBRE_LIBRE, RE_EMPRESA, RE_FORMA_CORTA
    global _RE_MENCIONES_ART_9
    RE_TRATAMIENTO = _compilar_tratamiento()
    RE_NOMBRE_LIBRE = _compilar_nombre_libre()
    RE_EMPRESA = _compilar_empresa()
    RE_FORMA_CORTA = _compilar_forma_corta()
    _RE_MENCIONES_ART_9 = _compilar_menciones_art_9()


def normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return re.sub(r"[^\w ]", "", sin_tildes).lower().strip()


def _tokens(nombre: str) -> list[str]:
    return [t for t in normalizar(nombre).split() if t]


def _es_parada(nombre: str) -> bool:
    partes = nombre.replace(".", "").split()
    if not partes:
        return True
    return any(parte in lexico.PARADA for parte in partes)


def _plausible_persona(nombre: str, con_tratamiento: bool) -> bool:
    partes = _tokens(nombre)
    if not partes or _es_parada(nombre):
        return False
    if con_tratamiento:
        return len(partes) >= 1
    if len(partes) < 2:
        return False
    utiles = [p for p in partes if p not in lexico.PARTICULAS]
    if len(utiles) < 2:
        return False
    tiene_pila = utiles[0] in lexico.NOMBRES_PILA
    tiene_apellido = any(p in lexico.APELLIDOS for p in utiles[1:])
    return tiene_pila or (tiene_apellido and len(utiles) >= 3)


@dataclass
class Persona:
    clave: str
    nombre_completo: str
    apellidos: tuple[str, ...]
    rol: str = "PERSONA"
    formas: set[str] = field(default_factory=set)
    """Literales que designan a esta persona: el nombre completo y la cola de
    apellidos («Pérez Molina»), que aparece sola en encabezados y carátulas."""


@dataclass
class ContextoNombres:
    """Estado compartido entre bloques para resolver la coreferencia."""

    personas: dict[str, Persona] = field(default_factory=dict)
    apellido_a_claves: dict[str, set[str]] = field(default_factory=dict)
    empresas: dict[str, str] = field(default_factory=dict)   # clave -> denominación

    def registrar_persona(self, nombre: str, rol: str) -> Persona:
        clave = normalizar(nombre)
        persona = self.personas.get(clave)
        if persona is None:
            partes = [p for p in _tokens(nombre) if p not in lexico.PARTICULAS]
            apellidos = tuple(partes[1:]) if len(partes) > 1 else tuple(partes)
            persona = Persona(clave=clave, nombre_completo=nombre, apellidos=apellidos, rol=rol)
            self.personas[clave] = persona
            for apellido in apellidos:
                self.apellido_a_claves.setdefault(apellido, set()).add(clave)

        persona.formas.add(nombre.strip())
        piezas = [p for p in nombre.split() if p.lower() not in lexico.PARTICULAS]
        if len(piezas) >= 3:
            # «Pérez Molina» a partir de «Juan Antonio Pérez Molina».
            cola = " ".join(piezas[-2:])
            if len(cola) > 6:
                persona.formas.add(cola)
        elif persona.rol == "PERSONA" and rol != "PERSONA":
            persona.rol = rol
        return persona

    def resolver_forma_corta(self, fragmento: str) -> Persona | None:
        """Devuelve la persona si —y solo si— no hay ambigüedad de apellido."""
        partes = [p for p in _tokens(fragmento) if p not in lexico.PARTICULAS]
        if not partes:
            return None
        candidatas: set[str] | None = None
        for parte in partes:
            claves = self.apellido_a_claves.get(parte)
            if claves is None:
                return None
            candidatas = set(claves) if candidatas is None else candidatas & claves
        if not candidatas or len(candidatas) != 1:
            return None
        return self.personas[next(iter(candidatas))]

    def formas_literales(self) -> dict[str, Persona]:
        """Literales que designan sin ambigüedad a una única persona registrada."""
        recuento: dict[str, set[str]] = {}
        for persona in self.personas.values():
            for forma in persona.formas:
                recuento.setdefault(normalizar(forma), set()).add(persona.clave)

        resultado: dict[str, Persona] = {}
        for persona in self.personas.values():
            for forma in persona.formas:
                if len(recuento[normalizar(forma)]) == 1:
                    resultado[forma] = persona
        return resultado

    def registrar_empresa(self, denominacion: str) -> str:
        clave = normalizar(denominacion)
        self.empresas.setdefault(clave, denominacion)
        return clave


def _recortar_parada(nombre: str, inicio: int) -> tuple[str, int]:
    """Quita del principio las palabras que nunca son nombre propio.

    «Plaintiff Michael Anthony Rodriguez» empieza con una palabra de parada,
    pero el nombre está ahí. Rechazar la secuencia entera dejaba al cliente sin
    anonimizar, que es exactamente el fallo que no se puede permitir.
    """
    piezas = nombre.split()
    desplazamiento = 0
    while piezas and piezas[0].replace(".", "") in lexico.PARADA:
        desplazamiento += len(piezas[0]) + 1
        piezas.pop(0)
    return " ".join(piezas), inicio + desplazamiento


def _rol_por_contexto(texto: str, inicio: int, fin: int) -> str:
    """Papel procesal por el disparador MÁS ESPECÍFICO del entorno.

    «Counsel for Plaintiff Sarah Cohen» contiene tanto «counsel for» (letrado)
    como «plaintiff» (actor). Gana el disparador más largo: es el más
    específico, y aquí acierta.
    """
    previo = texto[max(0, inicio - 90):inicio].lower()
    # Ventana amplia: entre el nombre y «interpone demanda» suele mediar todo el
    # inciso de identificación (edad, DNI, domicilio, teléfono).
    posterior = texto[fin:fin + 320].lower()

    mejor_rol, mejor_longitud = "PERSONA", 0

    for rol, disparadores in lexico.ROLES_PREVIOS.items():
        for disparador in disparadores:
            if disparador in previo[-45:] and len(disparador) > mejor_longitud:
                mejor_rol, mejor_longitud = rol, len(disparador)

    if mejor_rol != "PERSONA":
        return mejor_rol

    for rol, disparadores in lexico.ROLES_POSTERIORES.items():
        for disparador in disparadores:
            if disparador in posterior and len(disparador) > mejor_longitud:
                mejor_rol, mejor_longitud = rol, len(disparador)

    return mejor_rol


def detectar_nombres(
    texto: str,
    contexto: ContextoNombres,
    bloque: int = 0,
    categorias: set[str] | None = None,
) -> list[Entidad]:
    """Detecta empresas, personas y datos del artículo 9 en un bloque de texto."""
    protegidas = zonas_protegidas(texto)
    ocupado: list[tuple[int, int]] = []
    entidades: list[Entidad] = []

    def libre(inicio: int, fin: int) -> bool:
        return not dentro_de(inicio, fin, protegidas) and not dentro_de(inicio, fin, ocupado)

    quiere = lambda cat: categorias is None or cat in categorias  # noqa: E731

    # 1) Empresas primero: la forma societaria es la señal más fiable y evita
    #    que «Inversiones Delta Sur» se confunda con un nombre de persona.
    if quiere("empresas"):
        for coincidencia in RE_EMPRESA.finditer(texto):
            inicio, fin = coincidencia.span()
            nucleo = coincidencia.group(1).strip(" ,")
            if not nucleo or _es_parada(nucleo) or not libre(inicio, fin):
                continue
            clave = contexto.registrar_empresa(coincidencia.group(0).strip(" ,"))
            entidades.append(
                Entidad("EMPRESA", inicio, fin, coincidencia.group(0).strip(" ,"),
                        bloque=bloque, clave=f"empresa:{clave}")
            )
            ocupado.append((inicio, fin))

    # 2) Personas con tratamiento: D. Juan Antonio Pérez Molina.
    if quiere("nombres"):
        for coincidencia in RE_TRATAMIENTO.finditer(texto):
            inicio, fin = coincidencia.span(1)
            nombre = coincidencia.group(1).strip()
            if not libre(inicio, fin) or not _plausible_persona(nombre, con_tratamiento=True):
                continue
            if len(_tokens(nombre)) < 2:
                continue  # forma corta: se trata más abajo
            rol = _rol_por_contexto(texto, coincidencia.start(), fin)
            persona = contexto.registrar_persona(nombre, rol)
            entidades.append(
                Entidad(persona.rol, inicio, fin, nombre, bloque=bloque,
                        clave=f"persona:{persona.clave}")
            )
            ocupado.append((inicio, fin))

        # 3) Nombres sin tratamiento, respaldados por el léxico de nombres de pila.
        for coincidencia in RE_NOMBRE_LIBRE.finditer(texto):
            inicio, fin = coincidencia.span(1)
            nombre = coincidencia.group(1).strip()
            # «Plaintiff Michael Anthony Rodriguez»: se recorta la palabra de
            # parada inicial en vez de descartar la secuencia entera.
            nombre, inicio = _recortar_parada(nombre, inicio)
            fin = inicio + len(nombre)
            if not nombre or not libre(inicio, fin):
                continue
            if not _plausible_persona(nombre, con_tratamiento=False):
                continue
            rol = _rol_por_contexto(texto, inicio, fin)
            persona = contexto.registrar_persona(nombre, rol)
            entidades.append(
                Entidad(persona.rol, inicio, fin, nombre, bloque=bloque,
                        clave=f"persona:{persona.clave}", confianza=0.8)
            )
            ocupado.append((inicio, fin))

    # 4) Empresas ya conocidas citadas por su núcleo: «la mercantil Delta Sur».
    if quiere("empresas"):
        for clave, denominacion in list(contexto.empresas.items()):
            nucleo = re.split(r",\s*", denominacion)[0].strip()
            if len(nucleo) < 5:
                continue
            for coincidencia in re.finditer(rf"\b{re.escape(nucleo)}\b", texto):
                inicio, fin = coincidencia.span()
                if not libre(inicio, fin):
                    continue
                entidades.append(
                    Entidad("EMPRESA", inicio, fin, coincidencia.group(0), bloque=bloque,
                            clave=f"empresa:{clave}", confianza=0.9)
                )
                ocupado.append((inicio, fin))

    return entidades


def detectar_formas_cortas(
    texto: str,
    contexto: ContextoNombres,
    bloque: int = 0,
    categorias: set[str] | None = None,
) -> list[Entidad]:
    """Segunda pasada: «el Sr. Pérez» se une con «D. Juan Antonio Pérez Molina».

    Solo actúa cuando el apellido identifica a una única persona ya registrada.
    """
    if categorias is not None and "nombres" not in categorias:
        return []

    protegidas = zonas_protegidas(texto)
    entidades: list[Entidad] = []

    for coincidencia in RE_FORMA_CORTA.finditer(texto):
        inicio, fin = coincidencia.span(1)
        fragmento = coincidencia.group(1).strip()
        if dentro_de(inicio, fin, protegidas):
            continue
        persona = contexto.resolver_forma_corta(fragmento)
        if persona is None:
            continue  # ambigüedad o desconocido: no se toca
        entidades.append(
            Entidad(persona.rol, inicio, fin, fragmento, bloque=bloque,
                    clave=f"persona:{persona.clave}", confianza=0.85)
        )

    # Nombres ya conocidos citados sin tratamiento: carátulas, encabezados,
    # pies de firma, celdas de tabla. Solo si el literal es inequívoco.
    for forma, persona in contexto.formas_literales().items():
        for coincidencia in re.finditer(rf"\b{re.escape(forma)}\b", texto):
            inicio, fin = coincidencia.span()
            if dentro_de(inicio, fin, protegidas):
                continue
            entidades.append(
                Entidad(persona.rol, inicio, fin, coincidencia.group(0), bloque=bloque,
                        clave=f"persona:{persona.clave}", confianza=0.95)
            )

    return entidades


def contar_menciones_articulo_9(texto: str) -> int:
    """Cuenta menciones a categoría especial que NO rigen complemento.

    «informe médico» revela que el expediente contiene datos de salud, pero lo
    que le sigue («aportado como documento n.º 3») no es el dato. Se cuenta para
    avisar; no se sustituye, porque sustituirlo daría falsos positivos.
    """
    return len(_RE_MENCIONES_ART_9.findall(texto))


def detectar_articulo_9(
    texto: str, bloque: int = 0, categorias: set[str] | None = None
) -> list[Entidad]:
    """Detecta el complemento que sigue a un disparador del artículo 9 del RGPD."""
    if categorias is not None and "sensibles" not in categorias:
        return []

    protegidas = zonas_protegidas(texto)
    entidades: list[Entidad] = []

    for tipo, disparadores in lexico.DISPARADORES_ARTICULO_9.items():
        for disparador in disparadores:
            patron = re.compile(
                rf"\b{re.escape(disparador)}\s+([^.,;:\n)]{{3,80}})", re.IGNORECASE
            )
            for coincidencia in patron.finditer(texto):
                inicio, fin = coincidencia.span(1)
                valor = coincidencia.group(1).strip()
                if not valor or dentro_de(inicio, fin, protegidas):
                    continue
                entidades.append(
                    Entidad(tipo, inicio, inicio + len(valor), valor,
                            bloque=bloque, confianza=0.7)
                )
    return entidades
