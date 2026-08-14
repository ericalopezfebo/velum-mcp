"""Léxicos en español. Todo local, sin descargas ni modelos."""

from __future__ import annotations

# Nombres de pila frecuentes en España e Hispanoamérica. No pretende ser
# exhaustivo: sirve para elevar la confianza de una secuencia capitalizada.
NOMBRES_PILA: frozenset[str] = frozenset(
    """
    antonio jose juan manuel francisco david javier daniel carlos miguel rafael pedro
    angel alejandro fernando luis sergio pablo jorge alberto ramon enrique jesus
    vicente eduardo raul ivan ruben oscar andres joaquin santiago victor mario
    diego adrian alvaro marcos gonzalo ignacio hugo martin nicolas emilio julio
    tomas felipe gabriel guillermo lucas mateo roberto salvador agustin arturo
    cesar cristian domingo esteban gerardo gustavo hector isidro jaime jaume joan
    josep lluis marc mohamed nestor octavio olegario patricio ramiro rodrigo
    sebastian teodoro ubaldo valentin xavier
    maria carmen ana isabel dolores pilar teresa rosa francisca antonia laura
    cristina marta elena lucia sara paula raquel patricia beatriz rocio silvia
    andrea irene alba julia natalia sonia monica susana eva nuria alicia angela
    concepcion consuelo esperanza inmaculada josefa juana manuela mercedes montserrat
    nieves noelia olga purificacion remedios sofia soledad veronica virginia yolanda
    amparo begona blanca clara claudia elisa emma esther gloria ines lorena lidia
    marina miriam nerea noemi rebeca sandra vanesa carolina catalina daniela
    """.split()
)

# Apellidos frecuentes. Se usan como refuerzo, nunca como condición única.
APELLIDOS: frozenset[str] = frozenset(
    """
    garcia gonzalez rodriguez fernandez lopez martinez sanchez perez gomez martin
    jimenez ruiz hernandez diaz moreno alvarez muñoz romero alonso gutierrez navarro
    torres dominguez vazquez ramos gil ramirez serrano blanco molina morales suarez
    ortega delgado castro ortiz rubio marin sanz nuñez iglesias medina garrido cortes
    castillo santos lozano guerrero cano prieto mendez cruz calvo gallego vidal leon
    herrera marquez peña cabrera flores campos vega fuentes carrasco diez caballero
    reyes nieto aguilar pascual herrero santana lorenzo montero hidalgo gimenez ibañez
    ferrer duran santiago benitez mora vicente arias carmona crespo roman pastor
    soto saez velasco moya soler parra esteban bravo gallardo rojas pardo merino
    franco espinosa lara izquierdo rivas silva rivera galan mateo arroyo redondo
    """.split()
)

# Partículas que unen los componentes de un nombre.
PARTICULAS: frozenset[str] = frozenset(
    "de del la las los y e i van von der da dos das do bin ben".split()
)

# Tratamientos y cargos que anuncian un nombre propio.
TRATAMIENTOS: tuple[str, ...] = (
    r"D\.ª", r"D\.", r"Dña\.", r"Dª", r"Doña", r"Don",
    r"Sr\.ª", r"Sra\.", r"Srta\.", r"Sr\.", r"Señor", r"Señora",
    r"Ilmo\.", r"Ilma\.", r"Excmo\.", r"Excma\.",
)

# Subconjunto que puede preceder a una FORMA CORTA («el Sr. Pérez»). No todo
# tratamiento sirve: «Excmo.» casi siempre acompaña al nombre completo.
TRATAMIENTOS_CORTOS: tuple[str, ...] = (
    r"Sr\.ª", r"Sra\.", r"Srta\.", r"Sr\.", r"D\.ª", r"Dña\.", r"Dª", r"D\.",
    r"Señor(?:a)?", r"Do[ñn]a?",
)

# Secuencias que preceden a un nombre y revelan su papel procesal.
ROLES_PREVIOS: dict[str, tuple[str, ...]] = {
    "DEMANDADO": (
        "frente a", "contra", "demandado", "demandada", "parte demandada",
        "codemandado", "codemandada", "ejecutado", "ejecutada", "querellado",
        "investigado", "investigada", "acusado", "acusada",
    ),
    "ACTOR": (
        "parte actora", "demandante", "el actor", "la actora", "ejecutante",
        "querellante", "denunciante", "recurrente", "solicitante",
    ),
    "LETRADO": (
        "letrado", "letrada", "abogado", "abogada", "procurador", "procuradora",
        "asistido por", "dirección letrada de", "colegiado", "colegiada",
    ),
    "PERITO": ("perito", "perita", "pericial de", "informe pericial de"),
    "TESTIGO": ("testigo", "declaración de", "testifical de"),
    "MENOR": ("menor", "hijo menor", "hija menor", "el menor", "la menor"),
}

# Secuencias posteriores al nombre que revelan el papel procesal.
ROLES_POSTERIORES: dict[str, tuple[str, ...]] = {
    "ACTOR": (
        "interpone demanda", "formula demanda", "presenta demanda", "interpone recurso",
        "como parte actora", "en su condición de demandante", "comparece como demandante",
    ),
    "DEMANDADO": ("como parte demandada", "en su condición de demandado"),
}

