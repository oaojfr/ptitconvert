"""
Gestionnaire de configuration pour PtitConvert
Gère les paramètres de qualité et les préférences utilisateur
"""

import json
import os
from pathlib import Path

class ConfigManager:
    """Gestionnaire de configuration et paramètres de qualité"""
    
    DEFAULT_CONFIG = {
        'version': '1.0',
        'ui': {
            'theme': 'light',  # 'light' ou 'dark'
            'language': 'fr',
            'auto_open_output': True,
            'remember_last_directory': True,
            'last_output_directory': str(Path.home() / 'Convertis')
        },
        'conversion': {
            'image': {
                'default_format': 'jpg',
                'jpeg_quality': 95,
                'png_compression': 6,
                'resize_large_images': False,
                'max_image_size': [4096, 4096],
                'preserve_metadata': True
            },
            'document': {
                'default_format': 'pdf',
                'pdf_compression': True,
                'preserve_formatting': True,
                'ocr_language': 'fra'
            },
            'spreadsheet': {
                'default_format': 'xlsx',
                'preserve_formulas': True,
                'include_charts': True
            },
            'audio': {
                'default_format': 'mp3',
                'bitrate': {
                    'low': '128k',
                    'medium': '192k',
                    'high': '320k'
                },
                'sample_rate': 44100,
                'normalize_audio': False
            },
            'video': {
                'default_format': 'mp4',
                'codec': 'libx264',
                'bitrate': {
                    'low': '500k',
                    'medium': '1500k',
                    'high': '3000k'
                },
                'fps': 'auto',
                'resolution': 'auto'
            },
            'archive': {
                'compression_level': 6,
                'preserve_permissions': True,
                'exclude_hidden_files': False
            }
        },
        'advanced': {
            'max_file_size_mb': 500,
            'concurrent_conversions': 1,
            'temp_directory': None,
            'keep_temp_files': False,
            'backup_original': False,
            'auto_update_check': True
        },
        'history': {
            'enabled': True,
            'max_entries': 1000,
            'auto_cleanup_days': 90
        }
    }
    
    def __init__(self, config_path=None):
        """
        Initialiser le gestionnaire de configuration
        
        Args:
            config_path (str): Chemin vers le fichier de configuration
        """
        if config_path is None:
            # Utiliser un dossier dans le répertoire utilisateur
            home_dir = Path.home()
            app_dir = home_dir / '.ptitconvert'
            app_dir.mkdir(exist_ok=True)
            config_path = app_dir / 'config.json'
            
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
    def load_config(self):
        """Charger la configuration depuis le fichier"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    
                # Fusionner avec la configuration par défaut
                config = self.DEFAULT_CONFIG.copy()
                config = self._merge_configs(config, user_config)
                return config
            else:
                # Créer le fichier de configuration par défaut
                self.save_config(self.DEFAULT_CONFIG)
                return self.DEFAULT_CONFIG.copy()
                
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            return self.DEFAULT_CONFIG.copy()
            
    def save_config(self, config=None):
        """
        Sauvegarder la configuration
        
        Args:
            config (dict): Configuration à sauvegarder (None = configuration actuelle)
        """
        try:
            if config is None:
                config = self.config
                
            # Créer le répertoire parent si nécessaire
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            
    def _merge_configs(self, base_config, user_config):
        """Fusionner la configuration utilisateur avec la configuration de base"""
        for key, value in user_config.items():
            if key in base_config:
                if isinstance(value, dict) and isinstance(base_config[key], dict):
                    base_config[key] = self._merge_configs(base_config[key], value)
                else:
                    base_config[key] = value
            else:
                base_config[key] = value
        return base_config
        
    def get(self, key_path, default=None):
        """
        Obtenir une valeur de configuration
        
        Args:
            key_path (str): Chemin vers la clé (ex: 'conversion.image.jpeg_quality')
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Valeur de configuration ou valeur par défaut
        """
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
                    
            return value
            
        except Exception:
            return default
            
    def set(self, key_path, value, save=True):
        """
        Définir une valeur de configuration
        
        Args:
            key_path (str): Chemin vers la clé
            value: Nouvelle valeur
            save (bool): Sauvegarder automatiquement
        """
        try:
            keys = key_path.split('.')
            config_ref = self.config
            
            # Naviguer jusqu'au dernier niveau
            for key in keys[:-1]:
                if key not in config_ref:
                    config_ref[key] = {}
                config_ref = config_ref[key]
                
            # Définir la valeur
            config_ref[keys[-1]] = value
            
            if save:
                self.save_config()
                
        except Exception as e:
            print(f"Erreur lors de la définition de la configuration: {e}")
            
    def get_quality_settings(self, media_type, quality_level='medium'):
        """
        Obtenir les paramètres de qualité pour un type de média
        
        Args:
            media_type (str): Type de média ('image', 'audio', 'video', etc.)
            quality_level (str): Niveau de qualité ('low', 'medium', 'high')
            
        Returns:
            dict: Paramètres de qualité
        """
        base_settings = self.get(f'conversion.{media_type}', {})
        
        if media_type == 'image':
            quality_map = {
                'low': {'jpeg_quality': 75, 'png_compression': 9},
                'medium': {'jpeg_quality': 85, 'png_compression': 6},
                'high': {'jpeg_quality': 95, 'png_compression': 3}
            }
            quality_settings = quality_map.get(quality_level, quality_map['medium'])
            return {**base_settings, **quality_settings}
            
        elif media_type == 'audio':
            bitrate = base_settings.get('bitrate', {}).get(quality_level, '192k')
            return {**base_settings, 'current_bitrate': bitrate}
            
        elif media_type == 'video':
            bitrate = base_settings.get('bitrate', {}).get(quality_level, '1500k')
            return {**base_settings, 'current_bitrate': bitrate}
            
        return base_settings
        
    def get_theme_settings(self):
        """Obtenir les paramètres de thème"""
        theme = self.get('ui.theme', 'light')
        
        if theme == 'dark':
            return {
                'bg_color': '#2b2b2b',
                'fg_color': '#ffffff',
                'button_bg': '#404040',
                'button_fg': '#ffffff',
                'entry_bg': '#404040',
                'entry_fg': '#ffffff',
                'frame_bg': '#353535'
            }
        else:  # light theme
            return {
                'bg_color': '#ffffff',
                'fg_color': '#000000',
                'button_bg': '#e1e1e1',
                'button_fg': '#000000',
                'entry_bg': '#ffffff',
                'entry_fg': '#000000',
                'frame_bg': '#f0f0f0'
            }
            
    def update_last_directory(self, directory):
        """Mettre à jour le dernier répertoire utilisé"""
        if self.get('ui.remember_last_directory', True):
            self.set('ui.last_output_directory', str(directory))
            
    def get_conversion_presets(self):
        """Obtenir les préréglages de conversion"""
        return {
            'web_optimized': {
                'description': 'Optimisé pour le web',
                'image': {'format': 'jpg', 'quality': 'medium', 'max_size': [1920, 1080]},
                'video': {'format': 'mp4', 'quality': 'medium', 'max_resolution': '1080p'}
            },
            'print_quality': {
                'description': 'Qualité impression',
                'image': {'format': 'png', 'quality': 'high'},
                'document': {'format': 'pdf', 'dpi': 300}
            },
            'archive_storage': {
                'description': 'Stockage archive',
                'image': {'format': 'tiff', 'quality': 'high'},
                'document': {'format': 'pdf', 'compression': False}
            },
            'mobile_friendly': {
                'description': 'Compatible mobile',
                'image': {'format': 'jpg', 'quality': 'medium', 'max_size': [800, 600]},
                'video': {'format': 'mp4', 'quality': 'low', 'max_resolution': '720p'},
                'audio': {'format': 'mp3', 'quality': 'medium'}
            }
        }
        
    def reset_to_defaults(self):
        """Réinitialiser la configuration par défaut"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        
    def export_config(self, output_path):
        """
        Exporter la configuration vers un fichier
        
        Args:
            output_path (str): Chemin du fichier de sortie
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"Configuration exportée vers: {output_path}")
        except Exception as e:
            print(f"Erreur lors de l'export de configuration: {e}")
            
    def import_config(self, input_path):
        """
        Importer la configuration depuis un fichier
        
        Args:
            input_path (str): Chemin du fichier de configuration
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                
            # Fusionner avec la configuration actuelle
            self.config = self._merge_configs(self.DEFAULT_CONFIG.copy(), imported_config)
            self.save_config()
            print(f"Configuration importée depuis: {input_path}")
            
        except Exception as e:
            print(f"Erreur lors de l'import de configuration: {e}")
            
    def validate_config(self):
        """
        Valider et corriger la configuration si nécessaire
        
        Returns:
            list: Liste des erreurs trouvées et corrigées
        """
        errors = []
        
        try:
            # Vérifier la structure de base
            for section in ['ui', 'conversion', 'advanced', 'history']:
                if section not in self.config:
                    self.config[section] = self.DEFAULT_CONFIG[section].copy()
                    errors.append(f"Section manquante '{section}' ajoutée")
                    
            # Vérifier les types de données
            if not isinstance(self.get('advanced.max_file_size_mb'), (int, float)):
                self.set('advanced.max_file_size_mb', 500, save=False)
                errors.append("Taille max de fichier corrigée")
                
            if not isinstance(self.get('conversion.image.jpeg_quality'), (int, float)):
                self.set('conversion.image.jpeg_quality', 85, save=False)
                errors.append("Qualité JPEG corrigée")
                
            # Vérifier les valeurs
            theme = self.get('ui.theme')
            if theme not in ['light', 'dark']:
                self.set('ui.theme', 'light', save=False)
                errors.append("Thème invalide corrigé")
                
            if errors:
                self.save_config()
                
        except Exception as e:
            errors.append(f"Erreur lors de la validation: {e}")
            
        return errors
    
    def get_config(self):
        """
        Obtenir la configuration actuelle
        
        Returns:
            dict: Configuration actuelle
        """
        return self.config.copy()
    
    def update_config(self, key_path, value):
        """
        Mettre à jour une valeur de configuration
        
        Args:
            key_path (str): Chemin vers la clé (ex: 'ui.theme')
            value: Nouvelle valeur
        """
        try:
            keys = key_path.split('.')
            current = self.config
            
            # Naviguer jusqu'à l'avant-dernier niveau
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Mettre à jour la valeur finale
            current[keys[-1]] = value
            
            # Sauvegarder
            self.save_config()
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la configuration: {e}")
