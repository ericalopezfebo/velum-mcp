# VELUM by Abogado Virtual

**Legal Document Anonymization & Privacy MCP**

Quita los datos personales de escritos jurídicos **en el propio ordenador**. Sin
modelo de lenguaje, sin llamadas de red y sin conservar copias: el expediente no
sale del equipo y no entra en la conversación con la IA.

```
Que D. Juan Antonio Pérez Molina, con DNI 45.892.113-Y y domicilio en la calle
Serrano n.º 47, 28001 Madrid, interpone demanda frente a Inversiones Delta Sur,
S.L., CIF B-87456323, por la transferencia de 34.500 € ordenada el 12 de marzo
de 2024 a la cuenta ES91 2100 0418 4502 0005 1332. Artículos 1101 y 1124 CC.
                                   ↓
Que D. [ACTOR_1], con DNI [DNI_1] y domicilio en la [DIRECCION_1], interpone
demanda frente a [EMPRESA_1], CIF [CIF_1], por la transferencia de 34.500 €
ordenada el 12 de marzo de 2024 a la cuenta [IBAN_1]. Artículos 1101 y 1124 CC.
```

El importe, la fecha de los hechos y las citas legales no se tocan. Son el fondo
del asunto, no el dato del cliente.

---

## Por qué

Un expediente pegado en el chat de una IA de consumo se trata fuera del control
del despacho y sin contrato de encargado del tratamiento. Eso choca con los
artículos 28 y 44 del RGPD y con el deber de secreto profesional.

VELUM lo resuelve por la vía más simple: si el documento ya no lleva datos
personales dentro, deja de haber tratamiento que proteger.

**No hay «procesamiento en servidores europeos» porque no hay procesamiento
fuera de su máquina.** La detección es determinista y auditable —reglas,
dígitos de control y léxico jurídico—, y eso se puede comprobar leyendo el
código: no hay una sola llamada de red.

---

## Garantías, y cómo se imponen

| Promesa | Cómo se impone |
| --- | --- |
| El documento no sale del equipo | Sin dependencias de red. Auditable en `src/velum/`. |
| El documento no entra en la conversación | `seguridad/salida.py` reconstruye cada respuesta desde su modelo público y bloquea cualquier clave de contenido. Si algo se filtrara, la respuesta no llega a emitirse. |
| Solo se abre lo autorizado | `seguridad/rutas.py`: raíces declaradas en `VELUM_RAICES`; se rechazan rutas relativas, travesías `..` y enlaces simbólicos. |
| El fichero es lo que dice ser | `seguridad/limites.py`: firma mágica coherente con la extensión y tamaño máximo. |
| Los errores no filtran nada | `seguridad/errores.py`: códigos cerrados y plantillas escritas de antemano. Ningún mensaje deriva de la entrada ni de una excepción. |

Las pruebas de `tests/test_seguridad.py` lo comprueban con canarios: si un
nombre, un DNI o un CIF apareciera en la respuesta de una herramienta
documental, la prueba falla.

---

## Qué se sustituye y qué se respeta

| Se sustituye | Se respeta intacto |
| --- | --- |
| Nombres y apellidos | Importes y cuantías |
| DNI, NIE, CIF, pasaporte, NSS, SSN | Fechas de los hechos |
| Direcciones postales | Artículos, leyes y reglas citadas |
| IBAN y tarjetas | Juzgados y tribunales |
| Teléfonos y correos | Números de procedimiento, autos y rollo |
| Matrículas y referencias catastrales | ECLI, ROJ, TSPR, DPR, KLAN |
| Denominaciones sociales | Estilos, tablas, notas y numeración |
| Datos del artículo 9 del RGPD | El relato de los hechos y los fundamentos |

Las fechas se conservan de serie: en un escrito jurídico suelen ser el hilo del
relato y borrarlas lo deja inservible.

---

## Instalación

```bash
git clone <url-del-repositorio> velum-mcp
cd velum-mcp
python3 -m venv .venv && ./.venv/bin/pip install -e .
```

Python 3.10 o superior.

### Claude Desktop

En `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "velum": {
      "command": "/ruta/absoluta/a/velum-mcp/.venv/bin/velum-mcp",
      "env": {
        "VELUM_RAICES": "/Users/usuario/Documents/Casos",
        "VELUM_JURISDICCION": "PUERTO_RICO"
      }
    }
  }
}
```

`VELUM_RAICES` es obligatorio en la práctica: VELUM solo abre ficheros situados
dentro de esas carpetas. Se pueden indicar varias separadas por `:`. Si no se
declara, se usa `~/Documents`.

`VELUM_JURISDICCION` admite `ESPANA` (por defecto) o `PUERTO_RICO`.

### Claude Code

