"""
URLs pour la gestion du profil utilisateur
"""
from django.urls import path
from ..views import user

app_name = 'users'

urlpatterns = [
    # Profil utilisateur
    path("", user.profile_view, name="profile"),
    path("dashboard/", user.dashboard_view, name="dashboard"),
    path("edit/", user.edit_profile_view, name="edit"),
    path("delete/", user.delete_account_view, name="delete"),
]
