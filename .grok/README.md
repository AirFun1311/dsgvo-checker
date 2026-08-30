# Grok-CLI Agent-Setup (Vorlage)

Diese Vorlage richtet die **Grok-CLI** (superagent-ai, npm-Paket `grok-dev`)
als Coding-Agent fuer dieses Repository ein - mit vordefinierten Sub-Agenten,
MCP-Anbindung und Projekt-Instructions.

Getestetes Zielgeraet: **Windows on ARM64 / Snapdragon X Elite** (dein L7).
Ein Linux-/Server-Pfad ist ebenfalls enthalten.

---

## Was hier drin ist

| Datei | Zweck | Wird committet? |
| :--- | :--- | :---: |
| `AGENTS.md` (Repo-Wurzel) | Projekt-Instructions, die Grok automatisch liest | Ja |
| `.grok/settings.json` | Aktive Projekt-Config (MCP-Server) | Ja |
| `.grok/settings.example.json` | Beispiel-MCP-Server zum Uebernehmen | Ja |
| `.grok/user-settings.example.json` | Vorlage fuer `~/.grok/user-settings.json` (Agenten, apiKey-Platzhalter) | Ja |
| `~/.grok/user-settings.json` | Deine echten Nutzereinstellungen inkl. apiKey | **Nein** (git-ignoriert) |
| `scripts/setup-grok.ps1` | Einrichtung auf Windows ARM64 | Ja |
| `scripts/setup-grok.sh` | Einrichtung auf Linux/Server | Ja |
| `scripts/grok-guard.sh` | Optionaler PreToolUse-Sicherheits-Hook | Ja |
| `scripts/grok-bootstrap.ps1` | DSF-Bootstrap: legt `~/.grok/{agents,skills,audit}` an, sammelt System-Audit, erzeugt DSF Commander + Inspektions-Skill | Ja |
| `.grok/skills/dsf-system-inspection/SKILL.md` | Projektweiter, versionierter Inspektions-Skill (via `/skills`) | Ja |

---

## Schnellstart auf dem L7 (Windows ARM64)

```powershell
cd <repo-wurzel>
powershell -ExecutionPolicy Bypass -File .\scripts\setup-grok.ps1

# API-Key setzen (dauerhaft), danach neues Terminal:
setx GROK_API_KEY "dein_key"

# Grok starten
grok
```

Auf Linux/Server:

```bash
bash scripts/setup-grok.sh
export GROK_API_KEY="dein_key"
grok
```

Das Setup-Skript ist **idempotent** und ueberschreibt eine vorhandene
`~/.grok/user-settings.json` nicht.

### DSF-Bootstrap (System-Audit + Agenten/Skills anlegen)

