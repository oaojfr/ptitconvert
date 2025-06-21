# 🚀 Guide de Démarrage Rapide - PtitConvert

## Installation Express

### Linux/macOS
```bash
git clone https://github.com/votre-username/ptitconvert.git
cd ptitconvert
chmod +x start.sh
./start.sh
```

### Windows
```cmd
git clone https://github.com/votre-username/ptitconvert.git
cd ptitconvert
start.bat
```

## Première Utilisation

### 1. Lancer l'application
- **Interface graphique** : Double-clic sur `start.sh` (Linux) ou `start.bat` (Windows)
- **Ligne de commande** : `python ptitconvert_cli.py --help`

### 2. Convertir vos premiers fichiers

#### Interface Graphique
1. Cliquez sur **"Ajouter fichiers"** ou **"Ajouter dossier"**
2. Sélectionnez le **format de sortie** dans la liste
3. Choisissez le **dossier de destination** 
4. Cliquez sur **"Convertir"**
5. L'application ouvrira automatiquement le dossier de résultats

#### Ligne de Commande
```bash
# Convertir une image
python ptitconvert_cli.py convert photo.jpg --format png

# Convertir un document  
python ptitconvert_cli.py convert document.pdf --format docx

# Convertir tout un dossier
python ptitconvert_cli.py batch ./images/ --format webp --output ./optimisees/
```

## Formats Supportés (Guide rapide)

| Depuis | Vers | Exemple |
|--------|------|---------|
| **Images** | PNG, JPG, PDF | `photo.jpg` → `photo.png` |
| **Documents** | PDF, DOCX, TXT, EPUB | `livre.epub` → `livre.pdf` |
| **Tableurs** | XLSX, CSV, ODS | `data.csv` → `data.xlsx` |
| **Archives** | ZIP, TAR, 7Z | `archive.rar` → `archive.zip` |
| **Audio** | MP3, WAV, FLAC | `musique.flac` → `musique.mp3` |
| **Vidéo** | MP4, AVI, MKV | `film.avi` → `film.mp4` |

## Fonctionnalités Clés

### 🌙 Mode Sombre
`Menu` → `Configuration` → `Thème` → `Sombre`

### 📊 Historique
`Menu` → `Fichier` → `Historique des conversions`

### ⚙️ Paramètres
`Menu` → `Configuration` → `Paramètres`
- Qualité JPEG/PDF
- Paramètres audio/vidéo
- Comportement de l'interface

## Raccourcis Utiles

### Interface Graphique
- **Ctrl+O** : Ajouter fichiers
- **Ctrl+Shift+O** : Ajouter dossier  
- **F5** : Actualiser la liste
- **Ctrl+H** : Afficher l'historique

### CLI
```bash
# Aide rapide
python ptitconvert_cli.py --help

# Formats supportés
python ptitconvert_cli.py formats

# Version et infos
python ptitconvert_cli.py --version
```

## Dépannage Express

### ❌ "Module not found"
```bash
pip install -r requirements.txt
```

### ❌ "Permission denied" (Linux)
```bash
chmod +x start.sh
```

### ❌ Conversion échoue
1. Vérifiez le format dans `Menu` → `Aide` → `À propos`
2. Consultez l'historique pour les détails d'erreur
3. Testez avec un fichier plus petit

### ❌ Interface ne s'affiche pas
```bash
# Vérifier tkinter
python -c "import tkinter; print('Tkinter OK')"

# Mettre à jour les dépendances
pip install --upgrade -r requirements.txt
```

## Support

- 📖 **Documentation complète** : [README.md](README.md)
- 🐛 **Signaler un bug** : [Issues GitHub](https://github.com/votre-username/ptitconvert/issues)
- 💬 **Questions** : Consultez l'historique intégré pour les logs d'erreur

---

**🎉 Bon conversion avec PtitConvert !**
