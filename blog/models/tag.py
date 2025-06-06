from django.db import models
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Manager


class Tag(models.Model):
    """Modèle pour les tags des articles"""
    name = models.CharField(max_length=50, verbose_name="Nom")
    article = models.ForeignKey(
        "blog.Article",
        on_delete=models.CASCADE,
        related_name="tags",
        verbose_name="Article"
    )
    color = models.CharField(
        max_length=7, 
        default="#3B82F6", 
        verbose_name="Couleur",
        help_text="Couleur hexadécimale pour l'affichage du tag (ex: #3B82F6)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']
        unique_together = ('name', 'article')  # Un tag avec le même nom ne peut pas être ajouté deux fois au même article

    def __str__(self):
        return f"{self.name} ({self.article.title})"

    if TYPE_CHECKING:
        objects: Manager["Tag"]
