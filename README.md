# DSGVO Compliance Checker

Automatisierter DSGVO-Check für Websites von kleinen und mittleren Unternehmen.

Das Tool analysiert eine Website und identifiziert konkrete Datenschutz-Risiken inklusive klarer Handlungsempfehlungen.

Ziel: Abmahnrisiken erkennen und systematisch beheben.

---

## Beispiel Analyse

Website: beispiel-firma.de  

Risk Score: 62 (MITTEL)

Ergebnisse:
- HTTPS: OK  
- Cookie Banner: FEHLT  
- Datenschutzerklärung: OK  
- SSL-Zertifikat: OK  

Bewertung:  
Mittleres Risiko – konkrete Abmahngefahr durch fehlenden Cookie-Banner (häufige Fehlerquelle).

Empfehlung:  
→ Cookie Consent Tool implementieren (z. B. Borlabs oder Cookiebot)

---

## Überblick

Schnelle Analyse von Webseiten auf grundlegende DSGVO-Risiken.

Klare Bewertung statt technischem Output.

---

## Was das Tool prüft

- HTTPS-Verschlüsselung (Grundschutz der Datenübertragung)  
- Vorhandensein einer Datenschutzerklärung (rechtlich erforderlich)  
- Cookie-Banner Implementierung (häufige Abmahnquelle)  
- SSL-Zertifikat Gültigkeit (technische Sicherheit)  

---

## Schnellstart

### Voraussetzungen
- Python 3.8 oder höher

### Installation

```bash
git clone https://github.com/AirFun1311/dsgvo-checker.git
cd dsgvo-checker
python -m pip install -r requirements.txt
