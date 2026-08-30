<#
==============================================================================
  Grok-CLI Agent-Setup  (Windows on ARM64 / Snapdragon X Elite)
------------------------------------------------------------------------------
  Richtet die Grok-CLI (superagent-ai, npm-Paket "grok-dev") fuer dieses
  Repository ein: installiert die CLI (falls noetig), legt ~/.grok an und
  uebernimmt die Vorlagen aus .grok/ - OHNE vorhandene Dateien zu ueberschreiben.

  Ausfuehrung (PowerShell, KEINE Adminrechte noetig):
      cd <repo-wurzel>
      powershell -ExecutionPolicy Bypass -File .\scripts\setup-grok.ps1

  Das Skript nimmt KEINE zerstoererischen Aenderungen vor und schreibt keinen
  API-Key. Den Key setzt du am Ende selbst (Anleitung wird ausgegeben).
==============================================================================
#>

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$GrokHome = Join-Path $env:USERPROFILE '.grok'

function Info($m) { Write-Host "[i] $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "[+] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[!] $m" -ForegroundColor Yellow }

Write-Host "=============================================================="
Write-Host "  Grok-CLI Agent-Setup  -  Windows ARM64"
Write-Host "=============================================================="

# --- 1. Architektur pruefen -------------------------------------------------
$arch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
Info "OS-Architektur: $arch"
if ($arch -ne 'Arm64') { Warn "Erwartet Arm64 (Snapdragon). Setup laeuft trotzdem weiter." }

# --- 2. Laufzeit pruefen (Bun bevorzugt, sonst Node/npm) ---------------------
$hasBun  = [bool](Get-Command bun  -ErrorAction SilentlyContinue)
$hasNode = [bool](Get-Command node -ErrorAction SilentlyContinue)
$hasNpm  = [bool](Get-Command npm  -ErrorAction SilentlyContinue)

if ($hasNode) {
    $nodeArch = (& node -p "process.arch" 2>$null)
    Info "Node gefunden: $(& node -v)  (Architektur: $nodeArch)"
    if ($nodeArch -ne 'arm64') {
        Warn "Node laeuft NICHT nativ als arm64 (aktuell: $nodeArch = x64-Emulation)."
        Warn "Fuer beste Performance native ARM64-Version von Node.js installieren."
    }
}
if ($hasBun)  { Info "Bun gefunden:  $(& bun --version)" }

# --- 3. Grok-CLI installieren (falls fehlt) ---------------------------------
$hasGrok = [bool](Get-Command grok -ErrorAction SilentlyContinue)
if ($hasGrok) {
    Ok "Grok-CLI bereits installiert: $(& grok --version 2>$null)"
} else {
    Info "Grok-CLI (grok-dev) wird installiert..."
    if ($hasBun) {
        & bun add -g grok-dev
    } elseif ($hasNpm) {
        & npm install -g grok-dev
    } else {
        Warn "Weder Bun noch npm gefunden. Bitte zuerst Node.js (ARM64) oder Bun installieren."
        Warn "Danach dieses Skript erneut ausfuehren."
        exit 1
    }
    if (Get-Command grok -ErrorAction SilentlyContinue) {
        Ok "Grok-CLI installiert: $(& grok --version 2>$null)"
    } else {
        Warn "Installation abgeschlossen, aber 'grok' ist noch nicht im PATH."
        Warn "Neue Terminal-Sitzung oeffnen und PATH pruefen."
    }
}

# --- 4. ~/.grok anlegen -----------------------------------------------------
if (-not (Test-Path $GrokHome)) {
    New-Item -ItemType Directory -Path $GrokHome -Force | Out-Null
    Ok "Verzeichnis angelegt: $GrokHome"
} else {
    Info "Verzeichnis vorhanden: $GrokHome"
}

# --- 5. user-settings.json aus Vorlage (nicht ueberschreiben) ----------------
$userTarget   = Join-Path $GrokHome 'user-settings.json'
$userTemplate = Join-Path $RepoRoot '.grok\user-settings.example.json'
if (Test-Path $userTarget) {
    Warn "Bereits vorhanden - wird NICHT ueberschrieben: $userTarget"
    Info "Vorlage zum Abgleich: $userTemplate"
} elseif (Test-Path $userTemplate) {
    Copy-Item $userTemplate $userTarget
    Ok "Vorlage kopiert nach: $userTarget"
    Warn "WICHTIG: apiKey in dieser Datei setzen ODER Umgebungsvariable GROK_API_KEY nutzen."
} else {
    Warn "Vorlage nicht gefunden: $userTemplate"
}

# --- 6. Hinweise zu Projekt-Config ------------------------------------------
$projSettings = Join-Path $RepoRoot '.grok\settings.json'
if (Test-Path $projSettings) { Ok "Projekt-Config vorhanden: .grok\settings.json (MCP-Server hier ergaenzen)" }
$agents = Join-Path $RepoRoot 'AGENTS.md'
if (Test-Path $agents) { Ok "Projekt-Instructions vorhanden: AGENTS.md" }

# --- 7. API-Key-Anleitung ---------------------------------------------------
Write-Host ""
Write-Host "--------------------------------------------------------------"
Write-Host "  Naechste Schritte"
Write-Host "--------------------------------------------------------------"
Write-Host "  1) API-Key setzen (eine Variante waehlen):"
Write-Host "       a) Dauerhaft (Benutzer-Umgebungsvariable):"
Write-Host "          setx GROK_API_KEY `"dein_key`""
Write-Host "          (neues Terminal oeffnen, damit sie greift)"
Write-Host "       b) Oder apiKey direkt in $userTarget eintragen"
Write-Host ""
Write-Host "  2) Grok im Projektordner starten:"
Write-Host "       cd `"$RepoRoot`""
Write-Host "       grok"
Write-Host ""
Write-Host "  3) In der TUI pruefen:"
Write-Host "       /agents   -> zeigt die Sub-Agenten (dsgvo-reviewer, security-review, test-writer)"
Write-Host "       /mcps     -> MCP-Server verwalten"
Write-Host "       /models   -> verfuegbare Modelle (ggf. 'model' in user-settings.json anpassen)"
Write-Host "--------------------------------------------------------------"
Ok "Setup abgeschlossen."
