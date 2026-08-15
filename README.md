<div align="center">

# DSGVO-Checker

### Automatisierte Datenschutz- und SicherheitsprÃ¼fung fÃ¼r Webseiten
**PrÃ¤zise technische Bestandsaufnahme fÃ¼r Unternehmen, Datenschutzbeauftragte und Webagenturen**

[![CI Qualitaetspipeline](https://github.com/AirFun1311/dsgvo-checker/actions/workflows/ci.yml/badge.svg)](https://github.com/AirFun1311/dsgvo-checker/actions)
[![CodeQL Sicherheitsanalyse](https://github.com/AirFun1311/dsgvo-checker/actions/workflows/codeql.yml/badge.svg)](https://github.com/AirFun1311/dsgvo-checker/actions)
[![Version: 2.0.0](https://img.shields.io/badge/Version-2.0.0-0969da.svg?logo=github)](https://github.com/AirFun1311/dsgvo-checker/releases)
[![Teststatus: 16 Bestanden](https://img.shields.io/badge/Tests-16%20Bestanden-238636.svg?logo=pytest&logoColor=white)](https://github.com/AirFun1311/dsgvo-checker/actions)
[![Lieferkettensicherheit: SLSA Stufe 3](https://img.shields.io/badge/Lieferkette-SLSA%20Stufe%203-238636.svg?logo=openssf)](https://slsa.dev/)
[![Software-Stueckliste: SPDX 2.3](https://img.shields.io/badge/SBOM-SPDX%202.3%20Automatisiert-8250df.svg)](https://spdx.dev/)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Docker Container](https://img.shields.io/badge/Container-Docker%20Bereit-2496ED.svg?logo=docker&logoColor=white)](Dockerfile)
[![Lizenz: Kommerziell](https://img.shields.io/badge/Lizenz-Kommerziell%20Source--Available-blue.svg)](LICENSE)

<p align="center">
  <strong>ZuverlÃ¤ssige und wiederholbare Compliance-PrÃ¼fung fÃ¼r deutsche Webauftritte.</strong><br>
  Analysiert Webseiten automatisiert auf unzulÃ¤ssige DatenÃ¼bertragungen (Â§ 25 TDDDG), unberechtigte Drittanbieter-Tracker, externe Schriftarten (LG MÃ¼nchen I) und technische SicherheitsmÃ¤ngel (Art. 32 DSGVO).
</p>

[Schnellstart](#schnellstart) â€¢ [Lizenzmodelle & Preise](#lizenzmodelle--preise) â€¢ [Technische Leistungsmerkmale](#technische-leistungsmerkmale) â€¢ [Rechtliche PrÃ¼ffelder](#rechtliche-pr%C3%BCffelder--gesetzesabgleich) â€¢ [Kommandozeile](#kommandozeilen-schnittstelle-cli)

</div>

---

## Lizenzmodelle & Preise

> **Professionelle PrÃ¼f-Software fÃ¼r den deutschen Mittelstand.**  
> In dieses System sind monatelange juristische und technische Recherchen aktueller Rechtsnormen (DSGVO, Â§ 25 TDDDG, BSI-Standards) sowie praxiserprobte Software-Architektur eingeflossen.  
> 
> Um eine kontinuierliche Pflege, rechtliche AktualitÃ¤t und technische Weiterentwicklung sicherzustellen, wird diese Software unter einem transparenten Lizenzmodell bereitgestellt:

### Ãœbersicht der Lizenzmodelle

| Lizenzmodell | Berechtigung & Einsatzbereich | VergÃ¼tung | Bezugsweg |
| :--- | :--- | :---: | :--- |
| **PersÃ¶nliche Lizenz** | FÃ¼r Einzelpersonen, Studierende und Forschung zur persÃ¶nlichen Weiterbildung & privaten Analyse. | **29 â‚¬** *(einmalig)* | Per E-Mail / Rechnung |
| **Gewerbliche Einzel-Lizenz** | FÃ¼r 1 Unternehmen / SelbststÃ¤ndigen zur eigenstÃ¤ndigen und dauerhaften PrÃ¼fung der eigenen Domain. | **129 â‚¬** *(einmalig)* | Per E-Mail / Rechnung |
| **Agentur- & Berater-Lizenz** | FÃ¼r Webagenturen, SystemhÃ¤user und IT-Berater. Unbegrenzte Mandanten-PrÃ¼fungen inklusive PDF-Export. | **390 â‚¬** *(einmalig)* | Per E-Mail / Rechnung |
| **Individueller Audit-Service** | DurchfÃ¼hrung der vollstÃ¤ndigen technischen PrÃ¼fung durch den Entwickler inklusive verifiziertem PDF-Bericht. | **190 â‚¬** *(pro Domain)* | Per E-Mail / Rechnung |

**Bestellungen & Rechnungsstellung (mit ausgewiesener Mehrwertsteuer):**  
Richten Sie Ihre Lizenzanfrage bitte formlos per E-Mail an: `sf.foodzeit@googlemail.com`  
*(Zahlung per BankÃ¼berweisung, PayPal oder Kreditkarte. Sie erhalten eine ordnungsgemÃ¤ÃŸe Rechnung sowie ein offizielles Lizenzzertifikat.)*

---

## Technische Leistungsmerkmale

* **VollstÃ¤ndige Browser-basierte Analyse**: Simuliert einen echten Webseitenbesuch Ã¼ber eine automatisierte Browser-Engine (Playwright / Chromium) zur lÃ¼ckenlosen Erkennung dynamischer Skripte, Werbenetzwerke und Session-Recorder.
* **PrÃ¼fung externer Schriften & CDNs**: Erkennt unzulÃ¤ssige Serververbindungen zu Drittstaaten (z. B. Google Fonts, Adobe Typekit) gemÃ¤ÃŸ der Rechtsprechung des *LG MÃ¼nchen I (Az. 3 O 17493/20)*.
* **VerschlÃ¼sselungs- & Sicherheits-Audit**: ÃœberprÃ¼ft TransportverschlÃ¼sselung (TLS), ZertifikatsgÃ¼ltigkeit, HSTS mit Preload sowie serverseitige Sicherheits-Header (CSP, X-Frame-Options, Referrer-Policy) nach Art. 32 DSGVO.
* **Einwilligungs- & Cookie-Erkennung**: Identifiziert Cookies und Web-Storage-Zugriffe, die vor einer ausdrÃ¼cklichen und informierten Nutzereinwilligung gesetzt werden (Â§ 25 Abs. 1 TDDDG).
* **PrÃ¼ffÃ¤hige Berichterstellung**: Erzeugt strukturierte, druckfertige PDF-PrÃ¼fberichte fÃ¼r GeschÃ¤ftsfÃ¼hrung, Kunden und Dokumentationspflichten sowie JSON-Daten fÃ¼r automatisierte Schnittstellen.
* **Integrierte QualitÃ¤ts-Schwellenwerte**: Konfigurierbare Abbruchkriterien (`--fail-on-risk`, `--fail-on-high`) zur automatischen FehlerÃ¼berwachung in Entwicklungs- und Freigabeprozessen.

---

## Systemarchitektur & Ablauf

```mermaid
flowchart TD
    A[Ziel-Website URL] --> B{PrÃ¼f-Orchestrator}
    
    B -->|Dynamische Analyse| C[Automatisierte Browser-Engine]
    B -->|SchnellprÃ¼fung| D[Direkte HTTP/HTML-Analyse]
    
    C --> E[Erfasste Netzwerk- & DOM-Telemetrie]
    D --> E
    
    E --> F[Compliance-Auswertungslogik]
    
    subgraph Prueffelder [PrÃ¼ffelder nach Rechtsnorm]
        F --> G1[Externe Schriften & Fremdserver]
        F --> G2[Tracker- & Statistik-Signaturen]
        F --> G3[Cookie-Setzung vor Einwilligung]
        F --> G4[TLS / HTTPS & Sicherheits-Header]
        F --> G5[Rechtstexte Impressum & Datenschutz]
    end
    
    Prueffelder --> H[Berechnung der Risikostufe & Strafmatrix]
    
    H --> I1[Strukturierte Terminal-Ausgabe]
    H --> I2[Druckfertiger PDF-PrÃ¼fbericht]
    H --> I3[Maschinenlesbarer JSON-Export]
    H --> I4[Grafische Web-BedienoberflÃ¤che]
```

---

## Schnellstart

### 1. Grafische Web-BedienoberflÃ¤che starten (Docker)

Startet die Web-OberflÃ¤che auf Port 8501:

```bash
docker run -d -p 8501:8501 --name dsgvo-checker ghcr.io/airfun1311/dsgvo-checker:latest
```

Die BedienoberflÃ¤che ist anschlieÃŸend unter `http://localhost:8501` im Webbrowser erreichbar.

---

### 2. Lokale Installation (Python)

```bash
# Quellcode herunterladen
git clone https://github.com/AirFun1311/dsgvo-checker.git
cd dsgvo-checker

# Virtuelle Python-Umgebung einrichten
python -m venv .venv

# Umgebung aktivieren:
# Linux / macOS:
source .venv/bin/activate
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# AbhÃ¤ngigkeiten installieren
pip install -r requirements.txt

# Browser-Komponente fÃ¼r JavaScript-PrÃ¼fung installieren:
playwright install chromium
```

---

## Kommandozeilen-Schnittstelle (CLI)

PrÃ¼fungen direkt Ã¼ber das Terminal ausfÃ¼hren:

```bash
# Standard-PrÃ¼fung mit Terminal-Ausgabe
python run_scan.py https://beispiel-unternehmen.de

# VollstÃ¤ndiges Audit: Erzeugt PDF-PrÃ¼fbericht und JSON-Datenexport
python run_scan.py https://beispiel-unternehmen.de --pdf --json -o ./berichte/

# Schnelle VorprÃ¼fung ohne Browser-Engine
python run_scan.py https://beispiel-unternehmen.de --no-js --pdf
```

### Ãœbersicht der Befehlsparameter

| Parameter | Typ | Beschreibung |
| :--- | :--- | :--- |
| `url` | `Text` | Ziel-URL der zu prÃ¼fenden Webseite *(Pflichtangabe)* |
| `--pdf` | `Schalter` | Erzeugt einen druckfertigen PDF-PrÃ¼fbericht |
| `--json` | `Schalter` | Exportiert alle PrÃ¼fergebnisse als strukturierte JSON-Datei |
| `--no-js` | `Schalter` | FÃ¼hrt die PrÃ¼fung im schnellen HTTP-Modus ohne Browser aus |
| `-o`, `--output-dir` | `Pfad` | Zielverzeichnis fÃ¼r generierte Berichte *(Standard: `. /`)* |
| `--fail-on-risk` | `Zahl` | Beendet mit RÃ¼ckgabewert `1`, wenn der Risikowert $\ge$ Schwellenwert ist (0â€“100) |
| `--fail-on-high` | `Schalter` | Beendet mit RÃ¼ckgabewert `1`, wenn mindestens ein schwerer VerstoÃŸ vorliegt |
| `-q`, `--quiet` | `Schalter` | UnterdrÃ¼ckt Textausgaben (geeignet fÃ¼r automatisierte HintergrundlÃ¤ufe) |

---

## Rechtliche PrÃ¼ffelder & Gesetzesabgleich

Die technischen PrÃ¼fungen sind direkt den geltenden deutschen und europÃ¤ischen Rechtsnormen zugeordnet:

| PrÃ¼fbereich | Gesetzliche Grundlage | Schweregrad | Technische Relevanz |
| :--- | :--- | :--- | :--- |
| **Externe Schriftarten / CDNs** | Art. 44 ff. DSGVO, *LG MÃ¼nchen I (3 O 17493/20)* | **HOCH** | UnzulÃ¤ssige Ãœbermittlung von IP-Adressen an Drittstaaten ohne Einwilligung |
| **Cookies & LocalStorage** | Â§ 25 Abs. 1 TDDDG, Art. 6 Abs. 1 lit. a DSGVO | **HOCH** | Speichern und Auslesen von Nutzerdaten vor aktiver Einwilligung |
| **TransportverschlÃ¼sselung** | Art. 32 Abs. 1 lit. a DSGVO | **KRITISCH** | Fehlende oder veraltete HTTPS/TLS-VerschlÃ¼sselung bei DatenÃ¼bertragungen |
| **Sicherheits-Header (HSTS/CSP)** | Art. 32 Abs. 1 lit. b DSGVO (TOMs) | **MITTEL** | Fehlende serverseitige Absicherung gegen Manipulation und Abfangen |
| **Transparenz der Rechtstexte** | Art. 12, 13 DSGVO | **MITTEL** | UnvollstÃ¤ndige Angaben oder fehlende DatenschutzerklÃ¤rung / Impressum |

---

## Software-QualitÃ¤tssicherung & Tests

Das System wird vor jeder VerÃ¶ffentlichung automatisiert auf FunktionalitÃ¤t und Richtigkeit geprÃ¼ft:

```bash
# Alle 16 automatisierten Tests ausfÃ¼hren
pytest tests/ -v

# Einhaltung von Quellcode- und Formatierungsstandards prÃ¼fen
ruff check .
```

---

## Betreiber & Kontakt

* **Entwickler & Inhaber**: DSF Consulting / AirFun1311  
* **Standort**: FÃ¼rth / Metropolregion NÃ¼rnberg, Deutschland  
* **Lizenz- und PrÃ¼fanfragen**: `sf.foodzeit@googlemail.com`  
* **Hinweis**: Dieses System fÃ¼hrt eine technische Bestandsaufnahme durch. Es ersetzt keine individuelle juristische Beratung durch einen Fachanwalt oder zertifizierten Datenschutzbeauftragten.

---

<div align="center">
  <sub>Entwickelt fÃ¼r den deutschen Mittelstand â€¢ DSF Consulting â€¢ FÃ¼rth, Deutschland</sub>
</div>

