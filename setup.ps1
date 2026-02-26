# JARVIS ONE-CLICK DEPLOYMENT SCRIPT (v4.0)
# Designed for rapid deployment on new workstations.

$ErrorActionPreference = "Stop"
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   STARK INDUSTRIES - J.A.R.V.I.S. SYSTEM SETUP     " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️ Python not found. Please install Python 3.10+ and restart." -ForegroundColor Red
    exit
}

# 2. Check for UV (High-performance manager)
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing UV dependency manager..." -ForegroundColor Yellow
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
}

# 3. Initialize Environment
Write-Host "📦 Synchronizing Neural Dependencies..." -ForegroundColor Yellow
uv sync

# 4. Create Directory Structure
Write-Host "📁 Creating Tactical Data Folders..." -ForegroundColor Yellow
$folders = @("models", "memory", "config", "logs")
foreach ($f in $folders) {
    if (!(Test-Path $f)) { New-Item -ItemType Directory -Path $f }
}

# 5. Download Speech Model (Vosk Indian English)
$modelPath = "models/vosk-model-en-in-0.5"
if (!(Test-Path $modelPath)) {
    Write-Host "🎙️ Speech Model (Indian English) not found. Downloading..." -ForegroundColor Yellow
    $url = "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip"
    $output = "models/model.zip"
    Invoke-WebRequest -Uri $url -OutFile $output
    
    Write-Host "📦 Extracting Acoustic Weights..." -ForegroundColor Yellow
    Expand-Archive -Path $output -DestinationPath "models/"
    Remove-Item $output
    Write-Host "✅ Speech Model Online." -ForegroundColor Green
} else {
    Write-Host "✅ Speech Model already configured." -ForegroundColor Green
}

# 6. Download MediaPipe Hand Landmarker
$handModelPath = "models/hand_landmarker.task"
if (!(Test-Path $handModelPath)) {
    Write-Host "👁️ MediaPipe Hand Landmarker not found. Downloading..." -ForegroundColor Yellow
    $url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    Invoke-WebRequest -Uri $url -OutFile $handModelPath
    Write-Host "✅ Hand Tracking Model Online." -ForegroundColor Green
}

# 7. Check for Ollama
Write-Host ""
Write-Host "🧠 CHECKING INTELLIGENCE LINK (OLLAMA)..." -ForegroundColor Cyan
if (!(Get-Process "ollama" -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️ OLLAMA is not running! JARVIS's brain requires the Ollama engine." -ForegroundColor Yellow
    Write-Host "👉 Please download it from https://ollama.com and run 'ollama run mistral'" -ForegroundColor White
} else {
    Write-Host "✅ Ollama Link Detected." -ForegroundColor Green
}

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "        J.A.R.V.I.S. IS READY FOR BOOTUP            " -ForegroundColor Green
Write-Host "        Run: 'uv run main.py' to initialize         " -ForegroundColor White
Write-Host "====================================================" -ForegroundColor Cyan
