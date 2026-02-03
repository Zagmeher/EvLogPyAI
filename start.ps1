# EvLogPyAI - Script di Avvio Rapido
# Esegui questo script per avviare tutto automaticamente

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  EvLogPyAI - Avvio Automatico  " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verifica Docker
Write-Host "[1/5] Verifica Docker Desktop..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker Desktop non è in esecuzione!" -ForegroundColor Red
    Write-Host "Avvia Docker Desktop e riprova." -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}
Write-Host "✅ Docker Desktop attivo" -ForegroundColor Green
Write-Host ""

# 2. Avvia Container
Write-Host "[2/5] Avvio container Ollama e N8N..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Errore durante l'avvio dei container!" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}
Write-Host "✅ Container avviati" -ForegroundColor Green
Write-Host ""

# 3. Attendi che i servizi siano pronti
Write-Host "[3/5] Attesa avvio servizi..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$maxAttempts = 12
$attempt = 0
$ollamaReady = $false

while ($attempt -lt $maxAttempts -and -not $ollamaReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
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
    Write-Host "✅ Ollama pronto" -ForegroundColor Green
} else {
    Write-Host "⚠️  Ollama potrebbe non essere pronto (continuo comunque)" -ForegroundColor Yellow
}
Write-Host ""

# 4. Verifica modello Ollama
Write-Host "[4/5] Verifica modello AI..." -ForegroundColor Yellow
$models = docker exec evlogpyai-ollama ollama list 2>&1
if ($models -match "llama2" -or $models -match "phi") {
    Write-Host "✅ Modello AI già installato" -ForegroundColor Green
} else {
    Write-Host "⚠️  Nessun modello trovato. Download llama2..." -ForegroundColor Yellow
    Write-Host "   (Questo può richiedere 5-15 minuti)" -ForegroundColor Gray
    docker exec -it evlogpyai-ollama ollama pull llama2
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Modello llama2 installato" -ForegroundColor Green
    } else {
        Write-Host "❌ Errore durante il download del modello" -ForegroundColor Red
    }
}
Write-Host ""

# 5. Informazioni finali
Write-Host "[5/5] Configurazione completata!" -ForegroundColor Green
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Servizi Disponibili:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  N8N:    http://localhost:5678" -ForegroundColor White
Write-Host "  Ollama: http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "Prossimi passi:" -ForegroundColor Yellow
Write-Host "  1. Vai su http://localhost:5678" -ForegroundColor White
Write-Host "  2. Importa il workflow da: n8n/workflows/evlogpyai-workflow.json" -ForegroundColor White
Write-Host "  3. Attiva il workflow" -ForegroundColor White
Write-Host "  4. Avvia EvLogPyAI.exe" -ForegroundColor White
Write-Host ""
Write-Host "Premi INVIO per aprire N8N nel browser..." -ForegroundColor Cyan
Read-Host

Start-Process "http://localhost:5678"