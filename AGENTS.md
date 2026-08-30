# AGENTS.md - Projektanweisungen fuer KI-Agenten (Grok-CLI)

Diese Datei wird von der Grok-CLI automatisch gelesen und in den System-Prompt
eingebunden (hierarchisch von der Git-Wurzel bis zum aktuellen Verzeichnis).
Sie gilt fuer alle Agenten, die in diesem Repository arbeiten.

## Projektueberblick

`dsgvo-checker` ist eine automatisierte Datenschutz- und Sicherheitspruefung fuer
Webseiten (Zielmarkt: deutscher Mittelstand, Datenschutzbeauftragte, Webagenturen).
Das System analysiert Webseiten auf:

- Externe Schriften / CDNs (Art. 44 ff. DSGVO, LG Muenchen I - 3 O 17493/20)
- Cookies / LocalStorage vor Einwilligung (Paragraph 25 Abs. 1 TDDDG)
- Transportverschluesselung TLS/HTTPS (Art. 32 DSGVO)
- Sicherheits-Header HSTS/CSP (Art. 32 DSGVO, TOMs)
- Transparenz der Rechtstexte Impressum/Datenschutz (Art. 12, 13 DSGVO)

## Architektur / wichtige Dateien

| Datei | Zweck |
| :--- | :--- |
| `dsgvo_scanner.py` | Kern-Scan-Engine (Prueflogik, Risikoberechnung) |
| `run_scan.py` | CLI-Einstiegspunkt |
| `app.py` | Streamlit-Weboberflaeche |
| `report_pdf.py` | PDF-Berichterstellung |
| `tests/` | pytest-Tests (Referenz: 16 Tests) |
| `beispiele/` | Beispiel-Berichte |

## Ausfuehren & Testen

```bash
# Umgebung
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
playwright install chromium

# Scan
python run_scan.py https://beispiel.de --pdf --json -o ./berichte/

# Tests und Linting (VOR jedem Commit ausfuehren)
pytest tests/ -v
ruff check .
```

## Konventionen

- **Sprache:** Antworten und Nutzertexte auf **Deutsch**. Code-Kommentare
  passend zum umgebenden Code.
- **Keine Emojis** in Code, Dokumentation, Commit-Messages oder Ausgaben
  (bewusste Projektentscheidung, siehe Git-Historie). Klare, sachliche
  Enterprise-Typografie.
- **Rechtliche Genauigkeit:** Gesetzeszuordnungen (DSGVO-Artikel, TDDDG,
  Urteile) niemals raten. Bei Aenderungen an der Pruef-/Zuordnungslogik die
  bestehende Quelle in `COMPLIANCE_MATRIX_2026.md` und README abgleichen.
- **Keine echten Secrets** committen (API-Keys, Lizenzschluessel). `.env`
  und `.grok/user-settings.json` sind bewusst git-ignoriert.
- **Fundstellen** immer als `Datei:Zeile` angeben.
- **Umfang:** Aenderungen minimal halten - nur was die Aufgabe erfordert.

## Sicherheit

- Der Scanner ruft externe URLs auf. Eingaben (Ziel-URLs) als nicht
  vertrauenswuerdig behandeln.
- Vor Aenderungen an TLS-/Header-/Netzwerklogik `SECURITY.md` beachten.
