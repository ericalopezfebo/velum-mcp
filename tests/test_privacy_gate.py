from velum.privacidad import PrivacyFinding, PrivacyStatus, privacy_gate


def test_external_sharing_blocks_high_risk_findings():
    report = privacy_gate([
        PrivacyFinding(
            category="case_identifier",
            severity="high",
            message="Número de expediente detectado.",
        )
    ])
    assert report.status is PrivacyStatus.BLOCKED
    assert report.publication_allowed is False


def test_equivalence_table_blocks_external_sharing():
    report = privacy_gate([], equivalence_table=True, external=True)
    assert report.status is PrivacyStatus.BLOCKED
    assert report.publication_allowed is False


def test_low_risk_finding_requires_human_review():
    report = privacy_gate([
        PrivacyFinding(
            category="indirect_identifier",
            severity="medium",
            message="Combinación potencialmente identificable.",
        )
    ])
    assert report.status is PrivacyStatus.REVIEW_REQUIRED
    assert report.publication_allowed is False


def test_clean_external_document_is_not_certified_as_privileged():
    report = privacy_gate([], external=True)
    data = report.as_dict()
    assert report.status is PrivacyStatus.SAFE
    assert report.publication_allowed is True
    assert "privilege" in data["disclaimer"]
