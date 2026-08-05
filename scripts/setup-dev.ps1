[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BackendDir = Join-Path $RepoRoot "backend"
$FrontendDir = Join-Path $RepoRoot "frontend"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required but was not found in PATH."
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm is required but was not found in PATH."
}

if (-not (Test-Path (Join-Path $BackendDir "pyproject.toml"))) {
    throw "Backend project not found at $BackendDir"
}

if (-not (Test-Path (Join-Path $FrontendDir "package.json"))) {
    throw "Frontend project not found at $FrontendDir"
}

Write-Host "Installing locked backend dependencies..."
Push-Location $BackendDir
try {
    uv sync --locked --dev
}
finally {
    Pop-Location
}

Write-Host "Installing locked frontend dependencies..."
Push-Location $FrontendDir
try {
    npm ci
}
finally {
    Pop-Location
}

Write-Host "SoundAtlas development dependencies are ready."
