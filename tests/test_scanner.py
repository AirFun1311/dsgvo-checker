import json
import pytest
from dsgvo_scanner import (
    DSGVOScanner,
    CheckResult,
    ScanResult,
    KNOWN_TRACKERS,
    SECURITY_HEADERS,
)


def test_scanner_init_url_normalization():
    """Test URL normalization during scanner initialization."""
    scanner1 = DSGVOScanner("example.com", use_playwright=False)
    assert scanner1.input_url == "https://example.com"
    assert scanner1.result.url == "https://example.com"
    assert scanner1.result.scan_id.startswith("DSF-")

    scanner2 = DSGVOScanner("http://my-domain.de/path/", use_playwright=False)
    assert scanner2.input_url == "http://my-domain.de/path"


def test_known_trackers_integrity():
    """Verify that all entries in the tracker database contain required fields."""
    assert len(KNOWN_TRACKERS) > 0
    required_keys = {"name", "category", "country", "risk"}
    valid_risks = {"hoch", "mittel", "niedrig", "keine", "unbekannt"}
    for domain, info in KNOWN_TRACKERS.items():
        assert isinstance(domain, str) and len(domain) > 0
        assert required_keys.issubset(info.keys()), f"Tracker {domain} missing required keys"
        assert info["risk"].lower() in valid_risks, f"Tracker {domain} has unexpected risk level: {info['risk']}"


def test_security_headers_catalog():
    """Verify security headers definition weights and structure."""
    assert "strict-transport-security" in SECURITY_HEADERS
    assert "content-security-policy" in SECURITY_HEADERS
    for header, meta in SECURITY_HEADERS.items():
        assert "name" in meta
        assert "weight" in meta
        assert isinstance(meta["weight"], int)


def test_scan_result_dataclass():
    """Test CheckResult and ScanResult data containers."""
    chk = CheckResult(
        key="test_ssl",
        status="PASS",
        title="SSL Encryption",
        detail="TLS 1.3 Active",
        penalty=0,
        rechtsgrundlage="Art. 32 DSGVO",
        empfehlung="Everything looks good.",
        sub_findings=["Valid certificate", "Strong cipher"],
    )
    assert chk.status == "PASS"
    assert len(chk.sub_findings) == 2

    res = ScanResult(
        url="https://test.example",
        scan_date="15.08.2026",
        scan_id="DSF-TEST1234",
        risk_score=10,
        risk_level="NIEDRIG",
        checks=[chk],
    )
    assert res.risk_level == "NIEDRIG"
    assert len(res.checks) == 1


def test_scanner_to_dict_and_json(tmp_path):
    """Test serialization of scan results into Python dict and JSON file."""
    scanner = DSGVOScanner("https://example.org", use_playwright=False)
    scanner.result.risk_score = 25
    scanner.result.risk_level = "NIEDRIG"
    scanner.result.checks.append(
        CheckResult(
            key="https_check",
            status="PASS",
            title="HTTPS Enforced",
            detail="All requests redirected to HTTPS",
        )
    )

    data = scanner.to_dict()
    assert isinstance(data, dict)
    assert data["url"] == "https://example.org"
    assert data["risk_score"] == 25
    assert len(data["checks"]) == 1

    json_file = tmp_path / "report.json"
    json_str = scanner.to_json(str(json_file))

    assert json_file.exists()
    loaded = json.loads(json_str)
    assert loaded["scan_id"] == scanner.result.scan_id
    assert loaded["checks"][0]["key"] == "https_check"
