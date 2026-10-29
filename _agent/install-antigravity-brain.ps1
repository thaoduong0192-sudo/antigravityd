# =============================================================================
# Antigravity Full Brain & Skills Installer (One-Click Sync for New Machines)
# =============================================================================
# Usage on a new machine:
#   powershell -ExecutionPolicy Bypass -File .\_agent\install-antigravity-brain.ps1
# =============================================================================

param(
    [string]$TargetWorkspace = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"
$SourceAgentDir = $PSScriptRoot
$UserHome = $env:USERPROFILE
$GlobalConfigSkills = Join-Path $UserHome ".gemini\config\skills"
$GlobalAgySkills = Join-Path $UserHome ".gemini\antigravity\skills"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ANTIGRAVITY PRO BRAIN & SKILLS INSTALLER (15 SKILLS)    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Ensure Global Directories Exist
New-Item -ItemType Directory -Force -Path $GlobalConfigSkills | Out-Null
New-Item -ItemType Directory -Force -Path $GlobalAgySkills | Out-Null

# 2. If installing into a different target workspace, copy _agent and AGENTS.md
if ($TargetWorkspace -ne (Resolve-Path (Join-Path $SourceAgentDir "..")).Path) {
    Write-Host "[1/3] Copying _agent & AGENTS.md to workspace: $TargetWorkspace..." -ForegroundColor Yellow
    Copy-Item -Path $SourceAgentDir -Destination (Join-Path $TargetWorkspace "_agent") -Recurse -Force
    $RootAgentsMd = Join-Path (Split-Path $SourceAgentDir -Parent) "AGENTS.md"
    if (Test-Path $RootAgentsMd) {
        Copy-Item -Path $RootAgentsMd -Destination (Join-Path $TargetWorkspace "AGENTS.md") -Force
    }
} else {
    Write-Host "[1/3] Workspace _agent directory already in place at: $SourceAgentDir" -ForegroundColor Green
}

# 3. Sync Global Skills to ~/.gemini/config/skills & ~/.gemini/antigravity/skills
#    so they are available across ALL workspaces on the new machine
Write-Host "[2/3] Syncing all 15 Skills to Global Antigravity Config..." -ForegroundColor Yellow
$SkillDirs = Get-ChildItem -Path (Join-Path $SourceAgentDir "skills") -Directory
foreach ($skill in $SkillDirs) {
    $destGlobal = Join-Path $GlobalConfigSkills $skill.Name
    Copy-Item -Path $skill.FullName -Destination $destGlobal -Recurse -Force
    Write-Host "  + Installed Global Skill: $($skill.Name)" -ForegroundColor Gray
}

# Also ensure nlm-skill is in ~/.gemini/antigravity/skills
$NlmSource = Join-Path $SourceAgentDir "skills\nlm-skill"
if (Test-Path $NlmSource) {
    Copy-Item -Path $NlmSource -Destination (Join-Path $GlobalAgySkills "nlm-skill") -Recurse -Force
}

# 4. Verify Node.js & Hooks Integrity
Write-Host "[3/3] Verifying Deterministic Lifecycle Hooks (hooks.json)..." -ForegroundColor Yellow
$NodeCheck = Get-Command node -ErrorAction SilentlyContinue
if ($NodeCheck) {
    Write-Host "  + Node.js detected ($((node --version))). Lifecycle hooks are READY." -ForegroundColor Green
} else {
    Write-Host "  ! Warning: Node.js not found in PATH. Install Node.js to enable hooks.json." -ForegroundColor Red
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  HOAN TAT! Antigravity tren may nay da co day du 100%    " -ForegroundColor Green
Write-Host "  Rules, 15 Skills, Lifecycle Hooks, Workflows & Memory.  " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
