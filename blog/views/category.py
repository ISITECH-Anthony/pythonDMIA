from django.shortcuts import render
from django.db.models import Count, Q
from blog.models.category import Category
from blog.models.article import Article
from blog.models.user import User
from blog.models.article_view import ArticleView


def categories_view(request):
    categories = Category.objects.annotate(
        article_count=Count(
            "articles", distinct=True, filter=Q(articles__is_published=True)
        ),
        author_count=Count(
            "articles__author", distinct=True, filter=Q(articles__is_published=True)
        ),
    ).order_by("name")

    total_categories = categories.count()
    total_articles = Article.objects.filter(is_published=True).count()
    total_authors = User.objects.filter(articles__isnull=False).distinct().count()
    total_views = ArticleView.objects.count()

    for category in categories:
        category.latest_article = (
            Article.objects.filter(category=category, is_published=True)
            .order_by("-created_at")
            .first()
        )

    context = {
        "categories": categories,
        "total_categories": total_categories,
        "total_articles": total_articles,
        "total_authors": total_authors,
        "total_views": total_views,
    }

    return render(request, "blog/pages/categories/list.html", context)
