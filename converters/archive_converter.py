"""
Convertisseur d'archives pour PtitConvert
Gère la compression et décompression de ZIP, RAR, 7Z, TAR
"""

import os
import zipfile
import tarfile
import shutil
from pathlib import Path
try:
    import rarfile
    RAR_AVAILABLE = True
except ImportError:
    RAR_AVAILABLE = False

try:
    import py7zr
    SEVENZ_AVAILABLE = True
except ImportError:
    SEVENZ_AVAILABLE = False

class ArchiveConverter:
    """Convertisseur pour les archives"""
    
    SUPPORTED_FORMATS = {'.zip', '.tar', '.tar.gz', '.tar.bz2', '.rar', '.7z'}
    
    def __init__(self):
        """Initialiser le convertisseur d'archives"""
        pass
        
    def compress_folder(self, folder_path, output_path, archive_format='zip'):
        """
        Compresser un dossier en archive
        
        Args:
            folder_path (str): Chemin du dossier à compresser
            output_path (str): Chemin de l'archive de sortie
            archive_format (str): Format d'archive ('zip', 'tar', '7z')
            
        Returns:
            bool: True si la compression a réussi
        """
        try:
            folder_path = Path(folder_path)
            output_path = Path(output_path)
            
            if not folder_path.exists() or not folder_path.is_dir():
                print(f"Le dossier {folder_path} n'existe pas")
                return False
                
            archive_format = archive_format.lower()
            
            if archive_format == 'zip':
                return self._create_zip(folder_path, output_path)
            elif archive_format.startswith('tar'):
                return self._create_tar(folder_path, output_path, archive_format)
            elif archive_format == '7z':
                return self._create_7z(folder_path, output_path)
            else:
                print(f"Format d'archive non supporté: {archive_format}")
                return False
                
        except Exception as e:
            print(f"Erreur lors de la compression: {e}")
            return False
            
    def extract_archive(self, archive_path, output_dir):
        """
        Extraire une archive
        
        Args:
            archive_path (str): Chemin de l'archive
            output_dir (str): Répertoire de destination
            
        Returns:
            bool: True si l'extraction a réussi
        """
        try:
            archive_path = Path(archive_path)
            output_dir = Path(output_dir)
            
            if not archive_path.exists():
                print(f"L'archive {archive_path} n'existe pas")
                return False
                
            # Créer le répertoire de sortie
            output_dir.mkdir(parents=True, exist_ok=True)
            
            file_ext = archive_path.suffix.lower()
            
            if file_ext == '.zip':
                return self._extract_zip(archive_path, output_dir)
            elif file_ext in ['.tar', '.gz', '.bz2'] or '.tar.' in archive_path.name:
                return self._extract_tar(archive_path, output_dir)
            elif file_ext == '.rar':
                return self._extract_rar(archive_path, output_dir)
            elif file_ext == '.7z':
                return self._extract_7z(archive_path, output_dir)
            else:
                print(f"Format d'archive non supporté: {file_ext}")
                return False
                
        except Exception as e:
            print(f"Erreur lors de l'extraction: {e}")
            return False
            
    def _create_zip(self, folder_path, output_path):
        """Créer une archive ZIP"""
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(folder_path)
                        zipf.write(file_path, arcname)
                        
            print(f"Archive ZIP créée: {output_path}")
            return True
            
        except Exception as e:
            print(f"Erreur création ZIP: {e}")
            return False
            
    def _create_tar(self, folder_path, output_path, archive_format):
        """Créer une archive TAR"""
        try:
            mode = 'w'
            if archive_format == 'tar.gz':
                mode = 'w:gz'
            elif archive_format == 'tar.bz2':
                mode = 'w:bz2'
                
            with tarfile.open(output_path, mode) as tar:
                tar.add(folder_path, arcname=folder_path.name)
                
            print(f"Archive TAR créée: {output_path}")
            return True
            
        except Exception as e:
            print(f"Erreur création TAR: {e}")
            return False
            
    def _create_7z(self, folder_path, output_path):
        """Créer une archive 7Z"""
        if not SEVENZ_AVAILABLE:
            print("py7zr n'est pas installé pour le support 7Z")
            return False
            
        try:
            with py7zr.SevenZipFile(output_path, 'w') as archive:
                archive.writeall(folder_path, folder_path.name)
                
            print(f"Archive 7Z créée: {output_path}")
            return True
            
        except Exception as e:
            print(f"Erreur création 7Z: {e}")
            return False
            
    def _extract_zip(self, archive_path, output_dir):
        """Extraire une archive ZIP"""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(output_dir)
                
            print(f"Archive ZIP extraite vers: {output_dir}")
            return True
            
        except Exception as e:
            print(f"Erreur extraction ZIP: {e}")
            return False
            
    def _extract_tar(self, archive_path, output_dir):
        """Extraire une archive TAR"""
        try:
            with tarfile.open(archive_path, 'r:*') as tar:
                tar.extractall(output_dir)
                
            print(f"Archive TAR extraite vers: {output_dir}")
            return True
            
        except Exception as e:
            print(f"Erreur extraction TAR: {e}")
            return False
            
    def _extract_rar(self, archive_path, output_dir):
        """Extraire une archive RAR"""
        if not RAR_AVAILABLE:
            print("rarfile n'est pas installé pour le support RAR")
            return False
            
        try:
            with rarfile.RarFile(archive_path) as rf:
                rf.extractall(output_dir)
                
            print(f"Archive RAR extraite vers: {output_dir}")
            return True
            
        except Exception as e:
            print(f"Erreur extraction RAR: {e}")
            return False
            
    def _extract_7z(self, archive_path, output_dir):
        """Extraire une archive 7Z"""
        if not SEVENZ_AVAILABLE:
            print("py7zr n'est pas installé pour le support 7Z")
            return False
            
        try:
            with py7zr.SevenZipFile(archive_path, 'r') as archive:
                archive.extractall(output_dir)
                
            print(f"Archive 7Z extraite vers: {output_dir}")
            return True
            
        except Exception as e:
            print(f"Erreur extraction 7Z: {e}")
            return False
    
    def get_archive_info(self, archive_path):
        """
        Obtenir les informations d'une archive
        
        Args:
            archive_path (str): Chemin de l'archive
            
        Returns:
            dict: Informations sur l'archive
        """
        try:
            archive_path = Path(archive_path)
            file_ext = archive_path.suffix.lower()
            
            info = {
                'file_size': archive_path.stat().st_size,
                'format': file_ext[1:].upper(),
                'files': []
            }
            
            if file_ext == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    info['files'] = zipf.namelist()
                    info['file_count'] = len(info['files'])
                    
            elif file_ext in ['.tar', '.gz', '.bz2'] or '.tar.' in archive_path.name:
                with tarfile.open(archive_path, 'r:*') as tar:
                    info['files'] = tar.getnames()
                    info['file_count'] = len(info['files'])
                    
            elif file_ext == '.rar' and RAR_AVAILABLE:
                with rarfile.RarFile(archive_path) as rf:
                    info['files'] = rf.namelist()
                    info['file_count'] = len(info['files'])
                    
            elif file_ext == '.7z' and SEVENZ_AVAILABLE:
                with py7zr.SevenZipFile(archive_path, mode="r") as archive:
                    info['files'] = archive.getnames()
                    info['file_count'] = len(info['files'])
                    
            return info
            
        except Exception as e:
            print(f"Erreur lors de la lecture des informations: {e}")
            return None
            
    def get_supported_formats(self):
        """Retourner les formats supportés selon les bibliothèques disponibles"""
        formats = ['zip', 'tar', 'tar.gz', 'tar.bz2']  # Formats toujours supportés
        
        if RAR_AVAILABLE:
            formats.append('rar')
            
        if SEVENZ_AVAILABLE:
            formats.append('7z')
            
        return formats
    
    def convert(self, input_file, output_dir, output_format):
        """
        Convertir une archive vers un autre format ou extraire/compresser
        
        Args:
            input_file (str): Chemin du fichier d'entrée
            output_dir (str): Répertoire de sortie
            output_format (str): Format de sortie ('zip', 'tar', '7z', 'extract')
            
        Returns:
            bool: True si la conversion a réussi
        """
        try:
            input_path = Path(input_file)
            output_dir = Path(output_dir)
            
            # Si le format de sortie est 'extract', extraire l'archive
            if output_format.lower() == 'extract':
                extract_dir = output_dir / input_path.stem
                return self.extract_archive(input_path, extract_dir)
            
            # Sinon, convertir vers un autre format d'archive
            # D'abord extraire dans un dossier temporaire
            temp_dir = output_dir / f"temp_{input_path.stem}"
            if not self.extract_archive(input_path, temp_dir):
                return False
            
            # Ensuite recompresser au nouveau format
            output_name = f"{input_path.stem}.{output_format.lower()}"
            output_path = output_dir / output_name
            
            success = self.compress_folder(temp_dir, output_path, output_format)
            
            # Nettoyer le dossier temporaire
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Erreur lors du nettoyage: {e}")
            
            return success
            
        except Exception as e:
            print(f"Erreur lors de la conversion: {e}")
            return False
