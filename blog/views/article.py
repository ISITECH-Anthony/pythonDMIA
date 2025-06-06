from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Count
from datetime import datetime, timedelta
from django.utils import timezone
import json
import os
from pathlib import Path

from ..models import Article, Category, Comment, Like, Bookmark, ArticleView
from ..forms import ArticleForm, CommentForm
from ..utils import get_client_ip
from ..services.gemini import GeminiService


@login_required
def add_article(request):
    """Vue pour ajouter un nouvel article"""
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)

        # Vérifier s'il y a une image générée par IA
        ai_image_path = request.POST.get("ai_generated_image_path", "").strip()

        # Si pas d'image uploadée mais qu'il y a une image IA, on l'utilise
        if not request.FILES.get("image") and ai_image_path:
            try:
                # Construire le chemin complet vers l'image générée
                from django.conf import settings

                full_image_path = os.path.join(
                    settings.MEDIA_ROOT, ai_image_path.replace("/media/", "")
                )

                if os.path.exists(full_image_path):
                    # Lire le fichier image
                    with open(full_image_path, "rb") as img_file:
                        image_content = img_file.read()

                    # Créer un objet ContentFile pour Django
                    image_name = os.path.basename(full_image_path)
                    content_file = ContentFile(image_content, name=image_name)

                    # Modifier temporairement le champ image du formulaire
                    form.files = form.files.copy()  # Créer une copie modifiable
                    form.files["image"] = content_file

                    print(f"Image IA utilisée: {ai_image_path}")
                else:
                    print(f"Image IA introuvable: {full_image_path}")
            except Exception as e:
                print(f"Erreur lors du traitement de l'image IA: {e}")

        print(f"Received POST request to add article : {form.is_valid()}")
        if form.is_valid():
            article = form.save(commit=False)
            article.author = (
                request.user
            )  # Assigner l'utilisateur connecté comme auteur

            # Déterminer si l'article doit être publié ou sauvegardé en brouillon
            action = request.POST.get("action")
            if action == "draft":
                article.is_published = False
                # Ne pas définir published_at pour un brouillon
                article.save()
                messages.success(
                    request, "Article sauvegardé en brouillon avec succès!"
                )
            else:  # action == 'publish' ou pas d'action spécifiée (par défaut on publie)
                article.save()  # Sauver d'abord l'article
                article.publish()  # Puis utiliser la méthode publish()
                messages.success(request, "Article publié avec succès!")

            # Sauvegarder les tags - le formulaire s'en charge déjà dans sa méthode save()
            form.save(commit=True)
            return redirect("blog:home")
    else:
        form = ArticleForm()

    # Récupérer toutes les catégories pour les afficher dans le template
    categories = Category.objects.all().order_by("name")

    context = {
        "form": form,
        "categories": categories,
    }
    return render(request, "blog/pages/articles/create.html", context)


