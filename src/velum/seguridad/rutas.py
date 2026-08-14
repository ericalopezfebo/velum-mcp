"""Raíces autorizadas del sistema de ficheros.

Sin esto, un mensaje malicioso —o un despiste— basta para que el servidor abra
cualquier fichero del ordenador. VELUM solo trabaja dentro de carpetas que el
usuario ha declarado de antemano en la variable de entorno VELUM_RAICES.

Adaptado de la clase AuthorizedRoots del esqueleto de seguridad de Codex.
"""

from __future__ import annotations

import os
from pathlib import Path

from .errores import CodigoError, ErrorSeguro

VARIABLE_ENTORNO = "VELUM_RAICES"
RAICES_POR_DEFECTO = ("~/Documents",)


class RaicesAutorizadas:
    def __init__(self, entradas: set[Path], salidas: set[Path] | None = None) -> None:
        self._entradas = self._canonicas(entradas)
        self._salidas = self._canonicas(salidas) if salidas else self._entradas

    @staticmethod
    def _canonicas(raices: set[Path]) -> tuple[Path, ...]:
        if not raices:
            raise ValueError("se requiere al menos una raíz autorizada")
        resueltas: list[Path] = []
        for raiz in raices:
            candidata = Path(raiz).expanduser()
            if candidata.is_symlink() or not candidata.is_dir():
                continue
            resueltas.append(candidata.resolve(strict=True))
        if not resueltas:
            raise ValueError("ninguna raíz autorizada es un directorio real")
        return tuple(resueltas)

    @classmethod
    def desde_entorno(cls) -> RaicesAutorizadas:
        crudo = os.environ.get(VARIABLE_ENTORNO, "")
        declaradas = [p for p in (t.strip() for t in crudo.split(os.pathsep)) if p]
        candidatas = declaradas or list(RAICES_POR_DEFECTO)
        return cls({Path(p) for p in candidatas})

    @property
    def entradas(self) -> tuple[str, ...]:
        return tuple(str(r) for r in self._entradas)

    @staticmethod
    def _dentro(ruta: Path, raices: tuple[Path, ...]) -> bool:
        return any(ruta == raiz or raiz in ruta.parents for raiz in raices)

    def resolver_entrada(self, aportada: str | Path, *, extensiones: set[str] | None = None) -> Path:
        return self._resolver(aportada, self._entradas, extensiones=extensiones, debe_existir=True)

    def resolver_carpeta(self, aportada: str | Path) -> Path:
        cruda = Path(aportada).expanduser()
        if not cruda.is_absolute() or any(p == ".." for p in cruda.parts):
            raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA)
        if cruda.is_symlink():
            raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA)
        try:
            candidata = cruda.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA) from error
        if not candidata.is_dir() or not self._dentro(candidata, self._entradas):
            raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA)
        return candidata

    def reservar_salida(self, aportada: str | Path, *, extension: str) -> Path:
        ruta = self._resolver(
            aportada, self._salidas, extensiones={extension}, debe_existir=False
        )
        if not ruta.exists():
            return ruta
        raiz, sufijo, indice = ruta.stem, ruta.suffix, 2
        while True:
            candidata = ruta.with_name(f"{raiz}_{indice}{sufijo}")
            if not candidata.exists():
                return candidata
            indice += 1

    def _resolver(
        self,
        aportada: str | Path,
        raices: tuple[Path, ...],
        *,
        extensiones: set[str] | None,
        debe_existir: bool,
    ) -> Path:
        cruda = Path(aportada).expanduser()
        if not cruda.is_absolute():
            raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA)
        if any(parte == ".." for parte in cruda.parts):
            raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA)
        if cruda.exists() and cruda.is_symlink():
            raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA)
        if extensiones and cruda.suffix.lower() not in {e.lower() for e in extensiones}:
            raise ErrorSeguro(CodigoError.FORMATO_NO_ADMITIDO)
        try:
            padre = cruda.parent.resolve(strict=debe_existir)
            candidata = (padre / cruda.name).resolve(strict=debe_existir)
        except (FileNotFoundError, RuntimeError, OSError) as error:
            raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA) from error
        if not self._dentro(candidata, raices):
            raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA)
        if debe_existir and (not candidata.is_file() or not os.access(candidata, os.R_OK)):
            raise ErrorSeguro(CodigoError.RUTA_NO_AUTORIZADA)
        return candidata
