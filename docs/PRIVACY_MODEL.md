# Entity Taxonomy and Privacy Policy

## Normalized taxonomy

Entity types are stable string identifiers with metadata in a registry, not a closed language enum embedded throughout the engine. Detectors emit a base type, optional legal role, span/location, normalized fingerprint, confidence, and evidence class. Only aggregate type/count data may leave the worker.

| Family | Types |
|---|---|
| People and roles | `PERSON`, `PLAINTIFF`, `DEFENDANT`, `ATTORNEY`, `JUDGE`, `WITNESS`, `MINOR` |
| Contact/location | `ADDRESS`, `EMAIL`, `PHONE` |
| Government identifiers | `SSN`, `DNI`, `DRIVER_LICENSE`, `PASSPORT`, `GOVERNMENT_ID` |
| Financial | `IBAN`, `BANK_ACCOUNT`, `CREDIT_CARD` |
| Organizations/tax | `COMPANY`, `CIF`, `EIN` |
| Legal/contextual | `CASE_NUMBER`, `DATE`, `MONEY`, `LEGAL_CITATION` |
| Special | `MEDICAL_IDENTIFIER`, `OTHER_SENSITIVE_DATA` |

Role types specialize `PERSON`. When reliable role context exists, `PERSON(role=PLAINTIFF)` renders as the role placeholder; otherwise it remains `PERSON`. A registry entry defines parent, sensitivity, placeholder label per locale, detector support, normalization strategy, and validation behavior. New types register through this interface without changing resolution, policy, or transformation code.

## Typed placeholders and resolution

Canonical internal labels are locale-neutral; rendered labels are policy-controlled. The requested Spanish defaults include:

```text
PLAINTIFF → [ACTOR_1]       DEFENDANT → [DEMANDADO_1]
PERSON → [PERSONA_1]        ADDRESS → [DIRECCION_1]
COMPANY → [EMPRESA_1]       SSN → [SSN_1]
IBAN → [IBAN_1]
```

Counters are per type, assigned deterministically by the first stable document position after resolution—not detector execution order. Repeated normalized entities reuse one placeholder. Hashes used for resolution are keyed, process-local fingerprints and are never reported. Cross-document consistency is disabled by default; an authorized case scope may hold an encrypted, short-lived mapping in a future milestone. Restoration is out of scope.

Overlapping findings resolve by: explicit policy protection, more-specific child type, validated structured identifier, longer span, then confidence. An uncertain role falls back to the more protective parent. Placeholder collision attacks are handled by escaping or first reserving literal placeholder-like source strings.

## Policy model

A versioned immutable policy contains:

```yaml
id: pr-legal-default
version: 1
jurisdiction: PUERTO_RICO
default_action: PROTECT
protect: [PERSON, PLAINTIFF, DEFENDANT, ATTORNEY, ADDRESS, EMAIL, PHONE, SSN]
preserve: [DATE, MONEY, CASE_NUMBER, LEGAL_CITATION]
mode: typed_placeholders
minimum_confidence: {contextual: 0.80, structured: 1.00}
uncertain_action: PROTECT
validation_profile: strict
placeholder_locale: es
```

The shipped presets are `STRICT`, `LEGAL_STANDARD`, and `CUSTOM`. `STRICT` protects everything detected as personal or sensitive. `LEGAL_STANDARD` may preserve `MONEY` and `LEGAL_CITATION`; `DATE` and `CASE_NUMBER` remain configurable. `CUSTOM` requires explicit selections. Ordinary MCP requests cannot preserve SSN, DNI, passport, driver’s-license, bank-account, IBAN, credit-card, equivalent high-risk identifiers, or minor identities; such requests fail closed.

Jurisdiction profiles configure detectors, validators, thresholds, defaults, and label localization. Initial profiles are Puerto Rico, United States, and European Union. They are detection/policy presets, not claims of legal compliance.

Caller sets are validated against the registry. The same type cannot appear in both sets. Child/parent conflicts are explicit: a preserved parent cannot silently preserve a protected child. Phase 1 precedence is `explicit protect > explicit preserve > jurisdiction rule > default action`; any contradictory parent/child rule returns `POLICY_CONFLICT` rather than guessing. Safety-critical categories configured as mandatory by a profile cannot be preserved without a future privileged policy mechanism.

Preservation means the selected category remains unmodified, not that contextual quasi-identifiers are guaranteed harmless. Reports record the exact policy identifier, version, and digest.

## Audit report

Reports are local, metadata-only records:

```text
VELUM Privacy Report
Document ID: <random UUID>
SHA-256: <hash of original bytes>
VELUM version: <version>
Policy: pr-legal-default@1 (<policy digest>)
Entities detected: 31
Entities anonymized: 31
Categories detected: PERSON, ADDRESS, SSN
Validation: PASS
Timestamp: <UTC RFC 3339>
Processing mode: LOCAL
```

Reports never include values, snippets, positions, mappings, input paths, sensitive filenames, parser messages, or user-provided labels. Hashes enable integrity but can correlate a known file; access and retention must therefore be restricted. Failed jobs record safe state and error codes only.
