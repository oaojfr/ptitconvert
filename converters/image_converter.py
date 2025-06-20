"""
Convertisseur d'images pour PtitConvert
Gère la conversion entre différents formats d'images
"""

from PIL import Image
import img2pdf
import os
from pathlib import Path

class ImageConverter:
    """Convertisseur pour les fichiers images"""
    
    SUPPORTED_INPUT_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
    SUPPORTED_OUTPUT_FORMATS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff', 'pdf'}
    
    def __init__(self):
        """Initialiser le convertisseur d'images"""
        pass
        
    def convert(self, input_path, output_dir, output_format):
        """
        Convertir une image vers le format spécifié
        
        Args:
            input_path (str): Chemin du fichier d'entrée
            output_dir (str): Répertoire de sortie
            output_format (str): Format de sortie ('png', 'jpg', 'pdf', etc.)
            
        Returns:
            bool: True si la conversion a réussi, False sinon
        """
        try:
            input_path = Path(input_path)
            output_format = output_format.lower()
            
            # Vérifier que le format d'entrée est supporté
            if input_path.suffix.lower() not in self.SUPPORTED_INPUT_FORMATS:
                print(f"Format d'entrée non supporté: {input_path.suffix}")
                return False
                
            # Vérifier que le format de sortie est supporté
            if output_format not in self.SUPPORTED_OUTPUT_FORMATS:
                print(f"Format de sortie non supporté: {output_format}")
                return False
                
            # Créer le nom de fichier de sortie
            output_name = f"{input_path.stem}.{output_format}"
            output_path = Path(output_dir) / output_name
            
            # Cas spécial pour la conversion en PDF
            if output_format == 'pdf':
                return self._convert_to_pdf(input_path, output_path)
            else:
                return self._convert_image(input_path, output_path, output_format)
                
        except Exception as e:
            print(f"Erreur lors de la conversion d'image: {e}")
            return False
            
    def _convert_image(self, input_path, output_path, output_format):
        """
        Convertir une image vers un autre format d'image
        
        Args:
            input_path (Path): Chemin du fichier d'entrée
            output_path (Path): Chemin du fichier de sortie
            output_format (str): Format de sortie
            
        Returns:
            bool: True si la conversion a réussi
        """
        try:
            with Image.open(input_path) as img:
                # Gestion spéciale pour JPEG (pas de transparence)
                if output_format in ['jpg', 'jpeg']:
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Créer un fond blanc pour remplacer la transparence
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    else:
                        img = img.convert('RGB')
                        
                # Optimiser la qualité pour JPEG
                save_kwargs = {}
                if output_format in ['jpg', 'jpeg']:
                    save_kwargs['quality'] = 95
                    save_kwargs['optimize'] = True
                    
                img.save(output_path, format='JPEG' if output_format.lower() in ['jpg', 'jpeg'] else output_format.upper(), **save_kwargs)
                
            print(f"Image convertie: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la conversion d'image: {e}")
            return False
            
    def _convert_to_pdf(self, input_path, output_path):
        """
        Convertir une image en PDF
        
        Args:
            input_path (Path): Chemin du fichier d'entrée
            output_path (Path): Chemin du fichier de sortie PDF
            
        Returns:
            bool: True si la conversion a réussi
        """
        try:
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(str(input_path)))
                
            print(f"Image convertie en PDF: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la conversion en PDF: {e}")
            return False
            
    def get_image_info(self, image_path):
        """
        Obtenir les informations d'une image
        
        Args:
            image_path (str): Chemin de l'image
            
        Returns:
            dict: Informations sur l'image (taille, format, mode)
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'size': img.size,
                    'format': img.format,
                    'mode': img.mode,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
        except Exception as e:
            print(f"Erreur lors de la lecture des informations d'image: {e}")
            return None
            
    def resize_image(self, input_path, output_path, size, maintain_aspect=True):
        """
        Redimensionner une image
        
        Args:
            input_path (str): Chemin du fichier d'entrée
            output_path (str): Chemin du fichier de sortie
            size (tuple): Nouvelle taille (largeur, hauteur)
            maintain_aspect (bool): Maintenir le ratio d'aspect
            
        Returns:
            bool: True si le redimensionnement a réussi
        """
        try:
            with Image.open(input_path) as img:
                if maintain_aspect:
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                else:
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    
                img.save(output_path)
                
            print(f"Image redimensionnée: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors du redimensionnement: {e}")
            return False
