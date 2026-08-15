# 🛡️ DSGVO / GDPR Compliance Checker

[![CI Quality Pipeline](https://github.com/AirFun1311/dsgvo-checker/actions/workflows/ci.yml/badge.svg)](https://github.com/AirFun1311/dsgvo-checker/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Testing: Pytest](https://img.shields.io/badge/tests-pytest-orange.svg)](https://docs.pytest.org/)

**Production-grade automated DSGVO/GDPR compliance verification engine & audit report generator for websites and web applications.**

Developed by **[AirFun1311 / DSF Consulting](https://github.com/AirFun1311)**.

---

## 🌟 Key Features

* 🔍 **Deep Scanner Engine**: Zero Trust / Fail-Closed scanner analyzing websites via Headless Browser (Playwright) or high-speed HTTP fallback.
* 🛑 **Tracker & Third-Party Identification**: Automatic recognition of 50+ tracking systems, advertising networks, CDNs, and third-party endpoints.
* 🔤 **Dynamic Font Leakage Detection**: Detects remote Google Fonts / Adobe Typekit calls violating European privacy rulings (e.g., LG München I).
* 🔒 **Security Headers & SSL Check**: Analyzes TLS ciphers, certificate expiration, HSTS, CSP, X-Frame-Options, and Referrer-Policy.
* 🍪 **Cookie & Consent Verification**: Identifies cookies set before explicit user consent.
* 📊 **Multi-Channel Reporting**:
  * Rich interactive terminal output with colored risk ratings
  * Machine-readable **JSON exports**
  * Audit-ready **PDF report generation** (via ReportLab)
  * Web interface powered by **Streamlit**

---

## 🏗️ Architecture

```text
dsgvo-checker/
├── dsgvo_scanner.py          # Core scanner engine (DSF-PRO-CORE v2.0)
├── report_pdf.py             # Professional PDF generator with risk traffic-light system
├── app.py                    # Streamlit Web User Interface
├── run_scan.py               # CLI entrypoint and orchestrator
├── tests/                    # Automated Pytest suite
│   ├── test_scanner.py       # Engine and parser unit tests
│   ├── test_report.py        # PDF report rendering verification
│   └── test_cli.py           # CLI argument handling tests
├── .github/
│   ├── workflows/ci.yml      # CI/CD matrix pipeline
│   └── dependabot.yml        # Automated dependency updates
├── pyproject.toml            # PEP 621 build configuration
└── requirements.txt          # Production dependencies
```

---

## ⚡ Quickstart

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/AirFun1311/dsgvo-checker.git
cd dsgvo-checker

# Set up virtual environment
python -m venv .venv

# Activate environment:
# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

*(Optional) Install Playwright browser binaries for full JavaScript rendering:*
```bash
playwright install chromium
```

---

## 💻 Usage

### Command Line Interface (CLI)

Run a compliance scan directly from your terminal:

```bash
# Basic scan (with terminal report)
python run_scan.py https://example.com

# Comprehensive scan: Generate JSON and PDF reports
python run_scan.py https://example.com --pdf --json

# Fast scan without JavaScript rendering
python run_scan.py https://example.com --no-js --pdf -o ./reports/
```

#### CLI Options:
| Flag | Description |
| :--- | :--- |
| `url` | Target website URL to audit |
| `--pdf` | Generate an audit-ready PDF report |
| `--json` | Export full scan telemetry as JSON |
| `--no-js` | Disable headless browser rendering (faster, fallback mode) |
| `-o`, `--output-dir` | Target directory for generated reports (default: `.`) |

---

### Web User Interface (Streamlit)

Launch the interactive web portal:

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser to run scans, inspect risk scores, and download reports interactively.

---

## 🧪 Testing & Quality Assurance

Run the automated test suite and code linters:

```bash
# Install test tools
pip install -r requirements-dev.txt

# Run pytest with code coverage
pytest tests/ -v --cov=.

# Run code style checks
flake8 .
```

---

## ⚖️ Legal Disclaimer

*This tool provides automated technical analysis based on publicly available web resources. It does not constitute formal legal advice. For legally binding compliance audits, consult a certified Data Protection Officer (DPO) or specialized legal counsel.*

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
