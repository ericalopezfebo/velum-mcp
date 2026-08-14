"""Privacy gate for preparing legal documents for external AI systems.

The gate is deliberately conservative: it reports findings and blocks the
external-sharing workflow when high-risk identifiers or reversible mappings
remain. It does not certify privilege or legal compliance.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class PrivacyStatus(str, Enum):
    SAFE = "SAFE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class PrivacyFinding:
    category: str
    severity: str
    message: str
    location: str | None = None


@dataclass
class PrivacyReport:
    status: PrivacyStatus
    findings: list[PrivacyFinding] = field(default_factory=list)
    equivalence_table: bool = False
    publication_allowed: bool = False

    @property
    def direct_identifiers(self) -> int:
        return sum(f.category == "direct_identifier" for f in self.findings)

    @property
    def case_identifiers(self) -> int:
        return sum(f.category == "case_identifier" for f in self.findings)

    @property
    def metadata_findings(self) -> int:
        return sum(f.category == "metadata" for f in self.findings)

    def as_dict(self) -> dict:
        return {
            "status": self.status.value,
            "direct_identifiers": self.direct_identifiers,
            "case_identifiers": self.case_identifiers,
            "metadata_findings": self.metadata_findings,
            "residual_findings": len(self.findings),
            "equivalence_table": self.equivalence_table,
            "publication_allowed": self.publication_allowed,
            "findings": [f.__dict__ for f in self.findings],
            "disclaimer": (
                "VELUM no determina si una información está protegida por "
                "attorney-client privilege, work product doctrine u otra "
                "protección jurídica. La revisión profesional sigue siendo requerida."
            ),
        }


def privacy_gate(
    findings: Iterable[PrivacyFinding],
    *,
    equivalence_table: bool = False,
    external: bool = True,
) -> PrivacyReport:
    """Apply a conservative gate before a document is sent to an AI/third party."""
    findings = list(findings)
    high = any(f.severity == "high" for f in findings)
    reversible = equivalence_table and external

    if high or reversible:
        status = PrivacyStatus.BLOCKED
    elif findings:
        status = PrivacyStatus.REVIEW_REQUIRED
    else:
        status = PrivacyStatus.SAFE

    return PrivacyReport(
        status=status,
        findings=findings,
        equivalence_table=equivalence_table,
        publication_allowed=(status == PrivacyStatus.SAFE and external),
    )
