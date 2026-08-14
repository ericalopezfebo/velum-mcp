# Puerto Rico Legal Profile

`PuertoRicoLegalProfile` is an offline profile for Spanish/English legal text. It is a detection configuration, not a certification or legal-compliance claim.

## Profile coverage

- Social Security, email, phone, IBAN, card, and structured identifier validators are shared with the local engine.
- Address heuristics recognize markers such as calle, avenida/ave., carretera/carr., urbanización, barrio, sector, apartado/P.O. Box, pueblo, and San Juan. ZIP+4 patterns are available as location signals, not automatic PII redaction decisions.
- Case markers include `Civil Núm.`, `Caso Núm.`, complaint/querella labels, and Puerto Rico appellate references `KLAN`, `KLCE`, `KLRA`, `TSPR`, and `DPR`.
- Corporate and banking identifiers are extension points requiring jurisdiction-specific fixtures and validators.
- Driver-license and cadastral/property identifiers are intentionally not treated as universal regex categories yet.

## Legal references versus privacy

TSPR/DPR, Article/Artículo, and case-number references are legal/contextual categories. Detection does not imply protection. The policy engine decides whether a detected value is protected, preserved, or unspecified. `LEGAL_STANDARD` preserves legal citations and money while protecting other configured categories; DATE and CASE_NUMBER remain configurable.

## Language handling

Unicode NFKC normalization, non-breaking-space normalization, accented Spanish vocabulary, English vocabulary, and mixed-language text are supported. No OCR or external language model is used.

