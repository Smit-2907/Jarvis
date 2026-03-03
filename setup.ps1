# JARVIS ONE-CLICK DEPLOYMENT SCRIPT (v4.0)
# Designed for rapid deployment on new workstations.

$ErrorActionPreference = "Stop"
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   STARK INDUSTRIES - J.A.R.V.I.S. SYSTEM SETUP     " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "!! Python not found. Please install Python 3.10+ and restart." -ForegroundColor Red
    exit
}

# 2. Check for UV (High-performance manager)
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host ">> Installing UV dependency manager..." -ForegroundColor Yellow
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
}

# 3. Initialize Environment
Write-Host ">> Synchronizing Neural Dependencies..." -ForegroundColor Yellow
uv sync

# 4. Create Directory Structure
Write-Host "-- Creating Tactical Data Folders..." -ForegroundColor Yellow
$folders = @("models", "memory", "config", "logs")
foreach ($f in $folders) {
    if (!(Test-Path $f)) { New-Item -ItemType Directory -Path $f }
}

# 5. Download Speech Model (Vosk Indian English)
$modelPath = "models/vosk-model-en-in-0.5"
$amPath = "models/vosk-model-en-in-0.5/am/final.mdl"

if (!(Test-Path $amPath)) {
    Write-Host ">> Speech Model (Indian English) not found or incomplete. Synchronizing..." -ForegroundColor Yellow
    
    # Ensure models dir exists
    if (!(Test-Path "models")) { New-Item -ItemType Directory -Path "models" }
    
    $url = "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip"
    $zipfile = "models/model.zip"
    Write-Host "<< Downloading Acoustic Weights (~40MB)..." -ForegroundColor Cyan
    $maxRetries = 3
    $retryCount = 0
    $success = $false
    
    while (-not $success -and $retryCount -lt $maxRetries) {
        try {
            Write-Host ">> Attempting download (Retry $($retryCount + 1)/$maxRetries)..." -ForegroundColor Cyan
            
            # Use curl if available for better resume/stability
            if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
                curl.exe -L -C - -o $zipfile $url
            } else {
                # Fallback to Invoke-WebRequest if curl isn't found
                if (Test-Path $zipfile) { Remove-Item $zipfile }
                Invoke-WebRequest -Uri $url -OutFile $zipfile -ErrorAction Stop
            }

            if (Test-Path $zipfile) {
                $size = (Get-Item $zipfile).Length
                if ($size -gt 10485760) {
                    $success = $true
                } else {
                    Write-Host "!! Download seems partial ($([math]::Round($size / 1048576, 2)) MB)." -ForegroundColor Yellow
                    $retryCount++
                }
            }
        } catch {
            $retryCount++
            Write-Host "!! Connection error: $($_.Exception.Message). Retrying..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }

    if (-not $success) {
        Write-Host "FATAL: Download failed after $maxRetries attempts." -ForegroundColor Red
        exit
    }
    
    Write-Host ">> Extracting Neural Layer..." -ForegroundColor Yellow
    Expand-Archive -Path $zipfile -DestinationPath "models/" -Force
    
    # Remove ZIP
    Remove-Item $zipfile
    
    if (Test-Path $amPath) {
        Write-Host "OK Speech Model Online." -ForegroundColor Green
    } else {
        Write-Host "!! EXTRACTION ERROR: Could not find acoustic files after unzip." -ForegroundColor Red
        Write-Host ">> Try manually extracting: 'models/model.zip' into 'models/' folder." -ForegroundColor White
    }
} else {
    Write-Host "OK Speech Model already configured and validated." -ForegroundColor Green
}

# 6. Download MediaPipe Hand Landmarker
$handModelPath = "models/hand_landmarker.task"
if (!(Test-Path $handModelPath)) {
    Write-Host ">> MediaPipe Hand Landmarker not found. Downloading..." -ForegroundColor Yellow
    $url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    Invoke-WebRequest -Uri $url -OutFile $handModelPath
    Write-Host "OK Hand Tracking Model Online." -ForegroundColor Green
}

# 7. Check for Ollama
Write-Host ""
Write-Host ">> CHECKING INTELLIGENCE LINK (OLLAMA)..." -ForegroundColor Cyan
if (!(Get-Process "ollama" -ErrorAction SilentlyContinue)) {
    Write-Host "!! OLLAMA is not running! JARVIS's brain requires the Ollama engine." -ForegroundColor Yellow
    Write-Host ">> Please download it from https://ollama.com and run 'ollama run mistral'" -ForegroundColor White
} else {
    Write-Host "OK Ollama Link Detected." -ForegroundColor Green
}

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "        J.A.R.V.I.S. IS READY FOR BOOTUP            " -ForegroundColor Green
Write-Host "        Run: 'uv run main.py' to initialize         " -ForegroundColor White
Write-Host "====================================================" -ForegroundColor Cyan
