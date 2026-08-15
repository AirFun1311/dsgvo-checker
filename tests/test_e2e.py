"""
End-to-End Integration & CLI Execution Test
Validates end-to-end execution of run_scan CLI, PDF generation, and ScanResult output.
"""

import sys
import json
import subprocess
from pathlib import Path
import pytest


def test_e2e_cli_json_and_pdf_export(tmp_path):
    """Run CLI in fast no-js mode with JSON and PDF export and verify files generated."""
    cmd = [
        sys.executable,
        "run_scan.py",
        "https://example.com",
        "--no-js",
        "--json",
        "--pdf",
        "-o",
        str(tmp_path),
        "--quiet",
    ]
    
    repo_root = Path(__file__).parent.parent
    
    result = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    
    # Check generated files in tmp_path
    json_files = list(tmp_path.glob("*.json"))
    pdf_files = list(tmp_path.glob("*.pdf"))
    
    assert len(json_files) == 1, f"Expected 1 JSON file, found {len(json_files)}. Stderr: {result.stderr}"
    assert len(pdf_files) == 1, f"Expected 1 PDF file, found {len(pdf_files)}. Stderr: {result.stderr}"
    
    with open(json_files[0], "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "url" in data
    assert "risk_score" in data
    assert "risk_level" in data
    assert "checks" in data
    assert len(data["checks"]) > 0
    assert pdf_files[0].stat().st_size > 1000