# Formas societarias que cierran una denominación social.
FORMAS_SOCIETARIAS: tuple[str, ...] = (
    r"S\.?\s?L\.?\s?U\.?", r"S\.?\s?A\.?\s?U\.?", r"S\.?\s?L\.?\s?P\.?",
    r"S\.?\s?L\.?\s?N\.?\s?E\.?", r"S\.?\s?L\.?", r"S\.?\s?A\.?",
    r"S\.?\s?C\.?\s?P\.?", r"S\.?\s?Coop\.?", r"S\.?\s?C\.?",
    r"C\.?\s?B\.?", r"A\.?\s?I\.?\s?E\.?", r"U\.?\s?T\.?\s?E\.?",
    r"S\.?\s?A\.?\s?S\.?", r"Ltd\.?", r"Inc\.?", r"GmbH", r"LLC", r"PLC", r"B\.?V\.?",
)

# Palabras capitalizadas que NUNCA son nombre propio de persona o empresa.
PARADA: frozenset[str] = frozenset(
    """
    Tribunal Supremo Constitucional Superior Justicia Audiencia Nacional Provincial
    Juzgado Juzgados Primera Instancia Sala Sección Secretaría Letrado Administración
    Código Civil Penal Comercio Ley Leyes Orgánica Real Decreto Reglamento Orden
    Directiva Reglamentos Estatuto Trabajadores Constitución Española España Estado
    Ministerio Consejería Ayuntamiento Diputación Comunidad Autónoma Agencia Tributaria
    Seguridad Social Hacienda Registro Mercantil Propiedad Notaría Colegio Abogados
    Procuradores Fiscalía Fiscal Ministerio Público Guardia Civil Policía Nacional
    Instituto Servicio Público Boletín Oficial BOE BORME Unión Europea Comisión
    Parlamento Consejo Antecedentes Hecho Hechos Fundamentos Derecho Suplico Otrosí
    Digo Primero Segundo Tercero Cuarto Quinto Sexto Séptimo Octavo Noveno Décimo
    Único Anexo Documento Doc Exponendo Alega Solicita Comparece Que Por En El La Los
    Las Un Una Del Al Sr Sra Don Doña Enero Febrero Marzo Abril Mayo Junio Julio
    Agosto Septiembre Octubre Noviembre Diciembre Lunes Martes Miércoles Jueves
    Viernes Sábado Domingo Euros Euro Madrid Barcelona Valencia Sevilla Zaragoza
    """.split()
)

# Disparadores del artículo 9 del RGPD que RIGEN un complemento: lo que sigue al
# disparador es el dato y se sustituye.
DISPARADORES_ARTICULO_9: dict[str, tuple[str, ...]] = {
    "SALUD": (
        "diagnosticado de", "diagnosticada de", "diagnosticados de", "diagnóstico de",
        "padece de", "padece", "en tratamiento por", "en tratamiento de",
        "baja médica por", "baja por", "incapacidad por", "intervenido de",
        "operado de", "operada de",
    ),
    "IDEOLOGIA": (
        "afiliado a", "afiliada a", "afiliado al", "afiliada al", "militante de",
        "miembro del sindicato", "confesión religiosa", "creencias religiosas",
        "profesa la religión", "ideología",
    ),
    "PENAL": (
        "condenado por", "condenada por", "investigado por", "investigada por",
        "acusado de", "acusada de",
    ),
}

# Menciones del artículo 9 que NO rigen complemento: solo sirven para avisar de
# que el documento contiene categoría especial. Sustituirlas produciría falsos
# positivos («informe médico aportado»), así que solo se cuentan.
MENCIONES_ARTICULO_9: tuple[str, ...] = (
    "historia clínica", "historial clínico", "informe médico", "informe forense",
    "parte de lesiones", "grado de discapacidad", "incapacidad permanente",
    "antecedentes penales", "certificado de antecedentes", "ejecutoria penal",
    "datos de salud", "orientación sexual", "origen étnico", "afiliación sindical",
    "datos genéticos", "datos biométricos",
)

# Seudónimos usados en modo "seudonimo".
SEUDONIMOS_PERSONA: tuple[str, ...] = (
    "Alberto Ríos Vela", "Beatriz Solana Prat", "Carlos Mendaro Gil",
    "Diana Vergel Lastra", "Emilio Cardeña Ruiz", "Fátima Olmedo Sanz",
    "Gonzalo Tarazona Vidal", "Helena Barbeito Cruz", "Ismael Quirós Fabra",
    "Julia Nevado Sierra", "Kevin Aranda Poveda", "Lucía Ferrán Ostos",
)

SEUDONIMOS_EMPRESA: tuple[str, ...] = (
    "Perfil Norte, S.L.", "Cauce Atlántico, S.A.", "Vértice Lumen, S.L.U.",
    "Ribera Ocre, S.L.", "Ancla Meridiana, S.A.", "Tramo Sexto, S.L.",
)
