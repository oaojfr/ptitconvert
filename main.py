#!/usr/bin/env python3
"""
PtitConvert - Convertisseur de fichiers avec interface graphique
Point d'entrée principal de l'application
"""

import sys
import tkinter as tk
from tkinter import messagebox
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    """Point d'entrée principal de l'application"""
    try:
        # Créer la fenêtre principale
        root = tk.Tk()
        root.title("PtitConvert - Convertisseur de Fichiers")
        root.geometry("800x600")
        root.minsize(600, 400)
        
        # Centrer la fenêtre
        root.eval('tk::PlaceWindow . center')
        
        # Créer l'application principale
        app = MainWindow(root)
        
        # Lancer la boucle principale
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du lancement de l'application:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
