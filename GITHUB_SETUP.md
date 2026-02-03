# 📚 Guida Pubblicazione su GitHub

## Passo 1: Inizializza Git Repository

Apri PowerShell nella cartella `EvLogPyAI`:

```powershell
# Inizializza repository
git init

# Aggiungi tutti i file
git add .

# Primo commit
git commit -m "Initial commit - EvLogPyAI v1.0.0"
```

## Passo 2: Crea Repository su GitHub

1. Vai su https://github.com/new
2. Repository name: `EvLogPyAI`
3. Description: `Analisi Intelligente dei Log di Windows con AI`
4. Visibilità: Public (o Private se preferisci)
5. **NON** inizializzare con README, .gitignore o license
6. Clicca "Create repository"

## Passo 3: Collega e Publica

```powershell
# Aggiungi remote 
git remote add origin https://github.com/zagmeher/EvLogPyAI.git

# Rinomina branch principale
git branch -M main

# Push iniziale
git push -u origin main
```

## Passo 4: Compila l'Eseguibile

```powershell
# Esegui lo script di build
.\build.ps1

# Oppure manualmente
python setup.py
```

L'eseguibile sarà creato in: `dist\EvLogPyAI.exe`

## Passo 5: Crea una Release

### Su GitHub Web:

1. Vai sul tuo repository
2. Clicca su "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Title: `EvLogPyAI v1.0.0 - Prima Release`
5. Description:
```markdown
## 🎉 Prima Release di EvLogPyAI!

### Caratteristiche
- ✅ Estrazione automatica log Windows
- ✅ Analisi AI con Ollama
- ✅ Report HTML formattati
- ✅ Workflow N8N integrato

### Download
Scarica `EvLogPyAI-v1.0.0.zip` e segui le istruzioni nel README.

### Requisiti
- Windows 10/11
- Docker Desktop
- 8GB RAM
```

6. **Upload Files**:
   - Crea uno ZIP con:
     - `dist/EvLogPyAI.exe`
     - `docker-compose.yml`
     - `n8n/workflows/evlogpyai-workflow.json`
     - `README.md`
     - `docs/INSTALLATION.md`
   - Nominalo: `EvLogPyAI-v1.0.0.zip`
   - Caricalo nella release

7. Clicca "Publish release"

## Passo 6: Personalizza README

Nel file `README.md`, sostituisci:

- `@tuousername` con il tuo username GitHub
- `tuaemail@example.com` con la tua email
- `Il Tuo Nome` con il tuo nome

## Passo 7: Aggiungi Screenshots (Opzionale)

Crea cartella screenshots:

```powershell
mkdir docs\screenshots
```

Fai screenshot di:
1. Interfaccia EvLogPyAI
2. Workflow N8N
3. Report HTML finale

Salvali in `docs/screenshots/` e aggiornali nel README.

## Passo 8: Crea GitHub Actions (Opzionale)

Per build automatico ad ogni commit, crea `.github/workflows/build.yml`:

```yaml
name: Build EvLogPyAI

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: python setup.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: EvLogPyAI
        path: dist/EvLogPyAI.exe
```

## Comandi Git Utili

```powershell
# Verifica stato
git status

# Aggiungi modifiche
git add .

# Commit modifiche
git commit -m "Descrizione modifica"

# Push
git push

# Crea nuovo tag
git tag v1.0.1
git push origin v1.0.1

# Verifica remote
git remote -v

# Pull ultime modifiche
git pull
```

## Checklist Prima della Pubblicazione

- [ ] README.md aggiornato con username/email corretti
- [ ] LICENSE con nome autore corretto
- [ ] Eseguibile compilato e testato
- [ ] Docker-compose testato
- [ ] Workflow N8N esportato
- [ ] Screenshots aggiunti
- [ ] .gitignore configurato
- [ ] Tutte le dipendenze in requirements.txt

## Pronto! 🚀

Il tuo progetto è ora pubblico su GitHub e pronto per essere condiviso!
