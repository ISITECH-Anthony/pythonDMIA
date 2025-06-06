"""
URLs principales du blog - Point d'entrée principal
"""

from django.urls import path, include
from ..views import home

app_name = "blog"

urlpatterns = [
    # Page d'accueil
    path("", home.home_view, name="home"),
    # Articles (avec namespace)
    path("articles/", include("blog.urls.articles", namespace="articles")),
    # Authentification
    path("", include("blog.urls.auth")),
    # Profil utilisateur
    path("profile/", include("blog.urls.users", namespace="users")),
    # API
    path("api/", include("blog.urls.api", namespace="api")),
    # Pages diverses
    path("", include("blog.urls.misc")),
]
