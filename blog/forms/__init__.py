# Imports des formulaires pour faciliter l'utilisation
from .auth import CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm
from .user import UserProfileForm
from .article import ArticleForm, CommentForm

__all__ = [
    'CustomUserCreationForm', 
    'CustomAuthenticationForm',
    'CustomPasswordResetForm',
    'CustomSetPasswordForm',
    'UserProfileForm',
    'ArticleForm', 
    'CommentForm'
]
