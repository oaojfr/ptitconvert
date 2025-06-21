"""
Gestionnaire d'historique pour PtitConvert
Stocke et gère l'historique des conversions
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import os

class ConversionHistory:
    """Gestionnaire de l'historique des conversions"""
    
    def __init__(self, db_path=None):
        """
        Initialiser le gestionnaire d'historique
        
        Args:
            db_path (str): Chemin vers la base de données SQLite
        """
        if db_path is None:
            # Utiliser un dossier dans le répertoire utilisateur
            home_dir = Path.home()
            app_dir = home_dir / '.ptitconvert'
            app_dir.mkdir(exist_ok=True)
            db_path = app_dir / 'history.db'
            
        self.db_path = str(db_path)
        self.init_database()
        
    def init_database(self):
        """Initialiser la base de données"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Créer la table d'historique
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversion_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        input_file TEXT NOT NULL,
                        input_format TEXT NOT NULL,
                        output_file TEXT NOT NULL,
                        output_format TEXT NOT NULL,
                        file_size INTEGER,
                        conversion_time REAL,
                        success BOOLEAN NOT NULL,
                        error_message TEXT,
                        quality TEXT DEFAULT 'medium'
                    )
                ''')
                
                # Créer la table des statistiques
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversion_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        total_conversions INTEGER DEFAULT 0,
                        successful_conversions INTEGER DEFAULT 0,
                        failed_conversions INTEGER DEFAULT 0,
                        total_size_processed INTEGER DEFAULT 0
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la base de données: {e}")
            
    def add_conversion(self, input_file, input_format, output_file, output_format, 
                      file_size=0, conversion_time=0, success=True, error_message=None, quality='medium'):
        """
        Ajouter une conversion à l'historique
        
        Args:
            input_file (str): Chemin du fichier source
            input_format (str): Format du fichier source
            output_file (str): Chemin du fichier de sortie
            output_format (str): Format de sortie
            file_size (int): Taille du fichier en octets
            conversion_time (float): Temps de conversion en secondes
            success (bool): Succès de la conversion
            error_message (str): Message d'erreur si échec
            quality (str): Qualité de conversion
        """
        try:
            timestamp = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO conversion_history 
                    (timestamp, input_file, input_format, output_file, output_format,
                     file_size, conversion_time, success, error_message, quality)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (timestamp, input_file, input_format, output_file, output_format,
                      file_size, conversion_time, success, error_message, quality))
                
                conn.commit()
                
            # Mettre à jour les statistiques
            self.update_daily_stats(success, file_size)
            
        except Exception as e:
            print(f"Erreur lors de l'ajout à l'historique: {e}")
            
    def update_daily_stats(self, success, file_size):
        """Mettre à jour les statistiques quotidiennes"""
        try:
            today = datetime.now().date().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Vérifier si une entrée existe déjà pour aujourd'hui
                cursor.execute('SELECT id FROM conversion_stats WHERE date = ?', (today,))
                existing = cursor.fetchone()
                
                if existing:
                    # Mettre à jour les statistiques existantes
                    cursor.execute('''
                        UPDATE conversion_stats 
                        SET total_conversions = total_conversions + 1,
                            successful_conversions = successful_conversions + ?,
                            failed_conversions = failed_conversions + ?,
                            total_size_processed = total_size_processed + ?
                        WHERE date = ?
                    ''', (1 if success else 0, 0 if success else 1, file_size, today))
                else:
                    # Créer une nouvelle entrée
                    cursor.execute('''
                        INSERT INTO conversion_stats 
                        (date, total_conversions, successful_conversions, failed_conversions, total_size_processed)
                        VALUES (?, 1, ?, ?, ?)
                    ''', (today, 1 if success else 0, 0 if success else 1, file_size))
                
                conn.commit()
                
        except Exception as e:
            print(f"Erreur lors de la mise à jour des statistiques: {e}")
            
    def get_recent_conversions(self, limit=50):
        """
        Obtenir les conversions récentes
        
        Args:
            limit (int): Nombre maximum de conversions à retourner
            
        Returns:
            list: Liste des conversions récentes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT timestamp, input_file, input_format, output_file, output_format,
                           file_size, conversion_time, success, error_message, quality
                    FROM conversion_history 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                
                conversions = []
                for row in rows:
                    conversions.append({
                        'timestamp': row[0],
                        'input_file': row[1],
                        'input_format': row[2],
                        'output_file': row[3],
                        'output_format': row[4],
                        'file_size': row[5],
                        'conversion_time': row[6],
                        'success': bool(row[7]),
                        'error_message': row[8],
                        'quality': row[9]
                    })
                    
                return conversions
                
        except Exception as e:
            print(f"Erreur lors de la récupération de l'historique: {e}")
            return []
            
    def get_conversion_stats(self, days=30):
        """
        Obtenir les statistiques de conversion
        
        Args:
            days (int): Nombre de jours à inclure
            
        Returns:
            dict: Statistiques de conversion
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Statistiques globales
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed,
                        SUM(file_size) as total_size,
                        AVG(conversion_time) as avg_time
                    FROM conversion_history
                    WHERE timestamp >= datetime('now', '-{} days')
                '''.format(days))
                
                global_stats = cursor.fetchone()
                
                # Statistiques par format
                cursor.execute('''
                    SELECT output_format, COUNT(*) as count
                    FROM conversion_history
                    WHERE timestamp >= datetime('now', '-{} days')
                    GROUP BY output_format
                    ORDER BY count DESC
                '''.format(days))
                
                format_stats = cursor.fetchall()
                
                # Statistiques quotidiennes récentes
                cursor.execute('''
                    SELECT date, total_conversions, successful_conversions, failed_conversions
                    FROM conversion_stats
                    WHERE date >= date('now', '-{} days')
                    ORDER BY date DESC
                '''.format(days))
                
                daily_stats = cursor.fetchall()
                
                return {
                    'global': {
                        'total_conversions': global_stats[0] or 0,
                        'successful_conversions': global_stats[1] or 0,
                        'failed_conversions': global_stats[2] or 0,
                        'total_size_processed': global_stats[3] or 0,
                        'average_conversion_time': global_stats[4] or 0
                    },
                    'by_format': [{'format': row[0], 'count': row[1]} for row in format_stats],
                    'daily': [{'date': row[0], 'total': row[1], 'successful': row[2], 'failed': row[3]} 
                             for row in daily_stats]
                }
                
        except Exception as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            return {
                'global': {'total_conversions': 0, 'successful_conversions': 0, 
                          'failed_conversions': 0, 'total_size_processed': 0, 
                          'average_conversion_time': 0},
                'by_format': [],
                'daily': []
            }
            
    def search_conversions(self, query, limit=50):
        """
        Rechercher dans l'historique des conversions
        
        Args:
            query (str): Terme de recherche
            limit (int): Nombre maximum de résultats
            
        Returns:
            list: Liste des conversions correspondantes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT timestamp, input_file, input_format, output_file, output_format,
                           file_size, conversion_time, success, error_message, quality
                    FROM conversion_history 
                    WHERE input_file LIKE ? OR output_file LIKE ? OR input_format LIKE ? OR output_format LIKE ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', limit))
                
                rows = cursor.fetchall()
                
                conversions = []
                for row in rows:
                    conversions.append({
                        'timestamp': row[0],
                        'input_file': row[1],
                        'input_format': row[2],
                        'output_file': row[3],
                        'output_format': row[4],
                        'file_size': row[5],
                        'conversion_time': row[6],
                        'success': bool(row[7]),
                        'error_message': row[8],
                        'quality': row[9]
                    })
                    
                return conversions
                
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []
            
    def clear_history(self, older_than_days=None):
        """
        Effacer l'historique
        
        Args:
            older_than_days (int): Effacer les entrées plus anciennes que X jours (None = tout effacer)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if older_than_days is None:
                    # Effacer tout l'historique
                    cursor.execute('DELETE FROM conversion_history')
                    cursor.execute('DELETE FROM conversion_stats')
                else:
                    # Effacer les entrées anciennes
                    cursor.execute('''
                        DELETE FROM conversion_history 
                        WHERE timestamp < datetime('now', '-{} days')
                    '''.format(older_than_days))
                    
                    cursor.execute('''
                        DELETE FROM conversion_stats 
                        WHERE date < date('now', '-{} days')
                    '''.format(older_than_days))
                
                conn.commit()
                
        except Exception as e:
            print(f"Erreur lors de l'effacement de l'historique: {e}")
            
    def export_history(self, output_file, format='json'):
        """
        Exporter l'historique vers un fichier
        
        Args:
            output_file (str): Chemin du fichier de sortie
            format (str): Format d'export ('json' ou 'csv')
        """
        try:
            conversions = self.get_recent_conversions(limit=10000)  # Toutes les conversions
            
            if format.lower() == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(conversions, f, indent=2, ensure_ascii=False)
                    
            elif format.lower() == 'csv':
                import csv
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    if conversions:
                        writer = csv.DictWriter(f, fieldnames=conversions[0].keys())
                        writer.writeheader()
                        writer.writerows(conversions)
                        
            print(f"Historique exporté vers: {output_file}")
            
        except Exception as e:
            print(f"Erreur lors de l'export: {e}")
