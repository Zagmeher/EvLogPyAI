# 🎯 Guida Rapida - 3 Passi per Iniziare

## 📦 Cosa Hai Scaricato

```
EvLogPyAI/
├── EvLogPyAI.exe              ← Applicazione principale
├── start.ps1                  ← Script di avvio Docker
├── stop.ps1                   ← Script di arresto Docker
├── docker-compose.yml         ← Configurazione container
└── n8n/workflows/
    └── evlogpyai-workflow.json ← Workflow da importare in N8N
```

---

## ⚡ Avvio in 3 Passi

### Passo 1: Avvia Docker

**Tasto destro su `start.ps1` → "Esegui con PowerShell"**

Questo script:
- ✅ Verifica Docker Desktop
- ✅ Avvia Ollama e N8N
- ✅ Scarica il modello AI (llama2)
- ✅ Apre N8N nel browser

**Tempo stimato**: 5-15 minuti (al primo avvio)

---

### Passo 2: Importa Workflow N8N

Quando si apre il browser su http://localhost:5678:

1. **Primo Accesso** (solo la prima volta):
   - Email: `tuaemail@example.com`
   - Password: `scegline una sicura`
   - Clicca "Setup"

2. **Importa Workflow**:
   - Menu (☰) → "Import from File"
   - Naviga in: `n8n\workflows\evlogpyai-workflow.json`
   - Clicca "Import"

3. **Configura Ollama** (se richiesto):
   - Clicca sul nodo "Ollama Chat Model"
   - Create New Credential
   - Base URL: `http://ollama:11434`
   - Salva

4. **ATTIVA il Workflow**:
   - Toggle in alto a destra → **VERDE** (ON)
   - Path deve essere: `/webhook/evlogpyai`

---

### Passo 3: Avvia EvLogPyAI

**Doppio click su `EvLogPyAI.exe`**

L'applicazione si apre. Ora puoi:

1. **Compila il form**:
   - Titolo: descrizione breve (es. "Errore Applicazione Chrome")
   - Categoria: seleziona da menu (Application, Security, System, ecc.)
   - Numero Righe: quanti log estrarre (es. 50)
   - Descrizione: dettagli del problema

2. **Clicca "📥 Estrai Log"**

3. **Attendi l'analisi**:
   - I log vengono salvati sul Desktop
   - N8N processa con Ollama AI (2-5 minuti)
   - Il browser si apre automaticamente con il report HTML

---

## 🔄 Utilizzi Successivi

**Ogni volta che usi EvLogPyAI:**

1. Verifica che Docker Desktop sia **avviato**
2. Se i container non sono attivi, esegui: `start.ps1`
3. Avvia `EvLogPyAI.exe`

---

## 🛑 Arresto

Quando hai finito, per risparmiare RAM:

**Tasto destro su `stop.ps1` → "Esegui con PowerShell"**

Questo ferma i container Docker.

---

## ❓ Risoluzione Problemi Comuni

### Docker non si avvia
```powershell
# Verifica che Docker Desktop sia aperto
# Icona balena nella system tray deve essere attiva
```

### N8N non risponde
```powershell
# Riavvia i container
.\stop.ps1
.\start.ps1
```

### Modello AI non trovato
```powershell
# Scarica manualmente
docker exec -it evlogpyai-ollama ollama pull llama2
```

### "ECONNREFUSED" quando estrai log
**Causa**: Il workflow N8N non è attivo

**Soluzione**:
1. Vai su http://localhost:5678
2. Apri il workflow "EvLogPyAI Workflow"
3. Attiva il toggle in alto a destra (deve essere VERDE)

### Browser non si apre con il report
**Causa**: Processo AI ancora in corso

**Soluzione**: Aspetta altri 2-3 minuti, Ollama sta ancora elaborando

---

## 📊 Verifica Stato Sistema

```powershell
# Verifica container attivi
docker ps

# Dovresti vedere:
# evlogpyai-ollama  (healthy)
# evlogpyai-n8n     (healthy)

# Verifica modelli AI installati
docker exec evlogpyai-ollama ollama list

# Dovresti vedere:
# llama2:latest
```

---

## 🎯 Checklist Prima dell'Uso

- [ ] Docker Desktop installato e avviato
- [ ] Eseguito `start.ps1`
- [ ] Importato workflow in N8N
- [ ] Workflow N8N **ATTIVO** (toggle verde)
- [ ] Modello llama2 scaricato
- [ ] EvLogPyAI.exe avviato

---

## 💡 Suggerimenti

- **Prima volta**: L'analisi può richiedere 5-10 minuti mentre il modello si carica
- **Utilizzi successivi**: L'analisi sarà più veloce (2-3 minuti)
- **RAM**: Chiudi applicazioni non necessarie per prestazioni migliori
- **Log Security**: Esegui EvLogPyAI.exe come **Amministratore** (tasto destro)

---

**🎉 Pronto all'uso! Buon lavoro con EvLogPyAI!**
