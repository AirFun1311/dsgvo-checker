# Security Policy

## Supported Versions

Proactive security updates, dependency vulnerability remediation, and mitigations are provided for the following releases:

| Version | Supported | Maintenance Tier | SLA Response |
| :--- | :--- | :--- | :--- |
| `2.0.x` | Yes | Active Support & Security SLA | 24 Hours |
| `1.x` | No | End of Life (EOL) | None |

---

## Reporting a Vulnerability

The maintainers prioritize data privacy, software supply chain integrity, and responsible disclosure. If you discover a security vulnerability, please adhere to our coordinated disclosure process.

### Disclosure Process

1. **Do not create public GitHub issues** for undisclosed security vulnerabilities.
2. Submit your advisory via **[GitHub Private Security Advisories](https://github.com/AirFun1311/dsgvo-checker/security/advisories/new)** or email directly to:
   * **Security Contact**: `sf.foodzeit@googlemail.com`
3. Please include the following details in your report:
   * **Summary**: Description of the vulnerability and affected module.
   * **Severity**: Estimated CVSS v3.1 rating or severity classification.
   * **Reproduction**: Step-by-step reproduction steps or Proof of Concept (PoC).
   * **Impact**: Potential attack vectors and impact on audited systems.
   * **Proposed Remediation**: (Optional) Patch or workaround.

---

## Response & Triage SLA

* **Initial Acknowledgement**: Within **24 hours**
* **Vulnerability Triage & Assessment**: Within **48 hours**
* **Patch Release & Advisory**: Within **7 business days** (for High / Critical severity)

---

## Compliance & Standards Alignment

Software development and supply chain workflows align with:

* **European Union**: NIS2 Directive (Directive EU 2022/2555), ISO/IEC 27001:2022, DSGVO Art. 32 TOMs
* **United States**: NIST SP 800-53 Rev. 5, Executive Order 14028 (Software Supply Chain Integrity)
* **OpenSSF**: SLSA Level 3 Provenance & Open Source Security Foundation Best Practices
* **Static Analysis**: Automated GitHub CodeQL, Bandit SAST, and `pip-audit` execution on all pull requests.
