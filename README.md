# PtitConvert - Convertisseur de Fichiers

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Un convertisseur de fichiers polyvalent avec interface graphique intuitive, compatible Windows et Linux.

## 🚀 Fonctionnalités

- **Conversion d'images** : PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP → PNG, JPG, PDF
- **Conversion de documents** : PDF, DOCX, TXT → PDF, DOCX, TXT  
- **Conversion de feuilles de calcul** : XLSX, CSV → XLSX, CSV, PDF
- **Interface graphique** moderne avec Tkinter
- **Conversion par lots** pour traiter plusieurs fichiers
- **Validation automatique** des fichiers d'entrée
- **Aperçu et informations** sur les fichiers
- **Cross-platform** : fonctionne sur Windows et Linux

## 📦 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation automatique

**Linux :**
```bash
git clone https://github.com/votre-username/ptitconvert.git
cd ptitconvert
chmod +x start.sh
./start.sh
```

**Windows :**
```cmd
git clone https://github.com/votre-username/ptitconvert.git
cd ptitconvert
start.bat
```

### Installation manuelle

1. Clonez le repository :
```bash
git clone https://github.com/votre-username/ptitconvert.git
cd ptitconvert
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancez l'application :
```bash
python main.py
```

## 🎯 Utilisation

1. **Lancer l'application** avec `python main.py` ou les scripts fournis
2. **Ajouter des fichiers** via le bouton "Ajouter fichiers" ou "Ajouter dossier"
3. **Sélectionner le format de sortie** dans la liste déroulante
4. **Choisir le dossier de destination** (par défaut : `~/Convertis`)
5. **Cliquer sur "Convertir"** et attendre la fin du processus

### Formats supportés

| Type | Formats d'entrée | Formats de sortie |
|------|-----------------|-------------------|
| **Images** | PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP | PNG, JPG, JPEG, BMP, GIF, TIFF, PDF |
| **Documents** | PDF, DOCX, TXT | PDF, DOCX, TXT |
| **Tableurs** | XLSX, CSV | XLSX, CSV, PDF |

## 📁 Structure du projet

```
ptitconvert/
├── main.py              # Point d'entrée de l'application
├── gui/                 # Interface graphique
│   ├── __init__.py
│   └── main_window.py   # Fenêtre principale
├── converters/          # Modules de conversion
│   ├── __init__.py
│   ├── image_converter.py
│   ├── document_converter.py
│   └── spreadsheet_converter.py
├── utils/               # Utilitaires
│   ├── __init__.py
│   ├── file_handler.py
│   └── validators.py
├── requirements.txt     # Dépendances
├── start.sh            # Script de démarrage Linux
├── start.bat           # Script de démarrage Windows
└── README.md           # Documentation
```

## 🛠️ Développement

### Architecture

Le projet suit une architecture **MVC (Model-View-Controller)** :
- **Model** : `converters/` - Logique de conversion
- **View** : `gui/` - Interface utilisateur
- **Controller** : `utils/` - Utilitaires et validation

### Dépendances principales

- **Pillow** : Manipulation d'images
- **PyPDF2** : Traitement des PDF
- **python-docx** : Documents Word
- **openpyxl** : Fichiers Excel
- **reportlab** : Génération de PDF
- **img2pdf** : Conversion d'images en PDF
- **pandas** : Manipulation de données

### Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push sur la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🐛 Rapporter des bugs

Si vous trouvez un bug, veuillez ouvrir une [issue](https://github.com/votre-username/ptitconvert/issues) avec :
- Description du problème
- Étapes pour reproduire
- Système d'exploitation
- Version de Python

## 🎨 Captures d'écran

_Screenshots à ajouter après tests complets de l'interface_

## ✨ Fonctionnalités futures

- [ ] Support de nouveaux formats (EPUB, ODT, etc.)
- [ ] Compression/décompression d'archives
- [ ] Conversion audio/vidéo
- [ ] Interface en ligne de commande
- [ ] Mode sombre
- [ ] Historique des conversions
- [ ] Configuration des paramètres de qualité
