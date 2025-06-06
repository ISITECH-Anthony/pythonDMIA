from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Manager
    from .user import User


class Article(models.Model):
    """Modèle pour les articles du blog"""

    title = models.CharField(
        max_length=200, verbose_name="Titre", null=False, blank=False
    )
    slug = models.SlugField(
        max_length=250, unique=True, blank=True, verbose_name="Slug"
    )
    content = models.TextField(verbose_name="Contenu", null=False, blank=False)
    author = models.ForeignKey(
        "blog.User",
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name="Auteur",
    )
    category = models.ForeignKey(
        "blog.Category",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="articles",
        verbose_name="Catégorie",
    )
    image = models.ImageField(
        upload_to="articles/",
        blank=False,
        null=False,
        verbose_name="Image d'illustration",
    )
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    published_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Date de première publication"
    )
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Date de modification"
    )

    @property
    def views_count(self):
        """Retourne le nombre de vues uniques pour cet article"""
        return self.unique_views.count()

    @property
    def comments_count(self):
        """Retourne le nombre de commentaires pour cet article"""
        return self.comments.count()

    @property
    def likes_count(self):
        """Retourne le nombre de likes pour cet article"""
        return self.likes.count()

    @property
    def bookmarks_count(self):
        """Retourne le nombre de signets pour cet article"""
        return self.bookmarks.count()

    @property
    def reading_time(self):
        """Calcule le temps de lecture estimé en minutes basé sur le nombre de mots"""
        if not self.content:
            return 1

        word_count = len(self.content.split())

        return max(1, round(word_count / 200))  # 200 mots par minute

    @property
    def word_count(self):
        """Retourne le nombre de mots dans le contenu de l'article"""
        if not self.content:
            return 0
        return len(self.content.split())

    @property
    def excerpt(self):
        """Retourne un extrait de l'article (les 20 premiers mots)"""
        if not self.content:
            return ""
        words = self.content.split()
        excerpt_words = words[:20]

        if len(words) > 20:
            excerpt_words.append("...")
        return " ".join(excerpt_words)

    def is_bookmarked_by(self, user):
        """Vérifie si l'article est marqué comme favori par l'utilisateur donné"""
        if not user or not user.is_authenticated:
            return False
        return self.bookmarks.filter(user=user).exists()

    @property
    def is_draft(self):
        """Retourne True si l'article est un brouillon (jamais publié)"""
        return not self.is_published and self.published_at is None

    @property
    def is_unpublished(self):
        """Retourne True si l'article a été dépublié (publié puis retiré)"""
        return not self.is_published and self.published_at is not None

    @property
    def status_display(self):
        """Retourne le statut de l'article pour l'affichage"""
        if self.is_published:
            return "Publié"
        elif self.is_draft:
            return "Brouillon"
        else:
            return "Dépublié"

    def publish(self):
        """Publie l'article et marque la date de première publication si nécessaire"""
        self.is_published = True
        if self.published_at is None:
            self.published_at = timezone.now()
        self.save(update_fields=["is_published", "published_at"])

    def unpublish(self):
        """Dépublie l'article (garde la date de publication)"""
        self.is_published = False
        self.save(update_fields=["is_published"])

    def save(self, *args, **kwargs):
        """Override save method to generate slug from title"""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    if TYPE_CHECKING:
        objects: Manager["Article"]
