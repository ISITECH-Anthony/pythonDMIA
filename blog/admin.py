from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Article, Comment, Category, Tag, ArticleView, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email", 
        "get_full_name",
        "avatar_thumbnail",
        "is_staff",
        "is_active",
        "date_joined",
        "articles_count",
        "total_views"
    )
    list_filter = ("is_staff", "is_active", "date_joined", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    
    # Configuration des champs dans le formulaire de détail
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Informations personnelles", {"fields": ("first_name", "last_name", "email", "bio", "avatar")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates importantes", {"fields": ("last_login", "date_joined")}),
    )
    
    # Configuration pour la création d'un nouvel utilisateur
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "first_name", "last_name", "password1", "password2"),
        }),
    )
    
    readonly_fields = ("date_joined", "last_login")

    def avatar_thumbnail(self, obj):
        """Affiche une miniature de l'avatar"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url
            )
        else:
            # Affichage des initiales si pas d'avatar
            return format_html(
                '<div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(45deg, #3B82F6, #8B5CF6); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px;">{}</div>',
                obj.get_initials()
            )
    
    avatar_thumbnail.short_description = "Avatar"

    def articles_count(self, obj):
        """Compte le nombre d'articles de l'utilisateur"""
        from .models import Article
        return Article.objects.filter(author=obj).count()
    
    articles_count.short_description = "Articles"

    def total_views(self, obj):
        """Affiche le nombre total de vues pour tous les articles de l'auteur"""
        return obj.get_total_views()
    
    total_views.short_description = "Vues totales"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name",)
    fields = ("name", "color")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("icon", "name", "slug", "color", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    fields = ("icon", "name", "slug", "description", "color")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "has_image",
        "is_published",
        "created_at",
    )
    list_filter = ("created_at", "author", "category", "is_published")
    search_fields = ("title", "content", "author__username")
    fields = ("title", "content", "author", "category", "image", "is_published")

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = "Image"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "article", "created_at")
    list_filter = ("created_at", "article")
    search_fields = ("author", "content")
    raw_id_fields = ("article",)


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ("article", "ip_address", "viewed_at")
    list_filter = ("viewed_at", "article__author", "article__category")
    search_fields = ("article__title", "ip_address")
    raw_id_fields = ("article",)
    readonly_fields = ("viewed_at",)

    def has_add_permission(self, request):
        # Empêcher l'ajout manuel de vues
        return False
