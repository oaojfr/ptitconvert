"""
Gestionnaire de fichiers pour PtitConvert
Utilitaires pour la manipulation et gestion des fichiers
"""

import os
import shutil
from pathlib import Path
import hashlib
import mimetypes

class FileHandler:
    """Gestionnaire de fichiers avec utilitaires de manipulation"""
    
    def __init__(self):
        """Initialiser le gestionnaire de fichiers"""
        pass
        
    def get_file_size(self, file_path):
        """
        Obtenir la taille d'un fichier en octets
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            int: Taille du fichier en octets
        """
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return 0
            
    def get_file_size_formatted(self, file_path):
        """
        Obtenir la taille d'un fichier formatée (KB, MB, GB)
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            str: Taille formatée
        """
        size = self.get_file_size(file_path)
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
        
    def get_file_hash(self, file_path, algorithm='md5'):
        """
        Calculer le hash d'un fichier
        
        Args:
            file_path (str): Chemin du fichier
            algorithm (str): Algorithme de hash ('md5', 'sha1', 'sha256')
            
        Returns:
            str: Hash du fichier ou None en cas d'erreur
        """
        try:
            hash_algo = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_algo.update(chunk)
                    
            return hash_algo.hexdigest()
            
        except Exception as e:
            print(f"Erreur lors du calcul du hash: {e}")
            return None
            
    def get_mime_type(self, file_path):
        """
        Obtenir le type MIME d'un fichier
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            str: Type MIME du fichier
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"
        
    def is_file_accessible(self, file_path):
        """
        Vérifier si un fichier est accessible en lecture
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            bool: True si le fichier est accessible
        """
        try:
            path = Path(file_path)
            return path.exists() and path.is_file() and os.access(path, os.R_OK)
        except Exception:
            return False
            
    def create_backup(self, file_path, backup_dir=None):
        """
        Créer une sauvegarde d'un fichier
        
        Args:
            file_path (str): Chemin du fichier à sauvegarder
            backup_dir (str): Répertoire de sauvegarde (optionnel)
            
        Returns:
            str: Chemin du fichier de sauvegarde ou None en cas d'erreur
        """
        try:
            source_path = Path(file_path)
            
            if backup_dir:
                backup_path = Path(backup_dir)
            else:
                backup_path = source_path.parent / "backups"
                
            backup_path.mkdir(exist_ok=True)
            
            backup_file = backup_path / f"{source_path.stem}_backup{source_path.suffix}"
            
            # Si le fichier de backup existe déjà, ajouter un numéro
            counter = 1
            while backup_file.exists():
                backup_file = backup_path / f"{source_path.stem}_backup_{counter}{source_path.suffix}"
                counter += 1
                
            shutil.copy2(source_path, backup_file)
            
            print(f"Sauvegarde créée: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            print(f"Erreur lors de la création de la sauvegarde: {e}")
            return None
            
    def clean_filename(self, filename):
        """
        Nettoyer un nom de fichier en supprimant les caractères invalides
        
        Args:
            filename (str): Nom de fichier à nettoyer
            
        Returns:
            str: Nom de fichier nettoyé
        """
        # Caractères invalides sur Windows et Linux
        invalid_chars = '<>:"/\\|?*'
        
        cleaned = filename
        for char in invalid_chars:
            cleaned = cleaned.replace(char, '_')
            
        # Supprimer les espaces en début et fin
        cleaned = cleaned.strip()
        
        # Remplacer les espaces multiples par un seul
        while '  ' in cleaned:
            cleaned = cleaned.replace('  ', ' ')
            
        return cleaned
        
    def ensure_unique_filename(self, file_path):
        """
        S'assurer qu'un nom de fichier est unique en ajoutant un numéro si nécessaire
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            str: Chemin unique du fichier
        """
        path = Path(file_path)
        
        if not path.exists():
            return str(path)
            
        counter = 1
        while True:
            new_name = f"{path.stem}_{counter}{path.suffix}"
            new_path = path.parent / new_name
            
            if not new_path.exists():
                return str(new_path)
                
            counter += 1
            
    def copy_file_with_progress(self, source, destination, chunk_size=64*1024):
        """
        Copier un fichier avec suivi de progression
        
        Args:
            source (str): Fichier source
            destination (str): Fichier de destination
            chunk_size (int): Taille des chunks en octets
            
        Returns:
            bool: True si la copie a réussi
        """
        try:
            source_size = self.get_file_size(source)
            copied = 0
            
            with open(source, 'rb') as src, open(destination, 'wb') as dst:
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                        
                    dst.write(chunk)
                    copied += len(chunk)
                    
                    # Calculer le pourcentage de progression
                    if source_size > 0:
                        progress = (copied / source_size) * 100
                        print(f"\rCopie en cours: {progress:.1f}%", end="", flush=True)
                        
            print(f"\nCopie terminée: {destination}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la copie: {e}")
            return False
            
    def get_directory_size(self, directory_path):
        """
        Calculer la taille totale d'un répertoire
        
        Args:
            directory_path (str): Chemin du répertoire
            
        Returns:
            int: Taille totale en octets
        """
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        pass
                        
            return total_size
            
        except Exception:
            return 0
            
    def find_files_by_extension(self, directory, extension, recursive=True):
        """
        Trouver tous les fichiers avec une extension donnée
        
        Args:
            directory (str): Répertoire de recherche
            extension (str): Extension à rechercher (avec ou sans point)
            recursive (bool): Recherche récursive
            
        Returns:
            list: Liste des fichiers trouvés
        """
        if not extension.startswith('.'):
            extension = '.' + extension
            
        files = []
        directory_path = Path(directory)
        
        try:
            if recursive:
                pattern = f"**/*{extension}"
                files = list(directory_path.glob(pattern))
            else:
                pattern = f"*{extension}"
                files = list(directory_path.glob(pattern))
                
            return [str(f) for f in files if f.is_file()]
            
        except Exception as e:
            print(f"Erreur lors de la recherche de fichiers: {e}")
            return []
