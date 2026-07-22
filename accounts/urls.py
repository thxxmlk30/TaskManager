from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.ConnexionView.as_view(), name="connexion"),
    path("deconnexion/", views.DeconnexionView.as_view(), name="deconnexion"),
    path("mot-de-passe-oublie/", views.PasswordResetRequestView.as_view(), name="password_reset"),
    path("mot-de-passe-oublie/done/", views.PasswordResetDone.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.PasswordResetConfirm.as_view(), name="password_reset_confirm"),
    path("reset/done/", views.PasswordResetComplete.as_view(), name="password_reset_complete"),
]
