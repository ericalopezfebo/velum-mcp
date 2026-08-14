# PDF Dependency Evaluation Plan

This planning document is superseded by the completed research deliverable [PDF Engine Evaluation](PDF_ENGINE_EVALUATION.md). It remains as the original evaluation checklist; the newer document contains the candidate comparison, authoritative license references, recommendation, and controlled-POC gate.

No production PDF library is selected for VELUM. This evaluation must be completed and approved before implementing the PDF adapter or adding a PDF runtime dependency.

## Candidates

Evaluate realistic candidates available for Python integration or a separately isolated native helper, including:

- PyMuPDF: technically strong redaction APIs; AGPL/commercial licensing requires explicit review.
- pypdf: permissive licensing and useful structural manipulation; verify whether it can provide true text removal and reliable sanitization rather than overlay-only behavior.
- qpdf: Apache-2.0 structural repair/transformation tool; assess whether paired with another redaction engine it meets the security contract.
- Poppler-based tooling: permissive components vary; assess extraction/rendering and whether it can perform destructive redaction.
- Commercial SDK candidates: evaluate licensing cost, redistribution rights, support, and security assurances.

The list is a starting point, not a presumption of selection. Exclude any candidate that cannot satisfy the redaction contract or whose license is incompatible without approved commercial licensing.

## Evaluation criteria

Score and document evidence for each candidate against:

1. proprietary/commercial distribution compatibility and license obligations/cost;
2. true PDF redaction and proof underlying text is no longer extractable;
3. metadata/XMP sanitization;
4. annotations and comments;
5. embedded files and attachments;
6. forms, actions, JavaScript, and active content;
7. malformed, hostile, and resource-exhaustion handling;
8. macOS Apple Silicon and Windows 11 x64 support;
9. maintenance, security history, release responsiveness, and provenance;
10. performance on representative legal PDFs;
11. deterministic behavior and testability;
12. dependency footprint, native toolchain, packaging, signing, and SBOM impact.

## Required proof tests

Use synthetic PDFs with canaries in visible text, hidden text, annotations, metadata, XMP, forms, attachments, embedded files, JavaScript/actions, incremental revisions, malformed objects, unusual encodings, and overlapping redaction regions. For every candidate:

- extract with at least two independent tools;
- inspect decompressed object/content streams and raw bytes for canaries;
- enumerate residual annotations, forms, attachments, actions, metadata, and revisions;
- render pages to assess reasonable readability and pagination;
- measure CPU, memory, output size, and timeout behavior;
- fuzz or replay malformed fixtures within an isolated worker;
- run offline on both target platforms where supported.

Overlay-only approaches fail automatically. A candidate is not acceptable merely because a black rectangle appears in rendered output.

## Decision record

The final record must include the scored matrix, test artifacts, license texts and counsel/business approval where needed, version pin, platform packaging plan, known limitations, rejected alternatives, and a named owner. The decision must explicitly state whether the selected dependency is compatible with proprietary VELUM distribution. Until then, the PDF component remains unimplemented.
