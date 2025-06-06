from django.db import models
from django.utils import timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Manager
    from .user import User
    from .article import Article


class Comment(models.Model):
    """Modèle pour les commentaires des articles"""
    article = models.ForeignKey(
        "blog.Article", 
        on_delete=models.CASCADE, 
        related_name="comments",
        verbose_name="Article"
    )
    author = models.ForeignKey(
        "blog.User",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Auteur"
    )
    content = models.TextField(verbose_name="Contenu")
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de création"
    )

    def __str__(self):
        return f"Commentaire de {self.author.get_full_name()} sur {self.article.title}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"

    if TYPE_CHECKING:
        objects: Manager["Comment"]