def article_detail(request, slug):
    """Vue pour afficher le détail d'un article avec ses commentaires"""
    article = get_object_or_404(
        Article.objects.select_related("category", "author").prefetch_related("tags"),
        slug=slug,
    )

    # Contrôle d'accès : seuls les articles publiés sont accessibles publiquement
    # Les brouillons et articles dépubliés ne sont accessibles qu'à leur auteur
    if not article.is_published:
        if not request.user.is_authenticated or request.user != article.author:
            messages.error(request, "Cet article n'est pas accessible.")
            return redirect("blog:home")

    # Enregistrer une vue unique seulement si l'utilisateur ne regarde pas son propre article
    if not (request.user.is_authenticated and request.user == article.author):
        client_ip = get_client_ip(request)

        if request.user.is_authenticated:
            # Pour les utilisateurs connectés, on vérifie par utilisateur
            ArticleView.objects.get_or_create(
                article=article, user=request.user, defaults={"ip_address": client_ip}
            )
        else:
            # Pour les utilisateurs anonymes, on vérifie par IP
            ArticleView.objects.get_or_create(
                article=article, ip_address=client_ip, user=None
            )

    comments = article.comments.all()

    if request.method == "POST" and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            messages.success(request, "Votre commentaire a été ajouté avec succès!")
            return redirect("blog:articles:detail", slug=slug)
    else:
        comment_form = CommentForm()

    # Vérifier si l'utilisateur a liké et/ou bookmarké cet article
    user_liked = False
    user_bookmarked = False
    is_author = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, article=article).exists()
        user_bookmarked = Bookmark.objects.filter(
            user=request.user, article=article
        ).exists()
        is_author = request.user == article.author

    # Récupérer des articles recommandés (même catégorie, pas le même article, max 2)
    recommended_articles_queryset = (
        Article.objects.filter(category=article.category, is_published=True)
        .exclude(pk=article.pk)
        .select_related("category")
    )

    # Exclure les articles de l'utilisateur connecté s'il est connecté
    if request.user.is_authenticated:
        recommended_articles_queryset = recommended_articles_queryset.exclude(
            author=request.user
        )

    recommended_articles = recommended_articles_queryset.order_by("-published_at")[:3]

    context = {
        "article": article,
        "comments": comments,
        "comment_form": comment_form,
        "comments_count": comments.count(),
        "likes_count": article.likes.count(),
        "user_liked": user_liked,
        "user_bookmarked": user_bookmarked,
        "is_author": is_author,
        "recommended_articles": recommended_articles,
    }
    return render(request, "blog/pages/articles/detail.html", context)


def articles_list(request):
    """Vue pour lister tous les articles"""
    # Récupérer tous les articles publiés
    articles_queryset = (
        Article.objects.filter(is_published=True)
        .select_related("author", "category")
        .prefetch_related("tags", "likes", "comments", "unique_views")
        .order_by("-created_at")
    )

    # Récupérer toutes les catégories avec le nombre d'articles publiés pour chacune
    from django.db.models import Q

    categories = Category.objects.annotate(
        published_articles_count=Count(
            "articles", filter=Q(articles__is_published=True)
        )
    ).order_by("name")

    # Gérer les paramètres de recherche et de tri
    search_query = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort", "recent")
    category_filter = request.GET.get("category", "")

    # Appliquer la recherche textuelle
    if search_query:
        articles_queryset = (
            articles_queryset.filter(title__icontains=search_query)
            | articles_queryset.filter(content__icontains=search_query)
            | articles_queryset.filter(author__username__icontains=search_query)
            | articles_queryset.filter(author__first_name__icontains=search_query)
            | articles_queryset.filter(author__last_name__icontains=search_query)
        )

    # Appliquer le filtre par catégorie
    selected_category = None
    if category_filter and category_filter != "all":
        articles_queryset = articles_queryset.filter(category__slug=category_filter)
        # Récupérer l'objet catégorie sélectionnée pour l'affichage
        try:
            selected_category = Category.objects.get(slug=category_filter)
        except Category.DoesNotExist:
            selected_category = None

    # Appliquer le tri
    if sort_by == "popular":
        articles_queryset = articles_queryset.annotate(
            total_likes=Count("likes")
        ).order_by("-total_likes", "-created_at")
    elif sort_by == "viewed":
        articles_queryset = articles_queryset.annotate(
            total_views=Count("unique_views")
        ).order_by("-total_views", "-created_at")
    elif sort_by == "commented":
        articles_queryset = articles_queryset.annotate(
            total_comments=Count("comments")
        ).order_by("-total_comments", "-created_at")
    else:  # recent par défaut
        articles_queryset = articles_queryset.order_by("-created_at")

    # Pagination - 9 articles par page
    paginator = Paginator(articles_queryset, 9)
    page_number = request.GET.get("page")
    articles = paginator.get_page(page_number)

    # Calculer les statistiques
    total_views = ArticleView.objects.filter(article__is_published=True).count()
    total_articles = Article.objects.filter(is_published=True).count()

    # Articles de cette semaine
    one_week_ago = timezone.now() - timedelta(days=7)
    articles_this_week = Article.objects.filter(
        is_published=True, created_at__gte=one_week_ago
    ).count()

    # Total des commentaires
    total_comments = Comment.objects.filter(article__is_published=True).count()

    context = {
        "articles": articles,
        "categories": categories,
        "selected_category": selected_category,
        "total_views": total_views,
        "total_articles": total_articles,
        "articles_this_week": articles_this_week,
        "total_comments": total_comments,
        "search_query": search_query,
        "sort_by": sort_by,
        "category_filter": category_filter,
    }
    return render(request, "blog/pages/articles/list.html", context)


