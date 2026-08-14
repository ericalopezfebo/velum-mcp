"""Perfil jurídico de Estados Unidos.

Cubre el escrito federal y estatal en inglés: identificadores estadounidenses
—SSN, EIN, licencia de conducir, número de ruta bancaria— y direcciones en
formato norteamericano, preservando el aparato de citación que sostiene el
argumento.

Advertencia deliberada, la misma que en los demás perfiles: **detectar no es
proteger**. Las citas —U.S.C., C.F.R., F.3d, Fed. R. Civ. P., números de caso,
tribunales— se detectan para PRESERVARLAS. Son el fondo del asunto.

Un aviso de alcance que conviene no perder de vista: este perfil facilita la
higiene de datos antes de que un documento llegue a una IA. No es, ni pretende
ser, un análisis de HIPAA, de la regla 5.4 del modelo de conducta profesional,
ni de las obligaciones estatales de notificación de brechas. Eso corresponde al
profesional.
"""

from __future__ import annotations

import re

# --- Zonas protegidas: el aparato de citación estadounidense ---------------

PROTEGIDOS_EEUU: dict[str, re.Pattern[str]] = {
    # Código y reglamento federal: 42 U.S.C. § 1983; 17 C.F.R. § 240.10b-5.
    "usc_cfr": re.compile(
        r"\b\d{1,2}\s+(?:U\.?\s?S\.?\s?C\.?|C\.?\s?F\.?\s?R\.?)\s*"
        r"(?:§{1,2}|sec(?:tion|s?)?\.?)?\s*[\d]+[\w.\-()§ ]{0,24}",
        re.IGNORECASE,
    ),
    # Reporteros federales: 550 U.S. 544; 127 S. Ct. 1955; 490 F.3d 143;
    # 253 F. Supp. 2d 1010; 202 F.R.D. 123.
    "reportero_federal": re.compile(
        r"\b\d{1,4}\s+(?:U\.?\s?S\.?|S\.?\s?Ct\.?|L\.?\s?Ed\.?(?:\s?2d)?|"
        r"F\.(?:\s?\d[a-z]{2})?|F\.\s?Supp\.(?:\s?\d[a-z]{2})?|F\.?\s?R\.?\s?D\.?|"
        r"B\.?\s?R\.?|Fed\.?\s?Appx\.?)\s+\d{1,4}\b"
    ),
    # Reporteros regionales y estatales: 21 N.E.3d 245; 305 P.3d 1; 88 A.3d 1;
    # 419 S.W.3d 76; 130 So. 3d 1; 168 Cal. Rptr. 3d 800; 45 N.Y.S.3d 12.
    "reportero_estatal": re.compile(
        r"\b\d{1,4}\s+(?:N\.?\s?[EW]\.?(?:\s?\d[a-z]{2})?|"
        r"S\.?\s?[EW]\.?(?:\s?\d[a-z]{2})?|P\.(?:\s?\d[a-z]{2})?|"
        r"A\.(?:\s?\d[a-z]{2})?|So\.(?:\s?\d[a-z]{2})?|"
        r"Cal\.\s?Rptr\.(?:\s?\d[a-z]{2})?|N\.?\s?Y\.?\s?S\.?(?:\s?\d[a-z]{2})?)"
        r"\s+\d{1,4}\b"
    ),
    # Reglas: Fed. R. Civ. P. 12(b)(6); FRCP 56; Fed. R. Evid. 702.
    "regla_federal": re.compile(
        r"\b(?:Fed\.?\s?R\.?\s?(?:Civ\.?\s?P\.?|Evid\.?|Crim\.?\s?P\.?|App\.?\s?P\.?|"
        r"Bankr\.?\s?P\.?)|F\.?R\.?(?:C\.?P\.?|E\.?|A\.?P\.?)|Rule)\s*"
        r"\d{1,4}(?:\([a-z0-9]{1,3}\))*",
        re.IGNORECASE,
    ),
    # Número de caso y expediente: No. 1:24-cv-01234-ABC; Case No. 22-35678;
    # Docket No. 21-1199; Civ. A. No. 3:20-cv-00417.
    "numero_caso": re.compile(
        r"\b(?:Case\s+No\.?|Civil\s+Action\s+No\.?|Civ\.?\s?A\.?\s+No\.?|"
        r"Docket\s+No\.?|Adv\.?\s?Pro\.?\s+No\.?|No\.)\s*"
        r"[\dA-Za-z][\dA-Za-z:\-]{3,24}",
        re.IGNORECASE,
    ),
    "caso_cv_cr": re.compile(r"\b\d{1,2}:\d{2}-(?:cv|cr|md|mc|bk|ap)-\d{3,6}(?:-[A-Z]{2,4})*\b"),
    # NOMBRES DE CASO CITADOS. Crítico: «Bell Atlantic Corp. v. Twombly» es la
    # autoridad en la que se apoya el argumento, no una parte del pleito.
    # Anonimizarlo destruiría el escrito. Se exige que le siga una cita de
    # reportero para no tragarse cualquier «X contra Y» del relato de hechos.
    "caso_citado": re.compile(
        r"\b[A-Z][\w.'&\-]*(?:\s+(?:[A-Z][\w.'&\-]*|of|and|the|for|&))*"
        r"\s+v\.?\s+"
        r"[A-Z][\w.'&\-]*(?:\s+(?:[A-Z][\w.'&\-]*|of|and|the|for|&))*"
        r"(?=,?\s+\d{1,4}\s+[A-Z])"
    ),
    "caso_in_re": re.compile(
        r"\b(?:In\s+re|Ex\s+parte|In\s+the\s+Matter\s+of)\s+"
        r"[A-Z][\w.'&\-]*(?:\s+[A-Z][\w.'&\-]*){0,5}"
        r"(?=,?\s+\d{1,4}\s+[A-Z])"
    ),
    # Tribunales.
    "tribunal_eeuu": re.compile(
        r"\b(?:(?:the\s+)?Supreme\s+Court\s+of\s+the\s+United\s+States|"
        r"United\s+States\s+(?:District|Bankruptcy|Tax|Claims)\s+Court(?:\s+for\s+the\s+"
        r"[A-Z][\w.]*(?:\s+[A-Z][\w.]*){0,5})?|"
        r"United\s+States\s+Court\s+of\s+Appeals(?:\s+for\s+the\s+"
        r"(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|"
        r"Eleventh|Federal|D\.?C\.?)\s+Circuit)?|"
        r"(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|"
        r"Eleventh|Federal)\s+Circuit|"
        r"Court\s+of\s+Appeals|Superior\s+Court|Circuit\s+Court|Probate\s+Court|"
        r"Court\s+of\s+Chancery)\b"
    ),
    # Agencias que aparecen constantemente y no son datos personales.
    "agencia_eeuu": re.compile(
        r"\b(?:E\.?E\.?O\.?C\.?|S\.?E\.?C\.?|F\.?T\.?C\.?|I\.?R\.?S\.?|D\.?O\.?J\.?|"
        r"N\.?L\.?R\.?B\.?|O\.?S\.?H\.?A\.?|U\.?S\.?P\.?T\.?O\.?|F\.?D\.?A\.?|"
        r"C\.?F\.?P\.?B\.?|H\.?H\.?S\.?)\b"
    ),
    # Importes en dólares y fechas en formato estadounidense.
    "importe_usd": re.compile(r"(?:US)?\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?"),
    "fecha_eeuu": re.compile(
        r"\b(?:January|February|March|April|May|June|July|August|September|"
        r"October|November|December|Jan\.|Feb\.|Mar\.|Apr\.|Jun\.|Jul\.|Aug\.|"
        r"Sept?\.|Oct\.|Nov\.|Dec\.)\s+\d{1,2},\s+\d{4}\b",
        re.IGNORECASE,
    ),
}

