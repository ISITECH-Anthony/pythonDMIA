"""
Utilitaires pour le système de logging de l'application blog.
"""

import logging
from functools import wraps
from django.conf import settings
from django.contrib.auth import get_user_model

# Récupération du logger pour l'application blog
logger = logging.getLogger("blog")


def log_user_action(action_type: str, user=None, details: str = None):
    """
    Log une action utilisateur avec des détails.

    Args:
        action_type: Type d'action (LOGIN, LOGOUT, CREATE_ARTICLE, etc.)
        user: Instance de l'utilisateur (optionnel)
        details: Détails supplémentaires (optionnel)
    """
    user_info = f"User {user.username} (ID: {user.id})" if user else "Anonymous user"
    message = f"[{action_type}] {user_info}"
    if details:
        message += f" - {details}"

    logger.info(message)


def log_error(error_type: str, error_message: str, user=None, extra_data: dict = None):
    """
    Log une erreur avec des informations contextuelles.

    Args:
        error_type: Type d'erreur
        error_message: Message d'erreur
        user: Utilisateur concerné (optionnel)
        extra_data: Données supplémentaires (optionnel)
    """
    user_info = f"User {user.username} (ID: {user.id})" if user else "System"
    message = f"[ERROR] {error_type} - {user_info}: {error_message}"

    if extra_data:
        message += f" | Extra data: {extra_data}"

    logger.error(message)


def log_view_access(view_name: str, user=None, request_method: str = None):
    """
    Log l'accès à une vue.

    Args:
        view_name: Nom de la vue
        user: Utilisateur qui accède à la vue
        request_method: Méthode HTTP utilisée
    """
    user_info = (
        f"User {user.username}" if user and user.is_authenticated else "Anonymous"
    )
    method_info = f"[{request_method}]" if request_method else ""

    logger.debug(f"View access {method_info}: {view_name} by {user_info}")


def logged_view(view_func):
    """
    Décorateur pour logger automatiquement l'accès aux vues.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        view_name = view_func.__name__
        user = getattr(request, "user", None)
        method = getattr(request, "method", None)

        log_view_access(view_name, user, method)

        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            log_error(
                error_type="VIEW_ERROR",
                error_message=str(e),
                user=user,
                extra_data={"view_name": view_name, "args": args, "kwargs": kwargs},
            )
            raise

    return wrapper


class DatabaseLogger:
    """
    Classe pour logger les opérations de base de données importantes.
    """

    @staticmethod
    def log_model_creation(model_instance, user=None):
        """Log la création d'un modèle."""
        model_name = model_instance.__class__.__name__
        instance_id = getattr(model_instance, "id", "Unknown")
        user_info = f" by {user.username}" if user else ""

        logger.info(f"[DB_CREATE] {model_name} (ID: {instance_id}) created{user_info}")

    @staticmethod
    def log_model_update(model_instance, user=None, changed_fields=None):
        """Log la mise à jour d'un modèle."""
        model_name = model_instance.__class__.__name__
        instance_id = getattr(model_instance, "id", "Unknown")
        user_info = f" by {user.username}" if user else ""
        fields_info = f" - Fields: {changed_fields}" if changed_fields else ""

        logger.info(
            f"[DB_UPDATE] {model_name} (ID: {instance_id}) updated{user_info}{fields_info}"
        )

    @staticmethod
    def log_model_deletion(model_instance, user=None):
        """Log la suppression d'un modèle."""
        model_name = model_instance.__class__.__name__
        instance_id = getattr(model_instance, "id", "Unknown")
        user_info = f" by {user.username}" if user else ""

        logger.info(f"[DB_DELETE] {model_name} (ID: {instance_id}) deleted{user_info}")


# Fonctions de logging spécifiques au blog
def log_article_action(action: str, article, user=None):
    """Log une action sur un article."""
    user_info = f" by {user.username}" if user else ""
    logger.info(
        f"[ARTICLE_{action.upper()}] Article '{article.title}' (ID: {article.id}){user_info}"
    )


def log_comment_action(action: str, comment, user=None):
    """Log une action sur un commentaire."""
    user_info = f" by {user.username}" if user else ""
    article_title = comment.article.title if hasattr(comment, "article") else "Unknown"
    logger.info(
        f"[COMMENT_{action.upper()}] Comment (ID: {comment.id}) on article '{article_title}'{user_info}"
    )


def log_authentication(action: str, user, success: bool = True, details: str = None):
    """Log les tentatives d'authentification."""
    status = "SUCCESS" if success else "FAILED"
    user_info = user.username if hasattr(user, "username") else str(user)
    details_info = f" - {details}" if details else ""

    logger.info(f"[AUTH_{action.upper()}] {status} for user {user_info}{details_info}")


# Exemples d'utilisation dans les commentaires
"""
Exemples d'utilisation :

# Dans une vue
from blog.logging_utils import log_user_action, logged_view

@logged_view
def my_view(request):
    # La vue sera automatiquement loggée
    pass

# Pour logger une action utilisateur
log_user_action("CREATE_ARTICLE", user=request.user, details="Article 'Mon titre' créé")

# Pour logger une erreur
log_error("VALIDATION_ERROR", "Email déjà utilisé", user=request.user)

# Dans un modèle (dans la méthode save par exemple)
from blog.logging_utils import DatabaseLogger

class Article(models.Model):
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            DatabaseLogger.log_model_creation(self)
"""
