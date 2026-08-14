# Threat Model

## Scope and security objectives

Phase 1 is a local `stdio` MCP server processing authorized text-based PDF and DOCX files. It excludes OCR, restoration, remote MCP, cloud models, desktop UI, licensing, and updates.

Security objectives, in priority order:

1. Original contents, detected values, and mappings never reach the AI client, logs, reports, telemetry, or network.
2. Sanitized output cannot reveal protected values through visible content, extraction, document internals, metadata, or active/embedded content.
3. VELUM accesses and writes only explicitly authorized filesystem locations.
4. Results are deterministic for the same bytes, policy, detector/model versions, and VELUM version.
5. Malformed or adversarial documents fail safely without corrupting or replacing inputs.

## Assets and trust boundaries

Assets include original documents, extracted in-memory text, entity spans/values, placeholder maps, sanitized outputs, audit metadata, policies, signing keys, and local model artifacts.

Trust boundaries are: AI client ↔ MCP adapter; MCP adapter ↔ sensitive worker; worker ↔ untrusted parser/document; worker ↔ filesystem; and release artifacts ↔ installed application. The AI client, input document, supplied paths, filenames, parser libraries, environment, and future plugins are not inherently trusted. The local OS/user account is a dependency, not a boundary VELUM can fully defend against.

## Primary threats and mitigations

| Threat | Impact | Required controls |
|---|---|---|
| MCP response/exception leakage | Client receives privileged content | Allowlisted result DTOs; stable error codes; recursive response sanitizer; no free-form internal errors; schema and canary tests |
| Prompt injection in document | Document manipulates AI/tool behavior | Never send content to the AI; treat text strictly as data; no tool execution driven by content |
| Missed or ambiguous PII | Unsafe output labeled safe | Hybrid detection; conservative policy; independent rescan; `UNSAFE`/`INDETERMINATE` states; no output publication on failure by default |
| Fake PDF redaction | Recoverable text under overlays | Apply destructive redactions; rebuild/clean output; two extractors; raw-object/canary checks; rendered inspection tests |
| Hidden OOXML content | PII remains in non-body parts | Package-level part inventory; deny-by-default allowlist; handle/remove headers, comments, revisions, properties, relationships, custom XML and hidden text |
| Malicious PDF/DOCX | RCE, resource exhaustion, parser escape | Process isolation; CPU/RAM/time limits; no network; dependency pinning; fuzzing; ZIP bomb and object limits; active-content stripping |
| Path traversal/symlink race | Read/write outside authorization | Explicit roots; absolute canonical paths; no-follow opens; regular-file checks; file identity verification; exclusive/atomic output creation |
| Output collision/input overwrite | Data loss | Reject identical input/output; no overwrite default; exclusive staging; atomic rename only after validation |
| Logs/report leakage | Persistent disclosure | Structured allowlisted event fields; opaque operation/document IDs; basename suppression; log sink tests with canaries |
| Mapping exposure or reuse | Re-identification/correlation | Ephemeral in-worker map; no serialization; explicit case scope; memory lifetime minimization; future restoration isolated and separately authorized |
| Dependency/model compromise | Code execution or altered detection | Locked dependencies; SBOM; signature/hash verification; provenance; offline install/runtime; security review and reproducible release goals |
| Local malicious process | Reads memory/files or invokes server | `stdio`; least-privilege OS account/sandbox; restrictive permissions; short worker lifetime; document this residual risk |
| Availability attack | Service exhaustion | Per-file and batch limits; bounded concurrency; deadlines; cancellation; circuit breakers; sanitized partial aggregate results |
| Tampered policy/report | Incorrect assurances | Versioned immutable policies; canonical policy digest; keyed/signature option in future; report derived after validation only |

## Abuse cases

- A client requests `/etc/passwd`, a sibling client matter, a symlink, device file, FIFO, or output outside the configured root.
- A filename or corrupt XML embeds PII in an exception message.
- A DOCX contains `../` ZIP members, external relationships, macros, oversized decompression, tracked deletions, text boxes, or alternate content.
- A PDF contains attachments, JavaScript, forms, comments, incremental revisions, malformed object graphs, invisible text, or image-only pages.
- A caller preserves `PERSON` while protecting `PLAINTIFF`, or supplies unknown categories to weaken policy.
- Batch processing uses output paths that collide or recursively processes its own output folder.

All are covered by validation or must yield a stable non-sensitive failure.

## Fail-closed state machine

```text
RECEIVED → VALIDATED → DETECTED → TRANSFORMED → VERIFIED → SAFE/PUBLISHED
     └────────────── any uncertainty/error ──────────────→ FAILED
                                      residual signal ──→ UNSAFE
```

`PASS` means the implemented checks found no residual protected signal; it is not a legal-compliance guarantee or proof of zero disclosure. Failed/unsafe staged outputs are removed and their paths are not returned. Aggregate folder status cannot be `PASS` if any item failed or is unsafe.

## Residual risks

Detection can produce false negatives; novel encodings and parser flaws can bypass controls; malware may exploit native parsers; local administrators/malware can inspect memory; filenames and filesystem metadata may disclose context; secure deletion is not guaranteed; and anonymized narratives may remain re-identifiable through combinations of non-PII facts. These limitations require documented user warnings, defense in depth, security updates, and human review for high-risk releases.