# --- Datos personales estadounidenses --------------------------------------

_TIPOS_VIA = (
    r"Street|St\.|Avenue|Ave\.|Road|Rd\.|Boulevard|Blvd\.|Drive|Dr\.|Lane|Ln\.|"
    r"Court|Ct\.|Circle|Cir\.|Place|Pl\.|Terrace|Ter\.|Highway|Hwy\.|Parkway|Pkwy\.|"
    r"Way|Trail|Trl\.|Square|Sq\."
)

_UNIDAD = (
    r"(?:Suite|Ste\.?|Apt\.?|Apartment|Unit|Floor|Fl\.?|Rm\.?|Room|#)\s*[\w\-]{1,8}"
)

_ESTADOS = (
    r"AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|"
    r"MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|"
    r"DC|PR|VI|GU|AS|MP"
)

PERSONALES_EEUU: dict[str, re.Pattern[str]] = {
    # 1234 Main Street, Suite 500, Springfield, IL 62701
    "DIRECCION": re.compile(
        rf"\b\d{{1,6}}\s+(?:[NSEW]\.?[EW]?\.?\s+)?"
        rf"(?:[A-Z][\w'\-\.]*\s+){{1,4}}(?:{_TIPOS_VIA})"
        rf"(?:\s*,?\s*{_UNIDAD})?"
        rf"(?:\s*,\s*[A-Z][\w'\-]*(?:\s+[A-Z][\w'\-]*){{0,2}})?"
        rf"(?:\s*,?\s*(?:{_ESTADOS})\.?)?"
        rf"(?:\s*,?\s*\d{{5}}(?:-\d{{4}})?)?"
    ),
    # P.O. Box 1234, Springfield, IL 62701
    "DIRECCION_APARTADO": re.compile(
        rf"\bP\.?\s?O\.?\s?Box\s+\d{{1,7}}"
        rf"(?:\s*,\s*[A-Z][\w'\-]*(?:\s+[A-Z][\w'\-]*){{0,2}})?"
        rf"(?:\s*,?\s*(?:{_ESTADOS})\.?)?(?:\s*,?\s*\d{{5}}(?:-\d{{4}})?)?",
        re.IGNORECASE,
    ),
    # Social Security Number: rechaza los bloques nunca emitidos.
    "SSN": re.compile(r"(?<!\d)(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}(?!\d)"),
    # Employer Identification Number: 12-3456789, con prefijo válido.
    "EIN": re.compile(r"(?<!\d)\d{2}-\d{7}(?!\d)"),
    # Número de ruta bancaria ABA: se valida con su dígito de control.
    "ABA": re.compile(
        r"\b(?:routing(?:\s+(?:number|no\.?|#))?|ABA(?:\s+number)?)\s*:?\s*(\d{9})\b",
        re.IGNORECASE,
    ),
    # Licencia de conducir, anclada a la palabra para no capturar cualquier cifra.
    "LICENCIA": re.compile(
        r"\b(?:driver'?s?\s+licen[sc]e|DL|license)\s*(?:no\.?|number|#)?\s*:?\s*"
        r"([A-Z]{0,2}[\-\s]?\d{5,13})\b",
        re.IGNORECASE,
    ),
    # Historia clínica y beneficiario de Medicare (HIPAA).
    "EXPEDIENTE_MEDICO": re.compile(
        r"\b(?:MRN|medical\s+record\s+(?:no\.?|number|#)|patient\s+ID)\s*:?\s*"
        r"([A-Z0-9\-]{4,15})\b",
        re.IGNORECASE,
    ),
    "MEDICARE": re.compile(r"\b[1-9][ACDEFGHJKMNPQRTUVWXY]\w\d[ACDEFGHJKMNPQRTUVWXY]"
                           r"[\w\d]\d[ACDEFGHJKMNPQRTUVWXY]{2}\d{2}\b"),
    # Teléfono estadounidense en cualquier formato corriente.
    "TELEFONO": re.compile(
        r"(?:\+?1[\s.-]?)?\(?[2-9]\d{2}\)?[\s.-]?[2-9]\d{2}[\s.-]?\d{4}(?!\d)"
    ),
    "PASAPORTE": re.compile(
        r"\bpassport\s*(?:no\.?|number|#)?\s*:?\s*([A-Z]?\d{6,9})\b", re.IGNORECASE
    ),
}

