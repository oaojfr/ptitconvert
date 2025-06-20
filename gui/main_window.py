"""
Fenêtre principale de l'application PtitConvert
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import threading

from converters.image_converter import ImageConverter
from converters.document_converter import DocumentConverter
from converters.spreadsheet_converter import SpreadsheetConverter
from utils.file_handler import FileHandler
from utils.validators import FileValidator

class MainWindow:
    """Fenêtre principale de l'application"""
    
    def __init__(self, root):
        """Initialiser la fenêtre principale"""
        self.root = root
        self.setup_ui()
        self.setup_converters()
        self.files_to_convert = []
        
    def setup_ui(self):
        """Créer l'interface utilisateur"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
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
        self.output_path.insert(0, str(Path.home() / "Convertis"))
        
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
        self.file_handler = FileHandler()
        self.validator = FileValidator()
        
    def add_files(self):
        """Ajouter des fichiers à convertir"""
        files = filedialog.askopenfilenames(
            title="Sélectionner les fichiers à convertir",
            filetypes=[
                ("Tous les fichiers supportés", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff;*.webp;*.pdf;*.docx;*.txt;*.xlsx;*.csv"),
                ("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff;*.webp"),
                ("Documents", "*.pdf;*.docx;*.txt"),
                ("Feuilles de calcul", "*.xlsx;*.csv"),
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
            supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp',
                                  '.pdf', '.docx', '.txt', '.xlsx', '.csv'}
            
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
        
        if input_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']:
            formats = ['PNG', 'JPG', 'JPEG', 'BMP', 'GIF', 'TIFF', 'PDF']
        elif input_extension in ['.pdf', '.docx', '.txt']:
            formats = ['PDF', 'DOCX', 'TXT']
        elif input_extension in ['.xlsx', '.csv']:
            formats = ['XLSX', 'CSV', 'PDF']
        
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
            try:
                self.root.after(0, self.update_progress, i, f"Conversion de {os.path.basename(file_path)}...")
                
                # Déterminer le type de fichier et le convertisseur approprié
                file_ext = Path(file_path).suffix.lower()
                
                if file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']:
                    success = self.image_converter.convert(file_path, output_dir, output_format.lower())
                elif file_ext in ['.pdf', '.docx', '.txt']:
                    success = self.document_converter.convert(file_path, output_dir, output_format.lower())
                elif file_ext in ['.xlsx', '.csv']:
                    success = self.spreadsheet_converter.convert(file_path, output_dir, output_format.lower())
                else:
                    success = False
                    
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"Erreur lors de la conversion de {file_path}: {e}")
                error_count += 1
                
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
            messagebox.showinfo("Succès", f"Tous les {success_count} fichiers ont été convertis avec succès!")
        else:
            messagebox.showwarning("Conversion terminée", 
                                 f"Conversion terminée:\n{success_count} fichiers convertis\n{error_count} erreurs")
