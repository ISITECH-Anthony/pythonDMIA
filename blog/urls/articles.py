"""
URLs pour la gestion des articles
"""
from django.urls import path
from ..views import article

app_name = 'articles'

urlpatterns = [
    # Liste et création d'articles
    path("", article.articles_list, name="list"),
    path("create/", article.add_article, name="create"),
    
    # Génération d'article avec IA
    path("generate-ai/", article.generate_article_with_ai, name="generate_ai"),
    
    # Gestion de la publication des articles
    path("<int:article_id>/publish/", article.publish_article, name="publish"),
    path("<int:article_id>/unpublish/", article.unpublish_article, name="unpublish"),
    path("<int:article_id>/delete/", article.delete_article, name="delete"),
    
    # Édition d'un article
    path("<slug:slug>/edit/", article.edit_article, name="edit"),
    
    # Détail d'un article
    path("<slug:slug>/", article.article_detail, name="detail"),
    
    # Gestion des commentaires
    path("comment/<int:comment_id>/delete/", article.delete_comment, name="delete_comment"),
]
