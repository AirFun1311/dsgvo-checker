#!/usr/bin/env python3
"""
DSF DSGVO / GDPR Compliance Verification Engine - CLI Orchestrator
==================================================================
Production-grade command-line interface for automated website auditing,
CI/CD security gates, and multi-format compliance report generation.

Usage:
    python run_scan.py <url> [OPTIONS]

Examples:
    # Standard terminal audit
    python run_scan.py https://example.com

    # Generate both JSON and PDF audit reports
    python run_scan.py https://example.com --pdf --json -o ./audit-results/

    # CI/CD Security Gate: Fail build if risk score >= 35 or if high-risk violation exists
    python run_scan.py https://example.com --fail-on-risk 35 --fail-on-high --no-js

Exit Codes:
    0: Success - Compliance checks passed within acceptable risk threshold
    1: Compliance Failure - Violations exceeded defined risk threshold
    2: Runtime Error - Network failure, invalid URL, or scanner crash
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from dsgvo_scanner import DSGVOScanner
from report_pdf import generate_report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dsgvo-scanner",
        description="DSF DSGVO / GDPR Compliance Scanner & CI/CD Security Gate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit Codes:
  0  Success / Compliant (Risk within acceptable threshold)
  1  Threshold Exceeded (High risk violations or risk score exceeded)
  2  Execution / Network / Argument Error

(c) 2026 DSF Consulting | AF13 Enterprise Systems Architecture
        """,
    )
    parser.add_argument("url", help="Target website URL to scan (e.g., https://example.de)")
    parser.add_argument(
        "--no-js",
        action="store_true",
        help="Disable JavaScript headless browser rendering (fast HTTP fallback mode)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Export comprehensive scan results as machine-readable JSON",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Generate an audit-ready executive PDF compliance report",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=".",
        help="Directory to save exported JSON/PDF reports (default: current directory)",
    )
    parser.add_argument(
        "--fail-on-risk",
        type=int,
        metavar="SCORE",
        default=None,
        help="Exit with code 1 if total risk score is equal to or exceeds SCORE (0-100)",
    )
    parser.add_argument(
        "--fail-on-high",
        action="store_true",
        help="Exit with code 1 if any high-risk violation or overall HIGH risk rating is detected",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Quiet mode: suppress non-essential output (optimized for CI/CD pipelines)",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    # Ensure output directory exists if files are to be written
    out_dir = Path(args.output_dir)
    if args.json or args.pdf:
        out_dir.mkdir(parents=True, exist_ok=True)

    use_js = not args.no_js

    if not args.quiet:
        print("\n=======================================================")
        print("  DSF DSGVO / GDPR Compliance Verification Engine (v2.0)")
        print("=======================================================")
        print(f"  Target URL:   {args.url}")
        print(f"  Engine Mode:  {'Headless Playwright (JavaScript)' if use_js else 'HTTP Fallback (Static DOM)'}")
        print("  Audit in progress...\n")

    try:
        scanner = DSGVOScanner(args.url, use_playwright=use_js)
        result = scanner.scan()
    except Exception as exc:
        print(f"[ERROR] Scanner execution failed: {exc}", file=sys.stderr)
        return 2

    # Render terminal report
    if not args.quiet:
        scanner.print_report()
    else:
        print(f"[AUDIT] URL: {result.url} | Score: {result.risk_score}/100 | Severity: {result.risk_level}")

    # Generate output file basename
    domain = result.final_url or result.url
    domain_clean = domain.replace("https://", "").replace("http://", "").replace("/", "_").rstrip("_")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    basename = f"DSGVO_Scan_{domain_clean}_{timestamp}"

    # JSON export
    if args.json:
        json_path = out_dir / f"{basename}.json"
        scanner.to_json(str(json_path))
        if not args.quiet:
            print(f"  [EXPORT] JSON saved: {json_path}")

    # PDF export
    if args.pdf:
        pdf_path = out_dir / f"{basename}.pdf"
        generate_report(scanner.to_dict(), str(pdf_path))
        if not args.quiet:
            print(f"  [EXPORT] PDF saved:  {pdf_path}")

    if (args.json or args.pdf) and not args.quiet:
        print()

    # CI/CD Security Gate Evaluation
    has_high_risk = result.risk_level == "HOCH" or any(
        getattr(c, "status", None) == "FAIL" and getattr(c, "penalty", 0) >= 25 for c in result.checks
    )

    if args.fail_on_high and has_high_risk:
        if not args.quiet:
            print("[CI GATE FAILED] High-severity compliance violation detected.", file=sys.stderr)
        return 1

    if args.fail_on_risk is not None and result.risk_score >= args.fail_on_risk:
        if not args.quiet:
            print(
                f"[CI GATE FAILED] Risk score {result.risk_score} exceeds defined threshold {args.fail_on_risk}.",
                file=sys.stderr,
            )
        return 1

    # Default fallback threshold
    return 0 if result.risk_score < 40 else 1


if __name__ == "__main__":
    sys.exit(main())
