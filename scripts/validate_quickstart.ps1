param(
    [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"

Write-Host "Cipla Execution Intelligence quickstart validation"
Write-Host "Phase 1 scaffold check"

$requiredPaths = @(
    "backend/requirements.txt",
    "ingestion/requirements.txt",
    "frontend/package.json",
    ".env.example",
    "data/raw/.gitkeep",
    "specs/002-execution-intelligence-platform/tasks.md"
)

foreach ($path in $requiredPaths) {
    if (-not (Test-Path $path)) {
        throw "Missing required path: $path"
    }
}

Write-Host "Required Phase 1 files are present."
Write-Host "Later phases will extend this script with migrations, ingestion, API, and frontend checks."
