"""
URLs pour l'API REST
"""
from django.urls import path
from ..views import article

app_name = 'api'

urlpatterns = [
    # API Articles - Actions AJAX
    path("articles/<int:article_id>/like/", article.toggle_like, name="article_like"),
    path("articles/<int:article_id>/bookmark/", article.toggle_bookmark, name="article_bookmark"),
]
