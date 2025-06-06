import random
import os
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from faker import Faker
import requests
from PIL import Image
from io import BytesIO

from blog.models import Article, Category, Comment, Tag, Like, Bookmark, ArticleView

User = get_user_model()
fake = Faker("fr_FR")


class Command(BaseCommand):
    help = "Génère des données de test pour la base de données"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=20,
            help="Nombre d'utilisateurs à créer (défaut: 20)",
        )
        parser.add_argument(
            "--articles",
            type=int,
            default=50,
            help="Nombre d'articles à créer (défaut: 50)",
        )
        parser.add_argument(
            "--comments",
            type=int,
            default=150,
            help="Nombre de commentaires à créer (défaut: 150)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Supprime toutes les données existantes avant de créer les nouvelles",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(
                self.style.WARNING("Suppression des données existantes...")
            )
            self.clear_existing_data()

        self.stdout.write(
            self.style.SUCCESS("Début de la génération des données de test...")
        )

        # Créer les catégories en premier
        categories = self.create_categories()
        self.stdout.write(self.style.SUCCESS(f"✅ {len(categories)} catégories créées"))

        # Créer les utilisateurs
        users = self.create_users(options["users"])
        self.stdout.write(self.style.SUCCESS(f"✅ {len(users)} utilisateurs créés"))

        # Créer les articles
        articles = self.create_articles(options["articles"], users, categories)
        self.stdout.write(self.style.SUCCESS(f"✅ {len(articles)} articles créés"))

        # Créer les commentaires
        comments = self.create_comments(options["comments"], users, articles)
        self.stdout.write(self.style.SUCCESS(f"✅ {len(comments)} commentaires créés"))

        # Créer les tags
        tags = self.create_tags(articles)
        self.stdout.write(self.style.SUCCESS(f"✅ {len(tags)} tags créés"))

        # Créer les likes
        likes = self.create_likes(users, articles)
        self.stdout.write(self.style.SUCCESS(f"✅ {len(likes)} likes créés"))

        # Créer les bookmarks
        bookmarks = self.create_bookmarks(users, articles)
        self.stdout.write(self.style.SUCCESS(f"✅ {len(bookmarks)} bookmarks créés"))

        # Créer les vues d'articles
        views = self.create_article_views(users, articles)
        self.stdout.write(self.style.SUCCESS(f"✅ {len(views)} vues d'articles créées"))

        self.stdout.write(
            self.style.SUCCESS("🎉 Génération des données terminée avec succès!")
        )

    def clear_existing_data(self):
        """Supprime toutes les données existantes (sauf les superusers)"""
        ArticleView.objects.all().delete()
        Bookmark.objects.all().delete()
        Like.objects.all().delete()
        Tag.objects.all().delete()
        Comment.objects.all().delete()
        Article.objects.all().delete()
        Category.objects.all().delete()
        # Ne supprime que les utilisateurs non-superusers
        User.objects.filter(is_superuser=False).delete()

    def create_categories(self):
        """Crée des catégories prédéfinies"""
        categories_data = [
            {
                "name": "Technologie",
                "slug": "technologie",
                "description": "Articles sur les nouvelles technologies, le développement web, l'IA et plus.",
                "icon": "💻",
                "color": "#3B82F6",
            },
            {
                "name": "Science",
                "slug": "science",
                "description": "Découvertes scientifiques, recherche et innovation.",
                "icon": "🔬",
                "color": "#8B5CF6",
            },
            {
                "name": "Design",
                "slug": "design",
                "description": "Design graphique, UX/UI, art numérique et créativité.",
                "icon": "🎨",
                "color": "#EC4899",
            },
            {
                "name": "Business",
                "slug": "business",
                "description": "Entrepreneuriat, économie et stratégies d'entreprise.",
                "icon": "💼",
                "color": "#059669",
            },
            {
                "name": "Cuisine",
                "slug": "cuisine",
                "description": "Recettes, techniques culinaires et gastronomie.",
                "icon": "👨‍🍳",
                "color": "#F59E0B",
            },
            {
                "name": "Sport",
                "slug": "sport",
                "description": "Actualités sportives, fitness et bien-être.",
                "icon": "⚽",
                "color": "#10B981",
            },
            {
                "name": "Voyage",
                "slug": "voyage",
                "description": "Guides de voyage, cultures et découvertes.",
                "icon": "✈️",
                "color": "#06B6D4",
            },
            {
                "name": "Santé",
                "slug": "sante",
                "description": "Santé, médecine et conseils de bien-être.",
                "icon": "🏥",
                "color": "#EF4444",
            },
            {
                "name": "Musique",
                "slug": "musique",
                "description": "Actualités musicales, critiques et découvertes.",
                "icon": "🎵",
                "color": "#8B5CF6",
            },
            {
                "name": "Lifestyle",
                "slug": "lifestyle",
                "description": "Mode de vie, tendances et développement personnel.",
                "icon": "🌟",
                "color": "#F97316",
            },
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"], defaults=cat_data
            )
            categories.append(category)

        return categories

    def create_users(self, count):
        """Crée des utilisateurs factices"""
        users = []

        for i in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = (
                f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
            )
            email = f"{username}@example.com"

            # Éviter les doublons d'email
            while User.objects.filter(email=email).exists():
                username = (
                    f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 9999)}"
                )
                email = f"{username}@example.com"

            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123",
                first_name=first_name,
                last_name=last_name,
                bio=fake.text(max_nb_chars=200),
            )

            # Ajouter un avatar pour certains utilisateurs (50% de chance)
            if random.choice([True, False]):
                try:
                    # Créer une image d'avatar simple avec les initiales
                    self.create_avatar_for_user(user)
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Impossible de créer l'avatar pour {user.username}: {e}"
                        )
                    )

            users.append(user)

        return users

    def create_avatar_for_user(self, user):
        """Crée un avatar simple avec les initiales de l'utilisateur"""
        from PIL import Image, ImageDraw, ImageFont

        # Couleurs d'arrière-plan possibles
        colors = [
            "#3B82F6",
            "#EF4444",
            "#10B981",
            "#F59E0B",
            "#8B5CF6",
            "#EC4899",
            "#06B6D4",
            "#84CC16",
        ]

        # Créer une image 200x200
        img = Image.new("RGB", (200, 200), random.choice(colors))
        draw = ImageDraw.Draw(img)

        # Obtenir les initiales
        initials = user.get_initials()

        # Essayer d'utiliser une police, sinon utiliser la police par défaut
        try:
            font = ImageFont.truetype("Arial.ttf", 80)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 80)
            except:
                font = ImageFont.load_default()

        # Calculer la position du texte pour le centrer
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (200 - text_width) // 2
        y = (200 - text_height) // 2

        # Dessiner le texte
        draw.text((x, y), initials, fill="white", font=font)

        # Sauvegarder l'image en mémoire
        output = BytesIO()
        img.save(output, format="PNG")
        output.seek(0)

        # Attacher l'image au profil utilisateur
        user.avatar.save(
            f"avatar_{user.username}.png", ContentFile(output.read()), save=True
        )

    def create_articles(self, count, users, categories):
        """Crée des articles factices"""
        articles = []

        # Titres d'exemple par catégorie
        title_templates = {
            "Technologie": [
                "L'intelligence artificielle révolutionne {}",
                "Comment {} change notre façon de travailler",
                "Guide complet pour débuter avec {}",
                "Les tendances {} en 2024",
                "Pourquoi {} est l'avenir de la tech",
            ],
            "Science": [
                "Découverte révolutionnaire en {}",
                "Les mystères de {} enfin élucidés",
                "Comment {} impacte notre quotidien",
                "Recherche avancée sur {}",
                "L'évolution de {} à travers les âges",
            ],
            "Design": [
                "Tendances design {} pour 2024",
                "Créer des {} époustouflants",
                "L'art de {} dans le design moderne",
                "Guide du {} pour débutants",
                "Inspiration {} : 10 projets remarquables",
            ],
            "Business": [
                "Stratégies {} pour entrepreneurs",
                "Comment réussir en {} en 2024",
                "Les secrets du {} selon les experts",
                "Développer son {} efficacement",
                "Marketing {} : guide pratique",
            ],
            "Cuisine": [
                "Recettes {} traditionnelles revisitées",
                "L'art de cuisiner {}",
                "Secrets de chef pour {}",
                "Cuisine {} saine et savoureuse",
                "Guide complet des {}",
            ],
        }

        # Mots-clés par catégorie
        keywords = {
            "Technologie": [
                "React",
                "Python",
                "Django",
                "JavaScript",
                "Machine Learning",
                "Blockchain",
                "DevOps",
                "Cloud",
            ],
            "Science": [
                "la physique quantique",
                "l'astronomie",
                "la biologie",
                "la chimie",
                "l'écologie",
                "les neurosciences",
            ],
            "Design": [
                "UX/UI",
                "Figma",
                "Adobe",
                "typographie",
                "couleurs",
                "wireframes",
                "prototypage",
            ],
            "Business": [
                "startup",
                "marketing digital",
                "leadership",
                "innovation",
                "e-commerce",
                "management",
            ],
            "Cuisine": [
                "pâtes",
                "légumes",
                "desserts",
                "plats végétariens",
                "épices",
                "techniques culinaires",
            ],
        }

        for i in range(count):
            category = random.choice(categories)
            author = random.choice(users)

            # Générer un titre en fonction de la catégorie
            if category.name in title_templates:
                template = random.choice(title_templates[category.name])
                keyword = random.choice(
                    keywords.get(category.name, ["sujets intéressants"])
                )
                title = template.format(keyword)
            else:
                title = fake.sentence(nb_words=6).rstrip(".")

            # Générer du contenu riche avec du Markdown
            content_paragraphs = []

            # Introduction
            content_paragraphs.append(
                f"## Introduction\n\n{fake.text(max_nb_chars=300)}"
            )

            # Sections principales
            for section_num in range(random.randint(2, 4)):
                section_title = fake.sentence(nb_words=4).rstrip(".")
                section_content = fake.text(max_nb_chars=500)
                content_paragraphs.append(f"## {section_title}\n\n{section_content}")

                # Ajouter parfois une liste
                if random.choice([True, False]):
                    list_items = [
                        f"- {fake.sentence(nb_words=8)}"
                        for _ in range(random.randint(3, 6))
                    ]
                    content_paragraphs.append("\n".join(list_items))

            # Conclusion
            content_paragraphs.append(f"## Conclusion\n\n{fake.text(max_nb_chars=200)}")

            content = "\n\n".join(content_paragraphs)

            # Date de création aléatoire dans les 6 derniers mois
            created_at = fake.date_time_between(
                start_date="-6M", end_date="now", tzinfo=timezone.get_current_timezone()
            )

            article = Article.objects.create(
                title=title,
                content=content,
                author=author,
                category=category,
                created_at=created_at,
                is_published=random.choice([True, True, True, False]),  # 75% publiés
            )

            # Créer une image d'illustration simple
            try:
                self.create_article_image(article, category)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"Impossible de créer l'image pour l'article {article.id}: {e}"
                    )
                )

            articles.append(article)

        return articles

    def create_article_image(self, article, category):
        """Crée une image d'illustration pour l'article"""
        from PIL import Image, ImageDraw, ImageFont

        # Couleurs basées sur la catégorie
        bg_color = category.color

        # Créer une image 800x400
        img = Image.new("RGB", (800, 400), bg_color)
        draw = ImageDraw.Draw(img)

        # Ajouter l'icône de la catégorie
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 120)
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Dessiner l'icône de la catégorie au centre
        icon = category.icon
        bbox = draw.textbbox((0, 0), icon, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (800 - text_width) // 2
        y = (400 - text_height) // 2 - 50

        draw.text((x, y), icon, fill="white", font=font_large)

        # Ajouter le nom de la catégorie en bas
        cat_name = category.name
        bbox = draw.textbbox((0, 0), cat_name, font=font_small)
        text_width = bbox[2] - bbox[0]
        x = (800 - text_width) // 2
        y = y + 150

        draw.text((x, y), cat_name, fill="white", font=font_small)

        # Sauvegarder l'image
        output = BytesIO()
        img.save(output, format="PNG")
        output.seek(0)

        article.image.save(
            f"article_{article.id}_{fake.uuid4()}.png",
            ContentFile(output.read()),
            save=True,
        )

    def create_comments(self, count, users, articles):
        """Crée des commentaires factices"""
        comments = []

        # Templates de commentaires
        comment_templates = [
            "Excellent article ! {}",
            "Très intéressant, surtout la partie sur {}.",
            "Merci pour ce partage. {}",
            "J'ai appris beaucoup de choses. {}",
            "Bravo pour ce travail de qualité ! {}",
            "Super contenu, vivement le prochain article !",
            "Très bien expliqué, facile à comprendre.",
            "Article très complet et bien documenté.",
            "Merci pour ces conseils pratiques !",
            "J'ai une question : {}",
            "Pourriez-vous développer le point sur {} ?",
            "Totalement d'accord avec votre analyse.",
        ]

        for i in range(count):
            article = random.choice(articles)
            author = random.choice(users)

            # Éviter que l'auteur commente son propre article (parfois)
            if author == article.author and random.choice([True, False, False]):
                author = random.choice([u for u in users if u != article.author])

            # Générer le contenu du commentaire
            template = random.choice(comment_templates)
            if "{}" in template:
                detail = fake.sentence(nb_words=random.randint(4, 8))
                content = template.format(detail)
            else:
                content = template

            # Date du commentaire (après la création de l'article)
            min_date = article.created_at
            max_date = min_date + timedelta(days=30)
            now_aware = timezone.now()
            if max_date > now_aware:
                max_date = now_aware

            created_at = fake.date_time_between(
                start_date=min_date, end_date=max_date, tzinfo=min_date.tzinfo
            )

            comment = Comment.objects.create(
                article=article, author=author, content=content, created_at=created_at
            )

            comments.append(comment)

        return comments

    def create_tags(self, articles):
        """Crée des tags pour les articles"""
        tags = []

        # Liste de tags prédéfinis
        tag_names = [
            "python",
            "django",
            "javascript",
            "react",
            "vue",
            "angular",
            "machine-learning",
            "ia",
            "blockchain",
            "devops",
            "cloud",
            "design",
            "ux",
            "ui",
            "figma",
            "adobe",
            "photoshop",
            "business",
            "startup",
            "marketing",
            "seo",
            "e-commerce",
            "science",
            "recherche",
            "innovation",
            "technologie",
            "cuisine",
            "recette",
            "gastronomie",
            "healthy",
            "sport",
            "fitness",
            "running",
            "yoga",
            "voyage",
            "culture",
            "exploration",
            "guide",
            "santé",
            "médecine",
            "bien-être",
            "nutrition",
            "musique",
            "concert",
            "artiste",
            "album",
            "lifestyle",
            "mode",
            "tendance",
            "style",
        ]

        # Couleurs pour les tags (noms Tailwind)
        tag_colors = [
            "blue",
            "green",
            "yellow",
            "orange",
            "red",
            "purple",
            "pink",
            "indigo",
            "teal",
            "cyan",
            "lime",
            "emerald",
            "violet",
            "fuchsia",
            "rose",
            "sky",
            "amber",
            "slate",
        ]

        for article in articles:
            # Chaque article a entre 1 et 5 tags
            num_tags = random.randint(1, 5)
            article_tags = random.sample(tag_names, min(num_tags, len(tag_names)))

            for tag_name in article_tags:
                tag = Tag.objects.create(
                    name=tag_name, article=article, color=random.choice(tag_colors)
                )
                tags.append(tag)

        return tags

    def create_likes(self, users, articles):
        """Crée des likes sur les articles"""
        likes = []

        for article in articles:
            # Chaque article reçoit entre 0 et 15 likes
            num_likes = random.randint(0, 15)
            likers = random.sample(users, min(num_likes, len(users)))

            for user in likers:
                # Un utilisateur ne peut pas liker son propre article
                if user != article.author:
                    like = Like.objects.create(user=user, article=article)
                    likes.append(like)

        return likes

    def create_bookmarks(self, users, articles):
        """Crée des bookmarks sur les articles"""
        bookmarks = []

        for user in users:
            # Chaque utilisateur bookmarke entre 0 et 8 articles
            num_bookmarks = random.randint(0, 8)
            bookmarked_articles = random.sample(
                articles, min(num_bookmarks, len(articles))
            )

            for article in bookmarked_articles:
                # Un utilisateur ne peut pas bookmarker son propre article
                if user != article.author:
                    bookmark = Bookmark.objects.create(user=user, article=article)
                    bookmarks.append(bookmark)

        return bookmarks

    def create_article_views(self, users, articles):
        """Crée des vues d'articles"""
        views = []

        for article in articles:
            # Chaque article reçoit entre 10 et 100 vues
            num_views = random.randint(10, 100)

            # Mélange d'utilisateurs connectés et d'IPs anonymes
            for i in range(num_views):
                if random.choice([True, False]) and users:
                    # Vue d'un utilisateur connecté
                    user = random.choice(users)
                    # Générer une IP réaliste
                    ip = fake.ipv4()

                    # Vérifier si cette vue existe déjà
                    if not ArticleView.objects.filter(
                        article=article, user=user
                    ).exists():
                        view = ArticleView.objects.create(
                            article=article, user=user, ip_address=ip
                        )
                        views.append(view)
                else:
                    # Vue anonyme (juste IP)
                    ip = fake.ipv4()

                    # Vérifier si cette IP a déjà vu cet article
                    if not ArticleView.objects.filter(
                        article=article, ip_address=ip, user__isnull=True
                    ).exists():
                        view = ArticleView.objects.create(
                            article=article, ip_address=ip, user=None
                        )
                        views.append(view)

        return views
