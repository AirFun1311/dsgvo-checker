import os
from report_pdf import generate_report, DSGVOReportPDF


def test_generate_pdf_report(tmp_path):
    """Test generating a professional PDF compliance audit report."""
    mock_data = {
        "url": "https://firma-beispiel.de",
        "final_url": "https://firma-beispiel.de",
        "scan_date": "15.08.2026 12:00:00 UTC",
        "scan_id": "DSF-A1B2C3D4E5F6",
        "risk_score": 35,
        "risk_level": "MITTEL",
        "summary": {
            "verdict": "Mittleres Risiko - Handlungsbedarf bei Third-Party Trackern.",
            "checks_pass": 4,
            "checks_warning": 1,
            "checks_fail": 1,
            "top_recommendations": [
                {
                    "prioritaet": "HOCH",
                    "bereich": "Einwilligungsmanagement",
                    "massnahme": "Cookie Banner mit Opt-In vor dem Laden von Skripten konfigurieren."
                },
                {
                    "prioritaet": "MITTEL",
                    "bereich": "Schriftarten",
                    "massnahme": "Google Fonts lokal auf dem Webserver hosten."
                }
            ]
        },
        "checks": [
            {
                "key": "https_enforced",
                "status": "PASS",
                "title": "HTTPS & SSL-Verschluesselung",
                "detail": "TLS 1.3 aktiv und Zertifikat gueltig.",
                "penalty": 0,
                "rechtsgrundlage": "Art. 32 Abs. 1 lit. a DSGVO",
                "empfehlung": "",
                "sub_findings": ["Zertifikat gueltig", "HSTS Header vorhanden"]
            },
            {
                "key": "google_fonts",
                "status": "FAIL",
                "title": "Google Fonts dynamisch eingebunden",
                "detail": "Dynamischer Abruf von fonts.googleapis.com uebertraegt IP-Adressen in Drittstaaten.",
                "penalty": 30,
                "rechtsgrundlage": "Art. 44 ff. DSGVO, LG Muenchen I (Az. 3 O 17493/20)",
                "empfehlung": "Schriften lokal auf dem eigenen Server hosten.",
                "sub_findings": ["fonts.googleapis.com gefunden", "fonts.gstatic.com gefunden"]
            }
        ],
        "third_parties": [
            {
                "name": "Google Fonts",
                "category": "fonts",
                "country": "US",
                "risk": "hoch"
            }
        ],
        "cookies_before_consent": [
            {
                "name": "_ga",
                "domain": ".firma-beispiel.de",
                "secure": True,
                "httpOnly": False
            }
        ],
        "dse_coverage": {
            "score": 80,
            "matched": ["Google Analytics"],
            "missing": []
        },
        "meta": {
            "engine": "DSF-PRO-CORE v2.0",
            "renderer": "requests",
            "js_rendering": False
        }
    }

    output_pdf = tmp_path / "dsgvo_audit_test.pdf"
    result_path = generate_report(mock_data, str(output_pdf))

    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 1000  # Non-empty valid PDF file