# --- Léxico en inglés -------------------------------------------------------

TRATAMIENTOS_EEUU: tuple[str, ...] = (
    r"Mr\.", r"Mrs\.", r"Ms\.", r"Miss", r"Dr\.", r"Prof\.",
    r"Hon\.", r"Honorable", r"Judge", r"Justice", r"Magistrate\s+Judge",
    r"Atty\.", r"Attorney", r"Officer", r"Detective", r"Sgt\.", r"Capt\.",
)

TRATAMIENTOS_CORTOS_EEUU: tuple[str, ...] = (
    r"Mr\.", r"Mrs\.", r"Ms\.", r"Dr\.", r"Hon\.", r"Judge", r"Justice",
)

ROLES_PREVIOS_EEUU: dict[str, tuple[str, ...]] = {
    "ACTOR": (
        "plaintiff", "plaintiffs", "petitioner", "claimant", "appellant",
        "movant", "complainant", "relator",
    ),
    "DEMANDADO": (
        "defendant", "defendants", "respondent", "appellee", "co-defendant",
        "third-party defendant", "v.", "vs.", "versus", "against",
    ),
    "LETRADO": (
        "counsel for", "attorney for", "represented by", "by his attorney",
        "by her attorney", "of counsel", "esq", "law offices of",
    ),
    "PERITO": ("expert witness", "expert report of", "opinion of"),
    "TESTIGO": ("witness", "deposition of", "declaration of", "affidavit of"),
    "MENOR": ("minor child", "the minor", "a minor", "juvenile"),
}

