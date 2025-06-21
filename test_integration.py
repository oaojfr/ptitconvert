#!/usr/bin/env python3
"""
Script de test d'intégration pour PtitConvert
Teste toutes les nouvelles fonctionnalités
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Tester les imports de tous les modules"""
    print("🔍 Test des imports...")
    
    try:
        from converters.image_converter import ImageConverter
        from converters.document_converter import DocumentConverter
        from converters.spreadsheet_converter import SpreadsheetConverter
        from converters.advanced_document_converter import AdvancedDocumentConverter
        from converters.archive_converter import ArchiveConverter
        from converters.media_converter import MediaConverter
        from utils.config import ConfigManager
        from utils.history import ConversionHistory
        from gui.main_window import MainWindow
        print("✅ Tous les imports sont réussis")
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_config():
    """Tester le gestionnaire de configuration"""
    print("\n🔧 Test de la configuration...")
    
    try:
        from utils.config import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # Tester la lecture
        print(f"  - Version: {config.get('version', 'N/A')}")
        print(f"  - Thème: {config.get('ui', {}).get('theme', 'N/A')}")
        
        # Tester la modification
        config_manager.update_config('ui.theme', 'dark')
        print("  - Mise à jour du thème: OK")
        
        print("✅ Configuration fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        return False

def test_history():
    """Tester l'historique des conversions"""
    print("\n📊 Test de l'historique...")
    
    try:
        from utils.history import ConversionHistory
        history = ConversionHistory()
        
        # Tester l'ajout d'une entrée
        history.add_conversion(
            input_file="/test/image.jpg",
            input_format="jpg",
            output_file="/test/image.png",
            output_format="png",
            file_size=1024,
            conversion_time=0.5,
            success=True
        )
        
        # Tester la récupération
        recent = history.get_recent_conversions(limit=5)
        print(f"  - Entrées récentes trouvées: {len(recent)}")
        
        print("✅ Historique fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur d'historique: {e}")
        return False

def test_cli():
    """Tester l'interface CLI"""
    print("\n💻 Test de l'interface CLI...")
    
    try:
        from ptitconvert_cli import PtitConvertCLI
        cli = PtitConvertCLI()
        print("  - CLI initialisée avec succès")
        
        print("✅ Interface CLI fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur CLI: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 Test d'intégration PtitConvert")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_history,
        test_cli
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📈 Résultats: {passed}/{len(tests)} tests réussis")
    
    if passed == len(tests):
        print("🎉 Tous les tests sont passés ! L'application est prête.")
        return True
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les dépendances.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
