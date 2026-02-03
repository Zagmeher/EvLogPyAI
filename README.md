# EvLogPyAI 

**Analisi Intelligente dei Log di Windows con AI**

EvLogPyAI è un'applicazione Windows che estrae automaticamente i log del Visualizzatore Eventi, li invia a un workflow N8N integrato con Ollama AI per l'analisi, e presenta i risultati in un report HTML dettagliato.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

##  Avvio Rapido - 3 Comandi

>  **Guida dettagliata**: Vedi [QUICKSTART.md](QUICKSTART.md) per istruzioni passo-passo con screenshots

**Per far funzionare tutto, esegui in ordine:**

```powershell
# 1. Avvia Docker (Ollama + N8N)
.\start.ps1

# 2. Importa workflow N8N manualmente
# Vai su http://localhost:5678
# Import from File → n8n/workflows/evlogpyai-workflow.json
# IMPORTANTE: Attiva il workflow (toggle in alto a destra → VERDE)

# 3. Avvia l'applicazione
.\EvLogPyAI.exe
# Oppure: python trigger.py
```

**Ordine di Esecuzione:**
1. **start.ps1** → Avvia container Docker + scarica modello AI (~10 min prima volta)
2. **N8N** → Importa e attiva workflow manualmente (vedi [n8n/workflows/README.md](n8n/workflows/README.md))
3. **EvLogPyAI.exe** → Avvia l'applicazione principale

---

## Caratteristiche

✅ **Interfaccia Grafica Moderna** - GUI intuitiva con CustomTkinter  
✅ **Estrazione Log Windows** - Accesso diretto al Visualizzatore Eventi  
✅ **Analisi AI Automatica** - Ollama analizza errori e propone soluzioni  
✅ **Report HTML Formattati** - Output professionale con stile dark theme  
✅ **Workflow N8N Integrato** - Automazione completa del processo  
✅ **Callback Asincrono** - Non blocca l'applicazione durante l'analisi  

---

## Installazione Completa

### Prerequisiti

- **Windows 10/11** (per accesso ai log di Windows)
- **Docker Desktop** installato e avviato
- **4GB RAM** disponibili per Ollama

### Installazione

#### Opzione 1: Eseguibile Pre-compilato (Consigliato)

1. Scarica l'ultima release da [GitHub Releases](https://github.com/zagmeher/EvLogPyAI/releases)
2. Estrai l'archivio in una cartella
3. Avvia Docker Desktop
4. Esegui lo script di avvio automatico:

```powershell
.\start.ps1
```

Questo script:
- ✅ Verifica che Docker sia attivo
- ✅ Avvia container Ollama e N8N
- ✅ Scarica automaticamente il modello AI (llama2)
- ✅ Apre N8N nel browser per configurazione

5. **IMPORTANTE**: Importa il workflow N8N:
   - Il browser si apre automaticamente su http://localhost:5678
   - Clicca su "Import from File"
   - Seleziona: `n8n/workflows/evlogpyai-workflow.json`
   - **ATTIVA** il workflow (toggle in alto a destra deve essere VERDE)

6. Lancia `EvLogPyAI.exe`

#### Opzione 2: Da Codice Sorgente

```powershell
# Clona il repository
git clone https://github.com/zagmeher/EvLogPyAI.git
cd EvLogPyAI

# Installa dipendenze Python
pip install -r requirements.txt

# Avvia Docker
docker-compose up -d

# Scarica modello Ollama
docker exec -it evlogpyai-ollama ollama pull llama2

# Importa workflow N8N (come sopra)

# Esegui l'applicazione
python trigger.py
```

---

## Utilizzo

### 1. Avvia l'Applicazione

Doppio click su `EvLogPyAI.exe` o esegui `python trigger.py`

### 2. Compila il Form

- **Titolo Problema**: Breve descrizione (es. "Errore Secure Boot")
- **Categoria Log**: Seleziona da Application, Security, System, Setup, ForwardedEvents
- **Numero Righe**: Quanti eventi estrarre (es. 50)
- **Descrizione Issue**: Dettagli del problema riscontrato

### 3. Estrai i Log

Clicca su **"Estrai Log"**. L'applicazione:
1. Legge i log dal Visualizzatore Eventi di Windows
2. Salva un file `.txt` sul Desktop
3. Avvia un server callback sulla porta 5050
4. Invia i dati a N8N

### 4. Attendi l'Analisi

- N8N riceve i dati e li formatta
- Ollama AI analizza i log (può richiedere 2-5 minuti)
- Il risultato viene inviato al callback di EvLogPyAI

### 5. Visualizza il Report

Il browser si apre automaticamente con un report HTML contenente:
- Diagnosi del problema
- Analisi degli errori più gravi
- Cause identificate
- Soluzioni proposte

---
## Architettura

```
┌─────────────────┐
│   EvLogPyAI     │ (Windows App)
│   trigger.py    │
└────────┬────────┘
         │ POST /webhook
         ▼
┌─────────────────┐
│   N8N Webhook   │ (Docker Container)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Edit Fields    │ (Formattazione)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Agent      │ (Ollama LLama2)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │ → POST http://host.docker.internal:5050/callback
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Callback Server │ (trigger.py:5050)
│  HTML Generator │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Browser     │ (Report HTML)
└─────────────────┘
```

---

## Configurazione Avanzata

### Cambio Porta Callback

Modifica in `trigger.py`:

```python
CALLBACK_PORT = 5050  # Cambia in una porta libera
```

Aggiorna anche l'URL in N8N nel nodo HTTP Request.

### Cambio Modello Ollama

Scarica un modello diverso:

```powershell
docker exec -it evlogpyai-ollama ollama pull mistral
```

Modifica il workflow N8N per usare il nuovo modello.

### Timeout Analisi AI

Modifica in `trigger.py` (riga ~1237):

```python
timeout=300  # 300 secondi = 5 minuti
```

---

## Struttura Progetto

```
EvLogPyAI/
├── trigger.py                  # Applicazione principale
├── requirements.txt            # Dipendenze Python
├── setup.py                    # Script build .exe
├── docker-compose.yml          # Configurazione Docker
├── README.md                   # Questo file
├── LICENSE                     # Licenza MIT
├── .gitignore                  # File da ignorare in Git
├── n8n/
│   └── workflows/
│       └── evlogpyai-workflow.json  # Workflow N8N
└── docs/
    ├── INSTALLATION.md         # Guida installazione dettagliata
    └── screenshots/            # Screenshot applicazione
```

---

**Soluzione**:
1. Verifica che EvLogPyAI sia in esecuzione
2. Verifica di aver cliccato "Estrai Log" (avvia il callback server)
3. Controlla che l'URL in N8N sia: `={{ $('Webhook').item.json.callback_url }}`

**Soluzione**:
- Esegui EvLogPyAI come **Amministratore** (tasto destro → "Esegui come amministratore")
- I log di Security richiedono privilegi elevati

## Autore
- GitHub: https://github.com/Zagmeher
- Email: info@angeloiandolo.it

**Fatto con ❤️ per semplificare l'analisi dei log di Windows**
