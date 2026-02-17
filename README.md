# EvLogPyAI

Applicazione Windows per estrarre log dal Visualizzatore Eventi, analizzarli con AI (Ollama) tramite N8N e generare un report HTML.

Windows application to extract Event Viewer logs, analyze them with AI (Ollama) via N8N and generate an HTML report.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## Requisiti / Requirements

- **Windows 10/11**
- **Docker Desktop** — https://www.docker.com/products/docker-desktop/
- **Python 3.10+** — https://www.python.org/downloads/

---

## Setup Automatico / Automatic Setup

```powershell
git clone https://github.com/YOUR_USERNAME/EvLogPyAI.git
cd EvLogPyAI
.\setup-evlogpyai.ps1
```

Lo script installa Python (se mancante), crea l'ambiente virtuale, avvia Docker e scarica il modello AI.
The script installs Python (if missing), creates a virtual environment, starts Docker and downloads the AI model.

---

## Guida Passo-Passo / Step-by-Step Guide

### Passo 1 — Avvia i Container Docker / Start Docker Containers

```powershell
.\start.ps1
```

Avvia Ollama (porta 11434) e N8N (porta 5678). La prima esecuzione scarica il modello llama2 (~4GB, 5-15 min).
Starts Ollama (port 11434) and N8N (port 5678). First run downloads the llama2 model (~4GB, 5-15 min).

### Passo 2 — Importa il Workflow N8N / Import the N8N Workflow

1. Apri / Open **http://localhost:5678**
2. Crea un account locale / Create a local account (solo al primo accesso / first time only)
3. Clicca **"Add workflow"** poi l'icona **⋮** in alto a destra → **"Import from File"**
   Click **"Add workflow"** then the **⋮** icon top-right → **"Import from File"**
4. Seleziona / Select `n8n/workflows/evlogpyai-workflow.json`
5. Apri il nodo **"Ollama Chat Model"** dentro l'AI Agent:
   Open the **"Ollama Chat Model"** node inside the AI Agent:
   - Clicca **"Create New Credential"** / Click **"Create New Credential"**
   - **Base URL**: `http://ollama:11434`
   - Salva / Save
6. **Attiva il workflow** — toggle in alto a destra → deve essere **VERDE**
   **Activate the workflow** — toggle top-right → must be **GREEN**
7. Salva / Save (**Ctrl+S**)

### Passo 3 — Avvia l'Applicazione / Start the Application

```powershell
# Con ambiente virtuale / With virtual environment
.\.venv\Scripts\Activate.ps1
python trigger.py

# Oppure con il launcher / Or with the launcher
.\EvLogPyAI.bat
```

### Passo 4 — Usa EvLogPyAI / Use EvLogPyAI

1. Compila il form: titolo, categoria log, numero righe, descrizione
   Fill the form: title, log category, number of rows, description
2. Clicca **"Estrai Log"** / Click **"Extract Logs"**
3. Attendi l'analisi AI (2-5 minuti) / Wait for AI analysis (2-5 min)
4. Il browser si apre con il report HTML / The browser opens with the HTML report

### Stop — Ferma tutto / Stop everything

```powershell
.\stop.ps1
```

---

## Architettura / Architecture

```
trigger.py (Windows)
    │
    ├── 1. Estrae log dal Visualizzatore Eventi
    │      Extracts logs from Windows Event Viewer
    │
    ├── 2. POST http://localhost:5678/webhook/evlogpyai
    │      Invia log + callback_url a N8N
    │      Sends logs + callback_url to N8N
    │
    │   [Docker Container: N8N]
    │   ├── Webhook riceve i dati / Webhook receives data
    │   ├── Edit Fields formatta il prompt / Edit Fields formats prompt
    │   ├── AI Agent → Ollama (llama2) analizza / analyzes
    │   └── HTTP Request → POST http://host.docker.internal:5050/callback
    │
    └── 3. Riceve risposta → genera HTML → apre browser
           Receives response → generates HTML → opens browser
```

---

## Struttura File / File Structure

```
EvLogPyAI/
├── trigger.py                  # App principale / Main app
├── docker-compose.yml          # Ollama + N8N containers
├── requirements.txt            # Dipendenze Python / Python dependencies
├── setup-evlogpyai.ps1         # Setup automatico / Automatic setup
├── start.ps1                   # Avvia containers / Start containers
├── stop.ps1                    # Ferma containers / Stop containers
├── build.ps1                   # Build .exe con PyInstaller
├── n8n/workflows/
│   └── evlogpyai-workflow.json # Workflow N8N da importare / N8N workflow to import
└── docs/
    └── INSTALLATION.md         # Guida dettagliata / Detailed guide
```

---

## Porte Utilizzate / Ports Used

| Servizio / Service | Porta / Port | URL                          |
|--------------------|--------------|------------------------------|
| N8N                | 5678         | http://localhost:5678        |
| Ollama             | 11434        | http://localhost:11434       |
| Callback Server    | 5050         | http://localhost:5050        |

---

## Risoluzione Problemi / Troubleshooting

| Problema / Problem | Soluzione / Solution |
|--------------------|----------------------|
| Webhook 404 | Il workflow N8N non è attivo. Attiva il toggle verde. / The N8N workflow is not active. Enable the green toggle. |
| "fetch failed" nell'AI Agent | Credenziali Ollama mancanti. Configura Base URL: `http://ollama:11434` / Missing Ollama credentials. Set Base URL: `http://ollama:11434` |
| Timeout callback | Firewall blocca porta 5050. Aggiungi regola: `New-NetFirewallRule -DisplayName "EvLogPyAI" -Direction Inbound -LocalPort 5050 -Protocol TCP -Action Allow` |
| Container non partono | Verifica Docker Desktop sia avviato: `docker ps` / Check Docker Desktop is running: `docker ps` |

---

## Licenza / License

MIT
