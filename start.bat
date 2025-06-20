@echo off
REM Script de démarrage pour PtitConvert
REM Compatible Windows

echo 🚀 Démarrage de PtitConvert...

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé. Veuillez l'installer pour continuer.
    pause
    exit /b 1
)

REM Vérifier si les dépendances sont installées
echo 🔍 Vérification des dépendances...
python -c "import tkinter, PIL, PyPDF2, docx, openpyxl, reportlab, img2pdf, pandas" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installation des dépendances...
    pip install -r requirements.txt
)

REM Lancer l'application
echo ✅ Lancement de PtitConvert...
python main.py

pause
