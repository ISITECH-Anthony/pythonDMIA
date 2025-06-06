"""
URLs pour les pages diverses (auteurs, catégories, etc.)
"""
from django.urls import path
from ..views import author, category, home

urlpatterns = [
    # Pages d'information
    path("authors/", author.authors_view, name="authors"),
    path("authors/<int:pk>/", author.author_detail_view, name="author_detail"),
    path("categories/", category.categories_view, name="categories"),
    path("about/", home.about_view, name="about"),
]
