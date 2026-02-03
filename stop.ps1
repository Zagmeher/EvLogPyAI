# EvLogPyAI - Script di Arresto
# Ferma tutti i container Docker

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  EvLogPyAI - Arresto Servizi   " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Arresto container..." -ForegroundColor Yellow
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Container arrestati con successo" -ForegroundColor Green
} else {
    Write-Host "❌ Errore durante l'arresto" -ForegroundColor Red
}

Write-Host ""
Write-Host "Premi INVIO per uscire..." -ForegroundColor Gray
Read-Host
