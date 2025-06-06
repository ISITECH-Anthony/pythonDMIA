from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordChangeView,
)
from django.urls import reverse_lazy

# Import du système de logging
from ..logging_utils import log_authentication, log_user_action, log_error, logged_view
from ..forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
)


@logged_view
def login_view(request):
    """Vue pour la connexion des utilisateurs"""
    if request.user.is_authenticated:
        return redirect("blog:home")

    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # Logger la connexion réussie
            log_authentication("LOGIN", user, success=True)
            log_user_action(
                "LOGIN",
                user,
                f"Connexion depuis IP: {request.META.get('REMOTE_ADDR', 'Unknown')}",
            )

            messages.success(request, f"Bienvenue {user.get_full_name()} !")

            # Rediriger vers la page demandée ou vers l'accueil
            next_url = request.GET.get("next", "blog:home")
            return redirect(next_url)
        else:
            # Logger la tentative de connexion échouée
            username = form.cleaned_data.get("username", "Unknown")
            log_authentication(
                "LOGIN", username, success=False, details="Identifiants incorrects"
            )
            log_error(
                "AUTH_FAILED",
                f"Tentative de connexion échouée pour {username}",
                extra_data={"ip": request.META.get("REMOTE_ADDR")},
            )

            messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = CustomAuthenticationForm()

    return render(request, "blog/auth/login.html", {"form": form})


@logged_view
def register_view(request):
    """Vue pour l'inscription des utilisateurs"""
    if request.user.is_authenticated:
        return redirect("blog:home")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)

            # Logger l'inscription réussie
            log_authentication("REGISTER", user, success=True)
            log_user_action(
                "REGISTER",
                user,
                f"Nouveau compte créé depuis IP: {request.META.get('REMOTE_ADDR', 'Unknown')}",
            )

            messages.success(
                request, f"Compte créé avec succès ! Bienvenue {user.get_full_name()} !"
            )
            return redirect("blog:home")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CustomUserCreationForm()

    return render(request, "blog/auth/register.html", {"form": form})


def logout_view(request):
    """Vue pour la déconnexion des utilisateurs"""
    if request.user.is_authenticated:
        messages.success(request, f"Au revoir {request.user.get_full_name()} !")
        auth_logout(request)
    return redirect("blog:home")


class CustomPasswordResetView(PasswordResetView):
    """Vue personnalisée pour la demande de réinitialisation de mot de passe"""

    form_class = CustomPasswordResetForm
    template_name = "blog/auth/password/reset.html"
    email_template_name = "blog/auth/password/reset_email.html"
    subject_template_name = "blog/auth/password/reset_subject.txt"
    success_url = reverse_lazy("blog:password_reset_done")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Un email de réinitialisation a été envoyé à votre adresse email.",
        )
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Vue personnalisée pour la confirmation de réinitialisation de mot de passe"""

    form_class = CustomSetPasswordForm
    template_name = "blog/auth/password/reset_confirm.html"
    success_url = reverse_lazy("blog:password_reset_complete")

    def form_valid(self, form):
        messages.success(
            self.request, "Votre mot de passe a été réinitialisé avec succès!"
        )
        return super().form_valid(form)


def password_reset_done_view(request):
    """Vue pour confirmer l'envoi de l'email de réinitialisation"""
    return render(request, "blog/auth/password/reset_done.html")


def password_reset_complete_view(request):
    """Vue pour confirmer la réinitialisation du mot de passe"""
    return render(request, "blog/auth/password/reset_complete.html")


class CustomPasswordChangeView(PasswordChangeView):
    """Vue personnalisée pour le changement de mot de passe"""

    template_name = "blog/auth/password/change.html"
    success_url = reverse_lazy("blog:password_change_done")

    def form_valid(self, form):
        messages.success(self.request, "Votre mot de passe a été changé avec succès!")
        return super().form_valid(form)


def password_change_done_view(request):
    """Vue pour confirmer le changement de mot de passe"""
    return render(request, "blog/auth/password/change_done.html")