```bash
claude mcp add velum -e VELUM_RAICES=/ruta/a/casos -- /ruta/a/.venv/bin/velum-mcp
```

---

## Herramientas

| Tool | Qué hace | ¿Devuelve contenido? |
| --- | --- | --- |
| `estado` | Conexión, jurisdicción y carpetas autorizadas | — |
| `revisar_texto` | Qué datos hay en un texto pegado | No |
| `revisar_documento` | Qué datos hay en un fichero | **No** |
| `revisar_carpeta` | Recuento por fichero de una carpeta | **No** |
| `anonimizar_texto` | Sustituye en un texto pegado | Sí, el texto ya anonimizado |
| `anonimizar_documento` | Anonimiza un fichero | **No**: devuelve rutas |
| `anonimizar_carpeta` | Anonimiza una carpeta | **No**: devuelve rutas |

**Modos:** `token` (`[ACTOR_1]`, por defecto), `seudonimo` (nombres falsos
coherentes), `redaccion` (tachado ███), `hash` (etiqueta con huella estable
entre documentos).

**Categorías:** `identificadores`, `contacto`, `economicos`, `bienes`,
`nombres`, `empresas`, `sensibles`.

---

## Qué se entrega

Por cada documento, tres ficheros junto al original —que **no se modifica**:

- `nombre_anonimizado.docx` — mismo formato, mismo aspecto.
- `nombre_anonimizado_acta.json` y `.md` — fecha, huella SHA-256 del original,
  recuento por tipo, método y control de calidad. Sin ningún dato personal.
- `nombre_anonimizado_equivalencias.xlsx` — qué etiqueta sustituyó a qué dato.

> **Anonimizar y seudonimizar no son lo mismo.** Si conserva la tabla de
> equivalencias, jurídicamente lo hecho es **seudonimización** (art. 4.5 RGPD) y
> el documento sigue siendo dato personal para quien tenga acceso a esa tabla.
> Por eso el fichero es opcional y lleva el aviso dentro. Para anonimización en
> sentido estricto, llame con `generar_equivalencias: false`.

---

## Jurisdicciones

**España** (por defecto). DNI, NIE y CIF con letra de control; IBAN con mod 97;
NSS; matrícula; referencia catastral; formas societarias peninsulares; ECLI y
ROJ preservados.

**Puerto Rico** (`VELUM_JURISDICCION=PUERTO_RICO`). Añade SSN, licencia de
conducir, teléfonos 787/939, direcciones con urbanización, barrio, sector y
apartado, ZIP+4, apellidos locales y formas societarias estadounidenses. Preserva
las citas propias del foro: `KLAN`, `KLCE`, `KLRA`, `TSPR`, `DPR`, `LPRA`,
`Civil Núm.`, las Reglas de Procedimiento Civil y los tribunales locales.

Un perfil **amplía** el léxico base, nunca lo sustituye: un escrito
puertorriqueño puede citar jurisprudencia local, federal y española en el mismo
párrafo.

---

## Limitaciones, dichas sin adornos

- **No detecta el cien por cien de los datos personales**, y ninguna herramienta
  lo hace. Un dato puede escaparse por una transcripción defectuosa, por una
  redacción inusual o por ser un dato indirecto que solo identifica en contexto.
- **Sin IA, la cobertura de nombres en prosa libre es menor.** Se detecta con
  tratamiento (`D. Fulano`), con léxico de nombres de pila o por coreferencia
  con un nombre ya identificado. Un apellido suelto y desconocido puede pasar.
- **No se admite PDF.** Los ficheros PDF se enumeran pero no se abren. La
  redacción seria exige eliminar los glifos del fichero, no pintar un rectángulo
  encima; la decisión de dependencia está documentada en
  `docs/PDF_DEPENDENCY_EVALUATION.md` y aún no está tomada.
- **Notas al pie:** la sustitución se hace nodo a nodo, de modo que un dato
  partido entre dos nodos puede escapar. El control de calidad lo señala.

---

## Pruebas

```bash
PYTHONPATH=src ./.venv/bin/python -m pytest tests -q
```

---

## Procedencia

Dos modelos recibieron la misma tarea. El motor de anonimización, el servidor
MCP y el manejo documental proceden de la implementación de Claude. La frontera
de seguridad —raíces autorizadas, sanitizador de salida, códigos de error
cerrados, validación de firma— y el perfil de Puerto Rico proceden del
esqueleto de arquitectura de Codex. La documentación de `docs/` es suya.

---

Ninguna herramienta detecta el cien por cien de los datos personales. La revisión
del documento antes de aportarlo, remitirlo o publicarlo corresponde al
profesional, que conserva su deber de secreto y su responsabilidad bajo el RGPD
y la LOPDGDD.
