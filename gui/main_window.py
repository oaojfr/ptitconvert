"""
Fenêtre principale de l'application PtitConvert
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import threading
from datetime import datetime

from converters.image_converter import ImageConverter
from converters.document_converter import DocumentConverter
from converters.spreadsheet_converter import SpreadsheetConverter
from converters.advanced_document_converter import AdvancedDocumentConverter
from converters.archive_converter import ArchiveConverter
from converters.media_converter import MediaConverter
from utils.file_handler import FileHandler
from utils.validators import FileValidator
from utils.config import ConfigManager
from utils.history import ConversionHistory

class MainWindow:
    """Fenêtre principale de l'application"""
    
    def __init__(self, root):
        """Initialiser la fenêtre principale"""
        self.root = root
        
        # Initialiser les managers
        self.config_manager = ConfigManager()
        self.history = ConversionHistory()
        
        # Charger la configuration
        self.config = self.config_manager.get_config()
        
        self.setup_ui()
        self.setup_converters()
        self.apply_theme()
        self.files_to_convert = []
        
    def setup_ui(self):
        """Créer l'interface utilisateur"""
        # Menu principal
        self.create_menu()
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration de la grille
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Titre
        title_label = ttk.Label(main_frame, text="PtitConvert", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Section sélection de fichiers
        files_frame = ttk.LabelFrame(main_frame, text="Fichiers à convertir", padding="10")
        files_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        
        # Boutons de sélection
        buttons_frame = ttk.Frame(files_frame)
        buttons_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Ajouter fichiers", 
                  command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Ajouter dossier", 
                  command=self.add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Effacer", 
                  command=self.clear_files).pack(side=tk.LEFT, padx=5)
        
        # Liste des fichiers
        self.files_listbox = tk.Listbox(files_frame, height=8)
        self.files_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Scrollbar pour la liste
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        
        # Section conversion
        convert_frame = ttk.LabelFrame(main_frame, text="Options de conversion", padding="10")
        convert_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        convert_frame.columnconfigure(1, weight=1)
        
        # Format de sortie
        ttk.Label(convert_frame, text="Format de sortie:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.output_format = ttk.Combobox(convert_frame, state="readonly")
        self.output_format.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Dossier de sortie
        ttk.Label(convert_frame, text="Dossier de sortie:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        output_frame = ttk.Frame(convert_frame)
        output_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_path = ttk.Entry(output_frame)
        self.output_path.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Utiliser le dernier répertoire de sortie ou le défaut
        last_dir = self.config.get('ui', {}).get('last_output_directory', str(Path.home() / "Convertis"))
        self.output_path.insert(0, last_dir)
        
        ttk.Button(output_frame, text="Parcourir", 
                  command=self.browse_output_folder).grid(row=0, column=1)
        
        # Bouton de conversion
        self.convert_button = ttk.Button(convert_frame, text="Convertir", 
                                       command=self.start_conversion, state="disabled")
        self.convert_button.grid(row=2, column=0, columnspan=3, pady=(20, 0))
        
        # Barre de progression
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        self.progress_frame.columnconfigure(0, weight=1)
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Bind events
        self.files_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
    def setup_converters(self):
        """Initialiser les convertisseurs"""
        self.image_converter = ImageConverter()
        self.document_converter = DocumentConverter()
        self.spreadsheet_converter = SpreadsheetConverter()
        self.advanced_document_converter = AdvancedDocumentConverter()
        self.archive_converter = ArchiveConverter()
        self.media_converter = MediaConverter()
        self.file_handler = FileHandler()
        self.validator = FileValidator()
        
    def add_files(self):
        """Ajouter des fichiers à convertir"""
        files = filedialog.askopenfilenames(
            title="Sélectionner les fichiers à convertir",
            filetypes=[
                ("Tous les fichiers supportés", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff;*.webp;*.pdf;*.docx;*.txt;*.epub;*.odt;*.rtf;*.xlsx;*.csv;*.ods;*.zip;*.tar;*.rar;*.7z;*.mp3;*.mp4;*.avi;*.wav;*.flac"),
                ("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff;*.webp"),
                ("Documents", "*.pdf;*.docx;*.txt;*.epub;*.odt;*.rtf"),
                ("Feuilles de calcul", "*.xlsx;*.csv;*.ods"),
                ("Archives", "*.zip;*.tar;*.rar;*.7z"),
                ("Média", "*.mp3;*.mp4;*.avi;*.wav;*.flac"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        for file in files:
            if file not in self.files_to_convert:
                self.files_to_convert.append(file)
                self.files_listbox.insert(tk.END, os.path.basename(file))
        
        self.update_ui_state()
        
    def add_folder(self):
        """Ajouter tous les fichiers d'un dossier"""
        folder = filedialog.askdirectory(title="Sélectionner un dossier")
        if folder:
            supported_extensions = {
                # Images
                '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp',
                # Documents
                '.pdf', '.docx', '.txt', '.epub', '.odt', '.rtf',
                # Feuilles de calcul
                '.xlsx', '.csv', '.ods',
                # Archives
                '.zip', '.tar', '.rar', '.7z',
                # Média
                '.mp3', '.mp4', '.avi', '.wav', '.flac'
            }
            
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if Path(file_path).suffix.lower() in supported_extensions:
                        if file_path not in self.files_to_convert:
                            self.files_to_convert.append(file_path)
                            self.files_listbox.insert(tk.END, os.path.basename(file_path))
            
            self.update_ui_state()
            
    def clear_files(self):
        """Effacer la liste des fichiers"""
        self.files_to_convert.clear()
        self.files_listbox.delete(0, tk.END)
        self.update_ui_state()
        
    def on_file_select(self, event):
        """Gérer la sélection d'un fichier dans la liste"""
        selection = self.files_listbox.curselection()
        if selection:
            file_path = self.files_to_convert[selection[0]]
            file_ext = Path(file_path).suffix.lower()
            
            # Mettre à jour les formats de sortie disponibles
            self.update_output_formats(file_ext)
            
    def update_output_formats(self, input_extension):
        """Mettre à jour les formats de sortie disponibles"""
        formats = []
        
        # Images
        if input_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']:
            formats = ['PNG', 'JPG', 'JPEG', 'BMP', 'GIF', 'TIFF', 'PDF']
        # Documents standards
        elif input_extension in ['.pdf', '.docx', '.txt']:
            formats = ['PDF', 'DOCX', 'TXT']
        # Documents avancés
        elif input_extension in ['.epub', '.odt', '.rtf']:
            formats = ['PDF', 'DOCX', 'TXT', 'EPUB', 'ODT', 'RTF']
        # Feuilles de calcul
        elif input_extension in ['.xlsx', '.csv', '.ods']:
            formats = ['XLSX', 'CSV', 'ODS', 'PDF']
        # Archives
        elif input_extension in ['.zip', '.tar', '.rar', '.7z']:
            formats = ['ZIP', 'TAR', '7Z']
        # Média audio
        elif input_extension in ['.mp3', '.wav', '.flac']:
            formats = ['MP3', 'WAV', 'FLAC', 'OGG']
        # Média vidéo
        elif input_extension in ['.mp4', '.avi']:
            formats = ['MP4', 'AVI', 'MKV', 'MOV']
        
        self.output_format['values'] = formats
        if formats:
            self.output_format.set(formats[0])
            
    def update_ui_state(self):
        """Mettre à jour l'état de l'interface"""
        has_files = len(self.files_to_convert) > 0
        self.convert_button.config(state="normal" if has_files else "disabled")
        
        if has_files:
            # Déterminer les formats communs
            extensions = {Path(f).suffix.lower() for f in self.files_to_convert}
            if len(extensions) == 1:
                self.update_output_formats(next(iter(extensions)))
            else:
                self.output_format['values'] = ['PDF']  # Format universel
                self.output_format.set('PDF')
                
    def browse_output_folder(self):
        """Sélectionner le dossier de sortie"""
        folder = filedialog.askdirectory(title="Sélectionner le dossier de sortie")
        if folder:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, folder)
            
    def start_conversion(self):
        """Démarrer la conversion en arrière-plan"""
        if not self.files_to_convert:
            messagebox.showwarning("Attention", "Aucun fichier sélectionné pour la conversion.")
            return
            
        output_format = self.output_format.get()
        output_dir = self.output_path.get()
        
        if not output_format:
            messagebox.showwarning("Attention", "Veuillez sélectionner un format de sortie.")
            return
            
        if not output_dir:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier de sortie.")
            return
            
        # Créer le dossier de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Sauvegarder le dernier répertoire utilisé
        if self.config.get('ui', {}).get('remember_last_directory', True):
            self.config_manager.update_config('ui.last_output_directory', output_dir)
        
        # Démarrer la conversion dans un thread séparé
        self.convert_button.config(state="disabled")
        self.progress_bar['maximum'] = len(self.files_to_convert)
        self.progress_bar['value'] = 0
        
        thread = threading.Thread(target=self.convert_files, 
                                args=(self.files_to_convert.copy(), output_format, output_dir))
        thread.daemon = True
        thread.start()
        
    def convert_files(self, files, output_format, output_dir):
        """Convertir les fichiers (exécuté dans un thread séparé)"""
        success_count = 0
        error_count = 0
        
        for i, file_path in enumerate(files):
            start_time = datetime.now()
            success = False
            error_message = None
            
            try:
                self.root.after(0, self.update_progress, i, f"Conversion de {os.path.basename(file_path)}...")
                
                # Déterminer le type de fichier et le convertisseur approprié
                file_ext = Path(file_path).suffix.lower()
                
                # Images
                if file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']:
                    success = self.image_converter.convert(file_path, output_dir, output_format.lower())
                # Documents standards
                elif file_ext in ['.pdf', '.docx', '.txt']:
                    success = self.document_converter.convert(file_path, output_dir, output_format.lower())
                # Documents avancés
                elif file_ext in ['.epub', '.odt', '.rtf']:
                    success = self.advanced_document_converter.convert(file_path, output_dir, output_format.lower())
                # Feuilles de calcul
                elif file_ext in ['.xlsx', '.csv', '.ods']:
                    success = self.spreadsheet_converter.convert(file_path, output_dir, output_format.lower())
                # Archives
                elif file_ext in ['.zip', '.tar', '.rar', '.7z']:
                    success = self.archive_converter.convert(file_path, output_dir, output_format.lower())
                # Média
                elif file_ext in ['.mp3', '.mp4', '.avi', '.wav', '.flac']:
                    success = self.media_converter.convert(file_path, output_dir, output_format.lower())
                else:
                    success = False
                    error_message = f"Format {file_ext} non supporté"
                    
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_message = str(e)
                print(f"Erreur lors de la conversion de {file_path}: {e}")
                error_count += 1
            
            # Enregistrer dans l'historique
            try:
                conversion_time = (datetime.now() - start_time).total_seconds()
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                
                # Générer le nom du fichier de sortie
                input_name = Path(file_path).stem
                output_file = os.path.join(output_dir, f"{input_name}.{output_format.lower()}")
                
                self.history.add_conversion(
                    input_file=file_path,
                    input_format=file_ext[1:],  # Sans le point
                    output_file=output_file,
                    output_format=output_format.lower(),
                    file_size=file_size,
                    conversion_time=conversion_time,
                    success=success,
                    error_message=error_message
                )
            except Exception as e:
                print(f"Erreur lors de l'enregistrement dans l'historique: {e}")
                
        # Mise à jour finale
        self.root.after(0, self.conversion_complete, success_count, error_count)
        
    def update_progress(self, current, message):
        """Mettre à jour la barre de progression"""
        self.progress_bar['value'] = current + 1
        self.progress_label.config(text=message)
        
    def conversion_complete(self, success_count, error_count):
        """Conversion terminée"""
        self.progress_label.config(text=f"Conversion terminée: {success_count} réussies, {error_count} échouées")
        self.convert_button.config(state="normal")
        
        if error_count == 0:
            message = f"Tous les {success_count} fichiers ont été convertis avec succès!"
            if self.config.get('ui', {}).get('auto_open_output', True):
                message += "\n\nVoulez-vous ouvrir le dossier de sortie ?"
                if messagebox.askyesno("Succès", message):
                    self.open_output_folder()
            else:
                messagebox.showinfo("Succès", message)
        else:
            messagebox.showwarning("Conversion terminée", 
                                 f"Conversion terminée:\n{success_count} fichiers convertis\n{error_count} erreurs")
    
    def open_output_folder(self):
        """Ouvrir le dossier de sortie dans l'explorateur de fichiers"""
        output_dir = self.output_path.get()
        if os.path.exists(output_dir):
            import subprocess
            import platform
            
            try:
                if platform.system() == "Windows":
                    os.startfile(output_dir)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", output_dir])
                else:  # Linux
                    subprocess.run(["xdg-open", output_dir])
            except Exception as e:
                print(f"Erreur lors de l'ouverture du dossier: {e}")
    
    def create_menu(self):
        """Créer le menu principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ajouter fichiers...", command=self.add_files)
        file_menu.add_command(label="Ajouter dossier...", command=self.add_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Historique des conversions", command=self.show_history)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Configuration
        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configuration", menu=config_menu)
        config_menu.add_command(label="Paramètres...", command=self.show_settings)
        
        # Menu Thème
        theme_menu = tk.Menu(config_menu, tearoff=0)
        config_menu.add_cascade(label="Thème", menu=theme_menu)
        theme_menu.add_command(label="Clair", command=lambda: self.change_theme('light'))
        theme_menu.add_command(label="Sombre", command=lambda: self.change_theme('dark'))
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)
    
    def apply_theme(self):
        """Appliquer le thème selon la configuration"""
        theme = self.config.get('ui', {}).get('theme', 'light')
        
        if theme == 'dark':
            # Configuration du thème sombre
            self.style.theme_use('clam')
            
            # Couleurs du thème sombre
            bg_color = '#2b2b2b'
            fg_color = '#ffffff'
            select_bg = '#404040'
            select_fg = '#ffffff'
            
            # Configuration des styles
            self.style.configure('TFrame', background=bg_color)
            self.style.configure('TLabel', background=bg_color, foreground=fg_color)
            self.style.configure('TButton', background='#404040', foreground=fg_color)
            self.style.configure('TLabelFrame', background=bg_color, foreground=fg_color)
            self.style.configure('TLabelFrame.Label', background=bg_color, foreground=fg_color)
            self.style.configure('TEntry', fieldbackground='#404040', foreground=fg_color)
            self.style.configure('TCombobox', fieldbackground='#404040', foreground=fg_color)
            
            # Configuration de la fenêtre principale
            self.root.configure(bg=bg_color)
        else:
            # Thème clair (défaut)
            self.style.theme_use('clam')
    
    def change_theme(self, theme):
        """Changer le thème de l'interface"""
        self.config_manager.update_config('ui.theme', theme)
        self.config = self.config_manager.get_config()
        self.apply_theme()
        messagebox.showinfo("Thème", f"Thème changé en mode {theme}. Redémarrez l'application pour voir tous les changements.")
    
    def show_settings(self):
        """Afficher la fenêtre de paramètres"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Paramètres")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Contenu des paramètres (version simplifiée)
        ttk.Label(settings_window, text="Paramètres de qualité", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Paramètres d'image
        image_frame = ttk.LabelFrame(settings_window, text="Images", padding="10")
        image_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(image_frame, text="Qualité JPEG:").grid(row=0, column=0, sticky="w")
        jpeg_quality = tk.IntVar(value=self.config.get('conversion', {}).get('image', {}).get('jpeg_quality', 95))
        quality_scale = ttk.Scale(image_frame, from_=10, to=100, orient="horizontal", variable=jpeg_quality)
        quality_scale.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # Boutons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="Enregistrer", 
                  command=lambda: self.save_settings(settings_window, {'jpeg_quality': jpeg_quality.get()})).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Annuler", 
                  command=settings_window.destroy).pack(side="right")
    
    def save_settings(self, window, settings):
        """Enregistrer les paramètres"""
        for key, value in settings.items():
            if key == 'jpeg_quality':
                self.config_manager.update_config('conversion.image.jpeg_quality', value)
        
        window.destroy()
        messagebox.showinfo("Paramètres", "Paramètres enregistrés avec succès!")
    
    def show_history(self):
        """Afficher l'historique des conversions"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Historique des conversions")
        history_window.geometry("800x600")
        history_window.transient(self.root)
        history_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(history_window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Barre de recherche
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(search_frame, text="Rechercher:").pack(side="left")
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Liste de l'historique avec Treeview
        columns = ('Date', 'Fichier source', 'Format source', 'Format cible', 'Statut')
        history_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            history_tree.heading(col, text=col)
            history_tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=history_tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=history_tree.xview)
        history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Placement des widgets
        history_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Charger l'historique
        self.load_history_data(history_tree)
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Actualiser", 
                  command=lambda: self.load_history_data(history_tree)).pack(side="left")
        ttk.Button(button_frame, text="Exporter", 
                  command=lambda: self.export_history()).pack(side="left", padx=(5, 0))
        ttk.Button(button_frame, text="Fermer", 
                  command=history_window.destroy).pack(side="right")
    
    def load_history_data(self, tree):
        """Charger les données d'historique dans le Treeview"""
        # Vider le tree
        for item in tree.get_children():
            tree.delete(item)
        
        # Charger les données depuis la base
        try:
            history_data = self.history.get_recent_conversions(limit=1000)
            for entry in history_data:
                # Format: (timestamp, input_file, input_format, output_format, success)
                status = "✓ Réussi" if entry[4] else "✗ Échoué"
                tree.insert('', 'end', values=(
                    entry[0][:19],  # Date/heure
                    os.path.basename(entry[1]),  # Nom du fichier
                    entry[2].upper(),  # Format source
                    entry[3].upper(),  # Format cible
                    status
                ))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de l'historique: {e}")
    
    def export_history(self):
        """Exporter l'historique vers un fichier CSV"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Exporter l'historique",
                defaultextension=".csv",
                filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
            )
            
            if file_path:
                self.history.export_to_csv(file_path)
                messagebox.showinfo("Export", f"Historique exporté vers {file_path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
    
    def show_about(self):
        """Afficher la fenêtre À propos"""
        about_text = """PtitConvert v1.0
        
Convertisseur de fichiers multiformat avec interface graphique

Formats supportés:
• Images: PNG, JPG, JPEG, BMP, GIF, TIFF, WebP
• Documents: PDF, DOCX, TXT, EPUB, ODT, RTF
• Feuilles de calcul: XLSX, CSV, ODS
• Archives: ZIP, TAR, RAR, 7Z
• Média: MP3, MP4, AVI, WAV, FLAC

Développé avec Python et Tkinter
Licence Apache 2.0"""
        
        messagebox.showinfo("À propos de PtitConvert", about_text)
