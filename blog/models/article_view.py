from django.db import models
from django.utils import timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Manager


class ArticleView(models.Model):
    """Modèle pour traquer les vues uniques des articles par adresse IP et utilisateur"""
    article = models.ForeignKey(
        "blog.Article",
        on_delete=models.CASCADE,
        related_name="unique_views",
        verbose_name="Article"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="Adresse IP"
    )
    user = models.ForeignKey(
        "blog.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="article_views",
        verbose_name="Utilisateur"
    )
    viewed_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de vue"
    )

    class Meta:
        # On garde l'unicité par IP pour les utilisateurs anonymes
        # et on ajoute une contrainte pour les utilisateurs connectés
        constraints = [
            models.UniqueConstraint(
                fields=['article', 'ip_address'],
                condition=models.Q(user__isnull=True),
                name='unique_view_anonymous'
            ),
            models.UniqueConstraint(
                fields=['article', 'user'],
                condition=models.Q(user__isnull=False),
                name='unique_view_authenticated'
            ),
        ]
        verbose_name = "Vue d'article"
        verbose_name_plural = "Vues d'articles"
        ordering = ['-viewed_at']

    def __str__(self):
        if self.user:
            return f"Vue de {self.article.title} par {self.user.get_full_name()}"
        return f"Vue de {self.article.title} par {self.ip_address}"

    if TYPE_CHECKING:
        objects: Manager["ArticleView"]
