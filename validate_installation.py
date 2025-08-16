#!/usr/bin/env python3
"""
Script de validation complète pour PtitConvert
Teste l'installation et toutes les fonctionnalités
"""

import sys
import os
import platform
from pathlib import Path

def print_header():
    """Afficher l'en-tête de validation"""
    print("=" * 60)
    print("🔍 VALIDATION COMPLÈTE - PTITCONVERT v1.0")
    print("=" * 60)
    print(f"🖥️  Système: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Répertoire: {os.getcwd()}")
    print("-" * 60)

def check_python_version():
    """Vérifier la version de Python"""
    print("🐍 Vérification de Python...")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requiert Python 3.8+")
        return False

def check_dependencies():
    """Vérifier les dépendances"""
    print("\n📦 Vérification des dépendances...")
    
    required_packages = [
        ('Pillow', 'PIL'),
        ('PyPDF2', 'PyPDF2'),
        ('python-docx', 'docx'),
        ('openpyxl', 'openpyxl'),
        ('reportlab', 'reportlab'),
        ('img2pdf', 'img2pdf'),
        ('pandas', 'pandas'),
        ('ebooklib', 'ebooklib'),
        ('odfpy', 'odf'),
        ('rarfile', 'rarfile'),
        ('py7zr', 'py7zr'),
        ('moviepy', 'moviepy'),
        ('pydub', 'pydub'),
        ('click', 'click'),
        ('colorama', 'colorama')
    ]
    
    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} - MANQUANT")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Dépendances manquantes: {', '.join(missing)}")
        print("   Exécutez: pip install -r requirements.txt")
        return False
    else:
        print("   🎉 Toutes les dépendances sont installées")
        return True

def check_modules():
    """Vérifier les modules de l'application"""
    print("\n🔧 Vérification des modules...")
    
    modules = [
        'gui.main_window',
        'converters.image_converter',
        'converters.document_converter',
        'converters.spreadsheet_converter',
        'converters.advanced_document_converter',
        'converters.archive_converter',
        'converters.media_converter',
        'utils.config',
        'utils.history',
        'utils.file_handler',
        'utils.validators'
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module} - {e}")
            failed.append(module)
    
    if failed:
        print(f"\n⚠️  Modules défaillants: {len(failed)}")
        return False
    else:
        print("   🎉 Tous les modules sont fonctionnels")
        return True

def check_files():
    """Vérifier la présence des fichiers essentiels"""
    print("\n📁 Vérification des fichiers...")
    
    essential_files = [
        'main.py',
        'ptitconvert_cli.py',
        'requirements.txt',
        'README.md',
        'LICENSE',
        'gui/main_window.py',
        'utils/config.py',
        'utils/history.py'
    ]
    
    missing = []
    for file_path in essential_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MANQUANT")
            missing.append(file_path)
    
    if missing:
        print(f"\n⚠️  Fichiers manquants: {len(missing)}")
        return False
    else:
        print("   🎉 Tous les fichiers essentiels sont présents")
        return True

def test_functionality():
    """Tester les fonctionnalités de base"""
    print("\n🧪 Test des fonctionnalités...")
    
    try:
        # Test config
        from utils.config import ConfigManager
        config = ConfigManager()
        config.get_config()
        print("   ✅ Configuration")
        
        # Test historique
        from utils.history import ConversionHistory
        history = ConversionHistory()
        print("   ✅ Historique")
        
        # Test CLI
        from ptitconvert_cli import PtitConvertCLI
        cli = PtitConvertCLI()
        print("   ✅ Interface CLI")
        
        # Test GUI (import seulement)
        from gui.main_window import MainWindow
        print("   ✅ Interface GUI")
        
        print("   🎉 Toutes les fonctionnalités de base marchent")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur de fonctionnalité: {e}")
        return False

def show_usage_info():
    """Afficher les informations d'utilisation"""
    print("\n" + "=" * 60)
    print("🚀 INSTALLATION VALIDÉE - PRÊT À UTILISER")
    print("=" * 60)
    print()
    print("💡 Pour démarrer:")
    print("   Interface graphique (Electron): cd electron && npm start")
    print("   Interface Tkinter (optionnelle): python main.py")
    print("   Ligne de commande:   python ptitconvert_cli.py --help")
    print()
    print("📖 Documentation:")
    print("   Guide complet:       README.md")
    print("   Démarrage rapide:    QUICK_START.md")
    print("   Historique:          CHANGELOG.md")
    print()
    print("🎨 Fonctionnalités:")
    print("   • Support 20+ formats (images, documents, archives, audio/vidéo)")
    print("   • Mode sombre/clair configurable") 
    print("   • Historique des conversions avec base SQLite")
    print("   • Interface CLI avancée avec couleurs")
    print("   • Configuration des paramètres de qualité")
    print("   • Conversion par lots optimisée")
    print()
    print("🎉 Bon conversion avec PtitConvert !")

def main():
    """Validation principale"""
    print_header()
    
    checks = [
        check_python_version,
        check_dependencies,
        check_files,
        check_modules,
        test_functionality
    ]
    
    passed = 0
    for check in checks:
        if check():
            passed += 1
    
    print(f"\n📊 RÉSULTATS: {passed}/{len(checks)} vérifications réussies")
    
    if passed == len(checks):
        show_usage_info()
        return True
    else:
        print("\n❌ ÉCHEC DE VALIDATION")
        print("   Corrigez les erreurs ci-dessus avant d'utiliser l'application.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
