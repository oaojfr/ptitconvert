# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-21

### ✨ Ajouté
- **Support de nouveaux formats** :
  - Documents avancés : EPUB, ODT, RTF
  - Archives : ZIP, TAR, RAR, 7Z avec conversion entre formats
  - Audio : MP3, WAV, FLAC, OGG
  - Vidéo : MP4, AVI, MKV, MOV
  - Feuilles de calcul : ODS

- **Interface graphique améliorée** :
  - Mode sombre/clair configurable
  - Menu complet avec navigation intuitive
  - Fenêtre de paramètres de qualité
  - Ouverture automatique du dossier de sortie

- **Historique des conversions** :
  - Base de données SQLite pour stockage persistant
  - Interface de consultation avec recherche
  - Export CSV de l'historique
  - Statistiques de conversions

- **Configuration avancée** :
  - Paramètres de qualité par format (JPEG, PDF, audio, etc.)
  - Préférences d'interface utilisateur
  - Sauvegarde automatique des réglages
  - Fichier de configuration JSON

- **Interface en ligne de commande** :
  - CLI complète avec `ptitconvert_cli.py`
  - Support des couleurs avec colorama
  - Mode batch pour traitement en lot
  - Options avancées avec click

- **Architecture modulaire** :
  - Convertisseurs spécialisés par type de format
  - Gestion d'erreurs robuste
  - Tests d'intégration automatisés
  - Documentation complète

### 🔧 Amélioré
- Performance de conversion par lots
- Gestion des erreurs avec messages détaillés
- Validation des fichiers d'entrée
- Interface utilisateur responsive
- Documentation et README complets

### 🛠️ Technique
- Architecture MVC respectée
- Code modulaire et maintenable
- Tests d'intégration complets
- Scripts de démarrage cross-platform
- Configuration Git et instructions Copilot

## [0.1.0] - Version initiale

### ✨ Ajouté
- Conversion d'images basiques (PNG, JPG, BMP)
- Conversion de documents simples (PDF, DOCX, TXT)
- Conversion de feuilles de calcul (XLSX, CSV)
- Interface graphique Tkinter basique
- Conversion par lots
- Scripts de démarrage Windows/Linux

---

**Légende** :
- ✨ Ajouté pour les nouvelles fonctionnalités
- 🔧 Amélioré pour les changements dans les fonctionnalités existantes
- 🐛 Corrigé pour les corrections de bugs
- 🛠️ Technique pour les changements techniques
- ⚠️ Déprécié pour les fonctionnalités bientôt supprimées
- 🗑️ Supprimé pour les fonctionnalités supprimées
