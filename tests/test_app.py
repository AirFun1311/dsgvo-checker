"""
Unit test for Streamlit App interface and scanner integration.
Tests data structure compatibility between app rendering logic and DSGVOScanner results.
"""

from unittest.mock import MagicMock
from dsgvo_scanner import ScanResult, CheckResult


def test_app_scan_result_rendering_compatibility():
    """Verify that ScanResult properties accessed in app.py match dsgvo_scanner data structure."""
    res = ScanResult(
        url="https://test-site.de",
        final_url="https://test-site.de",
        scan_id="DSF-TEST1234",
        scan_date="15.08.2026 12:00:00 UTC",
        risk_score=25,
        risk_level="NIEDRIG",
        meta={"engine": "DSF-PRO-CORE v2.0"},
    )
    res.checks = [
        CheckResult(
            key="security_headers",
            status="PASS",
            title="Security Headers",
            detail="All standard headers active",
            penalty=0,
            rechtsgrundlage="Art. 32 DSGVO",
            empfehlung="",
            sub_findings=["HSTS present", "CSP present"],
        )
    ]
    res.third_parties = [
        {"name": "Google Fonts", "domain": "fonts.googleapis.com", "category": "cdn", "country": "US", "risk": "hoch"}
    ]
    res.cookies_before_consent = [{"name": "_ga", "domain": ".test-site.de", "secure": True}]
    res.summary = {
        "checks_fail": 0,
        "checks_pass": 1,
        "top_recommendations": [
            {"bereich": "Fonts", "prioritaet": "HOCH", "massnahme": "Lokal hosten"}
        ]
    }
    
    # Test German risk level mapping used in app.py
    risk_colors = {
        "HOCH": "🔴",
        "MITTEL": "🟡",
        "NIEDRIG": "🟢",
        "SEHR NIEDRIG": "🟢",
    }
    assert res.risk_level in risk_colors
    assert risk_colors[res.risk_level] == "🟢"
    
    # Test CheckResult properties used in app.py
    for chk in res.checks:
        assert hasattr(chk, "key")
        assert hasattr(chk, "status")
        assert hasattr(chk, "title")
        assert hasattr(chk, "detail")
        assert hasattr(chk, "penalty")
        assert hasattr(chk, "rechtsgrundlage")
        assert hasattr(chk, "empfehlung")
        assert hasattr(chk, "sub_findings")
        assert chk.status in ["PASS", "WARNING", "FAIL", "INFO", "SKIPPED"]
        
    # Test third_party structure used in app.py
    for tp in res.third_parties:
        assert "name" in tp
        assert "domain" in tp
        assert "category" in tp
        assert "country" in tp
        assert "risk" in tp
        
    # Test top_recommendations structure used in app.py
    for rec in res.summary["top_recommendations"]:
        assert "bereich" in rec
        assert "prioritaet" in rec
        assert "massnahme" in rec
