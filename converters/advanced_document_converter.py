"""
Convertisseur de nouveaux formats pour PtitConvert
Gère EPUB, ODT, RTF et autres formats avancés
"""

import os
from pathlib import Path
try:
    import ebooklib
    from ebooklib import epub
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False

try:
    from odf.opendocument import OpenDocumentText
    from odf.text import P
    from odf import text, teletype
    ODT_AVAILABLE = True
except ImportError:
    ODT_AVAILABLE = False

from docx import Document
import zipfile
import xml.etree.ElementTree as ET

class AdvancedDocumentConverter:
    """Convertisseur pour les formats de documents avancés"""
    
    SUPPORTED_INPUT_FORMATS = {'.epub', '.odt', '.rtf'}
    SUPPORTED_OUTPUT_FORMATS = {'pdf', 'docx', 'txt', 'epub', 'odt'}
    
    def __init__(self):
        """Initialiser le convertisseur de documents avancés"""
        pass
        
    def convert(self, input_path, output_dir, output_format):
        """
        Convertir un document vers le format spécifié
        
        Args:
            input_path (str): Chemin du fichier d'entrée
            output_dir (str): Répertoire de sortie
            output_format (str): Format de sortie
            
        Returns:
            bool: True si la conversion a réussi
        """
        try:
            input_path = Path(input_path)
            output_format = output_format.lower()
            
            # Vérifier les formats
            if input_path.suffix.lower() not in self.SUPPORTED_INPUT_FORMATS:
                print(f"Format d'entrée non supporté: {input_path.suffix}")
                return False
                
            if output_format not in self.SUPPORTED_OUTPUT_FORMATS:
                print(f"Format de sortie non supporté: {output_format}")
                return False
                
            # Créer le nom de fichier de sortie
            output_name = f"{input_path.stem}.{output_format}"
            output_path = Path(output_dir) / output_name
            
            # Extraire le texte du document source
            text_content = self._extract_text(input_path)
            if text_content is None:
                return False
                
            # Convertir selon le format de sortie
            if output_format == 'txt':
                return self._create_txt(text_content, output_path)
            elif output_format == 'docx':
                return self._create_docx(text_content, output_path)
            elif output_format == 'epub':
                return self._create_epub(text_content, output_path, input_path.stem)
            elif output_format == 'odt':
                return self._create_odt(text_content, output_path)
            else:
                return False
                
        except Exception as e:
            print(f"Erreur lors de la conversion: {e}")
            return False
            
    def _extract_text(self, input_path):
        """Extraire le texte selon le format d'entrée"""
        file_ext = input_path.suffix.lower()
        
        if file_ext == '.epub':
            return self._extract_epub_text(input_path)
        elif file_ext == '.odt':
            return self._extract_odt_text(input_path)
        elif file_ext == '.rtf':
            return self._extract_rtf_text(input_path)
        else:
            return None
            
    def _extract_epub_text(self, epub_path):
        """Extraire le texte d'un fichier EPUB"""
        if not EPUB_AVAILABLE:
            print("ebooklib n'est pas installé pour le support EPUB")
            return None
            
        try:
            book = epub.read_epub(str(epub_path))
            text_content = []
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    content = item.get_content().decode('utf-8')
                    # Extraire le texte du HTML
                    import re
                    text = re.sub('<[^<]+?>', '', content)
                    text = text.strip()
                    if text:
                        text_content.append(text)
                        
            return '\n\n'.join(text_content)
            
        except Exception as e:
            print(f"Erreur lors de l'extraction EPUB: {e}")
            return None
            
    def _extract_odt_text(self, odt_path):
        """Extraire le texte d'un fichier ODT"""
        try:
            # ODT est un ZIP contenant du XML
            with zipfile.ZipFile(odt_path, 'r') as zip_file:
                content_xml = zip_file.read('content.xml')
                
            # Parser le XML
            root = ET.fromstring(content_xml)
            
            # Extraire tout le texte
            text_content = []
            for elem in root.iter():
                if elem.text:
                    text_content.append(elem.text.strip())
                    
            return '\n'.join([t for t in text_content if t])
            
        except Exception as e:
            print(f"Erreur lors de l'extraction ODT: {e}")
            return None
            
    def _extract_rtf_text(self, rtf_path):
        """Extraire le texte d'un fichier RTF (version basique)"""
        try:
            with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                
            # Supprimer les codes RTF basiques
            import re
            # Supprimer les commandes RTF
            text = re.sub(r'\\[a-z]+\d*\s?', '', content)
            text = re.sub(r'[{}]', '', text)
            text = re.sub(r'\\\*.*?;', '', text)
            
            return text.strip()
            
        except Exception as e:
            print(f"Erreur lors de l'extraction RTF: {e}")
            return None
            
    def _create_txt(self, text_content, output_path):
        """Créer un fichier TXT"""
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(text_content)
            print(f"TXT créé: {output_path}")
            return True
        except Exception as e:
            print(f"Erreur création TXT: {e}")
            return False
            
    def _create_docx(self, text_content, output_path):
        """Créer un document Word"""
        try:
            doc = Document()
            
            paragraphs = text_content.split('\n\n')
            for para_text in paragraphs:
                if para_text.strip():
                    doc.add_paragraph(para_text)
                    
            doc.save(str(output_path))
            print(f"DOCX créé: {output_path}")
            return True
        except Exception as e:
            print(f"Erreur création DOCX: {e}")
            return False
            
    def _create_epub(self, text_content, output_path, title):
        """Créer un fichier EPUB"""
        if not EPUB_AVAILABLE:
            print("ebooklib n'est pas installé pour créer des EPUB")
            return False
            
        try:
            book = epub.EpubBook()
            
            # Métadonnées
            book.set_identifier('id123456')
            book.set_title(title)
            book.set_language('fr')
            book.add_author('PtitConvert')
            
            # Créer un chapitre
            chap = epub.EpubHtml(title='Chapitre 1', file_name='chap_01.xhtml', lang='fr')
            
            # Convertir le texte en HTML simple
            html_content = '<h1>Contenu</h1>'
            paragraphs = text_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    html_content += f'<p>{para}</p>'
                    
            chap.content = html_content
            
            # Ajouter le chapitre au livre
            book.add_item(chap)
            
            # Table des matières
            book.toc = (epub.Link("chap_01.xhtml", "Chapitre 1", "intro"),)
            
            # Navigation
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # Style CSS basique
            style = 'body { font-family: serif; }'
            nav_css = epub.EpubItem(uid="nav", file_name="style/nav.css", media_type="text/css", content=style)
            book.add_item(nav_css)
            
            # Structure
            book.spine = ['nav', chap]
            
            # Écrire le fichier
            epub.write_epub(str(output_path), book, {})
            
            print(f"EPUB créé: {output_path}")
            return True
            
        except Exception as e:
            print(f"Erreur création EPUB: {e}")
            return False
            
    def _create_odt(self, text_content, output_path):
        """Créer un document ODT"""
        if not ODT_AVAILABLE:
            print("odfpy n'est pas installé pour créer des ODT")
            return False
            
        try:
            doc = OpenDocumentText()
            
            paragraphs = text_content.split('\n\n')
            for para_text in paragraphs:
                if para_text.strip():
                    p = P()
                    p.addText(para_text)
                    doc.text.addElement(p)
                    
            doc.save(str(output_path))
            print(f"ODT créé: {output_path}")
            return True
            
        except Exception as e:
            print(f"Erreur création ODT: {e}")
            return False
            
    def get_supported_formats(self):
        """Retourner les formats supportés selon les bibliothèques disponibles"""
        formats = {
            'input': ['.rtf'],  # RTF toujours supporté
            'output': ['txt', 'docx']  # Formats de base toujours supportés
        }
        
        if EPUB_AVAILABLE:
            formats['input'].append('.epub')
            formats['output'].append('epub')
            
        if ODT_AVAILABLE:
            formats['input'].append('.odt')
            formats['output'].append('odt')
            
        return formats
