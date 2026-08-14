# VELUM: uso profesional de IA sin exponer expedientes

VELUM no decide si una información está protegida por attorney-client privilege,
work product, secreto profesional u otra doctrina. Su función es reducir el
riesgo técnico antes de que un documento pueda salir del equipo del abogado.

## Flujo recomendado

```text
Expediente local
    -> VELUM local
    -> detección y anonimización
    -> revisión de residuos
    -> Privacy Gate
    -> copia externa
    -> IA / tercero
```

El expediente original nunca debe enviarse a una IA para que la IA lo anonimice.

## Política conservadora

- La tabla de equivalencias está desactivada por el lanzador seguro.
- Un documento con una tabla reversible no se considera apto para compartir con
  un tercero.
- Hallazgos de alta severidad bloquean el flujo externo.
- Hallazgos de severidad media requieren revisión humana.
- Un estado `SAFE` significa solamente que VELUM no detectó los hallazgos que
  busca; no es una certificación de anonimización absoluta ni de privilegio.
- El abogado conserva el juicio profesional y debe revisar el resultado antes
  de divulgarlo o usarlo ante un tribunal.

## Privacidad y ética profesional

El uso de tecnología no elimina los deberes profesionales. Antes de utilizar un
proveedor externo, el abogado debe evaluar, según las circunstancias, sus
condiciones de servicio, retención, entrenamiento, seguridad, subprocesadores,
ubicación y controles de acceso, y las obligaciones derivadas de la relación con
el cliente.

En Puerto Rico, la competencia tecnológica incluye conocer las capacidades,
limitaciones y riesgos de la tecnología y proteger la información confidencial y
privilegiada. Cuando exista un riesgo significativo de exposición o divulgación,
debe considerarse la comunicación al cliente y el consentimiento informado
cuando corresponda. La ABA aplica principios equivalentes mediante sus reglas
sobre competencia, confidencialidad, supervisión y uso de tecnología.

Estas consideraciones son una guía de diseño de seguridad y no una opinión legal
sobre un caso concreto.

## No confundir

**Anonimización:** no debe existir una vía razonable para volver a identificar a
la persona usando la información que se conserva.

**Seudonimización:** los identificadores son sustituidos, pero existe información
adicional que permite volver a atribuirlos. Una tabla de equivalencias es un
caso típico.

**Privilegio/confidencialidad:** no son sinónimos de anonimización. Un documento
puede seguir conteniendo información confidencial aunque no tenga nombres.

## Regla operativa

> Si existe duda razonable sobre si el documento puede salir del entorno del
> despacho, no se comparte todavía. Se ejecuta una nueva revisión y el abogado
> decide.
