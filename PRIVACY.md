# Privacy Principles

VELUM’s Phase 1 design is local-first: document bytes are processed on the user’s machine and are not sent to third-party AI or network services. The AI client supplies a path or authorized reference and receives only sanitized output references and non-sensitive aggregate metadata.

VELUM must not intentionally persist extracted plaintext. Entity values and placeholder mappings remain ephemeral inside the sensitive worker. Logs and reports exclude contents, values, excerpts, mappings, input paths, and avoidable filenames. Audit records use opaque IDs and may include a document hash; because a hash can correlate a known document, report access and retention must be restricted.

Temporary artifacts use operating-system secure temporary locations and restrictive permissions, then are removed after processing. Removal does not guarantee physical erasure on SSDs, copy-on-write filesystems, snapshots, backups, or a compromised host.

No real client document may be used in tests, diagnostics, bug reports, fixtures, or demonstrations. Only purpose-built synthetic documents are permitted.

Jurisdiction profiles configure detection and handling behavior. They do not establish legal compliance. Automated anonymization can miss contextual or novel identifiers, and combinations of preserved facts may enable re-identification. High-risk use requires human review and organizational safeguards.

