# ============================================================================
# EvLogPyAI - Setup Automatico Completo
# ============================================================================
# Questo script configura automaticamente tutto il necessario:
# - Python 3.12 (se non presente)
# - Ambiente virtuale con dipendenze
# - Docker containers (Ollama + N8N)
# - Modello AI (llama2)
# ============================================================================

param(
    [switch]$SkipPython,
    [switch]$SkipDocker,
    [switch]$SkipModel
)

# === CONFIGURAZIONE ===
$PYTHON_VERSION = "3.12.8"
$PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-amd64.exe"
$PYTHON_INSTALLER = "$env:TEMP\python-$PYTHON_VERSION-installer.exe"
$VENV_DIR = ".venv"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# === FUNZIONI HELPER ===
function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host ""
    Write-Host "[$Step] $Message" -ForegroundColor Yellow
    Write-Host ("-" * 60) -ForegroundColor DarkGray
}

function Write-OK {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Fail {
    param([string]$Message)
    Write-Host "  [X] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  [i] $Message" -ForegroundColor Cyan
}

# === INIZIO SETUP ===
Clear-Host
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "       EvLogPyAI - Setup Automatico Completo" -ForegroundColor Cyan
Write-Host "       Windows Event Log AI Analyzer" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Questo script configurera automaticamente:" -ForegroundColor White
Write-Host "  1. Python 3.12 (se non presente)" -ForegroundColor White
Write-Host "  2. Ambiente virtuale + dipendenze" -ForegroundColor White
Write-Host "  3. Docker containers (Ollama + N8N)" -ForegroundColor White
Write-Host "  4. Modello AI (llama2)" -ForegroundColor White
Write-Host ""

# Imposta directory di lavoro
Set-Location $SCRIPT_DIR
Write-Info "Directory di lavoro: $SCRIPT_DIR"

# ================================================================
# FASE 1: VERIFICA / INSTALLAZIONE PYTHON
# ================================================================
Write-Step "1/5" "Verifica Python..."

$pythonCmd = $null
$pythonFound = $false

if (-not $SkipPython) {
    # Cerca Python nel sistema
    $pythonPaths = @(
        "python",
        "python3",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe",
        "$env:ProgramFiles\Python310\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python314\python.exe"
    )

    foreach ($path in $pythonPaths) {
        try {
            $version = & $path --version 2>&1
            if ($version -match "Python 3\.(\d+)") {
                $minorVer = [int]$Matches[1]
                if ($minorVer -ge 10) {
                    $pythonCmd = $path
                    $pythonFound = $true
                    Write-OK "Python trovato: $version ($path)"
                    break
                }
            }
        } catch {
            continue
        }
    }

    if (-not $pythonFound) {
        Write-Info "Python 3.10+ non trovato. Installazione automatica..."
        Write-Info "Download Python $PYTHON_VERSION..."
        
        try {
            # Download installer
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $PYTHON_INSTALLER_URL -OutFile $PYTHON_INSTALLER -UseBasicParsing
            Write-OK "Download completato"
            
            # Installazione silente
            Write-Info "Installazione Python $PYTHON_VERSION (potrebbe richiedere un minuto)..."
            $installArgs = "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_tcltk=1"
            $process = Start-Process -FilePath $PYTHON_INSTALLER -ArgumentList $installArgs -Wait -PassThru
            
            if ($process.ExitCode -eq 0) {
                Write-OK "Python $PYTHON_VERSION installato con successo"
                
                # Aggiorna PATH per la sessione corrente
                $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")
                
                # Trova il nuovo Python
                $pythonCmd = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
                if (Test-Path $pythonCmd) {
                    $pythonFound = $true
                } else {
                    $pythonCmd = "python"
                    $pythonFound = $true
                }
            } else {
                Write-Fail "Installazione Python fallita (Exit code: $($process.ExitCode))"
                Write-Info "Installa manualmente Python 3.10+ da https://www.python.org/downloads/"
                Read-Host "Premi INVIO per uscire"
                exit 1
            }
        } catch {
            Write-Fail "Errore durante il download/installazione: $_"
            Write-Info "Installa manualmente Python 3.10+ da https://www.python.org/downloads/"
            Read-Host "Premi INVIO per uscire"
            exit 1
        } finally {
            # Pulizia installer
            if (Test-Path $PYTHON_INSTALLER) {
                Remove-Item $PYTHON_INSTALLER -Force -ErrorAction SilentlyContinue
            }
        }
    }
} else {
    Write-Info "Skip Python (--SkipPython)"
    $pythonCmd = "python"
    $pythonFound = $true
}

# ================================================================
# FASE 2: CREAZIONE AMBIENTE VIRTUALE
# ================================================================
Write-Step "2/5" "Configurazione ambiente virtuale..."

$venvPython = "$SCRIPT_DIR\$VENV_DIR\Scripts\python.exe"
$venvPip = "$SCRIPT_DIR\$VENV_DIR\Scripts\pip.exe"
$venvActivate = "$SCRIPT_DIR\$VENV_DIR\Scripts\Activate.ps1"

if (Test-Path $venvPython) {
    Write-OK "Ambiente virtuale gia esistente: $VENV_DIR"
} else {
    Write-Info "Creazione ambiente virtuale..."
    & $pythonCmd -m venv $VENV_DIR
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path $venvPython)) {
        Write-OK "Ambiente virtuale creato: $VENV_DIR"
    } else {
        Write-Fail "Errore nella creazione dell'ambiente virtuale"
        Read-Host "Premi INVIO per uscire"
        exit 1
    }
}

