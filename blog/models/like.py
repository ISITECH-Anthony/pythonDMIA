from django.db import models
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Manager
    from .user import User
    from .article import Article


class Like(models.Model):
    """Modèle pour les likes des articles"""
    user = models.ForeignKey(
        "blog.User",
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Utilisateur"
    )
    article = models.ForeignKey(
        "blog.Article",
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Article"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Liké le"
    )

    class Meta:
        unique_together = ('user', 'article')  # Un utilisateur ne peut liker qu'une fois le même article
        verbose_name = "Like"
        verbose_name_plural = "Likes"

    def __str__(self):
        return f"{self.user} likes {self.article.title}"

    if TYPE_CHECKING:
        objects: Manager["Like"]
