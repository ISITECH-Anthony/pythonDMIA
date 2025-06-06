from django.db import models
from django.contrib.auth.models import AbstractUser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Manager


class User(AbstractUser):
    """Modèle utilisateur personnalisé pour les auteurs du blog"""

    first_name = models.CharField(max_length=30, verbose_name="Prénom")
    last_name = models.CharField(max_length=30, verbose_name="Nom")
    email = models.EmailField(unique=True, verbose_name="Email")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biographie")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Photo de profil"
    )

    # Utiliser l'email comme identifiant de connexion
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_initials(self):
        """Retourne les initiales pour l'avatar par défaut"""
        return f"{self.first_name[0] if self.first_name else ''}{self.last_name[0] if self.last_name else ''}".upper()

    def get_total_views(self):
        """Calcule le nombre total de vues pour tous les articles publiés de cet auteur"""
        from .article_view import ArticleView

        return ArticleView.objects.filter(article__author=self, article__is_published=True).count()

    def get_published_articles_count(self):
        """Retourne le nombre d'articles publiés de cet auteur"""
        return self.articles.filter(is_published=True).count()

    def get_latest_published_article(self):
        """Retourne le dernier article publié de cet auteur"""
        return self.articles.filter(is_published=True).order_by('-published_at').first()

    def get_total_likes(self):
        """Calcule le nombre total de likes pour tous les articles publiés de cet auteur"""
        from .like import Like
        return Like.objects.filter(article__author=self, article__is_published=True).count()

    if TYPE_CHECKING:
        objects: Manager["User"]
