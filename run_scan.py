#!/usr/bin/env python3
"""
DSF DSGVO Scanner - CLI
=======================
Usage:
    python run_scan.py <url> [--no-js] [--json] [--pdf]

Beispiele:
    python run_scan.py example.com
    python run_scan.py https://firma.de --pdf
    python run_scan.py firma.de --no-js --json --pdf
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

from dsgvo_scanner import DSGVOScanner
from report_pdf import generate_report


def main():
    parser = argparse.ArgumentParser(
        description="DSF DSGVO Compliance Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="(c) 2026 DSF Consulting | AF13-NEXUS"
    )
    parser.add_argument("url", help="Zu scannende Website-URL")
    parser.add_argument("--no-js", action="store_true",
                        help="Kein JS-Rendering (schneller, aber weniger genau)")
    parser.add_argument("--json", action="store_true",
                        help="JSON-Report speichern")
    parser.add_argument("--pdf", action="store_true",
                        help="PDF-Report generieren")
    parser.add_argument("--output-dir", "-o", default=".",
                        help="Ausgabeverzeichnis (Standard: aktueller Ordner)")

    args = parser.parse_args()

    # Output-Verzeichnis
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Scanner
    use_js = not args.no_js
    scanner = DSGVOScanner(args.url, use_playwright=use_js)

    print(f"\n  DSF DSGVO Scanner startet...")
    print(f"  URL: {args.url}")
    print(f"  JS-Rendering: {'aktiv' if use_js else 'deaktiviert'}")
    print(f"  Bitte warten...\n")

    result = scanner.scan()

    # Terminal-Output
    scanner.print_report()

    # Dateiname-Basis
    domain = result.final_url or result.url
    domain_clean = domain.replace("https://", "").replace("http://", "").replace("/", "_").rstrip("_")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    basename = f"DSGVO_Scan_{domain_clean}_{timestamp}"

    # JSON
    if args.json:
        json_path = out_dir / f"{basename}.json"
        scanner.to_json(str(json_path))
        print(f"  JSON gespeichert: {json_path}")

    # PDF
    if args.pdf:
        pdf_path = out_dir / f"{basename}.pdf"
        generate_report(scanner.to_dict(), str(pdf_path))
        print(f"  PDF gespeichert:  {pdf_path}")

    if args.json or args.pdf:
        print()

    return 0 if result.risk_score < 40 else 1


if __name__ == "__main__":
    sys.exit(main())
