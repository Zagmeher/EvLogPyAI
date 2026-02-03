# 📖 Configurazione N8N Workflow

## Importazione Workflow

1. **Apri N8N**: http://localhost:5678

2. **Importa Workflow**:
   - Menu (☰) → "Import from File"
   - Seleziona: `evlogpyai-workflow.json`
   - Clicca "Import"

3. **Configura Credenziali Ollama**:
   - Clicca sul nodo "Ollama Chat Model"
   - Se richiesto, crea nuove credenziali:
     - Name: `Ollama API`
     - Base URL: `http://ollama:11434`
     - Salva

4. **ATTIVA il Workflow**:
   - Toggle in alto a destra → **ON** (deve essere VERDE)
   - Verifica che il path sia: `/webhook/evlogpyai`

## 🔍 Struttura Workflow

```
Webhook (POST)
    ↓
Edit Fields (formatta dati)
    ↓
AI Agent (Ollama + Memory)
    ↓
HTTP Request (callback a trigger.py)
```

## ⚙️ Nodi Configurati

### 1. Webhook
- **Path**: `evlogpyai`
- **Method**: POST
- **Respond**: On Received (subito)

### 2. Edit Fields
- **sessionId**: `={{ $json.title }}`
- **text**: Formatta tutti i log per l'AI

### 3. AI Agent
- **Model**: Ollama Chat Model (llama2)
- **Memory**: Simple Memory (sessione per titolo)
- **Input**: Campo `text` da Edit Fields

### 4. HTTP Request
- **URL**: `={{ $('Webhook').item.json.callback_url }}`
  - Prende automaticamente: `http://host.docker.internal:5050/callback`
- **Body**: `{ "output": "={{ $json.output }}" }`

## ✅ Verifica Configurazione

Dopo l'importazione, controlla:

- [ ] Workflow attivo (toggle verde)
- [ ] Credenziali Ollama configurate
- [ ] Path webhook: `/webhook/evlogpyai`
- [ ] Nodo HTTP Request usa: `$('Webhook').item.json.callback_url`

## 🚨 Note Importanti

- **NON** modificare manualmente l'URL nel nodo HTTP Request
- L'URL callback viene inviato automaticamente da trigger.py
- `host.docker.internal` permette a N8N (Docker) di raggiungere il PC host
- Il workflow deve essere **ATTIVO** per funzionare in produzione

## 🧪 Test

Dopo aver attivato il workflow:

1. Avvia `EvLogPyAI.exe`
2. Compila il form
3. Clicca "Estrai Log"
4. Verifica in N8N: Executions → Dovresti vedere l'esecuzione
5. Dopo 2-5 minuti, il browser si apre con il report

## 🔧 Troubleshooting

**Workflow non si attiva**:
- Verifica credenziali Ollama
- Controlla che llama2 sia scaricato: `docker exec evlogpyai-ollama ollama list`

**Errore HTTP Request**:
- Verifica che trigger.py sia in esecuzione
- Controlla che il callback server sia attivo (porta 5050)

**Ollama non risponde**:
```bash
docker restart evlogpyai-ollama
```
