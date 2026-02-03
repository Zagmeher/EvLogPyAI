"""
Setup script per creare l'eseguibile Windows di EvLogPyAI
Usa PyInstaller per compilare trigger.py in un file .exe standalone
"""

import PyInstaller.__main__
import os
import sys

def create_exe():
    """
    Crea l'eseguibile Windows con PyInstaller
    """
    
    # Parametri per PyInstaller
    params = [
        'trigger.py',                           # File principale
        '--name=EvLogPyAI',                     # Nome dell'eseguibile
        '--onefile',                            # Singolo file .exe (non cartella)
        '--windowed',                           # Nasconde la console (GUI app)
        '--icon=NONE',                          # Nessuna icona personalizzata
        '--add-data=requirements.txt;.',        # Include requirements.txt
        '--hidden-import=customtkinter',        # Import esplicito CustomTkinter
        '--hidden-import=PIL',                  # Import esplicito Pillow
        '--hidden-import=PIL._tkinter_finder',  # TKinter finder per Pillow
        '--hidden-import=win32evtlog',          # Import esplicito pywin32
        '--hidden-import=win32evtlogutil',      # Utility pywin32
        '--hidden-import=win32con',             # Costanti Windows
        '--hidden-import=requests',             # Import esplicito requests
        '--collect-all=customtkinter',          # Includi tutti i file CustomTkinter
        '--clean',                              # Pulisci build precedenti
        '--noconfirm',                          # Non chiedere conferma
    ]
    
    print("="*80)
    print("🚀 Creazione eseguibile EvLogPyAI per Windows")
    print("="*80)
    print("\n📦 Configurazione:")
    print("  - File sorgente: trigger.py")
    print("  - Output: EvLogPyAI.exe")
    print("  - Tipo: Single file (--onefile)")
    print("  - Modalità: Windowed (GUI)")
    print("\n⏳ Compilazione in corso...\n")
    
    # Esegui PyInstaller
    PyInstaller.__main__.run(params)
    
    print("\n" + "="*80)
    print("✅ Compilazione completata!")
    print("="*80)
    print(f"\n📁 Eseguibile disponibile in: {os.path.join(os.getcwd(), 'dist', 'EvLogPyAI.exe')}")
    print("\n💡 Prossimi passi:")
    print("  1. Testa l'eseguibile: dist/EvLogPyAI.exe")
    print("  2. Avvia Docker: docker-compose up -d")
    print("  3. Configura N8N: http://localhost:5678")
    print("  4. Importa il workflow da: n8n/workflows/evlogpyai-workflow.json")
    print("\n🎉 Pronto per la distribuzione!\n")

if __name__ == "__main__":
    # Verifica che lo script sia eseguito dalla directory corretta
    if not os.path.exists('trigger.py'):
        print("❌ Errore: trigger.py non trovato!")
        print("💡 Esegui questo script dalla directory del progetto EvLogPyAI")
        sys.exit(1)
    
    create_exe()