ROLES_POSTERIORES_EEUU: dict[str, tuple[str, ...]] = {
    "ACTOR": (
        "brings this action", "files this complaint", "hereby complains",
        "as plaintiff", "plaintiff herein",
    ),
    "DEMANDADO": ("as defendant", "defendant herein", "answering defendant"),
    "LETRADO": (", esq", ", esquire"),
}

FORMAS_SOCIETARIAS_EEUU: tuple[str, ...] = (
    r"Inc\.?", r"Incorporated", r"Corp\.?", r"Corporation", r"Company",
    r"Co\.", r"L\.?\s?L\.?\s?C\.?", r"L\.?\s?L\.?\s?P\.?", r"L\.?\s?P\.?",
    r"P\.?\s?L\.?\s?L\.?\s?C\.?", r"P\.?\s?C\.?", r"P\.?\s?A\.?",
    r"Ltd\.?", r"N\.?\s?A\.?", r"Trust", r"Partnership", r"Holdings",
)

# Palabras capitalizadas del inglés jurídico que NUNCA son nombre de persona.
PARADA_EEUU: frozenset[str] = frozenset(
    """
    United States America State Commonwealth County City Town Village District
    Supreme Court Courts Appeals Appellate Circuit Superior Chancery Probate
    Bankruptcy Judicial Judge Justice Magistrate Clerk Marshal Sheriff Jury
    Plaintiff Plaintiffs Defendant Defendants Petitioner Respondent Appellant
    Appellee Movant Complaint Answer Motion Memorandum Brief Order Judgment
    Opinion Verdict Docket Exhibit Affidavit Declaration Deposition Discovery
    Interrogatories Subpoena Stipulation Settlement Agreement Contract Lease
    Statute Statutes Code Rule Rules Regulation Regulations Act Amendment
    Constitution Article Section Chapter Title Paragraph Count Counts Claim
    Congress Senate House Department Bureau Agency Commission Board Office
    Attorney General Counsel Esquire Firm Associates Partners Company
    January February March April May June July August September October
    November December Monday Tuesday Wednesday Thursday Friday Saturday Sunday
    Whereas Wherefore Therefore Hereby Herein Thereof Pursuant Notwithstanding
    Federal National International American Northern Southern Eastern Western
    Central Middle First Second Third Fourth Fifth Sixth Seventh Eighth Ninth
    Tenth Eleventh Twelfth
    """.split()
)

