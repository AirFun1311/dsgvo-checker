# ============================================================
# DSF / GROK BUILD - AGENT BOOTSTRAP
# Target: Windows ARM64 / Snapdragon X Elite
# Purpose: Prepare Grok Build agent environment
# Does NOT modify NEXUS.
# ============================================================

$ErrorActionPreference = "Stop"

$Root = Join-Path $HOME ".grok"
$Agents = Join-Path $Root "agents"
$Skills = Join-Path $Root "skills"
$Audit  = Join-Path $Root "audit"

Write-Host ""
Write-Host "=============================================="
Write-Host "        GROK COMMAND CENTER BOOTSTRAP"
Write-Host "=============================================="
Write-Host ""

# ------------------------------------------------------------
# 1. Create isolated Grok directories
# ------------------------------------------------------------

$Directories = @(
    $Root,
    $Agents,
    $Skills,
    $Audit
)

foreach ($Directory in $Directories) {
    if (-not (Test-Path $Directory)) {
        New-Item -ItemType Directory -Path $Directory -Force | Out-Null
    }
}

# ------------------------------------------------------------
# 2. Basic system information
# ------------------------------------------------------------

$System = Get-ComputerInfo

$Report = [ordered]@{
    Timestamp          = Get-Date
    ComputerName       = $env:COMPUTERNAME
    User               = $env:USERNAME
    OS                 = $System.WindowsProductName
    WindowsVersion     = $System.WindowsVersion
    Build              = $System.OsBuildNumber
    Architecture       = $System.OsArchitecture
    Processor          = $System.CsProcessors.Name
    Model              = $System.CsModel
    RAM_GB             = [math]::Round(
        $System.CsTotalPhysicalMemory / 1GB, 2
    )
    PowerShell         = $PSVersionTable.PSVersion.ToString()
}

$Report | ConvertTo-Json -Depth 5 |
    Set-Content (Join-Path $Audit "system.json") -Encoding UTF8

# ------------------------------------------------------------
# 3. Detect development environment
# ------------------------------------------------------------

$Commands = @(
    "grok",
    "git",
    "gh",
    "node",
    "npm",
    "python",
    "wsl",
    "code"
)

$Tools = foreach ($Command in $Commands) {

    $Result = Get-Command $Command -ErrorAction SilentlyContinue

    if ($Result) {

        $Version = try {
            & $Command --version 2>&1 |
                Select-Object -First 1 |
                Out-String
        }
        catch {
            "version unavailable"
        }

        [PSCustomObject]@{
            Command = $Command
            Path    = $Result.Source
            Version = $Version.Trim()
        }

    } else {

        [PSCustomObject]@{
            Command = $Command
            Path    = $null
            Version = "NOT FOUND"
        }
    }
}

$Tools |
    ConvertTo-Json -Depth 5 |
    Set-Content (Join-Path $Audit "tools.json") -Encoding UTF8

# ------------------------------------------------------------
# 4. Inspect existing Grok installation
# ------------------------------------------------------------

$GrokState = [ordered]@{
    GrokCommand = $null
    GrokPath    = $null
    GrokVersion = $null
    GrokHome    = $env:GROK_HOME
    DotGrok     = $Root
}

$GrokCommand = Get-Command grok -ErrorAction SilentlyContinue

if ($GrokCommand) {

    $GrokState.GrokCommand = $true
    $GrokState.GrokPath = $GrokCommand.Source

    try {
        $GrokState.GrokVersion =
            (& grok --version 2>&1 | Out-String).Trim()
    }
    catch {
        $GrokState.GrokVersion = "version unavailable"
    }

} else {

    $GrokState.GrokCommand = $false
}

$GrokState |
    ConvertTo-Json -Depth 5 |
    Set-Content (Join-Path $Audit "grok.json") -Encoding UTF8

# ------------------------------------------------------------
# 5. Existing Grok configuration inventory
# ------------------------------------------------------------

$Inventory = @()

if (Test-Path $Root) {

    $Inventory = Get-ChildItem `
        -Path $Root `
        -Recurse `
        -Force `
        -File `
        -ErrorAction SilentlyContinue |
        Select-Object FullName, Length, LastWriteTime
}

$Inventory |
    ConvertTo-Json -Depth 5 |
    Set-Content (Join-Path $Audit "grok-files.json") -Encoding UTF8

# ------------------------------------------------------------
# 6. Create a SAFE Commander agent
# ------------------------------------------------------------

$Commander = @'
# DSF Commander

You are the primary orchestration agent for the DSF Grok environment.

## Mission

Turn user objectives into verified, executable work.

## Operating rules

1. Understand the requested objective before acting.
2. Inspect the available environment before making assumptions.
3. Prefer existing tools, repositories, skills and agents over duplicating them.
4. Plan complex tasks before execution.
5. Keep changes scoped to the requested task.
6. Never expose API keys, tokens, passwords or credentials.
7. Never delete or overwrite important data without explicit authorization.
8. After making changes, verify the result.
9. If a task fails, diagnose the failure and attempt a safe correction.
10. Report exactly what was changed and what remains unresolved.

## Delegation

Use specialized agents or skills when available.

Typical delegation:

- Research → research capabilities
- Programming → coding capabilities
- System administration → system capabilities
- Security → security capabilities
- Git/GitHub → repository capabilities

## Completion standard

A task is not complete merely because an action was attempted.

A task is complete when there is reasonable evidence that the requested result exists and works.
'@

$Commander |
    Set-Content `
        (Join-Path $Agents "dsf-commander.md") `
        -Encoding UTF8

# ------------------------------------------------------------
# 7. Create a system inspection skill
# ------------------------------------------------------------

$SystemSkill = @'
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
'@

$SkillDir = Join-Path $Skills "dsf-system-inspection"

if (-not (Test-Path $SkillDir)) {
    New-Item -ItemType Directory -Path $SkillDir -Force | Out-Null
}

$SystemSkill |
    Set-Content `
        (Join-Path $SkillDir "SKILL.md") `
        -Encoding UTF8

# ------------------------------------------------------------
# 8. Create an environment manifest
# ------------------------------------------------------------

$Manifest = @"
# DSF Grok Environment

Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Host: $env:COMPUTERNAME

Architecture:
$($System.OsArchitecture)

Windows:
$($System.WindowsProductName)
$($System.WindowsVersion)
Build $($System.OsBuildNumber)

Processor:
$($System.CsProcessors.Name)

RAM:
$([math]::Round($System.CsTotalPhysicalMemory / 1GB,2)) GB

Grok Home:
$($env:GROK_HOME)

Grok Config Root:
$Root

This file contains no credentials.
"@

$Manifest |
    Set-Content `
        (Join-Path $Audit "ENVIRONMENT.md") `
        -Encoding UTF8

# ------------------------------------------------------------
# 9. Final output
# ------------------------------------------------------------

Write-Host ""
Write-Host "BOOTSTRAP COMPLETE"
Write-Host ""
Write-Host "Grok directory:"
Write-Host "  $Root"
Write-Host ""
Write-Host "Audit:"
Write-Host "  $Audit"
Write-Host ""
Write-Host "Created:"
Write-Host "  ~/.grok/agents/dsf-commander.md"
Write-Host "  ~/.grok/skills/dsf-system-inspection/SKILL.md"
Write-Host ""
Write-Host "NO NEXUS FILES WERE MODIFIED."
Write-Host ""
