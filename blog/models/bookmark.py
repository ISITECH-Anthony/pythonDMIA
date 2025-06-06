from django.db import models
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Manager
    from .user import User
    from .article import Article


class Bookmark(models.Model):
    """Modèle pour les favoris (bookmarks) des articles"""
    user = models.ForeignKey(
        "blog.User",
        on_delete=models.CASCADE,
        related_name="bookmarks",
        verbose_name="Utilisateur"
    )
    article = models.ForeignKey(
        "blog.Article",
        on_delete=models.CASCADE,
        related_name="bookmarks",
        verbose_name="Article"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ajouté aux favoris le"
    )

    class Meta:
        unique_together = ('user', 'article')  # Un utilisateur ne peut mettre en favori qu'une fois le même article
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} bookmarked {self.article.title}"

    if TYPE_CHECKING:
        objects: Manager["Bookmark"]
