# Contributing Guidelines

Thank you for contributing to the **DSGVO / GDPR Compliance Verification Engine**.

This document details the development environment setup, coding standards, and pull request procedures required for all contributions.

---

## Code of Conduct

All contributors and participants must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Development Environment Setup

### System Prerequisites
* Python 3.10, 3.11, 3.12, or 3.13
* Git 2.30+
* (Optional) Docker & Docker Compose

### Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/AirFun1311/dsgvo-checker.git
   cd dsgvo-checker
   ```

2. **Initialize Virtual Environment**:
   ```bash
   python -m venv .venv
   
   # Linux / macOS:
   source .venv/bin/activate
   
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install Headless Browser Dependencies**:
   ```bash
   playwright install chromium
   ```

5. **Configure Pre-Commit Hooks**:
   ```bash
   pre-commit install
   ```

---

## Quality Assurance & Testing Requirements

All pull requests must pass the automated CI quality gates:

```bash
# Run pytest test suite
pytest tests/ -v

# Run linting and code formatting checks
ruff check .
ruff format --check .

# Run static application security testing (SAST)
bandit -r . -ll -ii

# Run static type checking
mypy --ignore-missing-imports .
```

---

## Version Control & Commit Standards

We enforce [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>(<scope>): <summary in imperative mood>

[optional body providing technical justification]

[optional footer(s)]
```

### Approved Commit Types:
* `feat`: New feature or audit rule
* `fix`: Bug fix
* `docs`: Documentation updates only
* `style`: Formatting, whitespace adjustments
* `refactor`: Code reorganization without functional changes
* `perf`: Performance optimization
* `test`: Adding or updating test cases
* `ci`: Continuous integration and build automation changes
* `chore`: Build configuration or dependency updates

---

## Pull Request Lifecycle

1. Fork the repository and create a feature branch (`feat/short-description` or `fix/short-description`).
2. Implement your changes following PEP 8 and project typing annotations.
3. Add unit tests in `tests/` covering new logic or regression cases.
4. Verify all tests pass locally.
5. Submit a pull request against the `main` branch with a complete description of the changes.

---

## Security Disclosures

Do not open public GitHub issues for undisclosed security vulnerabilities. Follow the coordinated disclosure procedure outlined in [SECURITY.md](SECURITY.md).

---

## License

All contributions will be licensed under the project's [MIT License](LICENSE).
