#!/usr/bin/env bash
# ============================================================================
#  Grok-CLI Agent-Setup  (Linux / Server - z. B. dein Grok-Server)
# ----------------------------------------------------------------------------
#  Richtet die Grok-CLI (superagent-ai, npm-Paket "grok-dev") fuer dieses
#  Repository ein: installiert die CLI (falls noetig), legt ~/.grok an und
#  uebernimmt die Vorlagen aus .grok/ - OHNE vorhandene Dateien zu ueberschreiben.
#
#  Ausfuehrung:
#      bash scripts/setup-grok.sh
#
#  Nimmt keine zerstoererischen Aenderungen vor und schreibt keinen API-Key.
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GROK_HOME="${HOME}/.grok"

info() { printf '\033[36m[i]\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m[+]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[!]\033[0m %s\n' "$*"; }

echo "=============================================================="
echo "  Grok-CLI Agent-Setup  -  Linux / Server"
echo "=============================================================="

# --- 1. Architektur / Laufzeit ---------------------------------------------
info "Architektur: $(uname -m)"

HAS_BUN=0; HAS_NPM=0
command -v bun >/dev/null 2>&1 && HAS_BUN=1 && info "Bun gefunden:  $(bun --version)"
command -v node >/dev/null 2>&1 && info "Node gefunden: $(node -v) (arch: $(node -p 'process.arch' 2>/dev/null || echo '?'))"
command -v npm >/dev/null 2>&1 && HAS_NPM=1

# --- 2. Grok-CLI installieren ----------------------------------------------
if command -v grok >/dev/null 2>&1; then
    ok "Grok-CLI bereits installiert: $(grok --version 2>/dev/null || echo '?')"
else
    info "Grok-CLI (grok-dev) wird installiert..."
    if [ "$HAS_BUN" -eq 1 ]; then
        bun add -g grok-dev
    elif [ "$HAS_NPM" -eq 1 ]; then
        npm install -g grok-dev
    else
        warn "Weder Bun noch npm gefunden. Bitte zuerst Node.js oder Bun installieren."
        exit 1
    fi
    command -v grok >/dev/null 2>&1 && ok "Grok-CLI installiert: $(grok --version 2>/dev/null)" \
        || warn "Installiert, aber 'grok' noch nicht im PATH (neue Shell oeffnen)."
fi

# --- 3. ~/.grok anlegen -----------------------------------------------------
if [ ! -d "$GROK_HOME" ]; then
    mkdir -p "$GROK_HOME"; ok "Verzeichnis angelegt: $GROK_HOME"
else
    info "Verzeichnis vorhanden: $GROK_HOME"
fi

# --- 4. user-settings.json aus Vorlage (nicht ueberschreiben) ---------------
USER_TARGET="${GROK_HOME}/user-settings.json"
USER_TEMPLATE="${REPO_ROOT}/.grok/user-settings.example.json"
if [ -f "$USER_TARGET" ]; then
    warn "Bereits vorhanden - wird NICHT ueberschrieben: $USER_TARGET"
    info "Vorlage zum Abgleich: $USER_TEMPLATE"
elif [ -f "$USER_TEMPLATE" ]; then
    cp "$USER_TEMPLATE" "$USER_TARGET"
    ok "Vorlage kopiert nach: $USER_TARGET"
    warn "WICHTIG: apiKey setzen ODER Umgebungsvariable GROK_API_KEY nutzen."
else
    warn "Vorlage nicht gefunden: $USER_TEMPLATE"
fi

# --- 5. Hinweise ------------------------------------------------------------
[ -f "${REPO_ROOT}/.grok/settings.json" ] && ok "Projekt-Config vorhanden: .grok/settings.json"
[ -f "${REPO_ROOT}/AGENTS.md" ] && ok "Projekt-Instructions vorhanden: AGENTS.md"

cat <<EOF

--------------------------------------------------------------
  Naechste Schritte
--------------------------------------------------------------
  1) API-Key setzen (z. B. in ~/.bashrc oder ~/.profile):
       export GROK_API_KEY="dein_key"
     Oder apiKey direkt in $USER_TARGET eintragen.

  2) Grok im Projektordner starten:
       cd "$REPO_ROOT" && grok

  3) In der TUI:
       /agents  -> Sub-Agenten (dsgvo-reviewer, security-review, test-writer)
       /mcps    -> MCP-Server
       /models  -> verfuegbare Modelle
--------------------------------------------------------------
EOF
ok "Setup abgeschlossen."
