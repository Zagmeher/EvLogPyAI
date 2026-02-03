# 📦 Checklist Creazione Pacchetto Release

## File da Includere nella Release ZIP

```
EvLogPyAI-v1.0.0/
├── EvLogPyAI.exe                    ✅ Eseguibile compilato
├── docker-compose.yml               ✅ Config container
├── start.ps1                        ✅ Script avvio
├── stop.ps1                         ✅ Script arresto
├── README.md                        ✅ Documentazione principale
├── QUICKSTART.md                    ✅ Guida rapida 3 passi
├── LICENSE                          ✅ Licenza MIT
└── n8n/
    └── workflows/
        ├── evlogpyai-workflow.json  ✅ Workflow N8N
        └── README.md                ✅ Istruzioni import workflow
```

## Comandi per Creare il Pacchetto

```powershell
# 1. Compila l'eseguibile
.\build.ps1

# 2. Crea cartella release
New-Item -ItemType Directory -Path "release-package" -Force

# 3. Copia file necessari
Copy-Item "dist\EvLogPyAI.exe" -Destination "release-package\"
Copy-Item "docker-compose.yml" -Destination "release-package\"
Copy-Item "start.ps1" -Destination "release-package\"
Copy-Item "stop.ps1" -Destination "release-package\"
Copy-Item "README.md" -Destination "release-package\"
Copy-Item "QUICKSTART.md" -Destination "release-package\"
Copy-Item "LICENSE" -Destination "release-package\"
Copy-Item "n8n" -Destination "release-package\" -Recurse

# 4. Comprimi per distribuzione
Compress-Archive -Path "release-package\*" -DestinationPath "EvLogPyAI-v1.0.0.zip" -Force

# 5. Verifica contenuto
Expand-Archive -Path "EvLogPyAI-v1.0.0.zip" -DestinationPath "test-extract" -Force
Get-ChildItem "test-extract" -Recurse
```

## Test Pre-Release

### Test 1: Estrazione Pacchetto
- [ ] ZIP si estrae correttamente
- [ ] Tutti i file presenti
- [ ] Nessun file mancante

### Test 2: Avvio Docker
```powershell
cd test-extract
.\start.ps1
```
- [ ] Docker si avvia senza errori
- [ ] Container Ollama healthy
- [ ] Container N8N healthy
- [ ] Modello llama2 scaricato
- [ ] N8N si apre nel browser

### Test 3: Import Workflow
- [ ] Workflow JSON si importa correttamente
- [ ] Credenziali Ollama configurabili
- [ ] Workflow si attiva (toggle verde)
- [ ] Path webhook: `/webhook/evlogpyai`

### Test 4: Eseguibile
```powershell
.\EvLogPyAI.exe
```
- [ ] Applicazione si avvia
- [ ] GUI si visualizza correttamente
- [ ] Form funziona
- [ ] "Estrai Log" funziona
- [ ] File salvato su Desktop
- [ ] Callback ricevuto da N8N
- [ ] Browser si apre con report HTML

### Test 5: Funzionalità Completa
- [ ] Estrazione log Application
- [ ] Estrazione log System
- [ ] Estrazione log Security (come Admin)
- [ ] AI genera risposta sensata
- [ ] HTML formattato correttamente
- [ ] Nessun crash o errore

### Test 6: Stop
```powershell
.\stop.ps1
```
- [ ] Container si fermano correttamente
- [ ] Nessun errore

## Configurazioni Verificate

### docker-compose.yml
- [ ] Nessun `version:` (deprecato)
- [ ] Healthcheck Ollama funzionante
- [ ] Healthcheck N8N funzionante
- [ ] Volumi persistenti configurati
- [ ] Network configurato

### Workflow N8N
- [ ] Webhook path: `evlogpyai`
- [ ] Edit Fields formatta correttamente
- [ ] AI Agent usa Ollama
- [ ] HTTP Request usa: `$('Webhook').item.json.callback_url`
- [ ] Modello: llama2

### trigger.py
- [ ] CALLBACK_HOST: `127.0.0.1`
- [ ] CALLBACK_URL_FOR_N8N: `host.docker.internal`
- [ ] N8N_WEBHOOK_URL: `/webhook/evlogpyai` (produzione)
- [ ] Server callback bind: `0.0.0.0`
- [ ] Timeout: 300s

## Documentazione Verificata

### README.md
- [ ] Ordine esecuzione chiaro all'inizio
- [ ] Link a QUICKSTART.md
- [ ] Link a n8n/workflows/README.md
- [ ] Username GitHub corretto
- [ ] Email corretta
- [ ] Badge versione aggiornato

### QUICKSTART.md
- [ ] 3 passi chiari
- [ ] Screenshots presenti (opzionale)
- [ ] Troubleshooting completo
- [ ] Checklist finale

### n8n/workflows/README.md
- [ ] Istruzioni import chiare
- [ ] URL Ollama corretto
- [ ] Path webhook corretto
- [ ] Configurazione HTTP Request corretta

## GitHub Release

### Repository
- [ ] README.md aggiornato
- [ ] Tag versione: `v1.0.0`
- [ ] Branch: `main`
- [ ] .gitignore configurato

### Release Notes
```markdown
## 🎉 EvLogPyAI v1.0.0 - Prima Release

### Caratteristiche
- ✅ Estrazione automatica log Windows
- ✅ Analisi AI con Ollama (llama2)
- ✅ Report HTML formattati
- ✅ Workflow N8N integrato
- ✅ Callback asincrono

### Download
📥 **[EvLogPyAI-v1.0.0.zip](link-al-file)**

### Requisiti
- Windows 10/11
- Docker Desktop
- 8GB RAM

### Installazione
Vedi [QUICKSTART.md](QUICKSTART.md) per istruzioni dettagliate.

### Known Issues
Nessuno

### Changelog
- Prima release pubblica
```

### File Release
- [ ] `EvLogPyAI-v1.0.0.zip` caricato
- [ ] Dimensione file ragionevole (<50MB eseguibile)
- [ ] Hash SHA256 fornito

## Post-Release

- [ ] Release pubblicata su GitHub
- [ ] README.md include link release
- [ ] Annuncio su community (opzionale)
- [ ] Documentazione aggiornata

## Comandi Rapidi Cleanup

```powershell
# Rimuovi file temporanei
Remove-Item "release-package" -Recurse -Force
Remove-Item "test-extract" -Recurse -Force
Remove-Item "build" -Recurse -Force
Remove-Item "dist" -Recurse -Force
Remove-Item "*.spec" -Force

# Pulisci Docker
docker-compose down
docker system prune -af --volumes
```

---

**Firma**: _______________ Data: _______________
