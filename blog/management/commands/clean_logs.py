"""
Commande Django pour nettoyer les anciens fichiers de logs.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import glob
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Nettoie les anciens fichiers de logs selon une politique de rétention"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Supprimer les logs plus anciens que X jours (défaut: 30)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Afficher ce qui serait supprimé sans le faire",
        )
        parser.add_argument(
            "--compress",
            action="store_true",
            help="Compresser les logs anciens au lieu de les supprimer",
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]
        compress = options["compress"]

        self.stdout.write(self.style.SUCCESS(f"=== NETTOYAGE DES LOGS ==="))

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Mode DRY-RUN activé - aucun fichier ne sera supprimé"
                )
            )

        # Date limite
        cutoff_date = datetime.now() - timedelta(days=days)
        self.stdout.write(
            f'Suppression des logs antérieurs au: {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}'
        )

        # Trouver tous les fichiers de logs
        log_patterns = [
            "django_*.log.*",  # Fichiers rotationnels
            "*.log.old",  # Anciens fichiers
            "*.log.bak",  # Fichiers de sauvegarde
        ]

        total_files = 0
        total_size = 0

        for pattern in log_patterns:
            files = glob.glob(os.path.join(settings.LOGDIR, pattern))

            for file_path in files:
                try:
                    # Vérifier l'âge du fichier
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    file_size = os.path.getsize(file_path)

                    if file_mtime < cutoff_date:
                        total_files += 1
                        total_size += file_size

                        if dry_run:
                            self.stdout.write(
                                f"Serait supprimé: {file_path} ({self.format_size(file_size)})"
                            )
                        else:
                            if compress:
                                self.compress_file(file_path)
                            else:
                                os.remove(file_path)
                                self.stdout.write(
                                    f"Supprimé: {file_path} ({self.format_size(file_size)})"
                                )

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erreur avec {file_path}: {e}"))

        # Nettoyer aussi les fichiers de logs trop volumineux
        self.clean_large_files(dry_run, compress)

        # Résumé
        if total_files > 0:
            action = "seraient supprimés" if dry_run else "supprimés"
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ {total_files} fichiers {action} "
                    f"({self.format_size(total_size)} libérés)"
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Aucun fichier à nettoyer"))

    def clean_large_files(self, dry_run, compress):
        """Nettoie les fichiers de logs trop volumineux."""
        max_size = 100 * 1024 * 1024  # 100 MB

        log_files = ["django_error.log", "django_general.log", "django_debug.log"]

        for log_file in log_files:
            file_path = os.path.join(settings.LOGDIR, log_file)

            if os.path.exists(file_path):
                try:
                    file_size = os.path.getsize(file_path)

                    if file_size > max_size:
                        if dry_run:
                            self.stdout.write(
                                f"Fichier volumineux détecté: {file_path} "
                                f"({self.format_size(file_size)})"
                            )
                        else:
                            if compress:
                                self.compress_file(file_path)
                            else:
                                # Tronquer le fichier en gardant seulement les dernières lignes
                                self.truncate_log_file(file_path)

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erreur avec {file_path}: {e}"))

    def compress_file(self, file_path):
        """Compresse un fichier de log."""
        import gzip
        import shutil

        try:
            compressed_path = f"{file_path}.gz"

            with open(file_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Supprimer le fichier original après compression
            os.remove(file_path)

            original_size = (
                os.path.getsize(file_path) if os.path.exists(file_path) else 0
            )
            compressed_size = os.path.getsize(compressed_path)

            self.stdout.write(
                f"Compressé: {file_path} -> {compressed_path} "
                f"({self.format_size(compressed_size)})"
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Erreur de compression pour {file_path}: {e}")
            )

    def truncate_log_file(self, file_path, keep_lines=10000):
        """Tronque un fichier de log en gardant seulement les dernières lignes."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if len(lines) > keep_lines:
                # Garder seulement les dernières lignes
                lines_to_keep = lines[-keep_lines:]

                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines_to_keep)

                self.stdout.write(
                    f"Tronqué: {file_path} "
                    f"({len(lines)} -> {len(lines_to_keep)} lignes)"
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Erreur de troncature pour {file_path}: {e}")
            )

    def format_size(self, size_bytes):
        """Formate une taille en bytes en format lisible."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