@login_required
@require_http_methods(["POST"])
def delete_article(request, article_id):
    """Vue pour supprimer définitivement un article"""
    article = get_object_or_404(Article, id=article_id, author=request.user)

    # Stocker le titre pour le message de confirmation
    article_title = article.title

    # Supprimer l'article (Django supprimera automatiquement les objets liés grâce aux CASCADE)
    article.delete()

    messages.success(
        request, f"L'article '{article_title}' a été supprimé définitivement."
    )

    # Rediriger vers la liste des articles
    return redirect("blog:articles:list")


@login_required
@require_http_methods(["POST"])
def delete_comment(request, comment_id):
    """Vue pour supprimer un commentaire (seulement l'auteur peut supprimer)"""
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.user != comment.author and not request.user.is_staff:
        messages.error(
            request, "Vous ne pouvez supprimer que vos propres commentaires."
        )
        return redirect("blog:articles:detail", slug=comment.article.slug)

    if request.method == "POST":
        article_slug = comment.article.slug
        comment.delete()
        if request.user == comment.author:
            messages.success(request, "Votre commentaire a été supprimé avec succès.")
        else:
            messages.success(request, "Le commentaire a été supprimé avec succès.")
        return redirect("blog:articles:detail", slug=article_slug)

    return redirect("blog:articles:detail", slug=comment.article.slug)


@login_required
def toggle_like(request, article_id):
    """Vue pour liker/unliker un article"""
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    article = get_object_or_404(Article, id=article_id)

    # Empêcher l'auteur d'aimer son propre article
    if request.user == article.author:
        return JsonResponse(
            {"error": "Vous ne pouvez pas aimer votre propre article"}, status=403
        )

    like, created = Like.objects.get_or_create(user=request.user, article=article)

    if not created:
        # Si le like existe déjà, on le supprime (unlike)
        like.delete()
        liked = False
        message = "Article retiré de vos favoris"
    else:
        # Sinon, le like est créé
        liked = True
        message = "Article ajouté à vos favoris"

    # Compter le nombre total de likes pour cet article
    likes_count = article.likes.count()

    return JsonResponse(
        {
            "success": True,
            "liked": liked,
            "likes_count": likes_count,
            "message": message,
        }
    )


