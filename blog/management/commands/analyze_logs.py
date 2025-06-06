"""
Commande Django pour analyser les logs de l'application.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import os


class Command(BaseCommand):
    help = 'Analyse les fichiers de logs et génère des statistiques'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Nombre de jours à analyser (défaut: 7)'
        )
        parser.add_argument(
            '--log-type',
            choices=['error', 'general', 'debug', 'all'],
            default='all',
            help='Type de log à analyser (défaut: all)'
        )
        parser.add_argument(
            '--show-errors',
            action='store_true',
            help='Afficher le détail des erreurs'
        )
        parser.add_argument(
            '--show-requests',
            action='store_true',
            help='Afficher les statistiques des requêtes'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== ANALYSE DES LOGS ===\n'))
        
        days = options['days']
        log_type = options['log_type']
        show_errors = options['show_errors']
        show_requests = options['show_requests']
        
        # Calculer la date limite
        date_limit = datetime.now() - timedelta(days=days)
        
        # Analyser selon le type de log
        if log_type == 'all':
            self.analyze_all_logs(date_limit, show_errors, show_requests)
        else:
            self.analyze_specific_log(log_type, date_limit, show_errors, show_requests)

    def analyze_all_logs(self, date_limit, show_errors, show_requests):
        """Analyse tous les types de logs."""
        log_files = {
            'error': settings.LOGDIR / 'django_error.log',
            'general': settings.LOGDIR / 'django_general.log',
            'debug': settings.LOGDIR / 'django_debug.log'
        }
        
        for log_type, log_file in log_files.items():
            if os.path.exists(log_file):
                self.stdout.write(f"\n--- ANALYSE DU LOG {log_type.upper()} ---")
                self.analyze_log_file(log_file, date_limit, show_errors, show_requests)
            else:
                self.stdout.write(f"Fichier {log_file} non trouvé")

    def analyze_specific_log(self, log_type, date_limit, show_errors, show_requests):
        """Analyse un type de log spécifique."""
        log_file = settings.LOGDIR / f'django_{log_type}.log'
        
        if os.path.exists(log_file):
            self.analyze_log_file(log_file, date_limit, show_errors, show_requests)
        else:
            self.stdout.write(f"Fichier {log_file} non trouvé")

    def analyze_log_file(self, log_file, date_limit, show_errors, show_requests):
        """Analyse un fichier de log spécifique."""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de la lecture du fichier {log_file}: {e}"))
            return

        # Patterns pour parser les logs
        date_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
        level_pattern = r'\[(\w+)\]'
        
        # Compteurs
        total_lines = 0
        level_counts = Counter()
        hourly_activity = defaultdict(int)
        error_details = []
        request_stats = defaultdict(int)
        user_activity = Counter()
        
        for line in lines:
            # Extraire la date
            date_match = re.search(date_pattern, line)
            if date_match:
                try:
                    log_date = datetime.strptime(date_match.group(1), '%Y-%m-%d %H:%M:%S')
                    if log_date < date_limit:
                        continue
                except:
                    continue
            else:
                continue
            
            total_lines += 1
            
            # Extraire le niveau
            level_match = re.search(level_pattern, line)
            if level_match:
                level = level_match.group(1)
                level_counts[level] += 1
            
            # Activité par heure
            hour = log_date.hour
            hourly_activity[hour] += 1
            
            # Analyse des erreurs
            if 'ERROR' in line or 'WARNING' in line:
                error_details.append({
                    'date': log_date,
                    'line': line.strip()
                })
            
            # Analyse des requêtes
            if 'REQUEST_' in line:
                if 'REQUEST_SUCCESS' in line:
                    request_stats['success'] += 1
                elif 'REQUEST_ERROR' in line:
                    request_stats['error'] += 1
                elif 'REQUEST_START' in line:
                    request_stats['total'] += 1
            
            # Activité des utilisateurs
            user_match = re.search(r'User: (\w+)', line)
            if user_match:
                username = user_match.group(1)
                if username != 'Anonymous':
                    user_activity[username] += 1

        # Affichage des statistiques
        self.display_statistics(
            total_lines, level_counts, hourly_activity, 
            error_details, request_stats, user_activity,
            show_errors, show_requests
        )

    def display_statistics(self, total_lines, level_counts, hourly_activity, 
                         error_details, request_stats, user_activity,
                         show_errors, show_requests):
        """Affiche les statistiques analysées."""
        
        self.stdout.write(f"📊 Total des entrées de log: {total_lines}")
        
        # Statistiques par niveau
        if level_counts:
            self.stdout.write("\n📈 Répartition par niveau:")
            for level, count in level_counts.most_common():
                percentage = (count / total_lines) * 100
                self.stdout.write(f"  {level}: {count} ({percentage:.1f}%)")
        
        # Activité par heure
        if hourly_activity:
            self.stdout.write("\n🕐 Activité par heure:")
            for hour in sorted(hourly_activity.keys()):
                count = hourly_activity[hour]
                bar = '█' * min(count // 10, 50)  # Barre visuelle
                self.stdout.write(f"  {hour:02d}h: {count:4d} {bar}")
        
        # Statistiques des requêtes
        if show_requests and request_stats:
            self.stdout.write("\n🌐 Statistiques des requêtes:")
            for stat_type, count in request_stats.items():
                self.stdout.write(f"  {stat_type.title()}: {count}")
        
        # Activité des utilisateurs
        if user_activity:
            self.stdout.write("\n👥 Top 10 des utilisateurs actifs:")
            for username, count in user_activity.most_common(10):
                self.stdout.write(f"  {username}: {count} actions")
        
        # Détail des erreurs
        if show_errors and error_details:
            self.stdout.write("\n❌ Dernières erreurs:")
            for error in error_details[-10:]:  # 10 dernières erreurs
                date_str = error['date'].strftime('%Y-%m-%d %H:%M:%S')
                self.stdout.write(f"  [{date_str}] {error['line']}")
        
        # Résumé des alertes
        error_count = level_counts.get('ERROR', 0)
        warning_count = level_counts.get('WARNING', 0)
        
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"\n⚠️  {error_count} erreurs détectées"))
        if warning_count > 0:
            self.stdout.write(self.style.WARNING(f"⚠️  {warning_count} avertissements détectés"))
        
        if error_count == 0 and warning_count == 0:
            self.stdout.write(self.style.SUCCESS("\n✅ Aucune erreur ni avertissement détecté"))

    def format_duration(self, seconds):
        """Formate une durée en secondes."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}min"
        else:
            return f"{seconds/3600:.1f}h"
