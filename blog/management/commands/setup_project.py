"""
Commande de management Django pour configurer automatiquement le projet
"""

import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import connection
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = "Configure automatiquement le projet Django (migrations, superuser, données de test)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-migrations", action="store_true", help="Ignorer les migrations"
        )
        parser.add_argument(
            "--skip-superuser",
            action="store_true",
            help="Ignorer la création du superutilisateur",
        )
        parser.add_argument(
            "--skip-data",
            action="store_true",
            help="Ignorer le peuplement des données de test",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forcer la recréation (efface la base de données)",
        )
        parser.add_argument(
            "--superuser-email",
            type=str,
            default="admin@bloghub.com",
            help="Email du superutilisateur (défaut: admin@bloghub.com)",
        )
        parser.add_argument(
            "--superuser-password",
            type=str,
            default="admin",
            help="Mot de passe du superutilisateur (défaut: admin)",
        )

    def handle(self, *args, **options):
        """Point d'entrée principal de la commande"""

        self.stdout.write(
            self.style.SUCCESS(
                "\n" + "=" * 60 + "\n" "🚀 CONFIGURATION DU PROJET DJANGO\n" + "=" * 60
            )
        )

        try:
            # 1. Vérifier la connexion à la base de données
            self._check_database_connection()

            # 2. Gérer les migrations
            if not options["skip_migrations"]:
                self._handle_migrations(options["force"])
            else:
                self.stdout.write(self.style.WARNING("⏭️  Migrations ignorées"))

            # 3. Créer le superutilisateur
            if not options["skip_superuser"]:
                self._create_superuser(
                    options["superuser_email"], options["superuser_password"]
                )
            else:
                self.stdout.write(
                    self.style.WARNING("⏭️  Création du superutilisateur ignorée")
                )

            # 4. Peupler avec des données de test
            if not options["skip_data"]:
                self._populate_test_data()
            else:
                self.stdout.write(
                    self.style.WARNING("⏭️  Peuplement des données ignoré")
                )

            # 5. Afficher le résumé final
            self._display_summary(options)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur lors de la configuration: {str(e)}")
            )
            raise CommandError(f"Échec de la configuration: {str(e)}")

    def _check_database_connection(self):
        """Vérifier la connexion à la base de données"""
        self.stdout.write("🔍 Vérification de la connexion à la base de données...")

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(
                self.style.SUCCESS("✅ Connexion à la base de données OK")
            )
        except Exception as e:
            raise CommandError(
                f"Impossible de se connecter à la base de données: {str(e)}"
            )

    def _handle_migrations(self, force_reset):
        """Gérer les migrations de la base de données"""

        if force_reset:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Mode force activé - Suppression de la base de données..."
                )
            )

            # Confirmer la suppression
            confirm = input(
                "Êtes-vous sûr de vouloir supprimer toutes les données ? (y/n): "
            )
            if confirm.lower() not in ["oui", "o", "yes", "y"]:
                self.stdout.write(self.style.ERROR("❌ Opération annulée"))
                return

            # Supprimer et recréer la base de données
            try:
                call_command("flush", "--noinput", verbosity=0)
                self.stdout.write(self.style.SUCCESS("✅ Base de données vidée"))
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Impossible de vider la base: {str(e)}")
                )

        # Exécuter les migrations
        self.stdout.write("🔄 Application des migrations...")
        try:
            call_command("makemigrations", verbosity=0)
            call_command("migrate", verbosity=0)
            self.stdout.write(
                self.style.SUCCESS("✅ Migrations appliquées avec succès")
            )
        except Exception as e:
            raise CommandError(f"Erreur lors des migrations: {str(e)}")

    def _create_superuser(self, email, password):
        """Créer un superutilisateur"""
        self.stdout.write("👤 Création du superutilisateur...")

        # Vérifier si un superutilisateur existe déjà
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING("⚠️  Un superutilisateur existe déjà"))
            confirm = input("Voulez-vous en créer un nouveau ? (y/n): ")
            if confirm.lower() not in ["oui", "o", "yes", "y"]:
                self.stdout.write(
                    self.style.WARNING("⏭️  Création du superutilisateur ignorée")
                )
                return

        try:
            # Supprimer l'ancien admin s'il existe
            User.objects.filter(email=email).delete()
            User.objects.filter(username="admin").delete()

            # Créer le nouveau superutilisateur
            user = User.objects.create_superuser(
                username="admin",
                email=email,
                password=password,
                first_name="Admin",
                last_name="Blog",
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Superutilisateur créé avec succès!\n"
                    f"   📧 Email: {email}\n"
                    f"   🔑 Mot de passe: {password}"
                )
            )

        except Exception as e:
            raise CommandError(
                f"Erreur lors de la création du superutilisateur: {str(e)}"
            )

    def _populate_test_data(self):
        """Peupler la base de données avec des données de test"""
        self.stdout.write(
            "📊 Peuplement de la base de données avec des données de test..."
        )

        try:
            call_command("populate_db", verbosity=0)
            self.stdout.write(
                self.style.SUCCESS("✅ Données de test créées avec succès")
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Erreur lors du peuplement des données: {str(e)}\n"
                    "   Vous pouvez exécuter manuellement: python manage.py populate_db"
                )
            )

    def _display_summary(self, options):
        """Afficher le résumé de la configuration"""

        # Statistiques de la base de données
        try:
            users_count = User.objects.count()

            # Importer dynamiquement les modèles pour éviter les erreurs
            from blog.models import Article, Category, Tag, Comment

            articles_count = Article.objects.count()
            categories_count = Category.objects.count()
            tags_count = Tag.objects.count()
            comments_count = Comment.objects.count()
        except Exception:
            users_count = articles_count = categories_count = tags_count = (
                comments_count
            ) = "?"

        summary = f"""
{self.style.SUCCESS("="*60)}
{self.style.SUCCESS("🎉 CONFIGURATION TERMINÉE AVEC SUCCÈS!")}
{self.style.SUCCESS("="*60)}

📊 STATISTIQUES DE LA BASE DE DONNÉES:
   👥 Utilisateurs: {users_count}
   📰 Articles: {articles_count}
   🏷️  Catégories: {categories_count}
   🔖 Tags: {tags_count}
   💬 Commentaires: {comments_count}

🌐 ACCÈS AU PROJET:
   🔗 Site web: http://localhost:8000/
   ⚙️  Admin: http://localhost:8000/admin/
   
🚀 COMMANDES UTILES:
   Démarrer le serveur: python manage.py runserver
   Accéder au shell: python manage.py shell
   Collecter les fichiers statiques: python manage.py collectstatic

💡 CONSEILS:
   • Utilisez --help pour voir toutes les options disponibles
   • Exécutez python manage.py populate_db pour ajouter plus de données
   • N'oubliez pas de configurer vos variables d'environnement en production

{self.style.SUCCESS("="*60)}
"""

        self.stdout.write(summary)

        # Informer l'utilisateur sur le démarrage du serveur
        self.stdout.write(
            self.style.SUCCESS(
                "\n🚀 Pour démarrer le serveur de développement, exécutez :\n"
                "   python manage.py runserver\n"
                "\n📱 Puis ouvrez votre navigateur sur : http://localhost:8000/"
            )
        )