@login_required
def toggle_bookmark(request, article_id):
    """Vue pour bookmarker/unbookmarker un article"""
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    article = get_object_or_404(Article, id=article_id)

    # Empêcher l'auteur de bookmarker son propre article
    if request.user == article.author:
        return JsonResponse(
            {"error": "Vous ne pouvez pas ajouter votre propre article aux favoris"},
            status=403,
        )

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user, article=article
    )

    if not created:
        # Si le bookmark existe déjà, on le supprime
        bookmark.delete()
        bookmarked = False
        message = "Article retiré de vos signets"
    else:
        # Sinon, le bookmark est créé
        bookmarked = True
        message = "Article ajouté à vos signets"

    return JsonResponse({"success": True, "bookmarked": bookmarked, "message": message})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def generate_article_with_ai(request):
    """Génère un article avec l'IA Gemini"""
    try:
        # Parser les données JSON de la requête
        data = json.loads(request.body)
        user_prompt = data.get("prompt", "").strip()
        options = data.get("options", {})

        # Validation des données
        if not user_prompt:
            return JsonResponse(
                {"success": False, "error": "Le prompt est requis"}, status=400
            )

        if len(user_prompt) > 500:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Le prompt ne peut pas dépasser 500 caractères",
                },
                status=400,
            )

        # Validation des options
        valid_lengths = ["short", "medium", "long"]
        valid_tones = [
            "professional",
            "casual",
            "educational",
            "entertaining",
            "persuasive",
        ]

        length = options.get("length", "medium")
        tone = options.get("tone", "professional")
        generate_image = options.get("generate_image", False)

        if length not in valid_lengths:
            length = "medium"
        if tone not in valid_tones:
            tone = "professional"

        # Initialiser le service Gemini
        try:
            gemini_service = GeminiService()
        except ValueError as e:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Service IA non configuré. Contactez l'administrateur.",
                },
                status=503,
            )

        # Générer l'article
        result = gemini_service.generate_article(
            user_prompt,
            {"length": length, "tone": tone, "generate_image": generate_image},
        )

        if result["success"]:
            return JsonResponse({"success": True, "data": result["data"]})
        else:
            return JsonResponse(
                {
                    "success": False,
                    "error": result.get(
                        "error", "Erreur inconnue lors de la génération"
                    ),
                },
                status=500,
            )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Format de données invalide"}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Erreur serveur: {str(e)}"}, status=500
        )


@login_required
@require_http_methods(["POST"])
def publish_article(request, article_id):
    """Vue pour publier un article (brouillon ou dépublié)"""
    article = get_object_or_404(Article, id=article_id, author=request.user)

    if article.is_published:
        messages.warning(request, "Cet article est déjà publié.")
    else:
        article.publish()
        if article.published_at:
            messages.success(request, "Article publié avec succès!")
        else:
            messages.success(request, "Brouillon publié avec succès!")

    return redirect("blog:articles:detail", slug=article.slug)


@login_required
@require_http_methods(["POST"])
def unpublish_article(request, article_id):
    """Vue pour dépublier un article"""
    article = get_object_or_404(Article, id=article_id, author=request.user)

    if not article.is_published:
        if article.is_draft:
            messages.warning(request, "Cet article est déjà un brouillon.")
        else:
            messages.warning(request, "Cet article est déjà dépublié.")
    else:
        article.unpublish()
        messages.success(request, "Article dépublié avec succès!")

    return redirect("blog:articles:detail", slug=article.slug)


@login_required
def edit_article(request, slug):
    """Vue pour éditer un article existant"""
    article = get_object_or_404(Article, slug=slug, author=request.user)

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)

        if form.is_valid():
            # Déterminer si l'article doit être publié ou sauvegardé en brouillon
            action = request.POST.get("action")
            article = form.save(commit=False)

            if action == "draft":
                article.is_published = False
                article.published_at = (
                    None  # Reset la date de publication si mis en brouillon
                )
                article.save()
                messages.success(request, "Article modifié et sauvegardé en brouillon!")
            else:  # action == 'publish' ou pas d'action spécifiée
                if not article.is_published:
                    # Si l'article n'était pas publié, on utilise la méthode publish()
                    article.save()
                    article.publish()
                    messages.success(request, "Article modifié et publié avec succès!")
                else:
                    # Si l'article était déjà publié, on garde la date de publication originale
                    article.save()
                    messages.success(request, "Article modifié avec succès!")

            # Sauvegarder les tags
            form.save(commit=True)
            return redirect("blog:articles:detail", slug=article.slug)
    else:
        form = ArticleForm(instance=article)

    # Récupérer toutes les catégories pour les afficher dans le template
    categories = Category.objects.all().order_by("name")

    context = {
        "form": form,
        "categories": categories,
        "article": article,
        "is_editing": True,
    }
    return render(request, "blog/pages/articles/edit.html", context)
