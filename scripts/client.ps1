param([switch]$Check)
$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..')
try {
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw 'Install uv first: winget install --id astral-sh.uv -e'
    }
    uv sync --locked
    if ($LASTEXITCODE -ne 0) { throw 'Client dependency setup failed.' }
    if ($Check) {
        uv run --locked python scripts/check_server.py
    } else {
        uv run --locked python main.py
    }
    if ($LASTEXITCODE -ne 0) { throw 'Client command failed; see the error above.' }
} finally {
    Pop-Location
}
