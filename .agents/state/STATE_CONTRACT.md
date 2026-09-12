# State-Contract: Reproduzierbarkeit, Persistenz, Zero-Trust, Self-Healing

Gemeinsamer Vertrag fuer den DSF-Agenten-Schwarm. Jedes Modell (Grok,
Antigravity/Claude, Gemini, DeepSeek, Qwen ...) liest diese Datei und das
gemeinsame Journal beim Start und schreibt seine Aktionen zurueck. So weiss
die linke Hand, was die rechte tut.

## Zuerst: drei Begriffe sauber trennen

Diese drei werden oft vermischt - sie loesen unterschiedliche Probleme:

| Begriff | Was es bedeutet | Was es NICHT tut |
| :--- | :--- | :--- |
| **Reproduzierbarkeit** | Gleiche Eingabe + gleiche Config -> (moeglichst) gleiches Ergebnis | Macht ein LLM nicht 100 % deterministisch |
| **Persistenz** | Zustand (was getan/entschieden/fehlgeschlagen) ueberlebt Neustarts | Verhindert keine Halluzination |
| **Grounding/Verifikation** | Ausgaben gegen Fakten/Tools pruefen | Ersetzt keine Persistenz |

**Wichtig zu deinem Gemini-Problem:** Halluzination wird **nicht** durch
Persistenz geheilt. Persistenz hilft dir, sie zu **erkennen und zu erholen**
(Self-Healing). Verhindern tust du sie durch Grounding + Verifikation
(Regel: "erst erledigt, wenn belegbar"). Eine Boot-Datei, die der Agent
jedes Mal liest ("wo war ich, was war falsch"), ist genau das richtige
Muster fuer Erkennen/Erholen - aber kein Halluzinations-Stopp an sich.

## Reproduzierbarkeit bei LLMs (realistisch)

Bit-genau ist bei LLMs nicht garantiert. Erreichbar ist **gebundene**
Reproduzierbarkeit:

1. **Modell + Version pinnen** (z. B. `gemini-3.1-pro`, exakte Revision) -
   nie "latest".
2. **Temperatur/Seed** so niedrig/fix wie moeglich fuer deterministische Schritte.
3. **Prompt + Kontext versionieren** (welche AGENTS.md, welche Skills, welche
   Eingaben) - im Journal mitschreiben.
4. **Werkzeug-Ergebnisse statt Modell-Meinung** fuer Fakten.

Genau diese vier Felder haelt das Journal fest, damit ein Lauf nachvollziehbar
und wiederholbar ist.

## Zero-Trust-Policy

1. **Kein impliziter Vertrauensvorschuss** - der Output eines Agenten wird von
   einem zweiten Schritt/Agenten verifiziert, bevor er als wahr gilt.
2. **Least Privilege** - jeder Agent bekommt nur die Rechte/Tools, die seine
   Aufgabe braucht.
3. **Alles ins Journal** - jede relevante Aktion wird protokolliert
   (Agent, Modell, Aktion, Ergebnis, Fehler).
4. **Secrets nie ins Journal/Audit** - nur Referenzen (Env-Var-Name), nie Werte.

## Persistenz: zwei Ebenen (redundant)

1. **Boot-/State-Datei** (`session-state.json`, Schema:
   `session-state.schema.json`) - klein, menschenlesbar, wird beim Start gelesen
   und fortgeschrieben. Die "linke Hand weiss, was die rechte tut"-Datei.
2. **Cloud-Kopie** - dieselbe State-Datei + Journal in der Cloud-Umgebung
   ablegen, weil Sandboxes fluechtig sind. Ueberlebt Container-Neustarts.

## Self-Healing-Schleife (beim Start jedes Agenten)

1. State-Datei + Journal lesen.
2. Letzten Eintrag pruefen: Status `in_progress` oder `failed`?
3. Wenn ja: letzten sicheren Checkpoint (`last_good_checkpoint`) ermitteln.
4. Ab Checkpoint **fortsetzen** oder auf ihn **zuruecksetzen** (nie blind neu
   starten, nie halbfertigen Zustand als fertig behandeln).
5. Ergebnis wieder ins Journal schreiben.

## Speicher-Wahl: JSON vs. SQLite vs. SQL-Server

**Wichtigster Stolperstein:** Wenn **mehrere Agenten gleichzeitig** in EINE
JSON-Datei schreiben, gibt es Races/Korruption. Das ist die wahrscheinlichste
Ursache dafuer, dass es "noch nicht funktioniert".

Empfehlung, gestuft (keep it simple):

| Bedarf | Empfehlung |
| :--- | :--- |
| Boot-Contract, kleiner Zustand, 1 Schreiber | **JSON-Datei** (diese hier) |
| Ereignis-/Metadaten-Log, mehrere Schreiber, Abfragen ueber viele Laeufe | **SQLite** (eine Datei, Datei-Locking, null Ops, reproduzierbar) |
| Echte Nebenlaeufigkeit/Skalierung, viele Clients, zentraler Dienst | Erst dann ein **SQL-Server** (Postgres/SQL Server) |

Fuer deinen Fall: **JSON-Contract fuer den Boot-Zustand + SQLite fuer das
Journal/Metadaten**. Ein voller SQL-Server ist aktuell Overkill; er lohnt erst
bei echter Nebenlaeufigkeit oder Skalierung. Wenn Metadaten spaeter zentral
abfragbar sein muessen, ist der Umstieg SQLite -> Postgres/SQL-Server klein,
weil das Schema (siehe JSON-Schema) schon steht.

## Dateien in diesem Ordner

| Datei | Zweck |
| :--- | :--- |
| `STATE_CONTRACT.md` | Dieser Vertrag |
| `session-state.schema.json` | JSON-Schema (Validierung) des Boot-/State-Objekts |
| `session-state.example.json` | Beispielzustand nach ein paar Schritten |
| `journal.py` | Lauffaehige Referenz: JSON-State + SQLite-Journal (WAL, mehr-schreiber-sicher) + Self-Healing. `python journal.py --selftest` demonstriert Absturz und Wiederaufsetzen. |
