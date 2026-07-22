from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import InscriptionForm

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.contrib import messages


def inscription(request):
    if request.user.is_authenticated:
        return redirect("projects:liste_projets")
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, "Votre compte a été créé et vous êtes connecté.")
            return redirect("projects:liste_projets")
    else:
        form = InscriptionForm()
    return render(request, "accounts/inscription.html", {"form": form})


class ConnexionView(LoginView):
    template_name = "accounts/connexion.html"


class DeconnexionView(LogoutView):
    next_page = reverse_lazy("accounts:connexion")


class PasswordResetRequestView(PasswordResetView):
    template_name = "accounts/password_reset_form.html"
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")


class PasswordResetDone(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class PasswordResetConfirm(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
