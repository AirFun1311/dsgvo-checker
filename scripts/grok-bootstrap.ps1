#Requires -Version 5.1
# ============================================================
# DSF / GROK BUILD - AGENT BOOTSTRAP
# Target: Windows ARM64 / Snapdragon X Elite
# Purpose: Prepare Grok Build agent environment
# Does NOT modify NEXUS.
# ------------------------------------------------------------
# Eigenschaften:
#  - Nicht-destruktiv: vorhandene Agent-/Skill-Dateien werden NICHT
#    ueberschrieben (Hand-Edits bleiben erhalten).
#  - Einzige Quelle der Wahrheit: Agent/Skill werden aus .agents/ KOPIERT,
#    nicht im Skript eingebettet (keine Drift).
#  - Robust: eine fehlgeschlagene Teilpruefung bricht das Skript nicht ab;
#    Fehler werden ins Audit geschrieben.
#  - Reines Audit, niemals Secrets.
# ============================================================

Set-StrictMode -Version Latest

# ------------------------------------------------------------
# Pfade
# ------------------------------------------------------------
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Root     = Join-Path $HOME ".grok"
$Agents   = Join-Path $Root "agents"
$Skills   = Join-Path $Root "skills"
$Audit    = Join-Path $Root "audit"

$SrcAgents = Join-Path $RepoRoot ".agents"
$SrcSkills = Join-Path $SrcAgents "skills"

