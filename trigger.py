"""
EvLogPyAI - Windows Event Log Manager
Applicazione per la gestione dei log del Visualizzatore Eventi di Windows

Questa applicazione permette di:
- Estrarre log dal Visualizzatore Eventi di Windows
- Filtrare per categoria (Applicazione, Sicurezza, Sistema, ecc.)
- Specificare il numero esatto di righe da estrarre
- Salvare i log in un file formattato sul Desktop
"""

# === IMPORTAZIONE LIBRERIE ===

# CustomTkinter: Libreria per creare interfacce grafiche moderne con tema dark/light
import customtkinter as ctk

# Messagebox: Modulo standard di tkinter per mostrare finestre di dialogo (alert, conferme, errori)
from tkinter import messagebox

# win32evtlog: Libreria per accedere ai log eventi di Windows (richiede pywin32)
import win32evtlog

# win32evtlogutil: Utilities per formattare i messaggi dei log eventi di Windows
import win32evtlogutil

# win32con: Costanti di Windows (come EVENTLOG_ERROR_TYPE, EVENTLOG_WARNING_TYPE, ecc.)
import win32con

# requests: Libreria per effettuare richieste HTTP (usata per inviare dati a N8N se necessario)
import requests

# json: Libreria per gestire dati in formato JSON
import json

# os: Libreria per operazioni sul sistema operativo (es. ottenere percorso Desktop)
import os

# datetime: Libreria per gestire date e orari (timestamp, formattazione date)
from datetime import datetime

# threading: Libreria per eseguire operazioni in background senza bloccare l'interfaccia grafica
import threading

# webbrowser: Libreria per aprire URL nel browser predefinito
import webbrowser

# tempfile: Libreria per creare file temporanei
import tempfile

# http.server: Libreria per creare un server HTTP locale
from http.server import HTTPServer, BaseHTTPRequestHandler

# socketserver: Per gestire il server in modo thread-safe
import socketserver

# urllib.parse: Per parsare i dati delle richieste
from urllib.parse import parse_qs


