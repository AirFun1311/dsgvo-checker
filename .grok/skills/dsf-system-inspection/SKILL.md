---
name: dsf-system-inspection
description: Inspect the local machine, development environment and Grok installation safely. Use when system state, versions, architecture, paths or installed tools need to be verified.
---

# DSF System Inspection

Inspect before modifying.

Collect:

- operating system
- architecture
- CPU
- memory
- disk
- PowerShell
- Git
- GitHub CLI
- Node
- Python
- WSL
- VS Code
- Grok Build

Never collect secrets.

Never print:

- API keys
- authentication tokens
- passwords
- private keys
- credential files

Write diagnostic output only to the designated audit directory.

## Referenz-Implementierung

Auf Windows ARM64 kann diese Inspektion vollautomatisch ueber das
Bootstrap-Skript ausgefuehrt werden:

    powershell -ExecutionPolicy Bypass -File .\scripts\grok-bootstrap.ps1

Die Ergebnisse werden ausschliesslich nach `~/.grok/audit/` geschrieben
(system.json, tools.json, grok.json, grok-files.json, ENVIRONMENT.md) -
niemals Secrets.