NOMBRES_PILA_EEUU: frozenset[str] = frozenset(
    """
    james john robert michael william david richard joseph thomas charles
    christopher daniel matthew anthony mark donald steven paul andrew joshua
    kenneth kevin brian george timothy ronald jason edward jeffrey ryan jacob
    gary nicholas eric jonathan stephen larry justin scott brandon benjamin
    samuel gregory alexander patrick frank raymond jack dennis jerry tyler
    aaron jose adam nathan henry zachary douglas peter kyle noah ethan jeremy
    walter christian keith roger terry austin sean gerald carl harold dylan
    mary patricia jennifer linda elizabeth barbara susan jessica sarah karen
    nancy lisa margaret betty sandra ashley dorothy kimberly emily donna
    michelle carol amanda melissa deborah stephanie rebecca laura sharon cynthia
    kathleen amy angela shirley anna brenda pamela nicole ruth katherine samantha
    christine emma catherine debra virginia rachel carolyn janet maria heather
    diane julie joyce victoria kelly christina joan evelyn lauren judith megan
    andrea cheryl hannah jacqueline martha gloria teresa ann sara madison
    """.split()
)

APELLIDOS_EEUU: frozenset[str] = frozenset(
    """
    smith johnson williams brown jones garcia miller davis rodriguez martinez
    hernandez lopez gonzalez wilson anderson thomas taylor moore jackson martin
    lee perez thompson white harris sanchez clark ramirez lewis robinson walker
    young allen king wright scott torres nguyen hill flores green adams nelson
    baker hall rivera campbell mitchell carter roberts gomez phillips evans
    turner diaz parker cruz edwards collins reyes stewart morris morales murphy
    cook rogers gutierrez ortiz morgan cooper peterson bailey reed kelly howard
    ramos kim cox ward richardson watson brooks chavez wood james bennett gray
    mendoza ruiz hughes price alvarez castillo sanders patel myers long ross
    foster jimenez powell jenkins perry russell sullivan bell coleman butler
    henderson barnes gonzales fisher vasquez simmons romero jordan patterson
    alexander hamilton graham reynolds griffin wallace west cole hayes bryant
    herrera gibson ellis tran medina aguilar stevens murray ford castro marshall
    """.split()
)


def instalar() -> None:
    """Inyecta el perfil estadounidense en los detectores y el léxico base.

    Amplía, no sustituye. Un escrito puede citar jurisprudencia federal y
    estatal, y un despacho puertorriqueño trabaja rutinariamente en los dos
    idiomas y los dos sistemas de citación a la vez.
    """
    from .. import detectores, lexico, nombres

    detectores.PATRONES_PROTEGIDOS.update(PROTEGIDOS_EEUU)
    for codigo, patron in PERSONALES_EEUU.items():
        clave = "DIRECCION" if codigo == "DIRECCION_APARTADO" else codigo
        if (clave, patron) not in detectores.PATRONES_EXTRA:
            detectores.PATRONES_EXTRA.append((clave, patron))

    lexico.PARADA = frozenset(lexico.PARADA | PARADA_EEUU)
    lexico.NOMBRES_PILA = frozenset(lexico.NOMBRES_PILA | NOMBRES_PILA_EEUU)
    lexico.APELLIDOS = frozenset(lexico.APELLIDOS | APELLIDOS_EEUU)

    if TRATAMIENTOS_EEUU[0] not in lexico.TRATAMIENTOS:
        lexico.TRATAMIENTOS = lexico.TRATAMIENTOS + TRATAMIENTOS_EEUU
        lexico.TRATAMIENTOS_CORTOS = lexico.TRATAMIENTOS_CORTOS + TRATAMIENTOS_CORTOS_EEUU
        lexico.FORMAS_SOCIETARIAS = lexico.FORMAS_SOCIETARIAS + FORMAS_SOCIETARIAS_EEUU

    for rol, disparadores in ROLES_PREVIOS_EEUU.items():
        lexico.ROLES_PREVIOS[rol] = tuple(
            dict.fromkeys(lexico.ROLES_PREVIOS.get(rol, ()) + disparadores)
        )
    for rol, disparadores in ROLES_POSTERIORES_EEUU.items():
        lexico.ROLES_POSTERIORES[rol] = tuple(
            dict.fromkeys(lexico.ROLES_POSTERIORES.get(rol, ()) + disparadores)
        )

    nombres.recompilar()
