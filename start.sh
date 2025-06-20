#!/bin/bash

# Script de démarrage pour PtitConvert
# Compatible Linux

echo "🚀 Démarrage de PtitConvert..."

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer pour continuer."
    exit 1
fi

# Vérifier si les dépendances sont installées
echo "🔍 Vérification des dépendances..."
python3 -c "import tkinter, PIL, PyPDF2, docx, openpyxl, reportlab, img2pdf, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installation des dépendances..."
    pip3 install -r requirements.txt
fi

# Lancer l'application
echo "✅ Lancement de PtitConvert..."
python3 main.py