# Aggiorna pip
Write-Info "Aggiornamento pip..."
& $venvPython -m pip install --upgrade pip --quiet 2>$null
Write-OK "pip aggiornato"

# Installa dipendenze
Write-Info "Installazione dipendenze Python..."
& $venvPip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-OK "Tutte le dipendenze installate"
} else {
    Write-Fail "Errore durante l'installazione delle dipendenze"
    Write-Info "Prova manualmente: $venvPip install -r requirements.txt"
}

# Verifica dipendenze critiche
Write-Info "Verifica dipendenze critiche..."
$checkImports = @"
import sys
try:
    import customtkinter; print('  [OK] customtkinter', customtkinter.__version__)
except: print('  [X] customtkinter NON trovato')
try:
    import win32evtlog; print('  [OK] pywin32 (win32evtlog)')
except: print('  [X] pywin32 NON trovato')
try:
    import requests; print('  [OK] requests', requests.__version__)
except: print('  [X] requests NON trovato')
"@
& $venvPython -c $checkImports

# ================================================================
# FASE 3: VERIFICA / AVVIO DOCKER
# ================================================================
Write-Step "3/5" "Verifica Docker Desktop..."

if (-not $SkipDocker) {
    $dockerRunning = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Docker Desktop non e in esecuzione!"
        Write-Info ""
        Write-Info "Opzioni:"
        Write-Info "  1. Avvia Docker Desktop manualmente"
        Write-Info "  2. Scaricalo da: https://www.docker.com/products/docker-desktop/"
        Write-Info ""
        
        $response = Read-Host "Docker Desktop e installato? Vuoi che provi ad avviarlo? (S/N)"
        if ($response -eq "S" -or $response -eq "s") {
            Write-Info "Tentativo di avvio Docker Desktop..."
            Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
            
            Write-Info "Attesa avvio Docker (max 120 secondi)..."
            $maxWait = 24
            $waited = 0
            while ($waited -lt $maxWait) {
                Start-Sleep -Seconds 5
                $waited++
                $dockerCheck = docker info 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-OK "Docker Desktop avviato!"
                    break
                }
                Write-Host "  Attesa... ($($waited * 5)s)" -ForegroundColor Gray
            }
            
            if ($waited -ge $maxWait) {
                Write-Fail "Timeout avvio Docker. Avvialo manualmente e riesegui lo script."
                Read-Host "Premi INVIO per uscire"
                exit 1
            }
        } else {
            Write-Info "Avvia Docker Desktop e riesegui: .\setup-evlogpyai.ps1 -SkipPython"
            Read-Host "Premi INVIO per uscire"
            exit 1
        }
    } else {
        Write-OK "Docker Desktop attivo"
    }

    # Avvio containers
    Write-Step "4/5" "Avvio containers Docker (Ollama + N8N)..."
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-OK "Containers avviati"
    } else {
        Write-Fail "Errore durante l'avvio dei containers"
        Write-Info "Prova manualmente: docker-compose up -d"
    }

    # Attendi che Ollama sia pronto
    Write-Info "Attesa avvio servizi..."
    Start-Sleep -Seconds 10

    $maxAttempts = 12
    $attempt = 0
    $ollamaReady = $false

    while ($attempt -lt $maxAttempts -and -not $ollamaReady) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                $ollamaReady = $true
            }
        } catch {
            $attempt++
            Write-Host "  Tentativo $attempt/$maxAttempts..." -ForegroundColor Gray
            Start-Sleep -Seconds 5
        }
    }

    if ($ollamaReady) {
        Write-OK "Ollama pronto"
    } else {
        Write-Info "Ollama potrebbe non essere ancora pronto (continuo comunque)"
    }
} else {
    Write-Info "Skip Docker (--SkipDocker)"
}

