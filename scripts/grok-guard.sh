#!/usr/bin/env bash
# ============================================================================
#  grok-guard.sh - OPTIONALER PreToolUse-Hook fuer die Grok-CLI
# ----------------------------------------------------------------------------
#  Beispiel-Guard: blockiert offensichtlich zerstoererische Shell-Kommandos,
#  bevor Grok sie ausfuehrt. Bewusst "fail-open": kann die Eingabe nicht
#  geparst werden, wird NICHT blockiert (exit 0), damit legitime Arbeit nie
#  faelschlich stoppt.
#
#  Aktivierung (in ~/.grok/user-settings.json):
#      "hooks": {
#        "PreToolUse": [
#          { "matcher": "bash",
#            "hooks": [ { "type": "command",
#                         "command": "./scripts/grok-guard.sh",
#                         "timeout": 10 } ] }
#        ]
#      }
#
#  Hinweis: Das exakte Eingabe-Format der Hook-Payload haengt von der
#  Grok-CLI-Version ab. Dieses Skript liest stdin und durchsucht den Rohtext
#  nach gefaehrlichen Mustern - robust gegenueber Formataenderungen.
#  Rueckgabewert != 0 signalisiert der CLI ein Veto.
# ============================================================================
set -uo pipefail

payload="$(cat 2>/dev/null || true)"

# Liste eindeutig zerstoererischer Muster (bewusst konservativ).
patterns=(
  'rm[[:space:]]+-rf[[:space:]]+/'
  'rm[[:space:]]+-rf[[:space:]]+~'
  ':\(\)\{.*\|.*&\};:'          # Fork-Bomb
  'mkfs\.'
  'dd[[:space:]]+if=.*of=/dev/'
  '>[[:space:]]*/dev/sd'
  'chmod[[:space:]]+-R[[:space:]]+777[[:space:]]+/'
  'git[[:space:]]+push[[:space:]]+.*--force.*origin[[:space:]]+main'
)

for p in "${patterns[@]}"; do
  if printf '%s' "$payload" | grep -Eq "$p"; then
    echo "grok-guard: blockiert - potentiell zerstoererisches Kommando erkannt (Muster: $p)" >&2
    exit 1
  fi
done

exit 0
