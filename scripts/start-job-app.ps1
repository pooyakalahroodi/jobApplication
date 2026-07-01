$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"
$PythonExe = Join-Path $BackendDir ".venv\Scripts\python.exe"
$BackendUrl = "http://127.0.0.1:8000"
$FrontendUrl = "http://127.0.0.1:5173"
$OllamaUrl = "http://localhost:11434"
$OllamaModel = "llama3.1:8b"

function Test-CommandExists {
    param([Parameter(Mandatory = $true)][string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

function Test-HttpOk {
    param([Parameter(Mandatory = $true)][string]$Url)
    try {
        Invoke-WebRequest $Url -UseBasicParsing -TimeoutSec 2 | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Start-NamedWindow {
    param(
        [Parameter(Mandatory = $true)][string]$Title,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string]$Command
    )

    Start-Process powershell.exe -WorkingDirectory $WorkingDirectory -ArgumentList @(
        "-NoExit",
        "-NoProfile",
        "-Command",
        "`$Host.UI.RawUI.WindowTitle = '$Title'; $Command"
    )
}

Write-Host "Starting Job Applications Dashboard..." -ForegroundColor Cyan

if (-not (Test-Path $PythonExe)) {
    Write-Host "Backend virtual environment was not found." -ForegroundColor Yellow
    Write-Host "Create it first with:" -ForegroundColor Yellow
    Write-Host "  cd $BackendDir"
    Write-Host "  python -m venv .venv"
    Write-Host "  .\.venv\Scripts\activate"
    Write-Host "  pip install -e `".[dev]`""
    Read-Host "Press Enter to close"
    exit 1
}

if (-not (Test-CommandExists "npm")) {
    Write-Host "npm was not found. Install Node.js first." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

if (-not (Test-CommandExists "ollama")) {
    Write-Host "Ollama was not found. Install Ollama first: https://ollama.com/download/windows" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

if (-not (Test-HttpOk $OllamaUrl)) {
    Write-Host "Starting Ollama..." -ForegroundColor Cyan
    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-NoProfile",
        "-Command",
        "`$Host.UI.RawUI.WindowTitle = 'Ollama'; ollama serve"
    )
    Start-Sleep -Seconds 4
}

$modelList = ollama list
if ($modelList -notmatch [regex]::Escape($OllamaModel)) {
    Write-Host "Pulling Ollama model $OllamaModel. This can take a while the first time." -ForegroundColor Cyan
    ollama pull $OllamaModel
}

Write-Host "Applying database migrations..." -ForegroundColor Cyan
Push-Location $BackendDir
& $PythonExe -m alembic upgrade head
Pop-Location

if (-not (Test-HttpOk $BackendUrl)) {
    Start-NamedWindow `
        -Title "Job App Backend" `
        -WorkingDirectory $BackendDir `
        -Command "& '$PythonExe' -m uvicorn app.main:app --reload"
} else {
    Write-Host "Backend already appears to be running." -ForegroundColor Green
}

if (-not (Test-HttpOk $FrontendUrl)) {
    Start-NamedWindow `
        -Title "Job App Frontend" `
        -WorkingDirectory $FrontendDir `
        -Command "npm run dev -- --host 127.0.0.1"
} else {
    Write-Host "Frontend already appears to be running." -ForegroundColor Green
}

Write-Host "Waiting for services..." -ForegroundColor Cyan
Start-Sleep -Seconds 5
Start-Process $FrontendUrl

Write-Host ""
Write-Host "Dashboard: $FrontendUrl" -ForegroundColor Green
Write-Host "Backend API: $BackendUrl/docs" -ForegroundColor Green
Write-Host "Close the Backend/Frontend/Ollama windows when you want to stop the app."
Read-Host "Press Enter to close this launcher window"