function Write-Info($m) { Write-Host "[i] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "[+] $m" -ForegroundColor Green }
function Write-Warn2($m){ Write-Host "[!] $m" -ForegroundColor Yellow }

# Bereinigt Tool-Ausgaben: entfernt Null-Bytes (UTF-16 z. B. bei wsl) und
# Steuerzeichen, nimmt die erste nicht-leere Zeile.
function Get-CleanVersion {
    param([string[]]$Lines)
    $joined = ($Lines -join "`n") -replace "`0", ""
    $clean  = ($joined -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" })
    if ($clean.Count -gt 0) { return $clean[0] }
    return "version unavailable"
}

# Schreibt ein Objekt als JSON ins Audit; Fehler werden nur gemeldet, nie fatal.
function Save-Json($Object, $FileName) {
    try {
        $target = Join-Path $Audit $FileName
        $Object | ConvertTo-Json -Depth 6 | Set-Content -Path $target -Encoding UTF8
        Write-Ok "Audit: $FileName"
    } catch {
        Write-Warn2 "Konnte $FileName nicht schreiben: $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "=============================================="
Write-Host "        GROK COMMAND CENTER BOOTSTRAP"
Write-Host "=============================================="
Write-Host ""

# ------------------------------------------------------------
# 1. Isolierte Grok-Verzeichnisse anlegen
# ------------------------------------------------------------
foreach ($Directory in @($Root, $Agents, $Skills, $Audit)) {
    if (-not (Test-Path $Directory)) {
        New-Item -ItemType Directory -Path $Directory -Force | Out-Null
    }
}

# ------------------------------------------------------------
# 2. Basis-Systeminformationen (gezielte CIM-Abfragen statt Get-ComputerInfo)
# ------------------------------------------------------------
$Report = [ordered]@{
    Timestamp    = (Get-Date).ToString("s")
    ComputerName = $env:COMPUTERNAME
    User         = $env:USERNAME
    OS           = $null
    Version      = $null
    Build        = $null
    Architecture = $null
    Processor    = $null
    Cores        = $null
    Model        = $null
    RAM_GB       = $null
    PowerShell   = $PSVersionTable.PSVersion.ToString()
}
try {
    $os  = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
    $cpu = Get-CimInstance Win32_Processor -ErrorAction Stop | Select-Object -First 1
    $cs  = Get-CimInstance Win32_ComputerSystem -ErrorAction Stop
    $Report.OS           = $os.Caption
    $Report.Version      = $os.Version
    $Report.Build        = $os.BuildNumber
    $Report.Architecture = $os.OSArchitecture
    $Report.Processor    = $cpu.Name
    $Report.Cores        = $cpu.NumberOfCores
    $Report.Model        = $cs.Model
    $Report.RAM_GB       = [math]::Round($cs.TotalPhysicalMemory / 1GB, 2)
} catch {
    Write-Warn2 "Systeminfo teilweise nicht verfuegbar: $($_.Exception.Message)"
    $Report.OS = "unavailable: $($_.Exception.Message)"
}
Save-Json $Report "system.json"

# ------------------------------------------------------------
# 3. Entwicklungsumgebung erkennen
# ------------------------------------------------------------
$Commands = @("grok", "git", "gh", "node", "npm", "python", "wsl", "code")
$Tools = foreach ($Command in $Commands) {
    $Result = Get-Command $Command -ErrorAction SilentlyContinue
    if ($Result) {
        $isStoreStub = ($Result.Source -like "*\WindowsApps\*") -and ($Command -eq "python")
        if ($isStoreStub) {
            $version = "NOT INSTALLED (Windows-Store-Alias)"
        } else {
            try {
                $raw = & $Command --version 2>&1
                $version = Get-CleanVersion ($raw | ForEach-Object { "$_" })
            } catch {
                $version = "version unavailable"
            }
        }
        [PSCustomObject]@{ Command = $Command; Path = $Result.Source; Version = $version }
    } else {
        [PSCustomObject]@{ Command = $Command; Path = $null; Version = "NOT FOUND" }
    }
}
Save-Json $Tools "tools.json"

# ------------------------------------------------------------
# 4. Vorhandene Grok-Installation pruefen
# ------------------------------------------------------------
$GrokState = [ordered]@{
    GrokCommand = $false
    GrokPath    = $null
    GrokVersion = $null
    GrokHome    = $env:GROK_HOME
    DotGrok     = $Root
}
$GrokCommand = Get-Command grok -ErrorAction SilentlyContinue
if ($GrokCommand) {
    $GrokState.GrokCommand = $true
    $GrokState.GrokPath    = $GrokCommand.Source
    try {
        $GrokState.GrokVersion = Get-CleanVersion ((& grok --version 2>&1) | ForEach-Object { "$_" })
    } catch {
        $GrokState.GrokVersion = "version unavailable"
    }
}
Save-Json $GrokState "grok.json"

# ------------------------------------------------------------
# 5. Inventar vorhandener Grok-Konfiguration
# ------------------------------------------------------------
$Inventory = @()
try {
    if (Test-Path $Root) {
        $Inventory = @(Get-ChildItem -Path $Root -Recurse -Force -File -ErrorAction SilentlyContinue |
            Select-Object FullName, Length, LastWriteTime)
    }
} catch {
    Write-Warn2 "Inventar unvollstaendig: $($_.Exception.Message)"
}
Save-Json $Inventory "grok-files.json"

# ------------------------------------------------------------
# 6. Agent + Skill aus .agents/ KOPIEREN (nicht ueberschreiben, nicht einbetten)
# ------------------------------------------------------------
function Copy-IfAbsent($SourcePath, $TargetPath, $Label) {
    if (-not (Test-Path $SourcePath)) {
        Write-Warn2 "Quelle fehlt, uebersprungen ($Label): $SourcePath"
        return
    }
    if (Test-Path $TargetPath) {
        Write-Warn2 "Vorhanden - NICHT ueberschrieben ($Label): $TargetPath"
        return
    }
    $parent = Split-Path -Parent $TargetPath
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    Copy-Item -Path $SourcePath -Destination $TargetPath -Force
    Write-Ok "Kopiert ($Label): $TargetPath"
}

# DSF Commander
Copy-IfAbsent (Join-Path $SrcAgents "dsf-commander.md") `
              (Join-Path $Agents "dsf-commander.md") "Agent"

# Skills (jeder Unterordner mit SKILL.md)
if (Test-Path $SrcSkills) {
    foreach ($skillDir in (Get-ChildItem -Path $SrcSkills -Directory -ErrorAction SilentlyContinue)) {
        $src = Join-Path $skillDir.FullName "SKILL.md"
        $dst = Join-Path (Join-Path $Skills $skillDir.Name) "SKILL.md"
        Copy-IfAbsent $src $dst "Skill: $($skillDir.Name)"
    }
} else {
    Write-Warn2 "Kein Quell-Skills-Ordner: $SrcSkills"
}

# ------------------------------------------------------------
# 7. Umgebungs-Manifest
# ------------------------------------------------------------
$Manifest = @"
# DSF Grok Environment

Created: $((Get-Date).ToString("yyyy-MM-dd HH:mm:ss"))
Host: $env:COMPUTERNAME

Architecture: $($Report.Architecture)
Windows:      $($Report.OS) $($Report.Version) (Build $($Report.Build))
Processor:    $($Report.Processor)
RAM:          $($Report.RAM_GB) GB

Grok Home:        $($env:GROK_HOME)
Grok Config Root: $Root

This file contains no credentials.
"@
try {
    $Manifest | Set-Content -Path (Join-Path $Audit "ENVIRONMENT.md") -Encoding UTF8
    Write-Ok "Audit: ENVIRONMENT.md"
} catch {
    Write-Warn2 "Konnte ENVIRONMENT.md nicht schreiben: $($_.Exception.Message)"
}

# ------------------------------------------------------------
# 8. Abschluss
# ------------------------------------------------------------
Write-Host ""
Write-Host "BOOTSTRAP COMPLETE"
Write-Host ""
Write-Host "Grok directory: $Root"
Write-Host "Audit:          $Audit"
Write-Host ""
Write-Host "Quelle (Single Source of Truth): $SrcAgents"
Write-Host "  -> ~/.grok/agents/dsf-commander.md"
Write-Host "  -> ~/.grok/skills/<name>/SKILL.md"
Write-Host ""
Write-Host "NO NEXUS FILES WERE MODIFIED."
Write-Host ""
