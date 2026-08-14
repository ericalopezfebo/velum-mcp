# VELUM by Abogado Virtual

**Legal AI Privacy & Anonymization MCP for Puerto Rico and U.S. lawyers**

VELUM ayuda a abogados a utilizar inteligencia artificial sin exponer innecesariamente la información confidencial de sus clientes. Procesa documentos jurídicos **localmente**, sin enviar el expediente a una IA externa para anonimizarlo.

> **Expediente local → VELUM → anonimización → revisión de residuos → Privacy Gate → copia externa → IA**

VELUM está diseñado para apoyar las obligaciones profesionales relacionadas con confidencialidad, competencia tecnológica, supervisión del abogado y protección de información confidencial. Su diseño toma en cuenta las reglas profesionales aplicables en Puerto Rico y el marco de responsabilidad profesional de la ABA.

**VELUM no certifica que un documento sea anónimo, no determina attorney-client privilege o work product y no sustituye el juicio profesional del abogado.**

---

## Ejemplo: Puerto Rico

Documento original:

```text
Que Carlos Javier Rivera Morales, vecino de Bayamón, Puerto Rico,
representado por la Lcda. Andrea M. Vega Rosario, comparece ante este
Honorable Tribunal y solicita que se declare con lugar la presente
contestación a la demanda. El asunto surge de un contrato de construcción
suscrito el 15 de enero de 2025 por la cantidad de $85,000.00.

Civil Núm. BY2026CV00482.
```

Después de VELUM:

```text
Que [DEMANDADO_1], vecino de [MUNICIPIO_1], Puerto Rico,
representado por [LETRADO_1], comparece ante este Honorable Tribunal y
solicita que se declare con lugar la presente contestación a la demanda.
El asunto surge de un contrato de construcción suscrito el [FECHA_1]
por la cantidad de $85,000.00.

Civil Núm. [NUMERO_CASO_1].
```

VELUM procura conservar el contenido jurídico necesario para comprender el asunto, incluyendo cuantías, hechos y citas legales, mientras sustituye identificadores configurados como información personal o del expediente. La política concreta depende de la jurisdicción y del modo de salida.

---

## Por qué existe VELUM

Un abogado no debería tener que escoger entre utilizar IA y entregar el expediente confidencial a un proveedor externo para que la propia IA lo anonimice.

VELUM invierte el flujo: **la información se reduce localmente antes de llegar a la IA**.

La detección es determinista y auditable: patrones, validadores, léxico jurídico y reglas específicas de jurisdicción. No se utiliza un modelo de lenguaje para decidir qué información debe salir del equipo.

Las herramientas que trabajan con ficheros están diseñadas para devolver rutas, recuentos, etiquetas y resultados estructurados, no el contenido original del expediente. Un sanitizador de salida impone esta frontera en el código.

---

## Privacy Gate

La anonimización no es suficiente por sí sola. VELUM incorpora un **Privacy Gate** para separar el procesamiento técnico de la decisión profesional sobre compartir un documento.

| Estado | Significado |
| --- | --- |
| `SAFE` | VELUM no detectó los hallazgos que busca. **No es una certificación jurídica.** |
| `REVIEW_REQUIRED` | Existen hallazgos que requieren revisión humana antes de compartir. |
| `BLOCKED` | Se detectó un riesgo que impide el flujo externo hasta corregirlo. |

El modo seguro bloquea situaciones como mapas reversibles de equivalencias y hallazgos de alta severidad.

### Regla práctica

> Si existe duda razonable sobre si el documento puede salir del entorno del despacho, no se comparte todavía. Se ejecuta una nueva revisión y el abogado decide.

---

## Privacidad profesional y uso de IA

VELUM está pensado como **control técnico**, no como sustituto del análisis ético o jurídico.

Antes de utilizar un proveedor externo, el abogado debe evaluar, según las circunstancias del caso, sus términos de servicio, retención, uso para entrenamiento, seguridad, subprocesadores, controles de acceso, ubicación de los datos y cualquier obligación asumida frente al cliente.

La tecnología tampoco elimina la obligación de revisar el resultado. Un abogado conserva responsabilidad por el contenido que utiliza, presenta ante un tribunal o comunica al cliente.

En Puerto Rico, el diseño de VELUM presta especial atención a la competencia y diligencia tecnológica, la protección de información confidencial y privilegiada y la supervisión profesional. El marco de la ABA se utiliza como referencia adicional para el uso responsable de tecnología y herramientas de IA.

**Esto es documentación de diseño y seguridad, no una opinión legal sobre un caso concreto.**

---

## Anonimización no es lo mismo que seudonimización

**Anonimización:** busca eliminar la posibilidad razonable de identificar nuevamente a una persona utilizando la información conservada.

**Seudonimización:** sustituye identificadores, pero existe información adicional que permite volver a atribuirlos. Una tabla de equivalencias es un ejemplo típico.

**Confidencialidad / privilege / work product:** son conceptos jurídicos distintos. El hecho de eliminar nombres no significa que el resto del documento deje de estar protegido o sea apropiado para divulgarse.

Por eso el modo de preparación para uso externo no debe conservar una tabla reversible.

---

## Qué se sustituye y qué se preserva

| Puede sustituirse | Normalmente se preserva cuando es parte del contexto jurídico |
| --- | --- |
| Nombres y apellidos | Importes y cuantías |
| SSN y otros identificadores personales | Fechas relevantes para el relato |
| Direcciones | Estatutos, reglas y artículos citados |
| Teléfonos y correos | Tribunales y foros jurídicos |
| Información bancaria | Citas jurisprudenciales |
| Matrículas y otros identificadores | Numeración jurídica necesaria para entender el argumento |
| Denominaciones de partes y entidades | ECLI y referencias de jurisprudencia, cuando correspondan |