Ergaenzend richtet `scripts/grok-bootstrap.ps1` die DSF-Umgebung ein:
legt `~/.grok/{agents,skills,audit}` an, schreibt ein reines System-Audit
(ohne Secrets) nach `~/.grok/audit/` und erzeugt den DSF Commander sowie
den Inspektions-Skill.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\grok-bootstrap.ps1
```

Erzeugte Audit-Dateien: `system.json`, `tools.json`, `grok.json`,
`grok-files.json`, `ENVIRONMENT.md`. Es werden keine NEXUS-Dateien veraendert.

> Hinweis ARM64: Installiere moeglichst die **native ARM64-Version** von
> Node.js (oder nutze Bun). Eine x64-emulierte Laufzeit funktioniert, ist
> auf dem Snapdragon aber spuerbar langsamer. Das Setup-Skript warnt, wenn
> Node nicht als `arm64` laeuft.

---

## Konfigurations-Hierarchie (Prioritaet hoch -> niedrig)

1. CLI-Flags (`--api-key`, `--model`, `--max-tool-rounds`)
2. Umgebungsvariablen (`GROK_API_KEY`, `GROK_BASE_URL`)
3. `~/.grok/user-settings.json` (global, benutzerweit)
4. `.grok/settings.json` (projektweit, dieses Repo)
5. Eingebaute Defaults

---

## API-Key setzen (vier Wege)

| Weg | Beispiel |
| :--- | :--- |
| Umgebungsvariable | `setx GROK_API_KEY "..."` (Win) / `export GROK_API_KEY=...` (Linux) |
| `.env` im Projekt | `GROK_API_KEY=...` (git-ignoriert) |
| CLI-Flag | `grok -k dein_key` |
| Nutzereinstellungen | `apiKey` in `~/.grok/user-settings.json` |

Niemals einen echten Key committen.

---

## Sub-Agenten (Agents)

Definiert in `~/.grok/user-settings.json` unter `subAgents`, aufrufbar in der
TUI mit `/agents`. Diese Vorlage bringt drei mit:

| Agent | Aufgabe |
| :--- | :--- |
| `dsf-commander` | Primaerer Orchestrierungs-Agent (plant, delegiert, verifiziert) |
| `dsgvo-reviewer` | Prueft Rechtszuordnung der Scan-Logik (DSGVO, TDDDG, Urteile) |
| `security-review` | Sicherheits-Review (TLS, Header, Secrets, Injection) |
| `test-writer` | Schreibt/erweitert pytest-Tests in `tests/` |

Hinweis: `scripts/grok-bootstrap.ps1` legt den DSF Commander zusaetzlich als
`~/.grok/agents/dsf-commander.md` ab. Ob die installierte Grok-CLI-Version
Agenten aus diesem Ordner automatisch laedt, ist versionsabhaengig - deshalb
ist der Commander hier zusaetzlich als `subAgent` registriert (laedt zuverlaessig).

Reservierte Namen (nicht verwendbar): `general`, `explore`, `vision`,
`verify`, `computer`.

Ein Agent hat die Felder `name`, `model` (optional; via `/models` pruefen),
`instruction`.

---

## MCP-Server

Definiert in `.grok/settings.json` unter `mcpServers`, verwaltbar in der TUI
mit `/mcps`. `.grok/settings.example.json` enthaelt fertige Beispiele
(Filesystem, GitHub). Zum Aktivieren die gewuenschten Eintraege in
`.grok/settings.json` uebernehmen; Secrets per `${ENV_VAR}` referenzieren,
nicht im Klartext.

---

## Projekt-Instructions (AGENTS.md)

Grok liest `AGENTS.md` hierarchisch von der Git-Wurzel bis zum aktuellen
Verzeichnis und haengt den Inhalt an den System-Prompt. Eine
`AGENTS.override.md` in einem Unterordner ueberschreibt geerbte Anweisungen.

---

## Optionaler Sicherheits-Hook

`scripts/grok-guard.sh` ist ein Beispiel fuer einen `PreToolUse`-Hook, der
offensichtlich zerstoererische Shell-Kommandos blockiert. Aktivierung durch
Ergaenzen eines `hooks`-Blocks in `~/.grok/user-settings.json` - siehe Kopf
des Skripts. Bewusst nicht standardmaessig aktiv, da das exakte Payload-Format
je nach Grok-CLI-Version variiert.

---

## Konzept-Mapping (Claude Code -> Grok-CLI)

| Claude Code | Grok-CLI Aequivalent |
| :--- | :--- |
| `CLAUDE.md` | `AGENTS.md` |
| Subagents | `subAgents` in `user-settings.json` |
| Skills | `~/.grok/skills/<name>/SKILL.md` (global) bzw. `.grok/skills/` (Projekt), Liste ueber `/skills` |
| MCP-Server | `mcpServers` in `.grok/settings.json` (identisches MCP-Protokoll) |
| Hooks | `hooks` in `user-settings.json` |
| Settings | `~/.grok/user-settings.json` + `.grok/settings.json` |

---

## Verifikation

```
grok --version      # CLI installiert
/agents             # zeigt die drei Sub-Agenten
/mcps               # zeigt konfigurierte MCP-Server
/models             # zeigt verfuegbare Modelle
```
