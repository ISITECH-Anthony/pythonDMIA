from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.utils import timezone

from ..models import User, Article, Like, ArticleView, Comment


def authors_view(request):
    """Vue pour afficher la liste des auteurs avec leurs statistiques"""
    # Récupérer le terme de recherche depuis l'URL
    search_query = request.GET.get("search", "").strip()

    # Base queryset avec annotations pour les statistiques
    authors = User.objects.annotate(
        articles_count=Count("articles", filter=Q(articles__is_published=True)),
        total_comments=Count(
            "articles__comments", filter=Q(articles__is_published=True)
        ),
    )#.filter(articles_count__gt=0)

    # Appliquer le filtre de recherche si un terme est fourni
    if search_query:
        authors = authors.filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    # Trier par nombre d'articles décroissant
    authors = authors.order_by("-articles_count")

    # Pagination (12 auteurs par page)
    paginator = Paginator(authors, 12)
    page_number = request.GET.get("page")
    authors_page = paginator.get_page(page_number)

    # Pour chaque auteur, ajouter le dernier article publié
    for author in authors_page:
        author.latest_published_article = author.get_latest_published_article()

    # Calculer les statistiques globales (sur tous les auteurs, pas seulement la page courante)
    total_authors = (
        User.objects.annotate(
            articles_count=Count("articles", filter=Q(articles__is_published=True))
        )
        .filter(articles_count__gt=0)
        .count()
    )

    total_articles = Article.objects.filter(is_published=True).count()
    total_comments = Comment.objects.filter(article__is_published=True).count()
    total_views = ArticleView.objects.filter(article__is_published=True).count()

    # Statistiques de la recherche
    search_results_count = authors.count() if search_query else None

    context = {
        "authors": authors_page,
        "total_authors": total_authors,
        "total_articles": total_articles,
        "total_comments": total_comments,
        "total_views": total_views,
        "search_query": search_query,
        "search_results_count": search_results_count,
        "paginator": paginator,
        "page_obj": authors_page,
    }
    return render(request, "blog/pages/authors/list.html", context)


def author_detail_view(request, pk):
    """Vue pour afficher le détail d'un auteur avec ses statistiques et articles"""
    # Récupérer l'auteur ou retourner 404
    author = get_object_or_404(User, pk=pk)

    # Récupérer les articles publiés de cet auteur avec optimisation des requêtes
    articles_queryset = (
        Article.objects.filter(author=author, is_published=True)
        .select_related("category")
        .prefetch_related("tags", "likes", "comments", "unique_views")
        .order_by("-created_at")
    )

    # Pagination des articles (6 par page)
    paginator = Paginator(articles_queryset, 6)
    page_number = request.GET.get("page")
    articles = paginator.get_page(page_number)

    # Calculer les statistiques de l'auteur de manière optimisée
    total_articles = articles_queryset.count()
    total_views = ArticleView.objects.filter(
        article__author=author, article__is_published=True
    ).count()
    total_likes = Like.objects.filter(
        article__author=author, article__is_published=True
    ).count()
    total_comments = Comment.objects.filter(
        article__author=author, article__is_published=True
    ).count()

    # Récupérer l'article le plus populaire (en termes de vues)
    most_popular_article = None
    if total_articles > 0:
        most_popular_article = (
            articles_queryset.annotate(total_views_count=Count("unique_views"))
            .order_by("-total_views_count")
            .first()
        )

    context = {
        "author": author,
        "articles": articles,
        "total_articles": total_articles,
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "most_popular_article": most_popular_article,
        "author_since": author.date_joined,
    }

    return render(request, "blog/pages/authors/detail.html", context)
