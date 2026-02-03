# 📖 Guida Completa all'Installazione di EvLogPyAI

Questa guida ti accompagnerà passo-passo nell'installazione e configurazione di EvLogPyAI.

---

## 📋 Indice

1. [Requisiti di Sistema](#requisiti-di-sistema)
2. [Installazione Docker Desktop](#installazione-docker-desktop)
3. [Download e Setup EvLogPyAI](#download-e-setup-evlogpyai)
4. [Configurazione Ollama](#configurazione-ollama)
5. [Configurazione N8N](#configurazione-n8n)
6. [Primo Utilizzo](#primo-utilizzo)
7. [Risoluzione Problemi](#risoluzione-problemi)

---

## 1️⃣ Requisiti di Sistema

### Hardware Minimo

- **CPU**: Intel Core i5 o AMD Ryzen 5 (4 core)
- **RAM**: 8GB (4GB per Ollama + 2GB per N8N + 2GB per Windows)
- **Disco**: 10GB di spazio libero
- **Rete**: Connessione Internet per download iniziale

### Software Richiesto

- **Sistema Operativo**: Windows 10 (build 19041+) o Windows 11
- **Privilegi**: Account con diritti di Amministratore
- **Browser**: Chrome, Firefox, Edge o Safari (qualsiasi browser moderno)

### Verifica Requisiti

Apri PowerShell e verifica:

```powershell
# Verifica versione Windows
winver

# Verifica RAM disponibile
systeminfo | findstr /C:"Memoria fisica totale"

# Verifica spazio disco
Get-PSDrive C | Select-Object Used,Free
```

---

## 2️⃣ Installazione Docker Desktop

### Download

1. Vai su https://www.docker.com/products/docker-desktop/
2. Clicca su **"Download for Windows"**
3. Salva il file `Docker Desktop Installer.exe`

### Installazione

1. **Esegui l'installer** come Amministratore
   - Tasto destro → "Esegui come amministratore"

2. **Configura le opzioni**:
   - ✅ Abilita "Use WSL 2 instead of Hyper-V" (consigliato)
   - ✅ Abilita "Add shortcut to desktop"

3. **Installa** e attendi il completamento (~5 minuti)

4. **Riavvia il PC** quando richiesto

### Configurazione Post-Installazione

1. **Avvia Docker Desktop**
   - Doppio click sull'icona sul desktop
   - Attendi che l'icona della tray diventi verde

2. **Alloca Risorse** (Importante!)
   - Clicca sull'icona Docker nella system tray
   - Settings → Resources → Advanced
   - **Memory**: 6 GB (minimo 4 GB)
   - **CPUs**: 4 (se disponibili)
   - **Apply & Restart**

3. **Verifica Installazione**

```powershell
# Verifica versione Docker
docker --version
# Output atteso: Docker version 24.x.x

# Verifica Docker Compose
docker-compose --version
# Output atteso: Docker Compose version v2.x.x

# Test funzionamento
docker run hello-world
# Output atteso: "Hello from Docker!"
```

---

## 3️⃣ Download e Setup EvLogPyAI

### Opzione A: Download Release (Consigliato per Utenti)

1. **Vai alla pagina Releases**
   - https://github.com/tuousername/EvLogPyAI/releases

2. **Scarica l'ultima versione**
   - Download: `EvLogPyAI-v1.0.0.zip`

3. **Estrai l'archivio**
   - Tasto destro → "Estrai tutto..."
   - Scegli una cartella (es. `C:\EvLogPyAI`)

4. **Verifica contenuto**
   ```
   C:\EvLogPyAI\
   ├── EvLogPyAI.exe
   ├── docker-compose.yml
   ├── README.md
   └── n8n\
       └── workflows\
           └── evlogpyai-workflow.json
   ```

### Opzione B: Clone Repository (Per Sviluppatori)

```powershell
# Installa Git se non presente
winget install --id Git.Git -e --source winget

# Clona il repository
git clone https://github.com/tuousername/EvLogPyAI.git
cd EvLogPyAI

# Installa Python 3.10+ se vuoi eseguire da sorgente
# Download da: https://www.python.org/downloads/

# Installa dipendenze Python
pip install -r requirements.txt

# (Opzionale) Crea eseguibile
pip install pyinstaller
python setup.py
```

---

## 4️⃣ Configurazione Ollama

### Avvio Container Docker

Apri PowerShell nella cartella di EvLogPyAI:

```powershell
# Avvia i container
docker-compose up -d

# Verifica che siano in esecuzione
docker ps

# Output atteso:
# CONTAINER ID   IMAGE                 STATUS        PORTS                    NAMES
# xxxxx          ollama/ollama:latest  Up 1 minute   0.0.0.0:11434->11434/tcp evlogpyai-ollama
# xxxxx          n8nio/n8n:latest      Up 1 minute   0.0.0.0:5678->5678/tcp   evlogpyai-n8n
```

### Download Modello AI

Il download del modello richiede **circa 4 GB** e può impiegare 5-15 minuti.

```powershell
# Download del modello Llama2 (consigliato)
docker exec -it evlogpyai-ollama ollama pull llama2

# Verifica installazione
docker exec -it evlogpyai-ollama ollama list

# Output atteso:
# NAME           ID              SIZE
# llama2:latest  xxxxxxxxxxxxx   3.8 GB
```

### Modelli Alternativi

**Più Veloce** (per PC meno potenti):
```powershell
docker exec -it evlogpyai-ollama ollama pull phi
```

**Migliore Qualità** (richiede 16GB RAM):
```powershell
docker exec -it evlogpyai-ollama ollama pull llama2:13b
```

### Test Ollama

```powershell
# Test manuale del modello
docker exec -it evlogpyai-ollama ollama run llama2 "Ciao, sei funzionante?"

# Output atteso: Risposta in italiano dal modello
```

---

## 5️⃣ Configurazione N8N

### Accesso Iniziale

1. **Apri il browser** e vai su: http://localhost:5678

2. **Setup Account** (prima volta):
   - Email: tuaemail@example.com
   - Password: (scegli una password sicura)
   - Clicca "Setup"

### Importazione Workflow

1. **Clicca su "Workflows"** nel menu laterale

2. **Importa Workflow**:
   - Menu (≡) → "Import from File"
   - Seleziona: `n8n/workflows/evlogpyai-workflow.json`
   - Clicca "Import"

3. **Verifica Nodi**:
   - ✅ Webhook
   - ✅ Edit Fields (Set)
   - ✅ AI Agent
   - ✅ HTTP Request

### Configurazione AI Agent

1. **Clicca sul nodo "AI Agent"**

2. **Configura Ollama**:
   - Chat Model: "Ollama Chat Model"
   - Clicca su "Create New Credential"
   - Base URL: `http://ollama:11434`
   - Model Name: `llama2`
   - Salva

3. **Configura Memory**:
   - Memory Type: "Simple Memory"
   - Session ID: `={{ $json.sessionId }}`

### Configurazione HTTP Request

1. **Clicca sul nodo "HTTP Request"**

2. **Verifica Parametri**:
   - Method: `POST`
   - URL: `={{ $('Webhook').item.json.callback_url }}`
   - Body Content Type: `JSON`
   - Body Parameters:
     - Name: `output`
     - Value: `={{ $json.output }}`

### Attivazione Workflow

**IMPORTANTE**: Scegli la modalità corretta:

#### Modalità Test (Per Testing)
- In alto a destra: **NON** attivare il toggle
- Workflow path: `/webhook-test/evlogpyai`
- Devi cliccare "Execute workflow" **PRIMA** di ogni test

#### Modalità Produzione (Automatico)
1. **Cambia URL in trigger.py** (riga 84):
   ```python
   N8N_WEBHOOK_URL = "http://localhost:5678/webhook/evlogpyai"
   ```

2. **Attiva Workflow**:
   - Toggle in alto a destra → ON (verde)
   - Workflow path: `/webhook/evlogpyai`
   - Funziona sempre automaticamente

---

## 6️⃣ Primo Utilizzo

### Test Completo End-to-End

1. **Avvia Docker**
   ```powershell
   docker-compose up -d
   ```

2. **Verifica servizi attivi**
   - Ollama: http://localhost:11434
   - N8N: http://localhost:5678

3. **Avvia EvLogPyAI**
   - Doppio click su `EvLogPyAI.exe`
   - Oppure: `python trigger.py`

4. **Compila il Form**:
   - **Titolo**: "Test Errore Applicazione"
   - **Categoria**: Applicazione
   - **Righe**: 20
   - **Descrizione**: "Test di funzionamento del sistema"

5. **Modalità Test**:
   - Vai su N8N
   - Clicca "Execute workflow"
   - Torna su EvLogPyAI
   - Clicca "📥 Estrai Log"

6. **Attendi**:
   - Console mostra: "Server callback avviato..."
   - N8N elabora i dati
   - Dopo 2-5 minuti, il browser si apre con il report

### Verifica Successo

✅ **File salvato sul Desktop**: `EvLog_Applicazione_Test_[timestamp].txt`  
✅ **Console mostra**: "📥 RISPOSTA RICEVUTA DA N8N"  
✅ **Browser aperto**: Report HTML con analisi AI  

---

## 7️⃣ Risoluzione Problemi

### Problema: Docker non si avvia

**Errore**: "Docker Desktop failed to start"

**Soluzione**:
```powershell
# Abilita WSL 2
wsl --install
wsl --set-default-version 2

# Riavvia PC
shutdown /r /t 0
```

### Problema: ECONNREFUSED dal workflow N8N

**Errore**: "connect ECONNREFUSED 127.0.0.1:5050"

**Cause**:
1. EvLogPyAI non è in esecuzione
2. Non hai cliccato "Estrai Log" (server callback non avviato)
3. URL errato in HTTP Request

**Soluzione**:
1. Verifica che EvLogPyAI sia aperto
2. Clicca "Estrai Log" PRIMA di eseguire il workflow N8N
3. Controlla che l'URL sia: `={{ $('Webhook').item.json.callback_url }}`

### Problema: Ollama non risponde

**Errore**: "Timeout connessione Ollama"

**Soluzione**:
```powershell
# Riavvia container Ollama
docker restart evlogpyai-ollama

# Verifica log
docker logs evlogpyai-ollama

# Verifica che il modello sia scaricato
docker exec -it evlogpyai-ollama ollama list
```

### Problema: "Nessun log trovato"

**Errore**: Estrazione restituisce 0 log

**Soluzione**:
- Esegui EvLogPyAI come **Amministratore**
- Tasto destro → "Esegui come amministratore"
- I log di Security/System richiedono privilegi elevati

### Problema: Browser non si apre

**Errore**: "Risposta ricevuta ma browser non si apre"

**Soluzione**:
- Controlla il file temporaneo in: `C:\Users\<utente>\AppData\Local\Temp\`
- Cerca file `.html` recenti
- Apri manualmente nel browser

### Problema: RAM insufficiente

**Sintomi**: PC lento, Docker crash

**Soluzione**:
```powershell
# Usa modello più leggero
docker exec -it evlogpyai-ollama ollama pull phi

# Riduci RAM allocata in Docker Desktop
# Settings → Resources → Memory: 4 GB
```

---

## 🆘 Supporto

Se incontri problemi non elencati qui:

1. **Verifica i log**:
   ```powershell
   # Log Docker
   docker-compose logs -f
   
   # Log N8N
   docker logs evlogpyai-n8n
   
   # Log Ollama
   docker logs evlogpyai-ollama
   ```

2. **Apri un Issue** su GitHub con:
   - Sistema operativo e versione
   - Messaggi di errore completi
   - Log dei container
   - Passi per riprodurre il problema

3. **Contatta**: tuaemail@example.com

---

**Buon utilizzo di EvLogPyAI! 🎉**
