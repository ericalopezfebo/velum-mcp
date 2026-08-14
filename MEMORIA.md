# VELUM — instrucción de memoria y biblioteca de prompts

## 1. Instrucción permanente (péguela una vez en el chat)

Sin esta instrucción, la IA abrirá el documento por su cuenta «para ayudar», y en
ese momento ya habrá leído el expediente del cliente. Copie el párrafo entero:

> Actualiza tu memoria con esta instrucción permanente: siempre que te pida
> anonimizar o revisar uno o varios documentos, **NO los abras ni leas su
> contenido tú mismo** con Read, con bash, ni con ninguna otra herramienta. Usa
> exclusivamente las herramientas de VELUM (`anonimizar_documento`,
> `anonimizar_carpeta`, `revisar_documento`, `revisar_carpeta`), que procesan el
> fichero íntegramente en mi propio ordenador, sin llamadas de red y sin
> conservar copias. Tú limítate a pasarles la ruta del fichero y a contarme el
> resultado: cuántos datos, de qué tipo y dónde ha quedado el documento
> anonimizado. No copies, no cites, no resumas ni reproduzcas el contenido de un
> documento antes de anonimizarlo: es material sujeto al RGPD y al secreto
> profesional, y no debe pasar por ningún sitio que no sea VELUM. Si te pego
> texto directamente en el chat, adviérteme de que ese texto ya ha salido de mi
> ordenador y recomiéndame usar la ruta del fichero en su lugar.

---

## 2. Prompts de trabajo

### Anonimizar una carpeta completa

> Anonimiza todos los expedientes de la carpeta `C:\Casos\Pérez` y déjalos listos
> para el perito.

VELUM recorre la carpeta y las subcarpetas, procesa lo compatible, enumera lo que
no lo es sin abrirlo y deja junto a cada expediente el documento anonimizado, su
acta y su tabla de equivalencias.

### Saber qué hay dentro sin leerlo

> ¿Qué datos personales hay en los documentos de esta carpeta? No los leas, solo
> dime cuántos y de qué tipo.

Usa `revisar_carpeta`. Devuelve el recuento por tipo y avisa si hay datos del
artículo 9 del RGPD o de personas menores de edad. Nunca el contenido.

### Anonimizar conservando el hilo del relato

> Anonimiza esta demanda pero deja las fechas y los números de procedimiento como
> están.

Es el comportamiento por defecto: fechas, importes, artículos, órganos judiciales
y números de procedimiento están en la lista de zonas protegidas.

### Preparar sentencias para publicar

> Prepara para publicar en el blog del despacho las sentencias de esta carpeta,
> con los nombres tachados.

Equivale a `anonimizar_carpeta` con `modo: "redaccion"` y
`generar_equivalencias: false`. Sin tabla reversible, lo hecho es anonimización
en sentido estricto y no seudonimización del artículo 4.5 del RGPD.

### Anonimizar solo los identificadores

> Anonimiza este escrito pero sustituye únicamente DNI, CIF, IBAN y direcciones;
> los nombres déjalos.

`categorias: ["identificadores", "contacto", "economicos"]`.

### Seudónimos coherentes para un informe pericial

> Anonimiza estos expedientes con nombres falsos en lugar de etiquetas, para que
> el perito pueda leerlos con naturalidad.

`modo: "seudonimo"`. Cada persona recibe siempre el mismo nombre falso dentro del
documento.

---

## 3. Advertencia que debe acompañar a todo resultado

Ninguna herramienta detecta el cien por cien de los datos personales. La revisión
del documento antes de aportarlo, remitirlo o publicarlo corresponde al
profesional, que conserva su deber de secreto y su responsabilidad bajo el RGPD y
la LOPDGDD.
