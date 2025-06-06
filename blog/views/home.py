from django.shortcuts import render
from ..models import Article, User, ArticleView, Comment
from django.db.models import Count


def home_view(request):
    """Vue pour la page d'accueil"""
    # Articles récents (publiés)
    recents_articles = (
        Article.objects.filter(is_published=True)
        .select_related("author", "category")
        .order_by("-published_at")[:3]
    )

    # Articles les plus populaires (publiés)
    # (basés sur le nombre de vues)
    popular_articles = (
        Article.objects.filter(is_published=True)
        .select_related("author", "category")
        .annotate(total_likes=Count("likes"))
        .order_by("-total_likes")[:3]
    )

    total_articles = Article.objects.filter(is_published=True).count()

    total_authors = User.objects.filter(articles__is_published=True).distinct().count()

    total_views = ArticleView.objects.filter(article__is_published=True).count()

    total_comments = Comment.objects.filter(article__is_published=True).count()

    context = {
        "recents_articles": recents_articles,
        "popular_articles": popular_articles,
        "total_articles": total_articles,
        "total_authors": total_authors,
        "total_views": total_views,
        "total_comments": total_comments,
    }

    return render(request, "blog/pages/home.html", context)


def about_view(request):
    """Vue pour la page À propos"""
    # Statistiques pour la page À propos
    total_articles = Article.objects.filter(is_published=True).count()
    total_authors = User.objects.filter(articles__isnull=False).distinct().count()
    total_views = ArticleView.objects.count()
    total_comments = Comment.objects.count()

    # Articles les plus populaires
    popular_articles = (
        Article.objects.filter(is_published=True)
        .annotate(total_likes=Count("likes"))
        .order_by("-total_likes")[:3]
    )

    context = {
        "total_articles": total_articles,
        "total_authors": total_authors,
        "total_views": total_views,
        "total_comments": total_comments,
        "popular_articles": popular_articles,
    }

    return render(request, "blog/pages/about.html", context)
