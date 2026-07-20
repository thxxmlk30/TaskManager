# Plateforme de Gestion de Tâches

Application web Django permettant à des équipes de créer des projets, d'assigner des tâches
à leurs membres et de suivre leur avancement. Projet réalisé dans le cadre du cours de
**Cloud Computing** — Licence Ingénierie Logiciel et Réseau, Université Numérique Cheikh
Hamidou Kane.

## Stack technique

- **Backend** : Django 6 (architecture MVT)
- **Base de données** : SQLite en local, PostgreSQL en production
- **Fichiers statiques** : Whitenoise
- **Serveur d'application** : Gunicorn
- **Tests** : unittest (Django) + pytest-django
- **CI/CD** : GitHub Actions
- **Hébergement** : Railway (PaaS)

## Démarrage rapide (local)

```bash
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

L'application est ensuite accessible sur http://127.0.0.1:8000

## Lancer les tests

```bash
pytest
```

## Déploiement

Voir le **Guide de reproduction de 0 au déploiement** fourni séparément, qui détaille pas
à pas : installation, développement local, tests, GitHub, CI/CD et déploiement sur Railway.

## Structure du projet

```
taskmanager/
├── config/          # Réglages et URLs globales du projet
├── accounts/        # Authentification (inscription, connexion, déconnexion)
├── projects/         # Projets et tâches (modèles, vues, formulaires)
├── templates/        # Gabarits HTML (Bootstrap 5)
├── .github/workflows/ci.yml   # Pipeline CI/CD
├── Procfile           # Commandes Railway (migration + lancement Gunicorn)
├── railway.json        # Configuration Railway (Infrastructure as Code)
└── requirements.txt
```