La preservación no es absoluta: un número de caso, una fecha o un tribunal pueden ser identificadores del expediente. Por eso el Privacy Gate también considera **identificadores del caso y riesgo de reidentificación**, no solamente PII tradicional.

---

## Puerto Rico

El perfil `PUERTO_RICO` amplía el motor base con patrones y léxico propios de la práctica puertorriqueña.

Incluye, entre otros:

- `KLAN`, `KLCE`, `KLRA`, `TSPR`, `DPR` y `LPRA`;
- `Civil Núm.`, `Caso Núm.` y otros marcadores de expediente;
- Tribunal General de Justicia, Tribunal de Apelaciones y Tribunal Supremo de Puerto Rico;
- CASP y otros foros administrativos configurados;
- teléfonos 787 y 939;
- direcciones con urbanización, barrio, sector, carretera, apartado y códigos postales de Puerto Rico;
- formas societarias habituales en Puerto Rico y Estados Unidos.

VELUM preserva las referencias jurídicas que son necesarias para el análisis. Por ejemplo, en una cita como `Pueblo v. Pérez, 202 DPR 123 (2019)`, el nombre de la autoridad no debe tratarse automáticamente como si fuera el nombre de una parte del expediente.

Puerto Rico también comparte con la práctica federal estadounidense categorías como SSN, identificadores bancarios y citas federales; por eso el perfil local se apoya en la cobertura de Estados Unidos.

---

## Estados Unidos

El perfil `ESTADOS_UNIDOS` está orientado a la práctica jurídica estadounidense e incluye categorías como SSN, EIN, teléfonos, direcciones, identificadores profesionales y referencias del sistema federal, además de preservar citas jurídicas y números de procedimiento cuando forman parte del contexto legal.

El objetivo de VELUM es servir tanto a abogados de Puerto Rico como a la comunidad jurídica hispana que ejerce en Estados Unidos.

---

## Seguridad por diseño

| Promesa | Cómo se intenta imponer |
| --- | --- |
| El expediente permanece local durante el procesamiento | El motor de anonimización no necesita una IA ni una llamada de red |
| Las herramientas documentales no devuelven el contenido original | El servidor expone resultados estructurados y el sanitizador de salida bloquea contenido documental |
| Solo se abren rutas autorizadas | `seguridad/rutas.py` restringe las raíces configuradas |
| Los errores no reproducen información de entrada | `seguridad/errores.py` usa códigos y mensajes cerrados |
| El flujo externo tiene un control explícito | `privacidad/gate.py` aplica `SAFE`, `REVIEW_REQUIRED` o `BLOCKED` |
| El modo seguro evita mapas reversibles | `secure_server.py` desactiva equivalencias salvo habilitación explícita |

Estas son propiedades técnicas del software, no garantías absolutas de anonimización ni de cumplimiento ético.

---

## Qué se entrega

El original no se modifica. El flujo puede producir:

- una copia anonimizada;
- un acta de auditoría;
- un informe de privacidad;
- opcionalmente, una tabla de equivalencias para **uso interno**.

La tabla reversible no forma parte del paquete destinado a una IA o tercero en el modo seguro.

Los artefactos de auditoría internos pueden contener información que no debe publicarse. Por ejemplo, una huella del documento original puede ser útil para control interno, pero no necesariamente debe acompañar a una copia pública.

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

`VELUM_RAICES` limita los ficheros que VELUM puede abrir. Se pueden indicar varias raíces según la plataforma.

### Claude Code

```bash
claude mcp add velum -e VELUM_RAICES=/ruta/a/casos -e VELUM_JURISDICCION=PUERTO_RICO -- /ruta/a/.venv/bin/velum-mcp
```

---

## Herramientas

| Tool | Qué hace | ¿Devuelve contenido original? |
| --- | --- | --- |
| `estado` | Conexión, jurisdicción y carpetas autorizadas | No |
| `revisar_texto` | Detecta categorías en texto proporcionado directamente | No reproduce los valores detectados |
| `revisar_documento` | Audita un fichero | No |
| `revisar_carpeta` | Audita una carpeta | No |
| `anonimizar_texto` | Anonimiza texto que el usuario ya decidió pegar en el chat | Devuelve texto ya procesado |
| `anonimizar_documento` | Anonimiza un fichero local | No: devuelve rutas y resultados |
| `anonimizar_carpeta` | Procesa documentos locales | No: devuelve rutas y resultados |

**Modos:** `token`, `seudonimo`, `redaccion` y `hash`, según el perfil y la operación.

La tabla de equivalencias debe considerarse un artefacto interno y reversible; el modo seguro no la utiliza para preparar documentos destinados a terceros.

---

## Limitaciones

- Ninguna herramienta detecta el cien por cien de la información personal o de los identificadores indirectos.
- Sin un modelo de lenguaje, algunos nombres o referencias atípicas pueden escapar a las reglas deterministas.
- La reidentificación puede producirse por la combinación de hechos aparentemente inocuos.
- La metadata de un documento puede contener información distinta de la que aparece visualmente; por eso la preparación externa debe sanitizar también las propiedades y revisiones cuando la herramienta lo soporte.
- Un documento que supera el Privacy Gate sigue requiriendo revisión profesional.

---

## Pruebas

```bash
PYTHONPATH=src ./.venv/bin/python -m pytest tests -q
```

---

## Licencia

MIT.

VELUM es una herramienta técnica para reducir riesgo de exposición de información. No constituye asesoramiento jurídico, certificación de privilege, certificación de cumplimiento profesional ni garantía de anonimización absoluta.
