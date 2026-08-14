# MCP Tool Contract

## Boundary rules

Phase 1 uses local `stdio` only. Each tool uses JSON Schema 2020-12 with `additionalProperties: false`, bounded strings/arrays, normalized enums, and both input and output schema validation. Paths are local absolute paths or a future opaque authorized reference; raw content, URLs, data URIs, and arbitrary URI schemes are rejected.

Tool responses contain structured JSON plus an identical minimal JSON text block only if required for client compatibility. They never contain document resources, embedded files, images, extracted text, entity values, snippets, mappings, stack traces, parser messages, or arbitrary exception strings.

## Shared types

```json
{
  "$defs": {
    "mode": {"enum": ["typed_placeholders", "redact"]},
    "jurisdiction": {"enum": ["PUERTO_RICO", "UNITED_STATES", "EUROPEAN_UNION"]},
    "validation_status": {"enum": ["PASS", "FAIL", "INDETERMINATE", "NOT_RUN"]},
    "error": {
      "type": "object",
      "additionalProperties": false,
      "required": ["code", "message"],
      "properties": {
        "code": {"enum": ["INVALID_REQUEST", "PATH_NOT_AUTHORIZED", "UNSUPPORTED_FORMAT", "FILE_TOO_LARGE", "MALFORMED_DOCUMENT", "OCR_REQUIRED", "OUTPUT_EXISTS", "POLICY_CONFLICT", "VALIDATION_FAILED", "PROCESSING_LIMIT_EXCEEDED", "INTERNAL_ERROR"]},
        "message": {"type": "string", "maxLength": 160}
      }
    }
  }
}
```

Error messages are prewritten templates keyed by code, not text derived from exceptions or inputs. Unknown exceptions become `INTERNAL_ERROR` with an opaque operation ID available only in safe local logs.

## `anonymize_document`

Input:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["file_path", "anonymization_mode", "categories_to_protect", "categories_to_preserve", "jurisdiction_profile"],
  "properties": {
    "file_path": {"type": "string", "minLength": 1, "maxLength": 4096},
    "output_path": {"type": "string", "minLength": 1, "maxLength": 4096},
    "anonymization_mode": {"$ref": "#/$defs/mode"},
    "categories_to_protect": {"type": "array", "uniqueItems": true, "maxItems": 64, "items": {"$ref": "taxonomy.schema.json#/$defs/entityType"}},
    "categories_to_preserve": {"type": "array", "uniqueItems": true, "maxItems": 64, "items": {"$ref": "taxonomy.schema.json#/$defs/entityType", "not": {"enum": ["SSN", "DNI", "PASSPORT", "DRIVER_LICENSE", "GOVERNMENT_ID", "BANK_ACCOUNT", "IBAN", "CREDIT_CARD", "MINOR"]}}},
    "jurisdiction_profile": {"$ref": "#/$defs/jurisdiction"}
  }
}
```

Schema validation is supplemented by policy validation: high-risk categories and `MINOR` are rejected from ordinary preservation requests even if a future schema version changes the registry reference. `STRICT`, `LEGAL_STANDARD`, and `CUSTOM` are policy presets; callers cannot weaken a mandatory protection through category arrays.

Output fields only: `success`, `operation_id` (random UUID), `output_path` (only on PASS), `entities_detected`, `entities_anonymized`, `categories_detected`, `validation_status`, `warnings` (stable codes), and `error`. Counts are non-negative; categories are enums; no per-entity details exist.

## `anonymize_folder`

Input uses `folder_path`, optional `output_folder`, shared policy fields, `recursive` (default false), bounded `max_documents`, and optional bounded `concurrency`. The input and output roots must be distinct, and symlinks, aliases, and unexpected mount points are never followed. Processing is bounded and independent per file.

Output fields only: `success`, `operation_id`, `documents_discovered`, `documents_safe`, `documents_failed`, `entities_detected`, `entities_anonymized`, `categories_detected`, `validation_status`, `outputs`, `warnings`, and `error`. Each `outputs` entry contains only opaque `document_id`, sanitized collision-safe `output_path`, and status. No input paths or filenames are echoed. Partial success yields overall `FAIL`, while individually verified output paths may be returned. Per-file failures expose only safe status/error codes.

## `review_document`

Input uses `file_path`, `jurisdiction_profile`, and optional protection/preservation categories. Output fields only: `success`, `operation_id`, aggregate `entities_detected`, `category_counts` (enum keys and integer values), `risk_status` (`DETECTED`, `NONE_DETECTED`, `INDETERMINATE`), `warnings`, and `error`. It never returns positions, pages, confidence values tied to individual findings, or contextual text.

## `scan_pii`

This is an internal application port, not advertised through MCP in Phase 1. Exposing it would unnecessarily enlarge the disclosure surface. It accepts a worker-owned parsed document and returns sensitive entity objects only inside the isolated worker. MCP callers use `review_document` for safe aggregates.

## `validate_anonymization`

Input uses only `file_path`, `jurisdiction_profile`, and the policy category sets. It is intended for sanitized candidates within authorized output roots; arbitrary originals are not assumed safe. Output fields only: `success`, `operation_id`, `validation_status`, `potential_entities_remaining`, `categories_detected`, `checks_performed` (enum codes), `warnings`, and `error`. `success` means the operation ran; only `validation_status: PASS` means publishable.

## `get_anonymization_report`

Input is an `operation_id` UUID, never a path. It is available only to an explicitly authorized local user/report owner; knowledge of an operation ID or hash alone is insufficient. Output fields only: `success`, `operation_id`, `document_id`, `sanitized_document_sha256`, `velum_version`, `policy_id`, `policy_version`, `policy_sha256`, counts, category names, `validation_status`, UTC timestamp, `processing_mode: LOCAL`, safe warning codes, and `error`. The sanitized-document hash may still be correlating metadata, so reports are not automatically exposed to AI callers. Future schema versions may add a signature envelope, signer identity, algorithm, and key identifier without including document contents, PII, excerpts, or mappings.

## Response sanitizer

Every result crosses a single final serializer that:

1. builds a new object from an allowlist (never serializes domain objects or `Exception`);
2. validates exact output schema and string length/character constraints;
3. permits only enumerated messages/warnings and authorized normalized output paths;
4. rejects keys matching content/value/span/context/mapping/trace/raw/input-path concepts;
5. runs canary/DLP defense-in-depth checks across serialized output;
6. replaces any failed serialization with a constant `INTERNAL_ERROR` response.

This sanitizer is mandatory even when upstream code claims its result is safe.
