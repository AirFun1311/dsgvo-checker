#!/usr/bin/env python3
"""
DSGVO-Checker - Kommandozeile
=============================
Prueft eine Website auf typische Datenschutz-Probleme und erstellt auf Wunsch
einen Bericht als PDF oder JSON.

Aufruf:
    python run_scan.py <adresse> [optionen]

Beispiele:
    # Einfacher Check im Terminal
    python run_scan.py https://beispiel.de

    # Kostenloser Bericht als PDF
    python run_scan.py https://beispiel.de --pdf

    # Vollstaendiger Bericht mit Schritt-fuer-Schritt-Anleitung (verkaufbare Version)
    python run_scan.py https://beispiel.de --pdf --full

    # Fuer automatische Ablaeufe: abbrechen ab Risiko 35
    python run_scan.py https://beispiel.de --fail-on-risk 35 --fail-on-high --no-js

Rueckgabe-Codes:
    0: In Ordnung - Risiko unter der Schwelle
    1: Zu hohes Risiko - Schwelle ueberschritten
    2: Fehler - z.B. Seite nicht erreichbar oder falsche Adresse

(c) 2026 DSF Consulting
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from dsgvo_scanner import DSGVOScanner
from report_pdf import generate_report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dsgvo-checker",
        description="DSGVO-Checker - Datenschutz-Pruefung fuer Websites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Rueckgabe-Codes:
  0  In Ordnung (Risiko unter der Schwelle)
  1  Zu hohes Risiko (Schwelle ueberschritten)
  2  Fehler (Netzwerk, Adresse oder Absturz)

(c) 2026 DSF Consulting
        """,
    )
    parser.add_argument("url", help="Adresse der zu pruefenden Website (z.B. https://beispiel.de)")
    parser.add_argument(
        "--no-js",
        action="store_true",
        help="Ohne Browser pruefen (schneller, aber erkennt weniger)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ergebnis zusaetzlich als JSON-Datei speichern",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Bericht als PDF erstellen",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Vollstaendige Version mit Schritt-fuer-Schritt-Anleitung (verkaufbarer Bericht)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=".",
        help="Ordner fuer die Berichte (Standard: aktueller Ordner)",
    )
    parser.add_argument(
        "--fail-on-risk",
        type=int,
        metavar="WERT",
        default=None,
        help="Mit Code 1 abbrechen, wenn das Risiko den WERT erreicht (0-100)",
    )
    parser.add_argument(
        "--fail-on-high",
        action="store_true",
        help="Mit Code 1 abbrechen, wenn ein hohes Risiko erkannt wird",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Stiller Modus: weniger Ausgabe (fuer automatische Ablaeufe)",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    # Ausgabe-Ordner anlegen, falls Dateien geschrieben werden
    out_dir = Path(args.output_dir)
    if args.json or args.pdf:
        out_dir.mkdir(parents=True, exist_ok=True)

    use_js = not args.no_js

    if not args.quiet:
        print("\n=======================================================")
        print("  DSGVO-Checker (DSF Consulting)")
        print("=======================================================")
        print(f"  Adresse:  {args.url}")
        print(f"  Modus:    {'Mit Browser (genauer)' if use_js else 'Ohne Browser (schnell)'}")
        print("  Pruefung laeuft...\n")

    try:
        scanner = DSGVOScanner(args.url, use_playwright=use_js)
        result = scanner.scan()
    except Exception as exc:
        print(f"[FEHLER] Pruefung fehlgeschlagen: {exc}", file=sys.stderr)
        return 2

    # Bericht im Terminal anzeigen
    if not args.quiet:
        scanner.print_report()
    else:
        print(f"[CHECK] Adresse: {result.url} | Risiko: {result.risk_score}/100 | Stufe: {result.risk_level}")

    # Dateiname fuer die Berichte
    domain = result.final_url or result.url
    domain_clean = domain.replace("https://", "").replace("http://", "").replace("/", "_").rstrip("_")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    basename = f"DSGVO_Scan_{domain_clean}_{timestamp}"

    # JSON speichern
    if args.json:
        json_path = out_dir / f"{basename}.json"
        scanner.to_json(str(json_path))
        if not args.quiet:
            print(f"  [GESPEICHERT] JSON: {json_path}")

    # PDF erstellen
    if args.pdf:
        suffix = "_vollstaendig" if args.full else ""
        pdf_path = out_dir / f"{basename}{suffix}.pdf"
        generate_report(scanner.to_dict(), str(pdf_path), full=args.full)
        if not args.quiet:
            art = "Vollversion mit Anleitung" if args.full else "Kurzbericht"
            print(f"  [GESPEICHERT] PDF ({art}):  {pdf_path}")

    if (args.json or args.pdf) and not args.quiet:
        print()

    # Abbruch-Schwelle pruefen (fuer automatische Ablaeufe)
    has_high_risk = result.risk_level == "HOCH" or any(
        getattr(c, "status", None) == "FAIL" and getattr(c, "penalty", 0) >= 25 for c in result.checks
    )

    if args.fail_on_high and has_high_risk:
        if not args.quiet:
            print("[ABBRUCH] Hohes Datenschutz-Risiko erkannt.", file=sys.stderr)
        return 1

    if args.fail_on_risk is not None and result.risk_score >= args.fail_on_risk:
        if not args.quiet:
            print(
                f"[ABBRUCH] Risiko {result.risk_score} erreicht die Schwelle {args.fail_on_risk}.",
                file=sys.stderr,
            )
        return 1

    # Standard-Schwelle
    return 0 if result.risk_score < 40 else 1


if __name__ == "__main__":
    sys.exit(main())
