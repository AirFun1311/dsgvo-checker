"""
Enterprise Unit & Mock Test Suite for DSGVO Scanner Engine
Tests network-isolated logic, header parsing, tracking evaluation, and penalty computations.
"""

from unittest.mock import MagicMock, patch
import pytest
from dsgvo_scanner import (
    DSGVOScanner,
    CheckResult,
    ScanResult,
    KNOWN_TRACKERS,
    SECURITY_HEADERS,
)


def test_penalty_and_risk_score_aggregation():
    """Verify that score computation correctly aggregates penalties and sets risk levels."""
    scanner = DSGVOScanner("test-site.de", use_playwright=False)
    
    # Add passing check
    chk_pass = CheckResult(
        key="security_headers",
        status="PASS",
        title="Security Headers",
        detail="All present",
        penalty=0,
        rechtsgrundlage="Art. 32 DSGVO",
        empfehlung="",
    )
    scanner._add_check(chk_pass)
    assert scanner.result.risk_score == 0
    
    # Add failing check with high penalty
    chk_fail = CheckResult(
        key="ssl_encryption",
        status="FAIL",
        title="SSL / TLS",
        detail="No SSL",
        penalty=45,
        rechtsgrundlage="Art. 32 DSGVO",
        empfehlung="Enable HTTPS",
    )
    scanner._add_check(chk_fail)
    assert scanner.result.risk_score == 45
    
    # Finalize and check risk level calculation
    scanner.finalize()
    assert scanner.result.risk_level == "MITTEL"
    assert scanner.result.summary["checks_fail"] == 1
    assert scanner.result.summary["checks_pass"] == 1
    assert len(scanner.result.summary["top_recommendations"]) == 1


def test_tracker_categorization_and_risk():
    """Test tracker domain matching and categorization against KNOWN_TRACKERS."""
    analytics_trackers = [d for d, m in KNOWN_TRACKERS.items() if m.get("category") == "analytics"]
    advertising_trackers = [d for d, m in KNOWN_TRACKERS.items() if m.get("category") == "advertising"]
    consent_tools = [d for d, m in KNOWN_TRACKERS.items() if m.get("category") == "consent"]
    
    assert len(analytics_trackers) >= 5
    assert len(advertising_trackers) >= 5
    assert len(consent_tools) >= 5
    assert "google-analytics.com" in KNOWN_TRACKERS
    assert KNOWN_TRACKERS["google-analytics.com"]["country"] == "US"


def test_security_header_analyzer_with_mock_headers():
    """Test HTTP security headers evaluation logic with simulated response headers."""
    scanner = DSGVOScanner("https://secure-enterprise.de", use_playwright=False)
    
    scanner._response_headers = {
        "strict-transport-security": "max-age=31536000; includeSubDomains; preload",
        "content-security-policy": "default-src 'self'",
        "x-frame-options": "DENY",
        "x-content-type-options": "nosniff",
        "referrer-policy": "strict-origin-when-cross-origin",
        "permissions-policy": "geolocation=()",
    }
    
    scanner.check_security_headers()
    
    # Locate security_headers check
    sec_check = next((c for c in scanner.result.checks if c.key == "security_headers"), None)
    assert sec_check is not None
    assert sec_check.status == "PASS"
    assert sec_check.penalty == 0


def test_third_party_detection_mocked():
    """Test detection of third-party domains and known services."""
    scanner = DSGVOScanner("https://example-shop.de", use_playwright=False)
    scanner._external_domains.add("google-analytics.com")
    scanner._external_domains.add("fonts.googleapis.com")
    
    scanner.check_third_parties()
    
    tp_check = next((c for c in scanner.result.checks if c.key == "third_parties"), None)
    assert tp_check is not None
    assert len(scanner.result.third_parties) >= 2


def test_forms_compliance_analysis():
    """Test forms analysis for privacy disclaimers and HTTPS actions."""
    scanner = DSGVOScanner("https://example-shop.de", use_playwright=False)
    scanner._html_raw = """
    <html>
        <body>
            <form action="https://example-shop.de/submit" method="post">
                <input type="email" name="email" placeholder="Deine E-Mail" />
                <p>Ich habe die Datenschutzerklärung zur Kenntnis genommen.</p>
                <button type="submit">Senden</button>
            </form>
        </body>
    </html>
    """
    scanner.check_forms()
    forms_check = next((c for c in scanner.result.checks if c.key == "forms"), None)
    assert forms_check is not None
    assert forms_check.status == "PASS"


def test_impressum_and_privacy_policy_detection():
    """Test detection of Impressum and Privacy Policy links in DOM."""
    scanner = DSGVOScanner("https://unternehmensberatung-berlin.de", use_playwright=False)
    scanner._html_raw = """
    <!DOCTYPE html>
    <html>
        <head><title>Test</title></head>
        <body>
            <a href="/impressum">Impressum</a>
            <a href="/datenschutz">Datenschutzerklärung</a>
        </body>
    </html>
    """
    scanner.check_impressum()
    scanner.check_privacy_policy()
    
    imp_chk = next((c for c in scanner.result.checks if c.key == "impressum"), None)
    dse_chk = next((c for c in scanner.result.checks if c.key == "privacy_policy"), None)
    
    assert imp_chk is not None
    assert dse_chk is not None
    assert imp_chk.status == "PASS"
    assert dse_chk.status == "PASS"

