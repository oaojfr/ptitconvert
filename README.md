# PtitConvert - Convertisseur de Fichiers Avancé

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Version](https://img.shields.io/badge/version-1.0-brightgreen.svg)

Un convertisseur de fichiers polyvalent et moderne avec interface graphique intuitive, mode sombre, historique des conversions et support étendu de formats. Compatible Windows et Linux.

## 🚀 Fonctionnalités

### 📁 Formats Supportés
- **Images** : PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP → PNG, JPG, PDF, BMP, GIF, TIFF
- **Documents** : PDF, DOCX, TXT, EPUB, ODT, RTF → conversions croisées entre tous les formats
- **Feuilles de calcul** : XLSX, CSV, ODS → XLSX, CSV, ODS, PDF
- **Archives** : ZIP, TAR, RAR, 7Z → conversion entre formats d'archives
- **Audio** : MP3, WAV, FLAC → MP3, WAV, FLAC, OGG
- **Vidéo** : MP4, AVI → MP4, AVI, MKV, MOV

### 🎨 Interface Utilisateur
- **Interface graphique moderne** avec Tkinter
- **Mode sombre/clair** configurable
- **Menu complet** avec toutes les options
- **Conversion par lots** pour traiter plusieurs fichiers
- **Barre de progression** en temps réel
- **Ouverture automatique** du dossier de sortie

### 📊 Gestion Avancée
- **Historique des conversions** avec base SQLite
- **Recherche et export** de l'historique (CSV)
- **Configuration des paramètres** de qualité par format
- **Validation automatique** des fichiers d'entrée
- **Gestion d'erreurs robuste** avec messages détaillés

### 💻 Interface en Ligne de Commande
- **CLI complète** avec options avancées
- **Support des couleurs** pour une meilleure expérience
- **Mode batch** pour l'automatisation
- **Cross-platform** : fonctionne sur Windows et Linux

## 📦 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation via Electron (recommandée)

```bash
git clone https://github.com/votre-username/ptitconvert.git
cd ptitconvert
# Installez les dépendances Python du backend
python3 -m venv .venv && source .venv/bin/activate || python -m venv .venv && .venv\\Scripts\\activate
python -m pip install -U pip
python -m pip install -r requirements.txt

# Lancez l'UI Electron (le backend démarre automatiquement)
cd electron
npm install
npm start
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

3. Lancez l'application (Tkinter, optionnel) :
```bash
python main.py
```

### Option: UI moderne (Electron)

- Backend Python (API FastAPI) sera lancé automatiquement par Electron. Pour installer et démarrer l'UI:
```bash
cd electron
npm install
npm start
```
L'UI se connecte à http://127.0.0.1:8787.

## 🎯 Utilisation

### Interface Graphique

1. **Lancer l'application (Electron)** :
   ```bash
   cd electron && npm start
   ```
   
2. **Utiliser le menu** :
   - `Fichier` → Ajouter fichiers/dossiers, consulter l'historique
   - `Configuration` → Paramètres de qualité, changer le thème
   - `Aide` → À propos de l'application

3. **Convertir des fichiers** :
   - Ajouter des fichiers via "Ajouter fichiers" ou "Ajouter dossier"
   - Sélectionner le format de sortie dans la liste déroulante
   - Choisir le dossier de destination
   - Cliquer sur "Convertir" et suivre la progression

### Interface en Ligne de Commande

```bash
# Afficher l'aide
python ptitconvert_cli.py --help

# Convertir un fichier
python ptitconvert_cli.py convert image.jpg --format png --output ./sortie/

# Convertir plusieurs fichiers
python ptitconvert_cli.py convert *.jpg --format pdf --output ./pdf/

# Mode batch pour dossier entier
python ptitconvert_cli.py batch ./images/ --format webp --output ./optimisees/
```

### Formats supportés

| Type | Formats d'entrée | Formats de sortie |
|------|-----------------|-------------------|
| **Images** | PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP | PNG, JPG, JPEG, BMP, GIF, TIFF, PDF |
| **Documents** | PDF, DOCX, TXT, EPUB, ODT, RTF | PDF, DOCX, TXT, EPUB, ODT, RTF |
| **Tableurs** | XLSX, CSV, ODS | XLSX, CSV, ODS, PDF |
| **Archives** | ZIP, TAR, RAR, 7Z | ZIP, TAR, 7Z |
| **Audio** | MP3, WAV, FLAC | MP3, WAV, FLAC, OGG |
| **Vidéo** | MP4, AVI | MP4, AVI, MKV, MOV |

## ⚙️ Configuration

L'application stocke ses paramètres dans `~/.ptitconvert/config.json` :

- **Thème** : Clair ou sombre
- **Qualité** : Paramètres par format (JPEG, PDF, audio, etc.)
- **Comportement** : Ouverture automatique du dossier, mémorisation des chemins

Accédez aux paramètres via `Configuration` → `Paramètres` dans le menu.

## 📁 Structure du projet

```
ptitconvert/
├── main.py                          # Point d'entrée GUI
├── ptitconvert_cli.py              # Interface en ligne de commande
├── test_integration.py             # Tests d'intégration
├── gui/                            # Interface graphique
│   ├── __init__.py
│   └── main_window.py              # Fenêtre principale avec thèmes
├── converters/                     # Modules de conversion
│   ├── __init__.py
│   ├── image_converter.py          # Images (PNG, JPG, etc.)
│   ├── document_converter.py       # Documents basiques (PDF, DOCX, TXT)
│   ├── advanced_document_converter.py # Documents avancés (EPUB, ODT, RTF)
│   ├── spreadsheet_converter.py    # Tableurs (XLSX, CSV, ODS)
│   ├── archive_converter.py        # Archives (ZIP, TAR, RAR, 7Z)
│   └── media_converter.py          # Audio/Vidéo (MP3, MP4, etc.)
├── utils/                          # Utilitaires
│   ├── __init__.py
│   ├── file_handler.py             # Gestion des fichiers
│   ├── validators.py               # Validation
│   ├── config.py                   # Configuration et paramètres
│   └── history.py                  # Historique des conversions
├── requirements.txt                # Dépendances Python
├── start.sh                       # Script de démarrage Linux
├── start.bat                      # Script de démarrage Windows
└── README.md                      # Documentation
```

## 🛠️ Développement

### Architecture

Le projet suit une architecture **MVC (Model-View-Controller)** modulaire :
- **Model** : `converters/` - Logique de conversion spécialisée par format
- **View** : `gui/` - Interface utilisateur avec thèmes et historique
- **Controller** : `utils/` - Configuration, historique, validation
- **CLI** : `ptitconvert_cli.py` - Interface en ligne de commande

### Dépendances principales

**Core :**
- **Pillow** : Manipulation d'images
- **PyPDF2** : Traitement des PDF
- **python-docx** : Documents Word
- **openpyxl** : Fichiers Excel
- **reportlab** : Génération de PDF

**Formats avancés :**
- **ebooklib** : Support EPUB
- **odfpy** : Support ODT/ODS
- **rarfile & py7zr** : Archives RAR et 7Z
- **moviepy & pydub** : Audio/Vidéo

**Interface :**
- **click & colorama** : CLI avec couleurs
- **sqlite3** : Base de données historique
- **tkinter** : Interface graphique (inclus avec Python)

### Contribution

## 🔧 Contribution

Les contributions sont les bienvenues ! Voici comment participer :

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push sur la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créez une Pull Request

### Tests

Avant de soumettre une PR, assurez-vous que les tests passent :
```bash
python test_integration.py
```

## 📝 Licence

Ce projet est sous licence Apache 2.0. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🐛 Support et Bugs

Si vous trouvez un bug ou avez besoin d'aide :
- Ouvrez une [issue](https://github.com/votre-username/ptitconvert/issues) 
- Consultez l'historique des conversions dans l'app (menu `Fichier` → `Historique`)
- Vérifiez les logs d'erreur dans la console

**Informations utiles à inclure :**
- Description du problème
- Étapes pour reproduire
- Format de fichier concerné
- Système d'exploitation et version Python

## 🎨 Captures d'écran

### Interface principale - Mode clair
![Interface claire](screenshots/interface-light.png)

### Interface principale - Mode sombre  
![Interface sombre](screenshots/interface-dark.png)

### Historique des conversions
![Historique](screenshots/history.png)

### Configuration des paramètres
![Configuration](screenshots/settings.png)

## 🚀 Roadmap et Mises à jour

### ✅ Version 1.0 (Actuelle)
- ✅ Support étendu de formats (EPUB, ODT, archives, audio/vidéo)
- ✅ Interface graphique avec mode sombre
- ✅ Historique des conversions avec base SQLite
- ✅ Interface en ligne de commande complète  
- ✅ Configuration avancée des paramètres de qualité
- ✅ Conversion par lots optimisée

### 🔮 Version 1.1 (Prochaine)
- [ ] Plugin system pour nouveaux formats
- [ ] Interface web optionnelle
- [ ] API REST pour intégration
- [ ] Reconnaissance OCR avancée
- [ ] Optimisation automatique des images

### 🌟 Version 2.0 (Future)
- [ ] Intelligence artificielle pour optimisation
- [ ] Synchronisation cloud
- [ ] Traitement en parallèle multi-thread
- [ ] Interface mobile companion

---

**PtitConvert** - Convertisseur de fichiers moderne et polyvalent 🚀
