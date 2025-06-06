from django import template
from django.contrib.auth.models import AnonymousUser
from urllib.parse import urlencode

register = template.Library()


@register.filter
def is_bookmarked_by(article, user):
    """
    Template filter pour vérifier si un article est mis en favoris par un utilisateur
    Usage: {{ article|is_bookmarked_by:user }}
    """
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return False
    return article.is_bookmarked_by(user)


@register.filter
def abs_diff(value, arg):
    """
    Calcule la différence absolue entre deux valeurs
    Usage: {{ page_number|abs_diff:current_page }}
    """
    try:
        return abs(int(value) - int(arg))
    except (ValueError, TypeError):
        return 0


@register.simple_tag
def url_replace(request, field, value):
    """
    Template tag pour remplacer ou ajouter un paramètre GET dans l'URL actuelle
    Usage: {% url_replace request 'page' 2 %}
    """
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()


@register.simple_tag
def pagination_url(request, page_number):
    """
    Template tag spécialement conçu pour la pagination qui préserve tous les paramètres existants
    Usage: {% pagination_url request 2 %}
    """
    dict_ = request.GET.copy()
    dict_['page'] = page_number
    return '?' + dict_.urlencode() if dict_.urlencode() else '?page=' + str(page_number)
