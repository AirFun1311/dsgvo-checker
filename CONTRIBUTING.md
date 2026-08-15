# Contributing to DSGVO Compliance Checker

Thank you for your interest in improving the DSF DSGVO Compliance Checker!

## 🛠️ Development Setup

1. Fork & clone the repository:
   ```bash
   git clone https://github.com/AirFun1311/dsgvo-checker.git
   cd dsgvo-checker
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
   ```

3. Install production & development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## 🧪 Running Tests & Linter

Run tests before submitting any pull request:
```bash
# Run pytest test suite
pytest tests/ -v

# Run linting with Flake8 / Ruff
flake8 .
ruff check .
```

## 📜 Pull Request Guidelines

- Ensure all tests pass.
- Maintain existing coding conventions and type hints.
- Update documentation and docstrings when adding new scanner rules or third-party trackers.
- Open a PR against the `main` branch with a clear description of your changes.
