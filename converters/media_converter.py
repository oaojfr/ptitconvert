"""
Convertisseur audio/vidéo pour PtitConvert
Gère la conversion de fichiers multimédia
"""

import os
from pathlib import Path
try:
    from moviepy.editor import VideoFileClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

class MediaConverter:
    """Convertisseur pour les fichiers audio et vidéo"""
    
    AUDIO_FORMATS = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
    VIDEO_FORMATS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
    
    def __init__(self):
        """Initialiser le convertisseur multimédia"""
        pass
        
    def convert_audio(self, input_path, output_dir, output_format, quality='medium'):
        """
        Convertir un fichier audio
        
        Args:
            input_path (str): Chemin du fichier audio source
            output_dir (str): Répertoire de sortie
            output_format (str): Format de sortie ('mp3', 'wav', 'flac', etc.)
            quality (str): Qualité ('low', 'medium', 'high')
            
        Returns:
            bool: True si la conversion a réussi
        """
        if not PYDUB_AVAILABLE:
            print("pydub n'est pas installé pour la conversion audio")
            return False
            
        try:
            input_path = Path(input_path)
            output_format = output_format.lower()
            
            # Créer le nom de fichier de sortie
            output_name = f"{input_path.stem}.{output_format}"
            output_path = Path(output_dir) / output_name
            
            # Charger l'audio
            audio = AudioSegment.from_file(str(input_path))
            
            # Configurer la qualité
            export_params = {}
            if output_format == 'mp3':
                if quality == 'low':
                    export_params['bitrate'] = '128k'
                elif quality == 'medium':
                    export_params['bitrate'] = '192k'
                elif quality == 'high':
                    export_params['bitrate'] = '320k'
                    
            elif output_format == 'wav':
                if quality == 'low':
                    export_params['parameters'] = ['-ar', '22050']
                elif quality == 'medium':
                    export_params['parameters'] = ['-ar', '44100']
                elif quality == 'high':
                    export_params['parameters'] = ['-ar', '48000']
                    
            # Exporter
            audio.export(str(output_path), format=output_format, **export_params)
            
            print(f"Audio converti: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la conversion audio: {e}")
            return False
            
    def convert_video(self, input_path, output_dir, output_format, quality='medium'):
        """
        Convertir un fichier vidéo
        
        Args:
            input_path (str): Chemin du fichier vidéo source
            output_dir (str): Répertoire de sortie
            output_format (str): Format de sortie ('mp4', 'avi', 'mkv', etc.)
            quality (str): Qualité ('low', 'medium', 'high')
            
        Returns:
            bool: True si la conversion a réussi
        """
        if not MOVIEPY_AVAILABLE:
            print("moviepy n'est pas installé pour la conversion vidéo")
            return False
            
        try:
            input_path = Path(input_path)
            output_format = output_format.lower()
            
            # Créer le nom de fichier de sortie
            output_name = f"{input_path.stem}.{output_format}"
            output_path = Path(output_dir) / output_name
            
            # Charger la vidéo
            video = VideoFileClip(str(input_path))
            
            # Configurer la qualité
            codec = 'libx264'
            audio_codec = 'aac'
            
            if quality == 'low':
                bitrate = '500k'
                audio_bitrate = '128k'
            elif quality == 'medium':
                bitrate = '1500k'
                audio_bitrate = '192k'
            elif quality == 'high':
                bitrate = '3000k'
                audio_bitrate = '320k'
                
            # Exporter
            video.write_videofile(
                str(output_path),
                codec=codec,
                audio_codec=audio_codec,
                bitrate=bitrate,
                audio_bitrate=audio_bitrate,
                verbose=False,
                logger=None
            )
            
            # Libérer la mémoire
            video.close()
            
            print(f"Vidéo convertie: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la conversion vidéo: {e}")
            return False
            
    def extract_audio_from_video(self, video_path, output_dir, audio_format='mp3'):
        """
        Extraire l'audio d'une vidéo
        
        Args:
            video_path (str): Chemin du fichier vidéo
            output_dir (str): Répertoire de sortie
            audio_format (str): Format audio de sortie
            
        Returns:
            bool: True si l'extraction a réussi
        """
        if not MOVIEPY_AVAILABLE:
            print("moviepy n'est pas installé pour l'extraction audio")
            return False
            
        try:
            video_path = Path(video_path)
            
            # Créer le nom de fichier de sortie
            output_name = f"{video_path.stem}.{audio_format}"
            output_path = Path(output_dir) / output_name
            
            # Charger la vidéo et extraire l'audio
            video = VideoFileClip(str(video_path))
            audio = video.audio
            
            if audio is None:
                print("Aucun audio trouvé dans la vidéo")
                video.close()
                return False
                
            # Exporter l'audio
            audio.write_audiofile(str(output_path), verbose=False, logger=None)
            
            # Libérer la mémoire
            audio.close()
            video.close()
            
            print(f"Audio extrait: {video_path} -> {output_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'extraction audio: {e}")
            return False
            
    def get_media_info(self, media_path):
        """
        Obtenir les informations d'un fichier multimédia
        
        Args:
            media_path (str): Chemin du fichier multimédia
            
        Returns:
            dict: Informations sur le fichier
        """
        try:
            media_path = Path(media_path)
            file_ext = media_path.suffix.lower()
            
            info = {
                'file_size': media_path.stat().st_size,
                'format': file_ext[1:].upper(),
                'type': 'unknown'
            }
            
            if file_ext in self.AUDIO_FORMATS:
                info['type'] = 'audio'
                if PYDUB_AVAILABLE:
                    try:
                        audio = AudioSegment.from_file(str(media_path))
                        info['duration'] = len(audio) / 1000  # en secondes
                        info['channels'] = audio.channels
                        info['frame_rate'] = audio.frame_rate
                    except Exception:
                        pass
                        
            elif file_ext in self.VIDEO_FORMATS:
                info['type'] = 'video'
                if MOVIEPY_AVAILABLE:
                    try:
                        video = VideoFileClip(str(media_path))
                        info['duration'] = video.duration
                        info['fps'] = video.fps
                        info['size'] = video.size
                        info['has_audio'] = video.audio is not None
                        video.close()
                    except Exception:
                        pass
                        
            return info
            
        except Exception as e:
            print(f"Erreur lors de la lecture des informations: {e}")
            return None
            
    def convert(self, input_path, output_dir, output_format, quality='medium'):
        """
        Convertir un fichier multimédia (point d'entrée général)
        
        Args:
            input_path (str): Chemin du fichier source
            output_dir (str): Répertoire de sortie  
            output_format (str): Format de sortie
            quality (str): Qualité de conversion
            
        Returns:
            bool: True si la conversion a réussi
        """
        try:
            input_path = Path(input_path)
            file_ext = input_path.suffix.lower()
            output_format = output_format.lower()
            
            # Déterminer le type de conversion
            if file_ext in self.AUDIO_FORMATS:
                if output_format in ['mp3', 'wav', 'flac', 'aac', 'ogg']:
                    return self.convert_audio(input_path, output_dir, output_format, quality)
                else:
                    print(f"Format de sortie audio non supporté: {output_format}")
                    return False
                    
            elif file_ext in self.VIDEO_FORMATS:
                if output_format in ['mp4', 'avi', 'mkv', 'mov', 'webm']:
                    return self.convert_video(input_path, output_dir, output_format, quality)
                elif output_format in ['mp3', 'wav', 'flac']:
                    # Extraction audio depuis vidéo
                    return self.extract_audio_from_video(input_path, output_dir, output_format)
                else:
                    print(f"Format de sortie vidéo non supporté: {output_format}")
                    return False
                    
            else:
                print(f"Format de fichier multimédia non supporté: {file_ext}")
                return False
                
        except Exception as e:
            print(f"Erreur lors de la conversion multimédia: {e}")
            return False
            
    def get_supported_formats(self):
        """Retourner les formats supportés selon les bibliothèques disponibles"""
        formats = {
            'audio_input': [],
            'audio_output': [],
            'video_input': [],
            'video_output': []
        }
        
        if PYDUB_AVAILABLE:
            formats['audio_input'] = list(self.AUDIO_FORMATS)
            formats['audio_output'] = ['mp3', 'wav', 'flac', 'aac', 'ogg']
            
        if MOVIEPY_AVAILABLE:
            formats['video_input'] = list(self.VIDEO_FORMATS)
            formats['video_output'] = ['mp4', 'avi', 'mkv', 'mov', 'webm']
            
        return formats
