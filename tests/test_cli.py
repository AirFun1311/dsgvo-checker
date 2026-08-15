import sys
import subprocess
from pathlib import Path
import pytest


def test_cli_help_flag():
    """Verify that CLI entry point accepts --help and returns exit code 0."""
    repo_root = Path(__file__).resolve().parent.parent
    cli_script = repo_root / "run_scan.py"

    result = subprocess.run(
        [sys.executable, str(cli_script), "--help"],
        capture_output=True,
        text=True,
        cwd=str(repo_root)
    )
    assert result.returncode == 0
    assert "DSF DSGVO Compliance Scanner" in result.stdout
    assert "--no-js" in result.stdout
    assert "--pdf" in result.stdout
    assert "--json" in result.stdout
