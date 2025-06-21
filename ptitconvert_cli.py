#!/usr/bin/env python3
"""
Interface en ligne de commande pour PtitConvert
Permet l'utilisation du convertisseur via terminal
"""

import sys
import os
from pathlib import Path
import argparse
try:
    import click
    from colorama import init, Fore, Style
    CLICK_AVAILABLE = True
    COLORAMA_AVAILABLE = True
    init()  # Initialiser colorama
except ImportError:
    CLICK_AVAILABLE = False
    COLORAMA_AVAILABLE = False

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converters.image_converter import ImageConverter
from converters.document_converter import DocumentConverter
from converters.spreadsheet_converter import SpreadsheetConverter
from converters.advanced_document_converter import AdvancedDocumentConverter
from converters.archive_converter import ArchiveConverter
from converters.media_converter import MediaConverter
from utils.validators import FileValidator

class PtitConvertCLI:
    """Interface en ligne de commande pour PtitConvert"""
    
    def __init__(self):
        """Initialiser l'interface CLI"""
        self.image_converter = ImageConverter()
        self.document_converter = DocumentConverter()
        self.spreadsheet_converter = SpreadsheetConverter()
        self.advanced_doc_converter = AdvancedDocumentConverter()
        self.archive_converter = ArchiveConverter()
        self.media_converter = MediaConverter()
        self.validator = FileValidator()
        
    def print_colored(self, text, color=None):
        """Afficher du texte coloré si colorama est disponible"""
        if COLORAMA_AVAILABLE and color:
            print(f"{color}{text}{Style.RESET_ALL}")
        else:
            print(text)
            
    def print_success(self, text):
        """Afficher un message de succès"""
        if COLORAMA_AVAILABLE:
            self.print_colored(f"✅ {text}", Fore.GREEN)
        else:
            print(f"✅ {text}")
            
    def print_error(self, text):
        """Afficher un message d'erreur"""
        if COLORAMA_AVAILABLE:
            self.print_colored(f"❌ {text}", Fore.RED)
        else:
            print(f"❌ {text}")
            
    def print_warning(self, text):
        """Afficher un avertissement"""
        if COLORAMA_AVAILABLE:
            self.print_colored(f"⚠️  {text}", Fore.YELLOW)
        else:
            print(f"⚠️  {text}")
            
    def print_info(self, text):
        """Afficher une information"""
        if COLORAMA_AVAILABLE:
            self.print_colored(f"ℹ️  {text}", Fore.CYAN)
        else:
            print(f"ℹ️  {text}")
            
    def convert_file(self, input_path, output_dir, output_format, quality='medium'):
        """
        Convertir un fichier
        
        Args:
            input_path (str): Chemin du fichier source
            output_dir (str): Répertoire de sortie
            output_format (str): Format de sortie
            quality (str): Qualité de conversion
            
        Returns:
            bool: True si la conversion a réussi
        """
        try:
            # Valider le fichier d'entrée
            validation = self.validator.validate_file(input_path)
            if not validation['is_valid']:
                self.print_error(f"Fichier invalide: {', '.join(validation['errors'])}")
                return False
                
            self.print_info(f"Conversion de {Path(input_path).name} vers {output_format.upper()}")
            
            # Créer le répertoire de sortie
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Déterminer le convertisseur approprié
            file_ext = Path(input_path).suffix.lower()
            category = validation['category']
            
            success = False
            
            if category == 'images':
                success = self.image_converter.convert(input_path, output_dir, output_format)
            elif category == 'documents':
                if file_ext in ['.pdf', '.docx', '.txt']:
                    success = self.document_converter.convert(input_path, output_dir, output_format)
                else:
                    success = self.advanced_doc_converter.convert(input_path, output_dir, output_format)
            elif category == 'spreadsheets':
                success = self.spreadsheet_converter.convert(input_path, output_dir, output_format)
            elif file_ext in ArchiveConverter.SUPPORTED_FORMATS:
                if output_format == 'extract':
                    success = self.archive_converter.extract_archive(input_path, output_dir)
                else:
                    self.print_error("Les archives ne peuvent être que extraites")
                    return False
            elif file_ext in (MediaConverter.AUDIO_FORMATS | MediaConverter.VIDEO_FORMATS):
                success = self.media_converter.convert(input_path, output_dir, output_format, quality)
            else:
                self.print_error(f"Type de fichier non supporté: {file_ext}")
                return False
                
            if success:
                self.print_success(f"Conversion réussie: {Path(input_path).name}")
                return True
            else:
                self.print_error(f"Échec de la conversion: {Path(input_path).name}")
                return False
                
        except Exception as e:
            self.print_error(f"Erreur lors de la conversion: {str(e)}")
            return False
            
    def batch_convert(self, input_paths, output_dir, output_format, quality='medium'):
        """
        Convertir plusieurs fichiers
        
        Args:
            input_paths (list): Liste des chemins de fichiers
            output_dir (str): Répertoire de sortie
            output_format (str): Format de sortie
            quality (str): Qualité de conversion
            
        Returns:
            dict: Statistiques de conversion
        """
        stats = {'success': 0, 'failed': 0, 'total': len(input_paths)}
        
        self.print_info(f"Conversion par lots: {stats['total']} fichier(s)")
        
        for i, input_path in enumerate(input_paths, 1):
            self.print_info(f"[{i}/{stats['total']}] Traitement de {Path(input_path).name}")
            
            if self.convert_file(input_path, output_dir, output_format, quality):
                stats['success'] += 1
            else:
                stats['failed'] += 1
                
        # Afficher les statistiques
        self.print_info(f"Conversion terminée:")
        self.print_success(f"  Réussies: {stats['success']}")
        if stats['failed'] > 0:
            self.print_error(f"  Échouées: {stats['failed']}")
            
        return stats
        
    def list_formats(self):
        """Afficher les formats supportés"""
        self.print_info("Formats supportés par PtitConvert:")
        
        print("\n📷 IMAGES:")
        print("  Entrée: PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP")
        print("  Sortie: PNG, JPG, JPEG, BMP, GIF, TIFF, PDF")
        
        print("\n📄 DOCUMENTS:")
        print("  Entrée: PDF, DOCX, TXT, EPUB, ODT, RTF")
        print("  Sortie: PDF, DOCX, TXT, EPUB, ODT")
        
        print("\n📊 FEUILLES DE CALCUL:")
        print("  Entrée: XLSX, CSV")
        print("  Sortie: XLSX, CSV, PDF")
        
        print("\n🗜️  ARCHIVES:")
        print("  Entrée: ZIP, TAR, TAR.GZ, TAR.BZ2, RAR, 7Z")
        print("  Sortie: extraction uniquement")
        
        print("\n🎵 AUDIO:")
        print("  Entrée: MP3, WAV, FLAC, AAC, OGG, M4A")
        print("  Sortie: MP3, WAV, FLAC, AAC, OGG")
        
        print("\n🎬 VIDÉO:")
        print("  Entrée: MP4, AVI, MKV, MOV, WMV, FLV, WEBM")
        print("  Sortie: MP4, AVI, MKV, MOV, WEBM, MP3 (audio)")

