from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from projects.models import Projet, Tache


class ProjetViewsTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        self.projet = Projet.objects.create(nom="Projet Alice", createur=self.alice)

    def test_liste_projets_redirige_si_non_connecte(self):
        response = self.client.get(reverse("projects:liste_projets"))
        self.assertEqual(response.status_code, 302)

    def test_liste_projets_affiche_seulement_les_projets_de_l_utilisateur(self):
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("projects:liste_projets"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Projet Alice")

    def test_createur_voit_son_projet(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(reverse("projects:liste_projets"))
        self.assertContains(response, "Projet Alice")

    def test_creation_projet_via_formulaire(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.post(
            reverse("projects:creer_projet"), {"nom": "Nouveau projet", "description": "Test"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Projet.objects.filter(nom="Nouveau projet").exists())

    def test_non_membre_ne_peut_pas_voir_le_detail(self):
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("projects:projet_detail", args=[self.projet.pk]))
        self.assertEqual(response.status_code, 403)

    def test_membre_peut_voir_le_detail(self):
        self.projet.membres.add(self.bob)
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("projects:projet_detail", args=[self.projet.pk]))
        self.assertEqual(response.status_code, 200)

    def test_seul_le_createur_peut_supprimer(self):
        self.projet.membres.add(self.bob)
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("projects:supprimer_projet", args=[self.projet.pk]))
        self.assertEqual(response.status_code, 403)


class TacheViewsTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.projet = Projet.objects.create(nom="Projet", createur=self.alice)
        self.client.login(username="alice", password="pass12345")

    def test_creation_tache(self):
        response = self.client.post(
            reverse("projects:creer_tache", args=[self.projet.pk]),
            {"titre": "Ma tâche", "statut": "a_faire", "priorite": "moyenne"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tache.objects.filter(titre="Ma tâche").exists())

    def test_suppression_tache(self):
        tache = Tache.objects.create(titre="À supprimer", projet=self.projet)
        response = self.client.post(
            reverse("projects:supprimer_tache", args=[self.projet.pk, tache.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tache.objects.filter(pk=tache.pk).exists())