# ================================================================
# FASE 4: DOWNLOAD MODELLO AI
# ================================================================
Write-Step "5/5" "Verifica modello AI..."

if (-not $SkipDocker -and -not $SkipModel) {
    $models = docker exec evlogpyai-ollama ollama list 2>&1
    if ($models -match "llama2") {
        Write-OK "Modello llama2 gia installato"
    } else {
        Write-Info "Download modello llama2 (~4GB, potrebbe richiedere 5-15 minuti)..."
        docker exec evlogpyai-ollama ollama pull llama2
        if ($LASTEXITCODE -eq 0) {
            Write-OK "Modello llama2 installato con successo"
        } else {
            Write-Fail "Errore durante il download del modello"
            Write-Info "Prova manualmente: docker exec evlogpyai-ollama ollama pull llama2"
        }
    }
} else {
    Write-Info "Skip download modello"
}

# ================================================================
# FASE FINALE: CREAZIONE LAUNCHER
# ================================================================

# Crea file batch per avvio rapido
$launcherContent = @"
@echo off
title EvLogPyAI - Windows Event Log AI Analyzer
echo.
echo  EvLogPyAI - Avvio Applicazione
echo  ================================
echo.

REM Verifica containers Docker
docker ps --filter "name=evlogpyai" --format "{{.Names}}" 2>nul | findstr "evlogpyai" >nul
if errorlevel 1 (
    echo  [!] I containers Docker non sono attivi.
    echo  [i] Avvio containers...
    docker-compose up -d
    timeout /t 15 /nobreak >nul
)

REM Attiva ambiente virtuale e avvia
cd /d "%~dp0"
call "$VENV_DIR\Scripts\activate.bat"
echo  [OK] Ambiente virtuale attivato
echo  [i]  Avvio EvLogPyAI...
echo.
python trigger.py
"@

$launcherPath = "$SCRIPT_DIR\EvLogPyAI.bat"
Set-Content -Path $launcherPath -Value $launcherContent -Encoding ASCII
Write-OK "Launcher creato: EvLogPyAI.bat"

# ================================================================
# RIEPILOGO FINALE
# ================================================================
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "       SETUP COMPLETATO CON SUCCESSO!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Riepilogo configurazione:" -ForegroundColor Cyan
Write-Host "  -------------------------" -ForegroundColor Cyan

if ($pythonFound) {
    Write-Host "  Python:     $($pythonCmd)" -ForegroundColor White
}
Write-Host "  Venv:       $SCRIPT_DIR\$VENV_DIR" -ForegroundColor White
Write-Host "  N8N:        http://localhost:5678" -ForegroundColor White
Write-Host "  Ollama:     http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "  ================================" -ForegroundColor Yellow
Write-Host "  COME USARE EvLogPyAI:" -ForegroundColor Yellow
Write-Host "  ================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "  METODO 1 - Doppio click:" -ForegroundColor White
Write-Host "    Apri EvLogPyAI.bat" -ForegroundColor Green
Write-Host ""
Write-Host "  METODO 2 - Terminale:" -ForegroundColor White
Write-Host "    .\$VENV_DIR\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "    python trigger.py" -ForegroundColor Green
Write-Host ""
Write-Host "  NOTA: Al primo utilizzo, importa il workflow N8N:" -ForegroundColor Yellow
Write-Host "    1. Apri http://localhost:5678" -ForegroundColor White
Write-Host "    2. Importa: n8n\workflows\evlogpyai-workflow.json" -ForegroundColor White
Write-Host "    3. Configura credenziali Ollama: http://ollama:11434" -ForegroundColor White
Write-Host "    4. Attiva il workflow (toggle verde)" -ForegroundColor White
Write-Host ""
Write-Host "  Per fermare i containers:" -ForegroundColor Yellow
Write-Host "    .\stop.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green

Read-Host "Premi INVIO per chiudere"
