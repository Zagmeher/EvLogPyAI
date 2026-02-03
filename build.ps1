# EvLogPyAI - Build Script
# Crea l'eseguibile Windows

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  EvLogPyAI - Build Eseguibile  " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verifica Python
Write-Host "[1/3] Verifica Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python non trovato!" -ForegroundColor Red
    Write-Host "Installa Python 3.10+ da https://www.python.org" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green
Write-Host ""

# Installa dipendenze
Write-Host "[2/3] Installazione dipendenze..." -ForegroundColor Yellow
pip install -r requirements.txt
pip install pyinstaller

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Errore installazione dipendenze!" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}
Write-Host "✅ Dipendenze installate" -ForegroundColor Green
Write-Host ""

# Compila eseguibile
Write-Host "[3/3] Compilazione eseguibile..." -ForegroundColor Yellow
python setup.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "  ✅ BUILD COMPLETATO!          " -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Eseguibile creato in: dist\EvLogPyAI.exe" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Errore durante la compilazione!" -ForegroundColor Red
}

Write-Host "Premi INVIO per uscire..." -ForegroundColor Gray
Read-Host
