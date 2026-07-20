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
from django.views import View
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm

from .forms import OTPRequestForm
from .models import OTP
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


def inscription(request):
    if request.user.is_authenticated:
        return redirect("projects:liste_projets")
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            # create inactive user and send OTP for email verification
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            otp = OTP.create_for_user(user)
            send_mail(
                subject="Confirmez votre inscription",
                message=f"Votre code de confirmation : {otp.code}",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
                recipient_list=[user.email],
            )
            messages.success(request, "Un code de confirmation a été envoyé par e-mail.")
            url = reverse_lazy("accounts:otp_verify")
            return redirect(f"{url}?mode=signup&email={user.email}")
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


class OTPRequestView(View):
    def get(self, request):
        form = OTPRequestForm()
        return render(request, "accounts/otp_request.html", {"form": form})

    def post(self, request):
        form = OTPRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Aucun utilisateur trouvé pour cet e-mail.")
                return render(request, "accounts/otp_request.html", {"form": form})
            otp = OTP.create_for_user(user)
            send_mail(
                subject="Code de récupération",
                message=f"Votre code de récupération : {otp.code}",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
                recipient_list=[email],
            )
            messages.success(request, "Un code de récupération a été envoyé par e-mail.")
            url = reverse_lazy("accounts:otp_verify")
            return redirect(f"{url}?mode=recovery&email={email}")
        return render(request, "accounts/otp_request.html", {"form": form})
 

class OTPVerifyView(View):
    """Verify OTP for signup (activate user) or recovery (set new password).

    Flow:
    - GET: show verification form. Query params: mode=(signup|recovery), email.
    - POST: if verifying OTP, check and then:
        - signup: activate user, log in, redirect.
        - recovery: set session flag and redirect to same view to show password form.
    - POST with password fields when mode=recovery and session allows: set password and login.
    """

    def get(self, request):
        mode = request.GET.get("mode", "signup")
        email = request.GET.get("email", "")
        otp_form = OTPRequestForm(initial={"email": email})
        show_password = False
        return render(request, "accounts/otp_verify.html", {"otp_form": otp_form, "mode": mode, "show_password": show_password})

    def post(self, request):
        mode = request.GET.get("mode", "signup")
        # If setting new password for recovery
        if mode == "recovery" and request.session.get("otp_recovery_user"):
            user_id = request.session.get("otp_recovery_user")
            user = get_object_or_404(User, pk=user_id)
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                # cleanup session
                del request.session["otp_recovery_user"]
                messages.success(request, "Mot de passe mis à jour. Vous êtes connecté.")
                user.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, user)
                return redirect("projects:liste_projets")
            otp_form = OTPRequestForm(initial={"email": user.email})
            return render(request, "accounts/otp_verify.html", {"otp_form": otp_form, "mode": mode, "show_password": True, "set_form": form})

        # Otherwise, verify OTP
        otp_form = OTPRequestForm(request.POST)
        if otp_form.is_valid():
            email = otp_form.cleaned_data["email"]
            code = request.POST.get("code")
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Utilisateur introuvable.")
                return render(request, "accounts/otp_verify.html", {"otp_form": otp_form, "mode": mode})
            otp_qs = OTP.objects.filter(user=user, code=code, used=False).order_by("-created_at")
            if not otp_qs.exists():
                messages.error(request, "Code invalide.")
                return render(request, "accounts/otp_verify.html", {"otp_form": otp_form, "mode": mode})
            otp = otp_qs.first()
            if not otp.is_valid():
                messages.error(request, "Code expiré.")
                return render(request, "accounts/otp_verify.html", {"otp_form": otp_form, "mode": mode})
            otp.mark_used()
            if mode == "signup":
                user.is_active = True
                user.save()
                user.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, user)
                messages.success(request, "Compte activé et connecté.")
                return redirect("projects:liste_projets")
                else:  # recovery
                # allow password set
                request.session["otp_recovery_user"] = user.id
                url = reverse_lazy("accounts:otp_verify")
                return redirect(f"{url}?mode=recovery")
            return render(request, "accounts/otp_verify.html", {"otp_form": otp_form, "mode": mode})
