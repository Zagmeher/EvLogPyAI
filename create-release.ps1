# EvLogPyAI - Script Creazione Pacchetto Release
# Crea il file ZIP pronto per la distribuzione

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  EvLogPyAI - Release Package   " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verifica eseguibile
Write-Host "[1/4] Verifica eseguibile..." -ForegroundColor Yellow
if (-not (Test-Path "dist\EvLogPyAI.exe")) {
    Write-Host "❌ EvLogPyAI.exe non trovato!" -ForegroundColor Red
    Write-Host "Esegui prima: .\build.ps1" -ForegroundColor Yellow
    Read-Host "Premi INVIO per uscire"
    exit 1
}
Write-Host "✅ Eseguibile trovato" -ForegroundColor Green
Write-Host ""

# Pulisci cartelle precedenti
Write-Host "[2/4] Pulizia cartelle precedenti..." -ForegroundColor Yellow
if (Test-Path "release-package") {
    Remove-Item "release-package" -Recurse -Force
}
if (Test-Path "EvLogPyAI-v1.0.0.zip") {
    Remove-Item "EvLogPyAI-v1.0.0.zip" -Force
}
Write-Host "✅ Pulizia completata" -ForegroundColor Green
Write-Host ""

# Crea struttura pacchetto
Write-Host "[3/4] Creazione pacchetto release..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "release-package" -Force | Out-Null

# Copia file necessari
Write-Host "  Copia eseguibile..." -ForegroundColor Gray
Copy-Item "dist\EvLogPyAI.exe" -Destination "release-package\"

Write-Host "  Copia configurazioni Docker..." -ForegroundColor Gray
Copy-Item "docker-compose.yml" -Destination "release-package\"

Write-Host "  Copia script PowerShell..." -ForegroundColor Gray
Copy-Item "start.ps1" -Destination "release-package\"
Copy-Item "stop.ps1" -Destination "release-package\"

Write-Host "  Copia documentazione..." -ForegroundColor Gray
Copy-Item "README.md" -Destination "release-package\"
Copy-Item "QUICKSTART.md" -Destination "release-package\"
Copy-Item "LICENSE" -Destination "release-package\"

Write-Host "  Copia workflow N8N..." -ForegroundColor Gray
Copy-Item "n8n" -Destination "release-package\" -Recurse

Write-Host "✅ File copiati" -ForegroundColor Green
Write-Host ""

# Crea archivio ZIP
Write-Host "[4/4] Creazione archivio ZIP..." -ForegroundColor Yellow
Compress-Archive -Path "release-package\*" -DestinationPath "EvLogPyAI-v1.0.0.zip" -Force

if (Test-Path "EvLogPyAI-v1.0.0.zip") {
    $zipSize = (Get-Item "EvLogPyAI-v1.0.0.zip").Length / 1MB
    Write-Host "✅ Archivio creato: EvLogPyAI-v1.0.0.zip ($([math]::Round($zipSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "❌ Errore durante la creazione dell'archivio!" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}
Write-Host ""

# Riepilogo contenuto
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Contenuto Pacchetto:          " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Get-ChildItem "release-package" -Recurse -File | ForEach-Object {
    $relativePath = $_.FullName.Replace((Get-Location).Path + "\release-package\", "")
    Write-Host "  ✓ $relativePath" -ForegroundColor White
}
Write-Host ""

# Calcola hash
Write-Host "Calcolo hash SHA256..." -ForegroundColor Yellow
$hash = (Get-FileHash "EvLogPyAI-v1.0.0.zip" -Algorithm SHA256).Hash
Write-Host "SHA256: $hash" -ForegroundColor Gray
Write-Host ""

Write-Host "================================" -ForegroundColor Green
Write-Host "  ✅ PACCHETTO PRONTO!          " -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "File: EvLogPyAI-v1.0.0.zip" -ForegroundColor White
Write-Host "Dimensione: $([math]::Round($zipSize, 2)) MB" -ForegroundColor White
Write-Host ""
Write-Host "Prossimi passi:" -ForegroundColor Yellow
Write-Host "  1. Testa il pacchetto estraendolo in una nuova cartella" -ForegroundColor White
Write-Host "  2. Verifica che tutto funzioni con RELEASE_CHECKLIST.md" -ForegroundColor White
Write-Host "  3. Carica su GitHub Releases" -ForegroundColor White
Write-Host ""
Write-Host "Vuoi aprire la cartella? (S/N): " -ForegroundColor Cyan -NoNewline
$response = Read-Host

if ($response -eq "S" -or $response -eq "s") {
    Start-Process "explorer.exe" -ArgumentList (Get-Location).Path
}

Write-Host ""
Write-Host "Fatto! 🎉" -ForegroundColor Green