class EvLogPyAI(ctk.CTk):
    """
    Classe principale dell'applicazione EvLogPyAI
    Eredita da ctk.CTk che è la finestra principale di CustomTkinter
    """
    
    # === DIZIONARIO CATEGORIE LOG ===
    # Mappa i nomi italiani mostrati nell'interfaccia con i nomi tecnici usati da Windows
    # Chiave: Nome visualizzato nel menu a tendina
    # Valore: Nome interno del log di Windows
    LOG_CATEGORIES = {
        "Applicazione": "Application",      # Log degli eventi delle applicazioni
        "Sicurezza": "Security",            # Log degli eventi di sicurezza (login, permessi, ecc.)
        "Installazione": "Setup",           # Log degli eventi di installazione/aggiornamento
        "Sistema": "System",                # Log degli eventi di sistema (hardware, driver, ecc.)
        "Eventi Inoltrati": "ForwardedEvents"  # Log degli eventi inoltrati da altri computer
    }
    
    # === URL WEBHOOK N8N ===
    # URL del webhook N8N per triggerare il workflow
    # Questo URL punta al workflow specifico creato in N8N
    # NOTA: /webhook-test/ viene usato in modalità test
    #       /webhook/ viene usato quando il workflow è attivato in produzione
    N8N_WEBHOOK_URL = "http://localhost:5678/webhook/evlogpyai"
    
    # === CONFIGURAZIONE SERVER CALLBACK ===
    # Porta su cui il server locale ascolta le risposte da N8N
    CALLBACK_PORT = 5050
    CALLBACK_HOST = "127.0.0.1"  # IPv4 esplicito per evitare problemi con IPv6
    CALLBACK_URL_FOR_N8N = "host.docker.internal"  # URL speciale per Docker su Windows/Mac
    
    def __init__(self):
        """
        Costruttore della classe EvLogPyAI
        Inizializza la finestra principale e configura l'interfaccia grafica
        """
        # Chiama il costruttore della classe padre (ctk.CTk)
        super().__init__()
        
        # === VARIABILI PER IL SERVER CALLBACK ===
        # Server HTTP per ricevere le risposte da N8N
        self.callback_server = None
        self.callback_thread = None
        self.pending_request_data = None  # Memorizza i dati della richiesta in corso
        
        # === CONFIGURAZIONE FINESTRA PRINCIPALE ===
        # Imposta il titolo della finestra che appare nella barra del titolo
        self.title("EvLogPyAI - Windows Event Log Manager")
        
        # Imposta la dimensione iniziale della finestra (larghezza x altezza in pixel)
        # Aumentata l'altezza a 650px per mostrare tutti i pulsanti senza dover espandere
        self.geometry("650x650")
        
        # Imposta le dimensioni minime della finestra (impedisce di ridimensionarla troppo)
        self.minsize(600, 600)
        
        # === CONFIGURAZIONE ICONA/LOGO ===
        # Crea un'icona per la finestra dell'applicazione
        self._set_window_icon()
        
        # === CONFIGURAZIONE TEMA ===
        # Imposta l'aspetto dell'applicazione in modalità scura
        ctk.set_appearance_mode("dark")
        
        # Imposta il tema dei colori predefinito (verde)
        ctk.set_default_color_theme("green")
        
        # === PALETTE COLORI PERSONALIZZATA ===
        # Dizionario che contiene tutti i colori usati nell'applicazione
        # Questo permette di cambiare facilmente lo schema di colori in un unico punto
        self.colors = {
            "primary": "#10B981",        # Verde smeraldo - Colore principale (header, pulsanti)
            "secondary": "#6B7280",      # Grigio - Colore secondario
            "success": "#10B981",        # Verde smeraldo - Indica successo operazioni
            "danger": "#EF4444",         # Rosso - Indica pericolo/annullamento
            "background": "#1F2937",     # Grigio scuro - Sfondo generale dell'applicazione
            "card": "#374151",           # Grigio card - Sfondo dei contenitori/card
            "text": "#F9FAFB",           # Bianco - Colore del testo principale
            "text_secondary": "#D1D5DB", # Grigio chiaro - Testo secondario/hint
            "border": "#4B5563",         # Grigio bordo - Colore dei bordi degli input
            "input_bg": "#4B5563"        # Grigio - Sfondo dei campi di input
        }
        
        # Applica il colore di sfondo alla finestra principale
        self.configure(fg_color=self.colors["background"])
        
        # === CREAZIONE INTERFACCIA ===
        # Chiama il metodo che crea tutti i componenti grafici
        self._create_widgets()
    
    def _set_window_icon(self):
        """
        Imposta l'icona della finestra dell'applicazione
        Crea un'icona personalizzata con PIL se disponibile
        """
        try:
            from PIL import Image, ImageDraw, ImageTk
            import io
            
            # Crea un'immagine 64x64 per l'icona
            size = 64
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Disegna un cerchio verde smeraldo (colore primario dell'app)
            circle_color = (16, 185, 129, 255)  # #10B981 in RGBA
            draw.ellipse([4, 4, size-4, size-4], fill=circle_color)
            
            # Disegna un rettangolo bianco al centro (rappresenta un documento/log)
            doc_color = (255, 255, 255, 255)
            draw.rectangle([20, 16, 44, 48], fill=doc_color)
            
            # Disegna linee orizzontali sul documento
            line_color = (31, 41, 55, 255)  # Grigio scuro
            draw.line([24, 22, 40, 22], fill=line_color, width=2)
            draw.line([24, 28, 40, 28], fill=line_color, width=2)
            draw.line([24, 34, 40, 34], fill=line_color, width=2)
            draw.line([24, 40, 40, 40], fill=line_color, width=2)
            
            # Converte l'immagine in PhotoImage per tkinter
            photo = ImageTk.PhotoImage(img)
            
            # Imposta l'icona della finestra
            self.iconphoto(True, photo)
            
            # Mantiene un riferimento per evitare che venga garbage collected
            self._icon_photo = photo
            
        except ImportError:
            # Se PIL non è disponibile, usa un'icona predefinita
            # CustomTkinter non supporta nativamente le icone, quindi saltiamo
            pass
        except Exception:
            # In caso di altri errori, ignora silenziosamente
            pass
        
    def _create_widgets(self):
        """
        Metodo che crea tutti i componenti grafici dell'interfaccia
        Questo include: header, campi del form, pulsanti e barra di stato
        """
        
        # === CONTAINER PRINCIPALE ===
        # Frame principale che contiene tutti gli altri elementi
        # fg_color: colore dello sfondo della card
        # corner_radius: raggio degli angoli arrotondati (15px)
        self.main_frame = ctk.CTkFrame(
            self,                              # Elemento padre: la finestra principale
            fg_color=self.colors["card"],      # Colore di sfondo grigio della card
            corner_radius=15                   # Angoli arrotondati
        )
        # pack: metodo per posizionare il widget nella finestra
        # fill="both": riempie tutto lo spazio disponibile (orizzontale e verticale)
        # expand=True: si espande quando la finestra viene ridimensionata
        # padx/pady: margine esterno di 20 pixel su tutti i lati
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # === HEADER CON TITOLO APPLICAZIONE ===
        # Frame che contiene il titolo dell'applicazione (barra verde in alto)
        self.header_frame = ctk.CTkFrame(
            self.main_frame,                   # Contenuto nel main_frame
            fg_color=self.colors["primary"],   # Sfondo verde smeraldo
            corner_radius=10,                  # Angoli arrotondati
            height=60                          # Altezza fissa di 60 pixel
        )
        # pack: posiziona l'header
        # fill="x": riempie orizzontalmente
        # padx=15: margine laterale di 15 pixel
        # pady=(15, 20): margine superiore 15px, inferiore 20px
        self.header_frame.pack(fill="x", padx=15, pady=(15, 20))
        
        # pack_propagate(False): impedisce al frame di ridimensionarsi in base al contenuto
        # Mantiene l'altezza fissa di 60 pixel
        self.header_frame.pack_propagate(False)
        
        # === LABEL DEL TITOLO ===
        # Etichetta che mostra il nome dell'applicazione
        self.header_label = ctk.CTkLabel(
            self.header_frame,                                     # Contenuta nell'header_frame
            text="📋 EvLogPyAI - Gestione Log Eventi Windows",    # Testo da visualizzare
            font=ctk.CTkFont(size=18, weight="bold"),             # Font: dimensione 18, grassetto
            text_color="#1F2937"                                   # Colore testo scuro (contrasto con sfondo verde)
        )
        # expand=True: centra la label nell'header
        self.header_label.pack(expand=True)
        
        # === CONTAINER DEL FORM ===
        # Frame trasparente che contiene tutti i campi del form
        self.form_frame = ctk.CTkFrame(
            self.main_frame,           # Contenuto nel main_frame
            fg_color="transparent"     # Sfondo trasparente (eredita il colore del parent)
        )
        # Riempie tutto lo spazio disponibile con margini
        self.form_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # === CAMPO 1: TITOLO PROBLEMA ===
        # Crea l'etichetta "Titolo Problema *" sopra il campo input
        self._create_label("Titolo Problema *")
        
        # Campo di input per il titolo del problema
        self.title_entry = ctk.CTkEntry(
            self.form_frame,                                        # Contenuto nel form_frame
            placeholder_text="Inserisci il titolo del problema...", # Testo di hint quando il campo è vuoto
            height=40,                                              # Altezza del campo in pixel
            border_color=self.colors["border"],                     # Colore del bordo
            fg_color=self.colors["input_bg"],                       # Colore di sfondo del campo
            text_color=self.colors["text"]                          # Colore del testo inserito
        )
        # fill="x": si espande orizzontalmente
        # pady=(0, 15): nessun margine sopra, 15px sotto (spaziatura dal campo successivo)
        self.title_entry.pack(fill="x", pady=(0, 15))
        
        # === CAMPO 2: CATEGORIA LOG (MENU A TENDINA) ===
        # Crea l'etichetta "Categoria Log *"
        self._create_label("Categoria Log *")
        
        # Variabile che memorizza la selezione dell'utente nel menu a tendina
        # StringVar è una classe di tkinter per gestire valori stringa collegati ai widget
        self.category_var = ctk.StringVar(value="")
        
        # ComboBox (menu a tendina) per selezionare la categoria di log
        self.category_menu = ctk.CTkComboBox(
            self.form_frame,                               # Contenuto nel form_frame
            values=list(self.LOG_CATEGORIES.keys()),       # Lista delle opzioni (Applicazione, Sicurezza, ecc.)
            variable=self.category_var,                    # Variabile che memorizza la selezione
            height=40,                                     # Altezza del menu
            border_color=self.colors["border"],            # Colore del bordo
            fg_color=self.colors["input_bg"],              # Colore di sfondo
            text_color=self.colors["text"],                # Colore del testo selezionato
            button_color=self.colors["primary"],           # Colore del pulsante dropdown (freccia)
            button_hover_color="#059669",                  # Colore del pulsante quando il mouse è sopra
            dropdown_fg_color=self.colors["card"],         # Colore di sfondo del menu dropdown
            dropdown_hover_color=self.colors["primary"],   # Colore dell'elemento quando il mouse è sopra
            dropdown_text_color=self.colors["text"],       # Colore del testo nel dropdown
            state="readonly"                               # Impedisce di digitare, solo selezione
        )
        self.category_menu.pack(fill="x", pady=(0, 15))
        
        # Imposta il valore predefinito mostrato nel menu
        self.category_menu.set("Seleziona categoria...")
        
        # === CAMPO 3: NUMERO RIGHE LOG ===
        # Crea l'etichetta "Numero Righe Log *"
        self._create_label("Numero Righe Log *")
        
        # Frame orizzontale trasparente per contenere il campo input e il testo di aiuto
        self.rows_frame = ctk.CTkFrame(
            self.form_frame,           # Contenuto nel form_frame
            fg_color="transparent"     # Sfondo trasparente
        )
        self.rows_frame.pack(fill="x", pady=(0, 15))
        
        # Campo di input per inserire il numero di righe (eventi) da estrarre
        self.rows_entry = ctk.CTkEntry(
            self.rows_frame,                    # Contenuto nel rows_frame
            placeholder_text="Es: 50",          # Testo di esempio
            height=40,                          # Altezza del campo
            width=150,                          # Larghezza fissa di 150 pixel
            border_color=self.colors["border"], # Colore del bordo
            fg_color=self.colors["input_bg"],   # Colore di sfondo
            text_color=self.colors["text"]      # Colore del testo
        )
        # side="left": posiziona il widget sul lato sinistro del rows_frame
        self.rows_entry.pack(side="left")
        
        # Label con testo di aiuto accanto al campo input
        self.rows_hint = ctk.CTkLabel(
            self.rows_frame,                            # Contenuta nel rows_frame
            text="(Numero di eventi da recuperare)",    # Testo di spiegazione
            font=ctk.CTkFont(size=12),                  # Font più piccolo (12px)
            text_color=self.colors["text_secondary"]    # Colore grigio chiaro
        )
        # side="left": posiziona a destra del campo input
        # padx=10: margine sinistro di 10px per distanziare dal campo
        self.rows_hint.pack(side="left", padx=10)
        
        # === CAMPO 4: DESCRIZIONE ISSUE ===
        # Crea l'etichetta "Descrizione Issue *"
        self._create_label("Descrizione Issue *")
        
        # Textbox (campo di testo multilinea) per inserire la descrizione del problema
        self.description_text = ctk.CTkTextbox(
            self.form_frame,                    # Contenuto nel form_frame
            height=120,                         # Altezza di 120 pixel (permette più righe di testo)
            border_color=self.colors["border"], # Colore del bordo
            fg_color=self.colors["input_bg"],   # Colore di sfondo
            text_color=self.colors["text"],     # Colore del testo
            border_width=2,                     # Spessore del bordo (2px)
            corner_radius=8                     # Angoli arrotondati
        )
        # fill="x": si espande orizzontalmente
        # pady=(0, 20): margine inferiore di 20px per distanziare dai pulsanti
        self.description_text.pack(fill="x", pady=(0, 20))
        
        # === FRAME CONTENITORE PULSANTI ===
        # Frame orizzontale trasparente che contiene i pulsanti Annulla ed Estrai
        self.buttons_frame = ctk.CTkFrame(
            self.main_frame,       # Contenuto nel main_frame
            fg_color="transparent" # Sfondo trasparente
        )
        # fill="x": si espande orizzontalmente
        # padx=15: margine laterale
        # pady=(0, 15): margine inferiore di 15px
        self.buttons_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # === PULSANTE ANNULLA ===
        # Pulsante rosso che chiude l'applicazione senza salvare
        self.cancel_btn = ctk.CTkButton(
            self.buttons_frame,                          # Contenuto nel buttons_frame
            text="Annulla",                           # Testo del pulsante con emoji
            width=140,                                   # Larghezza di 140 pixel
            height=45,                                   # Altezza di 45 pixel
            fg_color=self.colors["danger"],              # Colore di sfondo rosso
            hover_color="#DC2626",                       # Colore più scuro quando il mouse è sopra
            font=ctk.CTkFont(size=14, weight="bold"),   # Font grassetto dimensione 14
            command=self._on_cancel                      # Funzione da eseguire al click
        )
        # side="left": posiziona il pulsante a sinistra
        # padx=(0, 10): margine destro di 10px per distanziarlo dall'altro pulsante
        self.cancel_btn.pack(side="left", padx=(0, 10))
        
        # === PULSANTE ESTRAI LOG ===
        # Pulsante verde che estrae i log e li salva sul desktop
        self.submit_btn = ctk.CTkButton(
            self.buttons_frame,                          # Contenuto nel buttons_frame
            text="📥 Estrai Log",                        # Testo del pulsante con emoji
            width=180,                                   # Larghezza di 180 pixel
            height=45,                                   # Altezza di 45 pixel
            fg_color=self.colors["success"],             # Colore di sfondo verde smeraldo
            hover_color="#059669",                       # Colore più scuro quando il mouse è sopra
            font=ctk.CTkFont(size=14, weight="bold"),   # Font grassetto dimensione 14
            command=self._on_submit                      # Funzione da eseguire al click
        )
        # side="right": posiziona il pulsante a destra
        self.submit_btn.pack(side="right")
        
        # === BARRA DI STATO ===
        # Label in basso che mostra messaggi di stato durante le operazioni
        # (es. "Lettura log in corso...", "File salvato", ecc.)
        self.status_label = ctk.CTkLabel(
            self.main_frame,                         # Contenuta nel main_frame
            text="",                                 # Inizialmente vuota
            font=ctk.CTkFont(size=11),               # Font piccolo (11px)
            text_color=self.colors["text_secondary"] # Colore grigio chiaro
        )
        # pady=(0, 10): margine inferiore di 10px
        self.status_label.pack(pady=(0, 10))
        
    def _create_label(self, text: str):
        """
        Metodo di utilità per creare le etichette dei campi del form
        
        Args:
            text (str): Il testo da visualizzare nell'etichetta (es. "Titolo Problema *")
        """
        # Crea una label (etichetta) con stile uniforme per tutti i campi
        label = ctk.CTkLabel(
            self.form_frame,                         # Contenuta nel form_frame
            text=text,                               # Testo passato come parametro
            font=ctk.CTkFont(size=14, weight="bold"),# Font grassetto dimensione 14
            text_color=self.colors["text"],          # Colore bianco
            anchor="w"                               # Allineamento a sinistra (west)
        )
        # fill="x": si espande orizzontalmente
        # pady=(0, 5): margine inferiore di 5px (spazio tra label e campo input)
        label.pack(fill="x", pady=(0, 5))
        
    def _validate_fields(self) -> bool:
        """
        Valida tutti i campi obbligatori del form prima dell'estrazione dei log
        
        Returns:
            bool: True se tutti i campi sono validi, False altrimenti
        """
        # Lista che conterrà tutti i messaggi di errore trovati
        errors = []
        
        # === VALIDAZIONE CAMPO TITOLO ===
        # Verifica che il campo titolo non sia vuoto
        # get() recupera il testo, strip() rimuove spazi bianchi all'inizio e alla fine
        if not self.title_entry.get().strip():
            errors.append("• Il campo 'Titolo Problema' è obbligatorio")
            
        # === VALIDAZIONE CATEGORIA ===
        # Verifica che sia stata selezionata una categoria dal menu a tendina
        # Controlla se il valore è vuoto o ancora impostato al placeholder
        if self.category_var.get() == "" or self.category_var.get() == "Seleziona categoria...":
            errors.append("• Seleziona una categoria di log")
            
        # === VALIDAZIONE NUMERO RIGHE ===
        # Recupera il valore inserito nel campo numero righe
        rows_value = self.rows_entry.get().strip()
        
        # Verifica che il campo non sia vuoto
        if not rows_value:
            errors.append("• Il campo 'Numero Righe Log' è obbligatorio")
        # Verifica che sia un numero intero positivo
        # isdigit() controlla se la stringa contiene solo cifre
        elif not rows_value.isdigit() or int(rows_value) <= 0:
            errors.append("• Il numero di righe deve essere un numero positivo")
            
        # === VALIDAZIONE DESCRIZIONE ===
        # Verifica che il campo descrizione non sia vuoto
        # get("1.0", "end-1c") recupera tutto il testo dal textbox
        # "1.0" = riga 1, carattere 0 (inizio)
        # "end-1c" = fine meno 1 carattere (per escludere il newline finale)
        if not self.description_text.get("1.0", "end-1c").strip():
            errors.append("• Il campo 'Descrizione Issue' è obbligatorio")
            
        # === MOSTRA ERRORI SE PRESENTI ===
        # Se ci sono errori, mostra un messaggio di errore con tutti i problemi trovati
        if errors:
            messagebox.showerror(
                "Campi Obbligatori",                                    # Titolo della finestra
                "Compilare tutti i campi richiesti:\n\n" + "\n".join(errors)  # Messaggio con lista errori
            )
            return False  # Validazione fallita
            
        return True  # Validazione riuscita
    
    def _get_windows_logs(self, category: str, num_records: int) -> list:
        """
        Recupera i log dal Visualizzatore Eventi di Windows
        
        Args:
            category (str): Nome della categoria di log in italiano (es. "Applicazione")
            num_records (int): Numero esatto di eventi da recuperare
            
        Returns:
            list: Lista di dizionari, ognuno contenente i dati di un evento di log
        """
        # Lista che conterrà tutti gli eventi recuperati
        logs = []
        
        # Converte il nome della categoria dall'italiano al nome tecnico Windows
        # get() con secondo parametro fornisce un valore predefinito se la chiave non esiste
        log_type = self.LOG_CATEGORIES.get(category, "Application")
        
        try:
            # === APERTURA LOG EVENTI ===
            # OpenEventLog apre l'accesso al log eventi di Windows
            # None = computer locale, log_type = tipo di log (Application, System, ecc.)
            hand = win32evtlog.OpenEventLog(None, log_type)
            
            # === FLAGS DI LETTURA ===
            # EVENTLOG_BACKWARDS_READ: legge dal più recente al più vecchio
            # EVENTLOG_SEQUENTIAL_READ: legge in sequenza
            # L'operatore | combina le due flag (bitwise OR)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            
            # Contatore degli eventi letti finora
            events_read = 0
            
            # === CICLO DI LETTURA EVENTI ===
            # Continua a leggere finché non raggiungiamo il numero richiesto di eventi
            while events_read < num_records:
                # ReadEventLog legge un batch di eventi (di solito fino a 100 alla volta)
                # Ritorna una lista di oggetti evento
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                
                # Se non ci sono più eventi da leggere, esci dal ciclo
                if not events:
                    break
                    
                # === PROCESSA OGNI EVENTO ===
                # Itera su ogni evento nel batch appena letto
                for event in events:
                    # Se abbiamo già raggiunto il numero richiesto, ferma la lettura
                    if events_read >= num_records:
                        break
                        
                    # === DETERMINAZIONE TIPO EVENTO ===
                    # Converte il codice numerico del tipo evento in una stringa leggibile
                    event_type = "Info"  # Valore predefinito
                    
                    # EVENTLOG_ERROR_TYPE = 1: Evento di errore critico
                    if event.EventType == win32con.EVENTLOG_ERROR_TYPE:
                        event_type = "Errore"
                    # EVENTLOG_WARNING_TYPE = 2: Evento di avviso
                    elif event.EventType == win32con.EVENTLOG_WARNING_TYPE:
                        event_type = "Avviso"
                    # EVENTLOG_INFORMATION_TYPE = 4: Evento informativo
                    elif event.EventType == win32con.EVENTLOG_INFORMATION_TYPE:
                        event_type = "Informazione"
                    # EVENTLOG_AUDIT_SUCCESS = 8: Audit riuscito (eventi di sicurezza)
                    elif event.EventType == win32con.EVENTLOG_AUDIT_SUCCESS:
                        event_type = "Audit Success"
                    # EVENTLOG_AUDIT_FAILURE = 16: Audit fallito (eventi di sicurezza)
                    elif event.EventType == win32con.EVENTLOG_AUDIT_FAILURE:
                        event_type = "Audit Failure"
                    
                    # === RECUPERO MESSAGGIO EVENTO ===
                    # Tenta di formattare il messaggio dell'evento in modo leggibile
                    try:
                        # SafeFormatMessage converte il messaggio raw in testo formattato
                        msg = win32evtlogutil.SafeFormatMessage(event, log_type)
                    except:
                        # Se la formattazione fallisce, usa un messaggio predefinito
                        msg = "Messaggio non disponibile"
                    
                    # === CREAZIONE DIZIONARIO EVENTO ===
                    # Crea un dizionario con tutti i dati dell'evento
                    log_entry = {
                        "timestamp": event.TimeGenerated.Format(),  # Data/ora dell'evento formattata
                        "source": event.SourceName,                 # Nome dell'applicazione/servizio che ha generato l'evento
                        "event_id": event.EventID & 0xFFFF,         # ID univoco dell'evento (& 0xFFFF estrae i 16 bit bassi)
                        "type": event_type,                         # Tipo evento (Errore, Avviso, ecc.)
                        "category": event.EventCategory,            # Categoria numerica dell'evento
                        "message": msg[:500] if msg else "N/A"     # Messaggio (limitato a 500 caratteri per evitare file troppo grandi)
                    }
                    
                    # Aggiunge l'evento alla lista dei log
                    logs.append(log_entry)
                    
                    # Incrementa il contatore eventi letti
                    events_read += 1
                    
            # === CHIUSURA LOG ===
            # Chiude l'handle del log eventi (importante per liberare risorse)
            win32evtlog.CloseEventLog(hand)
            
        except Exception as e:
            # === GESTIONE ERRORI ===
            # Se si verifica un errore durante la lettura (es. permessi insufficienti)
            # mostra un messaggio di errore all'utente
            messagebox.showerror(
                "Errore Lettura Log",                                           # Titolo finestra
                f"Impossibile leggere i log di Windows:\n{str(e)}\n\n"
                "Assicurati di avere i permessi necessari."                     # Messaggio dettagliato
            )
            # Ritorna una lista vuota in caso di errore
            return []
            
        # Ritorna la lista di eventi recuperati
        return logs
    
    def _update_status(self, message: str):
        """
        Aggiorna il testo nella barra di stato in basso
        
        Args:
            message (str): Il messaggio da visualizzare nella status bar
        """
        # Imposta il testo della label di stato
        self.status_label.configure(text=message)
        
        # update() forza l'aggiornamento immediato della UI
        # Senza questo, il messaggio potrebbe non apparire finché la funzione non termina
        self.update()
        
    def _on_submit(self):
        """
        Gestisce il click sul pulsante "Estrai Log"
        Esegue la validazione, lettura dei log e salvataggio su desktop in un thread separato
        """
        # === VALIDAZIONE CAMPI ===
        # Prima di procedere, verifica che tutti i campi siano compilati correttamente
        if not self._validate_fields():
            return  # Se la validazione fallisce, esce dalla funzione
            
        # === DISABILITAZIONE PULSANTE ===
        # Disabilita il pulsante durante l'elaborazione per evitare click multipli
        # state="disabled": rende il pulsante non cliccabile
        # text: cambia il testo per dare feedback visivo all'utente
        self.submit_btn.configure(state="disabled", text="⏳ Estrazione...")
        
        # Aggiorna la status bar per informare l'utente
        self._update_status("📖 Lettura log di Windows...")
        
        # === FUNZIONE INTERNA PER ELABORAZIONE ===
        # Definisce una funzione interna che esegue l'effettivo lavoro
        def process():
            try:
                # === RECUPERO VALORI DAL FORM ===
                # Ottiene i valori inseriti dall'utente nei vari campi
                title = self.title_entry.get().strip()           # Titolo del problema
                category = self.category_var.get()               # Categoria selezionata
                num_rows = int(self.rows_entry.get().strip())    # Numero righe (convertito in intero)
                description = self.description_text.get("1.0", "end-1c").strip()  # Descrizione completa
                
                # === RECUPERO LOG DA WINDOWS ===
                # Chiama la funzione che legge i log dal Visualizzatore Eventi
                logs = self._get_windows_logs(category, num_rows)
                
                # === CONTROLLO LOG TROVATI ===
                # Se non sono stati trovati log, informa l'utente e termina
                if not logs:
                    self.submit_btn.configure(state="normal", text="📥 Estrai Log")  # Riabilita il pulsante
                    self._update_status("⚠️ Nessun log trovato")                     # Aggiorna status
                    return  # Esce dalla funzione
                
                # === SALVATAGGIO FILE ===
                # Chiama la funzione che salva i log in un file di testo sul desktop
                self._save_logs_to_desktop(title, category, description, logs, num_rows)
                
            finally:
                # === RIABILITAZIONE PULSANTE ===
                # Il blocco finally viene sempre eseguito, anche in caso di errore
                # Riabilita il pulsante e ripristina il testo originale
                self.submit_btn.configure(state="normal", text="📥 Estrai Log")
                
        # === ESECUZIONE IN THREAD SEPARATO ===
        # Crea ed avvia un thread daemon che esegue la funzione process()
        # daemon=True: il thread termina automaticamente quando l'app viene chiusa
        # Questo evita che l'interfaccia si blocchi durante la lettura dei log
        threading.Thread(target=process, daemon=True).start()
    
    def _save_logs_to_desktop(self, title: str, category: str, description: str, logs: list, num_rows: int):
        """
        Salva i log estratti in un file di testo formattato sul Desktop dell'utente
        
        Args:
            title (str): Titolo del problema
            category (str): Categoria di log selezionata
            description (str): Descrizione dettagliata del problema
            logs (list): Lista di dizionari contenenti gli eventi log
            num_rows (int): Numero di righe richieste dall'utente
        """
        try:
            # === DETERMINAZIONE PERCORSO DESKTOP ===
            # os.path.expanduser("~") ottiene la cartella home dell'utente corrente
            # es. "C:\Users\NomeUtente" su Windows
            # os.path.join() combina il percorso con "Desktop"
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # === GENERAZIONE NOME FILE ===
            # Crea un timestamp nel formato AAAAMMGG_HHMMSS (es. 20260202_153045)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Sanitizza il titolo rimuovendo caratteri non validi per i nomi file
            # Mantiene solo lettere, numeri, spazi, trattini e underscore
            # [:50] limita la lunghezza a 50 caratteri per evitare nomi troppo lunghi
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)[:50]
            
            # Compone il nome del file finale
            # Formato: EvLog_[Categoria]_[Titolo]_[Timestamp].txt
            filename = f"EvLog_{category}_{safe_title}_{timestamp}.txt"
            
            # Crea il percorso completo del file combinando desktop + nome file
            filepath = os.path.join(desktop, filename)
            
            # Aggiorna la status bar
            self._update_status("💾 Salvataggio file sul desktop...")
            
            # === SCRITTURA FILE ===
            # Apre il file in modalità scrittura con encoding UTF-8 (supporta caratteri speciali)
            # "with" assicura che il file venga chiuso automaticamente alla fine
            with open(filepath, "w", encoding="utf-8") as f:
                # === INTESTAZIONE FILE ===
                # Scrive una riga di separazione (80 caratteri "=")
                f.write("=" * 80 + "\n")
                # Titolo del report centrato
                f.write("  EvLogPyAI - Report Log Eventi Windows\n")
                f.write("=" * 80 + "\n\n")
                
                # === INFORMAZIONI ESTRAZIONE ===
                # Scrive i metadati dell'estrazione con emoji per migliore leggibilità
                f.write(f"📋 TITOLO: {title}\n")
                # Mostra sia il nome italiano che quello tecnico Windows della categoria
                f.write(f"📁 CATEGORIA: {category} ({self.LOG_CATEGORIES[category]})\n")
                # Data e ora dell'estrazione nel formato GG/MM/AAAA HH:MM:SS
                f.write(f"📅 DATA ESTRAZIONE: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                # Numero di righe richieste dall'utente
                f.write(f"📊 RIGHE RICHIESTE: {num_rows}\n")
                # Numero effettivo di righe estratte (potrebbe essere minore se non ci sono abbastanza log)
                f.write(f"📊 RIGHE ESTRATTE: {len(logs)}\n\n")
                
                # === SEZIONE DESCRIZIONE ISSUE ===
                # Riga di separazione (80 trattini)
                f.write("-" * 80 + "\n")
                f.write("  DESCRIZIONE ISSUE\n")
                f.write("-" * 80 + "\n")
                # Scrive la descrizione completa del problema
                f.write(f"{description}\n\n")
                
                # === SEZIONE LOG EVENTI ===
                f.write("=" * 80 + "\n")
                f.write("  LOG EVENTI\n")
                f.write("=" * 80 + "\n\n")
                
                # === CICLO DI SCRITTURA EVENTI ===
                # Itera su tutti gli eventi nella lista logs
                # enumerate(logs, 1) fornisce sia l'indice (partendo da 1) che l'evento
                for i, log in enumerate(logs, 1):
                    # Intestazione dell'evento con numero progressivo
                    f.write(f"--- Evento #{i} ---\n")
                    
                    # Scrive tutti i dettagli dell'evento in modo strutturato
                    f.write(f"  Timestamp: {log['timestamp']}\n")    # Data/ora evento
                    f.write(f"  Sorgente:  {log['source']}\n")       # Applicazione/servizio che ha generato l'evento
                    f.write(f"  Event ID:  {log['event_id']}\n")     # ID univoco dell'evento
                    f.write(f"  Tipo:      {log['type']}\n")         # Tipo (Errore, Avviso, Info, ecc.)
                    f.write(f"  Categoria: {log['category']}\n")     # Categoria numerica
                    f.write(f"  Messaggio:\n")
                    
                    # === FORMATTAZIONE MESSAGGIO ===
                    # Il messaggio può contenere più righe, quindi le splitta
                    # Indenta ogni riga con 4 spazi per migliore leggibilità
                    for line in log['message'].split('\n'):
                        f.write(f"    {line}\n")
                    
                    # Riga vuota tra un evento e l'altro per separazione visiva
                    f.write("\n")
                
                # === CHIUSURA FILE ===
                # Riga finale di separazione
                f.write("=" * 80 + "\n")
                f.write("  Fine Report\n")
                f.write("=" * 80 + "\n")
            
            # === NOTIFICA SUCCESSO ===
            # A questo punto il file è stato scritto e chiuso con successo
            
            # Aggiorna la status bar con il nome del file salvato
            self._update_status(f"✅ File salvato: {filename}")
            
            # Mostra una finestra di dialogo informativa all'utente
            messagebox.showinfo(
                "Estrazione Completata",                         # Titolo finestra
                f"Log estratti con successo!\n\n"
                f"📁 File: {filename}\n"                    # Nome del file creato
                f"📍 Posizione: Desktop\n"                  # Dove si trova il file
                f"📊 Eventi estratti: {len(logs)}"         # Quanti eventi sono stati salvati
            )
            
            # Pulisce i campi del form per permettere una nuova estrazione
            self._clear_form()
            
            # === INVIO TRIGGER A N8N ===
            # Dopo il salvataggio del file, invia i dati a N8N per triggerare il workflow
            self._send_to_n8n(title, category, description, logs, filename, filepath)
            
        except Exception as e:
            # === GESTIONE ERRORI ===
            # Se si verifica un errore durante il salvataggio del file
            # (es. permessi insufficienti, disco pieno, ecc.)
            
            # Aggiorna la status bar con messaggio di errore
            self._update_status("Errore salvataggio")
            
            # Mostra una finestra di errore con i dettagli
            messagebox.showerror(
                "Errore",                                         # Titolo finestra
                f"Impossibile salvare il file:\n{str(e)}"        # Messaggio di errore dettagliato
            )
    
    def _start_callback_server(self):
        """
        Avvia un server HTTP locale per ricevere le risposte da N8N
        Il server rimane in ascolto su CALLBACK_PORT in attesa della risposta dell'AI
        """
        # Riferimento all'istanza principale per accederla dall'handler
        app_instance = self
        
        class CallbackHandler(BaseHTTPRequestHandler):
            """
            Handler HTTP per gestire le richieste in arrivo da N8N
            """
            
            def log_message(self, format, *args):
                """Sovrascrive il log per evitare output su console"""
                print(f"📨 Server callback: {args[0]}")
            
            def do_POST(self):
                """
                Gestisce le richieste POST (risposta da N8N)
                """
                try:
                    # Legge la lunghezza del contenuto
                    content_length = int(self.headers['Content-Length'])
                    # Legge il corpo della richiesta
                    post_data = self.rfile.read(content_length)
                    
                    # Decodifica JSON
                    response_data = json.loads(post_data.decode('utf-8'))
                    
                    print("\n" + "="*80)
                    print("📥 RISPOSTA RICEVUTA DA N8N")
                    print("="*80)
                    print(f"📦 Dati ricevuti: {str(response_data)[:500]}")
                    print("="*80 + "\n")
                    
                    # Invia risposta OK a N8N
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "received"}).encode())
                    
                    # Processa la risposta nel thread principale della GUI
                    app_instance.after(100, lambda: app_instance._process_n8n_response(response_data))
                    
                except Exception as e:
                    print(f"❌ Errore elaborazione risposta: {str(e)}")
                    self.send_response(500)
                    self.end_headers()
            
            def do_GET(self):
                """
                Gestisce le richieste GET (health check)
                """
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"EvLogPyAI Callback Server Running")
        
        try:
            # Crea il server HTTP
            # Usa "" (stringa vuota) o "0.0.0.0" per ascoltare su tutte le interfacce
            # Questo permette connessioni sia IPv4 che IPv6
            self.callback_server = HTTPServer(
                ("", self.CALLBACK_PORT),  # "" = tutte le interfacce
                CallbackHandler
            )
            
            # Disabilita il timeout del server per gestire risposte lunghe dall'AI
            # None = nessun timeout, il server rimane in ascolto indefinitamente
            self.callback_server.timeout = None
            
            print(f"🖥️  Server callback avviato su http://{self.CALLBACK_HOST}:{self.CALLBACK_PORT}")
            print(f"📡 Ascolto su tutte le interfacce - porta {self.CALLBACK_PORT}")
            self._update_status(f"🖥️ Server in ascolto su porta {self.CALLBACK_PORT}...")
            
            # Avvia il server in un thread separato
            self.callback_thread = threading.Thread(
                target=self.callback_server.serve_forever,
                daemon=True
            )
            self.callback_thread.start()
            
            return True
            
        except OSError as e:
            print(f"❌ Errore avvio server: {str(e)}")
            if "Address already in use" in str(e) or "10048" in str(e):
                messagebox.showerror(
                    "Porta Occupata",
                    f"La porta {self.CALLBACK_PORT} è già in uso.\n"
                    "Chiudi altre istanze dell'applicazione o cambia la porta."
                )
            return False
        except Exception as e:
            print(f"❌ Errore server: {str(e)}")
            return False
    
    def _stop_callback_server(self):
        """
        Ferma il server callback se è in esecuzione
        """
        if self.callback_server:
            print("🛑 Arresto server callback...")
            self.callback_server.shutdown()
            self.callback_server = None
            self.callback_thread = None
    
    def _process_n8n_response(self, response_data: dict):
        """
        Processa la risposta ricevuta da N8N e apre il browser
        
        Args:
            response_data (dict): Dati JSON ricevuti da N8N contenenti l'output dell'AI
        """
        try:
            # Estrae l'output dell'AI dalla risposta
            # N8N invierà un JSON con il campo "output" contenente la risposta dell'AI
            ai_output = response_data.get("output", "")
            
            if not ai_output:
                # Prova altri possibili nomi di campo
                ai_output = response_data.get("text", "")
                if not ai_output:
                    ai_output = response_data.get("response", "")
                if not ai_output:
                    # Se ancora vuoto, usa l'intero JSON come stringa
                    ai_output = json.dumps(response_data, indent=2, ensure_ascii=False)
            
            print(f"📝 Output AI ricevuto ({len(ai_output)} caratteri)")
            
            # Genera l'HTML con la risposta
            html_content = self._generate_html_response(ai_output)
            
            # Apre nel browser
            self._open_response_in_browser(html_content)
            
            # Aggiorna lo stato
            self._update_status("✅ Analisi completata - Browser aperto")
            
            # Ferma il server callback (non più necessario)
            self._stop_callback_server()
            
        except Exception as e:
            print(f"❌ Errore elaborazione risposta: {str(e)}")
            self._update_status(f"❌ Errore: {str(e)}")
            messagebox.showerror("Errore", f"Errore durante l'elaborazione della risposta:\n{str(e)}")
    
    def _generate_html_response(self, ai_output: str) -> str:
        """
        Genera una pagina HTML formattata con la risposta dell'AI
        
        Args:
            ai_output (str): Testo della risposta dell'AI
            
        Returns:
            str: Pagina HTML completa
        """
        # Recupera i dati della richiesta originale se disponibili
        request_data = self.pending_request_data or {}
        title = request_data.get("title", "Analisi Log")
        category = request_data.get("category", "N/D")
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Escape HTML per sicurezza
        ai_output_escaped = ai_output.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Converte i newline in <br> per HTML
        ai_output_html = ai_output_escaped.replace("\n", "<br>\n")
        
        html_template = f'''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EvLogPyAI - Analisi AI</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1F2937 0%, #111827 100%);
            min-height: 100vh;
            padding: 40px 20px;
            color: #F9FAFB;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            padding: 30px;
            border-radius: 15px 15px 0 0;
            text-align: center;
            box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
        }}
        
        .header h1 {{
            color: #1F2937;
            font-size: 28px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        
        .header .subtitle {{
            color: #1F2937;
            opacity: 0.8;
            font-size: 14px;
        }}
        
        .meta-info {{
            background: #374151;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 15px;
            border-bottom: 1px solid #4B5563;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .meta-item .icon {{
            font-size: 18px;
        }}
        
        .meta-item .label {{
            color: #9CA3AF;
            font-size: 12px;
            text-transform: uppercase;
        }}
        
        .meta-item .value {{
            color: #F9FAFB;
            font-weight: 600;
        }}
        
        .content {{
            background: #374151;
            padding: 30px;
            border-radius: 0 0 15px 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }}
        
        .section-title {{
            color: #10B981;
            font-size: 18px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #10B981;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .ai-response {{
            background: #1F2937;
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid #10B981;
            line-height: 1.8;
            font-size: 15px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .ai-response p {{
            margin-bottom: 15px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #6B7280;
            font-size: 13px;
        }}
        
        .footer a {{
            color: #10B981;
            text-decoration: none;
        }}
        
        .footer a:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 600px) {{
            .header h1 {{
                font-size: 22px;
            }}
            
            .meta-info {{
                flex-direction: column;
            }}
            
            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 EvLogPyAI - Analisi AI</h1>
            <div class="subtitle">Report generato automaticamente dall'analisi dei log di Windows</div>
        </div>
        
        <div class="meta-info">
            <div class="meta-item">
                <span class="icon">📋</span>
                <div>
                    <div class="label">Titolo</div>
                    <div class="value">{title}</div>
                </div>
            </div>
            <div class="meta-item">
                <span class="icon">📁</span>
                <div>
                    <div class="label">Categoria</div>
                    <div class="value">{category}</div>
                </div>
            </div>
            <div class="meta-item">
                <span class="icon">🕐</span>
                <div>
                    <div class="label">Data Analisi</div>
                    <div class="value">{timestamp}</div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <div class="section-title">
                <span>🔍</span>
                <span>Diagnosi e Analisi</span>
            </div>
            <div class="ai-response">
{ai_output_html}
            </div>
        </div>
        
        <div class="footer">
            <p>Generato da <strong>EvLogPyAI</strong> con tecnologia <a href="#">Ollama AI</a></p>
            <p>© 2026 - Tutti i diritti riservati</p>
        </div>
    </div>
</body>
</html>'''
        
        return html_template
        
    def _send_to_n8n(self, title: str, category: str, description: str, logs: list, filename: str, filepath: str):
        """
        Invia i dati estratti al webhook N8N per triggerare il workflow
        Avvia un server callback locale per ricevere la risposta dell'AI
        
        Args:
            title (str): Titolo del problema
            category (str): Categoria di log selezionata
            description (str): Descrizione dettagliata del problema
            logs (list): Lista di dizionari contenenti gli eventi log
            filename (str): Nome del file salvato sul desktop
            filepath (str): Percorso completo del file salvato
        """
        try:
            # === AVVIO SERVER CALLBACK ===
            # Prima di inviare a N8N, avviamo il server locale per ricevere la risposta
            if not self._start_callback_server():
                self._update_status("❌ Impossibile avviare server callback")
                return
            
            # === MEMORIZZA DATI RICHIESTA ===
            # Salva i dati per usarli quando generiamo l'HTML
            self.pending_request_data = {
                "title": title,
                "category": category,
                "description": description,
                "total_logs": len(logs)
            }
            
            # === URL CALLBACK ===
            # URL dove N8N invierà la risposta dell'AI
            # Usa host.docker.internal se N8N è in Docker, altrimenti usa CALLBACK_HOST
            callback_url = f"http://{self.CALLBACK_URL_FOR_N8N}:{self.CALLBACK_PORT}/callback"
            
            # === PREPARAZIONE PAYLOAD ===
            # Crea un dizionario con tutti i dati da inviare a N8N
            payload = {
                "title": title,                                    # Titolo del problema
                "category": category,                              # Categoria italiana
                "category_windows": self.LOG_CATEGORIES[category], # Nome tecnico Windows
                "description": description,                        # Descrizione issue
                "timestamp": datetime.now().isoformat(),           # Timestamp ISO 8601
                "filename": filename,                              # Nome file creato
                "filepath": filepath,                              # Percorso completo
                "total_logs": len(logs),                          # Numero eventi estratti
                "logs": logs,                                      # Array con tutti gli eventi
                "callback_url": callback_url                       # URL per la risposta
            }
            
            # === DEBUG: Stampa informazioni invio ===
            print("\n" + "="*80)
            print("🚀 INVIO DATI A N8N")
            print("="*80)
            print(f"📍 URL Webhook: {self.N8N_WEBHOOK_URL}")
            print(f"📞 Callback URL: {callback_url}")
            print(f"📦 Payload: {len(logs)} log da inviare")
            print(f"📋 Titolo: {title}")
            print(f"📁 Categoria: {category}")
            print("="*80 + "\n")
            
            # === INVIO RICHIESTA HTTP POST ===
            # Aggiorna la status bar
            self._update_status("🚀 Invio a N8N... In attesa risposta AI...")
            
            # Invia una richiesta POST al webhook N8N
            # timeout=300: attende max 5 minuti per l'ACK iniziale
            # La risposta completa dell'AI arriverà al callback server (senza timeout)
            response = requests.post(
                self.N8N_WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300
            )
            
            # === DEBUG: Stampa risposta ===
            print(f"✅ ACK ricevuto - Status Code: {response.status_code}")
            print("="*80 + "\n")
            
            # === VERIFICA RISPOSTA ===
            # Controlla se N8N ha ricevuto correttamente la richiesta
            if response.status_code == 200:
                self._update_status("⏳ N8N sta elaborando... In attesa risposta AI...")
                print("✅ N8N ha ricevuto i dati. Server in ascolto per la risposta...")
                print(f"🖥️  Callback server attivo su: {callback_url}")
                # La risposta effettiva arriverà al callback server
                
            else:
                # Se il server risponde ma con un errore
                self._update_status(f"⚠️ N8N ha risposto con codice {response.status_code}")
                print(f"⚠️ ATTENZIONE: N8N risposta con status {response.status_code}")
                print(f"Corpo risposta: {response.text}")
                self._stop_callback_server()
                
        except requests.exceptions.Timeout:
            # === GESTIONE TIMEOUT ===
            self._update_status("⚠️ Timeout connessione N8N")
            print("\n" + "="*80)
            print("❌ ERRORE: Timeout connessione N8N")
            print("⏱️  N8N non risponde entro 5 minuti")
            print(f"📍 URL tentato: {self.N8N_WEBHOOK_URL}")
            print("="*80 + "\n")
            self._stop_callback_server()
            
        except requests.exceptions.ConnectionError as e:
            # === GESTIONE ERRORE CONNESSIONE ===
            self._update_status("⚠️ N8N non disponibile")
            print("\n" + "="*80)
            print("❌ ERRORE: Impossibile connettersi a N8N")
            print(f"📍 URL: {self.N8N_WEBHOOK_URL}")
            print(f"💡 Dettagli errore: {str(e)}")
            print("\n🔍 VERIFICHE DA FARE:")
            print("  1. N8N è in esecuzione? Controlla http://localhost:5678")
            print("  2. Il nodo Webhook è configurato nel workflow?")
            print("  3. Il webhook path è corretto? Deve essere 'evlogpyai'")
            print("  4. Il workflow è attivo/salvato?")
            print("="*80 + "\n")
            self._stop_callback_server()
            
        except Exception as e:
            # === GESTIONE ALTRI ERRORI ===
            self._update_status("❌ Errore invio N8N")
            print("\n" + "="*80)
            print("❌ ERRORE GENERICO durante invio a N8N")
            print(f"💥 Tipo errore: {type(e).__name__}")
            print(f"📄 Messaggio: {str(e)}")
            print("="*80 + "\n")
            self._stop_callback_server()
    
    def _open_response_in_browser(self, html_content: str):
        """
        Salva la risposta HTML in un file temporaneo e lo apre nel browser predefinito
        
        Args:
            html_content (str): Contenuto HTML da visualizzare
        """
        try:
            # Crea un file temporaneo con estensione .html
            # delete=False: non elimina il file automaticamente quando viene chiuso
            # suffix='.html': estensione del file
            # mode='w': modalità scrittura
            # encoding='utf-8': supporto caratteri speciali
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
                f.write(html_content)
                temp_file_path = f.name
            
            print(f"📄 Risposta salvata in: {temp_file_path}")
            
            # Apre il file HTML nel browser predefinito
            webbrowser.open('file://' + temp_file_path)
            
            print("🌐 Apertura browser con la risposta dell'AI...")
            
        except Exception as e:
            print(f"Errore apertura browser: {str(e)}")
            # Se fallisce l'apertura del browser, mostra almeno il path del file
            messagebox.showinfo(
                "Risposta AI disponibile",
                f"La risposta è stata salvata in:\n{temp_file_path}\n\n"
                "Apri il file manualmente nel browser."
            )
    
    def _on_cancel(self):
        """
        Gestisce il click sul pulsante Annulla
        Chiude immediatamente l'applicazione senza conferma
        """
        # quit() chiude la finestra e termina l'applicazione
        self.quit()
            
    def _clear_form(self):
        """
        Pulisce tutti i campi del form riportandoli allo stato iniziale
        Chiamata dopo un'estrazione riuscita per permettere una nuova ricerca
        """
        # Cancella il contenuto del campo titolo
        # delete(0, "end") rimuove tutto il testo dal carattere 0 alla fine
        self.title_entry.delete(0, "end")
        
        # Reimposta il menu categoria al valore predefinito
        self.category_menu.set("Seleziona categoria...")
        
        # Cancella il contenuto del campo numero righe
        self.rows_entry.delete(0, "end")
        
        # Cancella il contenuto del textbox descrizione
        # delete("1.0", "end") rimuove tutto il testo da riga 1, carattere 0 alla fine
        self.description_text.delete("1.0", "end")


def main():
    """
    Entry point (punto di ingresso) dell'applicazione
    Questa funzione viene chiamata all'avvio del programma
    """
    # Crea un'istanza della classe EvLogPyAI (inizializza l'applicazione)
    app = EvLogPyAI()
    
    # mainloop() avvia il loop principale dell'interfaccia grafica
    # Mantiene la finestra aperta e risponde agli eventi (click, digitazione, ecc.)
    # Il programma rimane in esecuzione finché la finestra non viene chiusa
    app.mainloop()


# === AVVIO APPLICAZIONE ===
# Controlla se questo file viene eseguito direttamente (non importato come modulo)
if __name__ == "__main__":
    # Avvia l'applicazione chiamando la funzione main()
    main()
