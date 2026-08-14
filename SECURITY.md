# Security Policy

VELUM’s Phase 1 architecture is frozen and the Milestone 2 security skeleton is implemented. Document processing is not implemented, so VELUM is not ready for use with confidential, privileged, personal, or production documents.

## Security governance

The intended future security contact is `security@abogadovirtual.com`. This mailbox and vulnerability program are reserved but are not operational until explicitly configured.

Before commercial public launch, VELUM will publish:

- a responsible vulnerability-disclosure process and supported-version policy;
- severity classification and remediation ownership;
- dependency vulnerability intake, triage, upgrade, and exception handling;
- incident-response ownership, escalation, evidence handling, and communications procedures;
- a security contact and public reporting instructions.

No contractual response-time SLA is claimed at this stage. SLAs will be defined before public launch.

## Reporting a vulnerability

A private reporting channel and response SLA must be established before any pilot or release. Until then, do not place sensitive details, exploit documents, client information, or personal data in public issues. Synthetic reproductions are required for development and testing.

## Security baseline

- Original document contents, detected values, excerpts, and placeholder mappings must never cross the MCP boundary.
- Runtime document processing is local and offline.
- Inputs are untrusted and processed within strict path, type, resource, and parser limits.
- Inputs are never modified in place; outputs are published only after independent validation.
- Logs, reports, protocol responses, and errors contain allowlisted non-sensitive metadata only.
- A validation uncertainty or residual signal fails closed and must not be described as safe.

See [Threat Model](docs/THREAT_MODEL.md) for threats, mitigations, and residual risks. These controls are design requirements, not claims that they have already been implemented or independently verified.

## Product claims

Approved positioning is: “Designed to reduce disclosure of sensitive information before documents are shared with AI systems or third parties.” VELUM may describe processing as “local” only when document contents remain on the user’s device. VELUM does not claim perfect or guaranteed anonymization, legal compliance, automatic GDPR/HIPAA/Puerto Rico confidentiality compliance, or zero risk. Jurisdiction profiles configure detection and privacy behavior; they are not certifications.
