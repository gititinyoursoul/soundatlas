param(
    [int] $BackendPort = 8000,
    [int] $FrontendPort = 5173
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$BackendDir = Join-Path $RepoRoot "backend"
$FrontendDir = Join-Path $RepoRoot "frontend"

if (-not (Test-Path (Join-Path $BackendDir "pyproject.toml"))) {
    throw "Backend project not found at $BackendDir"
}

if (-not (Test-Path (Join-Path $FrontendDir "package.json"))) {
    throw "Frontend project not found at $FrontendDir"
}

$BackendCommand = "cd `"$BackendDir`"; uv run uvicorn app.main:app --reload --host 127.0.0.1 --port $BackendPort"
$FrontendCommand = "cd `"$FrontendDir`"; `$env:VITE_API_BASE_URL='http://127.0.0.1:$BackendPort'; npm run dev -- --host 127.0.0.1 --port $FrontendPort"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCommand
Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCommand

Write-Host "SoundAtlas dev servers are starting..."
Write-Host "Backend:  http://127.0.0.1:$BackendPort"
Write-Host "Frontend: http://127.0.0.1:$FrontendPort"
