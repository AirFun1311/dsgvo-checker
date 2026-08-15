# Changelog

All notable changes to the **DSGVO / GDPR Compliance Verification Engine** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-08-15

### Added
- **Headless Browser Engine**: Playwright-based browser rendering for full JavaScript execution, single-page apps (SPA), and dynamic third-party tracking detection.
- **Fail-Safe HTTP Fallback**: High-speed fallback scanner via `requests` + `BeautifulSoup` when headless browser is disabled or unavailable.
- **Dynamic Font Leakage Detection**: Automated recognition of remote font calls (Google Fonts, Adobe Typekit) violating EU privacy rulings (LG Muenchen I, Az. 3 O 17493/20).
- **SSL / TLS & Security Headers Scanner**: In-depth evaluation of TLS ciphers, certificate expiration, HSTS, CSP, X-Frame-Options, and Referrer-Policy.
- **Audit-Ready PDF Generator**: Vector-rendered PDF reports powered by ReportLab with executive summary, risk ratings, and actionable remediation tasks.
- **Interactive Web Interface**: Streamlit-based web portal for real-time scans and immediate PDF report downloads.
- **Enterprise DevSecOps Pipeline**:
  - Matrix test suite across Python 3.10, 3.11, 3.12, 3.13.
  - Astral Ruff linting and formatting automation.
  - Automated Bandit SAST and GitHub CodeQL analysis.
  - SPDX/CycloneDX automated SBOM generation.
- **Containerization**: Multi-stage `Dockerfile` and `docker-compose.yml` supporting both Streamlit UI and headless CLI modes.
- **CLI Security Gates**: Added `--fail-on-risk` and `--fail-on-high` flags for direct CI/CD pipeline integration with standard exit codes.

### Changed
- Refactored scanner architecture to `DSF-PRO-CORE v2.0` with unified telemetry schema.
- Upgraded risk score calculation model to multi-vector weighted penalty system.
- Standardized documentation across all repositories with complete governance suite (`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`).

---

## [1.1.0] - 2026-02-10

### Added
- Initial automated detection for 30+ European and US tracking systems.
- Cookie telemetry before explicit consent check.
- Export scan results to machine-readable JSON format.

### Fixed
- Fixed URL normalization for subdomains with custom ports.
- Resolved encoding issues when parsing German characters in privacy policy pages.

---

## [1.0.0] - 2025-12-01

### Added
- Initial release of the DSGVO Compliance Quickcheck scanner.
- Basic HTTPS enforcement check and SSL certificate validity verification.
- Basic command-line interface with formatted terminal outputs.
- MIT Open-Source License.

---
<sub>[Unreleased]: https://github.com/AirFun1311/dsgvo-checker/compare/v2.0.0...HEAD</sub>
<sub>[2.0.0]: https://github.com/AirFun1311/dsgvo-checker/compare/v1.1.0...v2.0.0</sub>
<sub>[1.1.0]: https://github.com/AirFun1311/dsgvo-checker/compare/v1.0.0...v1.1.0</sub>
<sub>[1.0.0]: https://github.com/AirFun1311/dsgvo-checker/releases/tag/v1.0.0</sub>
