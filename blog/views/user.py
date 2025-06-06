from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from ..forms import UserProfileForm
from ..models import ArticleView, Like, Bookmark, Article, Comment


@login_required
def profile_view(request):
    """Vue pour afficher le profil utilisateur (lecture seule)"""
    # Calculer les statistiques de l'utilisateur
    published_articles = request.user.articles.filter(is_published=True)
    draft_articles = request.user.articles.filter(is_published=False, published_at__isnull=True)
    unpublished_articles = request.user.articles.filter(is_published=False, published_at__isnull=False)

    total_views = ArticleView.objects.filter(
        article__author=request.user, article__is_published=True
    ).count()
    total_likes = Like.objects.filter(
        article__author=request.user, article__is_published=True
    ).count()

    user_stats = {
        "articles_count": request.user.articles.count(),  # Total (publiés + brouillons + dépubliés)
        "published_articles_count": published_articles.count(),  # Articles publiés
        "draft_articles_count": draft_articles.count(),  # Brouillons (jamais publiés)
        "unpublished_articles_count": unpublished_articles.count(),  # Articles dépubliés
        "comments_count": request.user.comments.count(),
        "total_views": total_views,
        "total_likes": total_likes,
    }

    context = {
        "user_stats": user_stats,
    }
    return render(request, "blog/pages/users/profile.html", context)


@login_required
def edit_profile_view(request):
    """Vue pour éditer le profil utilisateur"""
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès !")
            return redirect("blog:users:profile")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = UserProfileForm(instance=request.user)

    context = {
        "form": form,
    }
    return render(request, "blog/pages/users/edit_profile.html", context)


@login_required
@require_POST
@csrf_protect
def delete_account_view(request):
    """Vue pour supprimer le compte utilisateur"""
    user = request.user
    username = user.username

    # Déconnecter l'utilisateur avant de supprimer le compte
    logout(request)

    # Supprimer le compte utilisateur
    # Django supprimera automatiquement les objets liés grâce aux ForeignKey avec CASCADE
    user.delete()

    # Message de confirmation
    messages.success(
        request,
        f"Le compte {username} a été supprimé avec succès. Nous sommes désolés de vous voir partir.",
    )

    # Rediriger vers la page d'accueil
    return redirect("blog:home")


@login_required
def dashboard_view(request):
    """Vue pour afficher le tableau de bord utilisateur avec toutes les statistiques"""
    
    # Articles que l'utilisateur a likés
    liked_articles = Article.objects.filter(
        likes__user=request.user,
        is_published=True
    ).select_related('category', 'author').prefetch_related('tags', 'likes', 'comments').order_by('-likes__created_at')[:10]
    
    # Articles que l'utilisateur a bookmarkés
    bookmarked_articles = Article.objects.filter(
        bookmarks__user=request.user,
        is_published=True
    ).select_related('category', 'author').prefetch_related('tags', 'likes', 'comments').order_by('-bookmarks__created_at')[:10]
    
    # Mes articles avec leurs statistiques
    my_articles = request.user.articles.filter(
        is_published=True
    ).select_related('category').prefetch_related('likes', 'comments', 'unique_views').order_by('-created_at')[:10]
    
    # Mes articles en brouillons (jamais publiés)
    draft_articles = request.user.articles.filter(
        is_published=False,
        published_at__isnull=True
    ).select_related('category').order_by('-created_at')[:10]
    
    # Mes articles dépubliés (anciennement publiés)
    unpublished_articles = request.user.articles.filter(
        is_published=False,
        published_at__isnull=False
    ).select_related('category').prefetch_related('likes', 'comments', 'unique_views').order_by('-updated_at')[:10]
    
    # Calculer les statistiques de la semaine passée
    week_ago = timezone.now() - timedelta(days=7)
    
    # Statistiques de la semaine pour mes articles
    week_stats = {
        'likes': Like.objects.filter(
            article__author=request.user,
            article__is_published=True,
            created_at__gte=week_ago
        ).count(),
        'bookmarks': Bookmark.objects.filter(
            article__author=request.user,
            article__is_published=True,
            created_at__gte=week_ago
        ).count(),
        'comments': Comment.objects.filter(
            article__author=request.user,
            article__is_published=True,
            created_at__gte=week_ago
        ).count(),
        'views': ArticleView.objects.filter(
            article__author=request.user,
            article__is_published=True,
            viewed_at__gte=week_ago
        ).count(),
    }
    
    # Statistiques globales de l'utilisateur
    total_stats = {
        'total_likes': Like.objects.filter(
            article__author=request.user,
            article__is_published=True
        ).count(),
        'total_bookmarks': Bookmark.objects.filter(
            article__author=request.user,
            article__is_published=True
        ).count(),
        'total_comments': Comment.objects.filter(
            article__author=request.user,
            article__is_published=True
        ).count(),
        'total_views': ArticleView.objects.filter(
            article__author=request.user,
            article__is_published=True
        ).count(),
        'published_articles': request.user.articles.filter(is_published=True).count(),
        'draft_articles': request.user.articles.filter(is_published=False, published_at__isnull=True).count(),
    }
    
    # Mes articles les plus populaires (par nombre de likes)
    popular_articles = request.user.articles.filter(
        is_published=True
    ).annotate(
        total_likes=Count('likes'),
        total_views=Count('unique_views'),
        total_comments=Count('comments')
    ).order_by('-total_likes', '-total_views')[:5]
    
    context = {
        'liked_articles': liked_articles,
        'bookmarked_articles': bookmarked_articles,
        'my_articles': my_articles,
        'draft_articles': draft_articles,
        'unpublished_articles': unpublished_articles,
        'week_stats': week_stats,
        'total_stats': total_stats,
        'popular_articles': popular_articles,
    }
    
    return render(request, "blog/pages/users/dashboard.html", context)
