"""
Paramètres Django du projet "Plateforme de Gestion de Tâches".

Ce fichier est conçu pour fonctionner à la fois :
- en local (DEBUG=True, base SQLite)
- en production sur Railway (DEBUG=False, PostgreSQL via DATABASE_URL)

Toutes les valeurs sensibles sont lues depuis des variables d'environnement
(fichier .env en local, "Variables" Railway en production).
"""

from pathlib import Path

import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Sécurité -------------------------------------------------------------

SECRET_KEY = config("SECRET_KEY", default="django-insecure-changeme-en-local-uniquement")

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

# Railway place l'application derrière un proxy HTTPS : on fait confiance
# à l'en-tête envoyé par Railway pour savoir que la requête est bien en HTTPS.
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS", default="", cast=Csv()
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Applications -----------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Applications du projet
    "accounts",
    "projects",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Base de données --------------------------------------------------------
# En local : SQLite (par défaut, aucune configuration nécessaire).
# En production (Railway) : la variable DATABASE_URL est fournie
# automatiquement par le service PostgreSQL ajouté au projet Railway.

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# --- Validation des mots de passe -------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalisation ---------------------------------------------------

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Fichiers statiques (CSS, JS, images) -----------------------------------
# Whitenoise sert les fichiers statiques directement depuis Gunicorn,
# sans avoir besoin d'un serveur web (Nginx) séparé : idéal pour un PaaS.

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Authentification --------------------------------------------------------

LOGIN_URL = "accounts:connexion"
LOGIN_REDIRECT_URL = "projects:liste_projets"
LOGOUT_REDIRECT_URL = "accounts:connexion"

# --- Sécurité supplémentaire en production ----------------------------------

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=(not DEBUG), cast=bool)
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --- Email ---------------------------------------------------------------
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@example.com")
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
    EMAIL_HOST = config("EMAIL_HOST", default="")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