def create_argument_parser():
    """Créer le parser d'arguments"""
    parser = argparse.ArgumentParser(
        description="PtitConvert - Convertisseur de fichiers en ligne de commande",
        epilog="Exemples:\n"
               "  ptitconvert-cli convert image.png --output ./sortie --format jpg\n"
               "  ptitconvert-cli batch *.pdf --output ./sortie --format docx\n"
               "  ptitconvert-cli extract archive.zip --output ./extraits",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande convert
    convert_parser = subparsers.add_parser('convert', help='Convertir un fichier')
    convert_parser.add_argument('input', help='Fichier à convertir')
    convert_parser.add_argument('--output', '-o', required=True, help='Répertoire de sortie')
    convert_parser.add_argument('--format', '-f', required=True, help='Format de sortie')
    convert_parser.add_argument('--quality', '-q', choices=['low', 'medium', 'high'], 
                               default='medium', help='Qualité de conversion')
    
    # Commande batch
    batch_parser = subparsers.add_parser('batch', help='Conversion par lots')
    batch_parser.add_argument('inputs', nargs='+', help='Fichiers à convertir')
    batch_parser.add_argument('--output', '-o', required=True, help='Répertoire de sortie')
    batch_parser.add_argument('--format', '-f', required=True, help='Format de sortie')
    batch_parser.add_argument('--quality', '-q', choices=['low', 'medium', 'high'], 
                             default='medium', help='Qualité de conversion')
    
    # Commande extract
    extract_parser = subparsers.add_parser('extract', help='Extraire une archive')
    extract_parser.add_argument('archive', help='Archive à extraire')
    extract_parser.add_argument('--output', '-o', required=True, help='Répertoire de sortie')
    
    # Commande formats
    subparsers.add_parser('formats', help='Lister les formats supportés')
    
    return parser

def main():
    """Point d'entrée principal du CLI"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    cli = PtitConvertCLI()
    
    try:
        if args.command == 'convert':
            success = cli.convert_file(args.input, args.output, args.format, args.quality)
            return 0 if success else 1
            
        elif args.command == 'batch':
            stats = cli.batch_convert(args.inputs, args.output, args.format, args.quality)
            return 0 if stats['failed'] == 0 else 1
            
        elif args.command == 'extract':
            success = cli.archive_converter.extract_archive(args.archive, args.output)
            if success:
                cli.print_success(f"Archive extraite vers: {args.output}")
                return 0
            else:
                cli.print_error("Échec de l'extraction")
                return 1
                
        elif args.command == 'formats':
            cli.list_formats()
            return 0
            
    except KeyboardInterrupt:
        cli.print_warning("Opération interrompue par l'utilisateur")
        return 1
    except Exception as e:
        cli.print_error(f"Erreur inattendue: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
