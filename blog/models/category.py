from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Manager


class Category(models.Model):
    """Modèle pour les catégories d'articles"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Description")
    icon = models.CharField(
        max_length=50,
        default="📂", 
        verbose_name="Icône",
        help_text="Emoji ou icône pour représenter la catégorie (ex: 💻, 🔬, 🎨)"
    )
    color = models.CharField(
        max_length=7, 
        default="#3B82F6", 
        verbose_name="Couleur",
        help_text="Couleur hexadécimale pour l'affichage (ex: #3B82F6)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name

    if TYPE_CHECKING:
        objects: Manager["Category"]
