"""
URLs pour l'authentification et la gestion des mots de passe
"""
from django.urls import path
from ..views import auth

urlpatterns = [
    # Authentification de base
    path("login/", auth.login_view, name="login"),
    path("register/", auth.register_view, name="register"),
    path("logout/", auth.logout_view, name="logout"),
    
    # Réinitialisation de mot de passe
    path("password-reset/", auth.CustomPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", auth.password_reset_done_view, name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", 
         auth.CustomPasswordResetConfirmView.as_view(), 
         name="password_reset_confirm"),
    path("password-reset/complete/", auth.password_reset_complete_view, name="password_reset_complete"),
    
    # Changement de mot de passe (utilisateur connecté)
    path("password-change/", auth.CustomPasswordChangeView.as_view(), name="password_change"),
    path("password-change/done/", auth.password_change_done_view, name="password_change_done"),
]
