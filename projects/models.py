from django.conf import settings
from django.db import models
from django.urls import reverse


class Projet(models.Model):
    """Un espace de travail collaboratif contenant des tâches."""

    nom = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projets_crees",
    )
    membres = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projets_membre",
        blank=True,
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse("projects:projet_detail", args=[self.pk])

    def nb_taches(self):
        return self.taches.count()

    def nb_taches_terminees(self):
        return self.taches.filter(statut="terminee").count()


class Tache(models.Model):
    """Le coeur de la plateforme : une tâche assignée dans un projet."""

    STATUT_CHOICES = [
        ("a_faire", "À faire"),
        ("en_cours", "En cours"),
        ("terminee", "Terminée"),
    ]

    PRIORITE_CHOICES = [
        ("basse", "Basse"),
        ("moyenne", "Moyenne"),
        ("haute", "Haute"),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="taches")
    assigne = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="taches_assignees",
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="a_faire")
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default="moyenne")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_echeance = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-priorite", "date_echeance"]

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse("projects:projet_detail", args=[self.projet.pk])
