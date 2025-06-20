"""
Validateurs de fichiers pour PtitConvert
Utilitaires pour valider les fichiers et formats
"""

import os
from pathlib import Path
import mimetypes
from PIL import Image
import PyPDF2
from docx import Document
import openpyxl
import csv

class FileValidator:
    """Validateur de fichiers et formats"""
    
    # Formats supportés par catégorie
    SUPPORTED_FORMATS = {
        'images': {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'},
        'documents': {'.pdf', '.docx', '.txt'},
        'spreadsheets': {'.xlsx', '.csv'}
    }
    
    # Tailles maximales de fichiers (en octets)
    MAX_FILE_SIZES = {
        'images': 100 * 1024 * 1024,    # 100 MB
        'documents': 50 * 1024 * 1024,   # 50 MB
        'spreadsheets': 25 * 1024 * 1024  # 25 MB
    }
    
    def __init__(self):
        """Initialiser le validateur"""
        pass
        
    def is_supported_format(self, file_path):
        """
        Vérifier si le format du fichier est supporté
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            tuple: (bool, str) - (est_supporté, catégorie)
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            for category, extensions in self.SUPPORTED_FORMATS.items():
                if file_ext in extensions:
                    return True, category
                    
            return False, None
            
        except Exception:
            return False, None
            
    def validate_file(self, file_path):
        """
        Validation complète d'un fichier
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            dict: Résultat de la validation avec détails
        """
        result = {
            'is_valid': False,
            'file_exists': False,
            'is_accessible': False,
            'format_supported': False,
            'size_valid': False,
            'content_valid': False,
            'category': None,
            'file_size': 0,
            'errors': []
        }
        
        try:
            path = Path(file_path)
            
            # Vérifier l'existence du fichier
            if not path.exists():
                result['errors'].append("Le fichier n'existe pas")
                return result
            result['file_exists'] = True
            
            # Vérifier l'accessibilité
            if not os.access(path, os.R_OK):
                result['errors'].append("Le fichier n'est pas accessible en lecture")
                return result
            result['is_accessible'] = True
            
            # Vérifier le format
            is_supported, category = self.is_supported_format(file_path)
            if not is_supported:
                result['errors'].append(f"Format de fichier non supporté: {path.suffix}")
                return result
            result['format_supported'] = True
            result['category'] = category
            
            # Vérifier la taille
            file_size = path.stat().st_size
            result['file_size'] = file_size
            
            max_size = self.MAX_FILE_SIZES.get(category, 10 * 1024 * 1024)  # 10MB par défaut
            if file_size > max_size:
                result['errors'].append(f"Fichier trop volumineux: {file_size} > {max_size} octets")
                return result
            result['size_valid'] = True
            
            # Validation du contenu selon le type
            content_valid = self._validate_content(file_path, category)
            if not content_valid:
                result['errors'].append("Le contenu du fichier n'est pas valide")
                return result
            result['content_valid'] = True
            
            result['is_valid'] = True
            
        except Exception as e:
            result['errors'].append(f"Erreur lors de la validation: {str(e)}")
            
        return result
        
    def _validate_content(self, file_path, category):
        """
        Valider le contenu d'un fichier selon sa catégorie
        
        Args:
            file_path (str): Chemin du fichier
            category (str): Catégorie du fichier
            
        Returns:
            bool: True si le contenu est valide
        """
        try:
            if category == 'images':
                return self._validate_image_content(file_path)
            elif category == 'documents':
                return self._validate_document_content(file_path)
            elif category == 'spreadsheets':
                return self._validate_spreadsheet_content(file_path)
            else:
                return False
                
        except Exception as e:
            print(f"Erreur lors de la validation du contenu: {e}")
            return False
            
    def _validate_image_content(self, file_path):
        """Valider le contenu d'une image"""
        try:
            with Image.open(file_path) as img:
                # Vérifier que l'image peut être ouverte
                img.verify()
                
            # Réouvrir l'image pour vérifications supplémentaires
            with Image.open(file_path) as img:
                # Vérifier les dimensions minimales
                if img.size[0] < 1 or img.size[1] < 1:
                    return False
                    
                # Vérifier les dimensions maximales
                if img.size[0] > 50000 or img.size[1] > 50000:
                    return False
                    
            return True
            
        except Exception:
            return False
            
    def _validate_document_content(self, file_path):
        """Valider le contenu d'un document"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    # Vérifier qu'il y a au moins une page
                    if len(pdf_reader.pages) == 0:
                        return False
                        
            elif file_ext == '.docx':
                doc = Document(file_path)
                # Le document peut être vide, c'est valide
                
            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Essayer de lire au moins le début du fichier
                    file.read(100)
                    
            return True
            
        except Exception:
            return False
            
    def _validate_spreadsheet_content(self, file_path):
        """Valider le contenu d'une feuille de calcul"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.xlsx':
                workbook = openpyxl.load_workbook(file_path)
                # Vérifier qu'il y a au moins une feuille
                if len(workbook.worksheets) == 0:
                    return False
                    
            elif file_ext == '.csv':
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Essayer de lire le CSV
                    csv.reader(file)
                    
            return True
            
        except Exception:
            return False
            
    def get_file_category(self, file_path):
        """
        Obtenir la catégorie d'un fichier
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            str: Catégorie du fichier ou None
        """
        _, category = self.is_supported_format(file_path)
        return category
        
    def validate_output_format(self, input_file, output_format):
        """
        Valider si une conversion est possible
        
        Args:
            input_file (str): Fichier d'entrée
            output_format (str): Format de sortie souhaité
            
        Returns:
            bool: True si la conversion est possible
        """
        try:
            category = self.get_file_category(input_file)
            if not category:
                return False
                
            output_format = output_format.lower()
            
            # Règles de conversion par catégorie
            conversion_rules = {
                'images': {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff', 'pdf'},
                'documents': {'pdf', 'docx', 'txt'},
                'spreadsheets': {'xlsx', 'csv', 'pdf'}
            }
            
            allowed_formats = conversion_rules.get(category, set())
            return output_format in allowed_formats
            
        except Exception:
            return False
            
    def batch_validate(self, file_paths):
        """
        Validation en lot de plusieurs fichiers
        
        Args:
            file_paths (list): Liste des chemins de fichiers
            
        Returns:
            dict: Résultats de validation pour chaque fichier
        """
        results = {}
        
        for file_path in file_paths:
            results[file_path] = self.validate_file(file_path)
            
        return results
        
    def get_conversion_options(self, file_path):
        """
        Obtenir les options de conversion disponibles pour un fichier
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            list: Liste des formats de sortie possibles
        """
        try:
            category = self.get_file_category(file_path)
            if not category:
                return []
                
            conversion_options = {
                'images': ['PNG', 'JPG', 'JPEG', 'BMP', 'GIF', 'TIFF', 'PDF'],
                'documents': ['PDF', 'DOCX', 'TXT'],
                'spreadsheets': ['XLSX', 'CSV', 'PDF']
            }
            
            return conversion_options.get(category, [])
            
        except Exception:
            return []
            
    def estimate_conversion_time(self, file_path, output_format):
        """
        Estimer le temps de conversion (approximatif)
        
        Args:
            file_path (str): Chemin du fichier
            output_format (str): Format de sortie
            
        Returns:
            float: Temps estimé en secondes
        """
        try:
            file_size = Path(file_path).stat().st_size
            category = self.get_file_category(file_path)
            
            # Estimations basées sur la taille et le type
            base_times = {
                'images': 0.1,      # 0.1 seconde par MB
                'documents': 0.2,   # 0.2 seconde par MB
                'spreadsheets': 0.5  # 0.5 seconde par MB
            }
            
            # Facteurs selon le format de sortie
            format_factors = {
                'pdf': 1.5,  # Plus lent pour générer des PDF
                'docx': 1.2,
                'xlsx': 1.3
            }
            
            file_size_mb = file_size / (1024 * 1024)
            base_time = base_times.get(category, 0.2)
            format_factor = format_factors.get(output_format.lower(), 1.0)
            
            estimated_time = file_size_mb * base_time * format_factor
            
            # Minimum 0.5 seconde, maximum 60 secondes
            return max(0.5, min(60, estimated_time))
            
        except Exception:
            return 2.0  # Valeur par défaut
