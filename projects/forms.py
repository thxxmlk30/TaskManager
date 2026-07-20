from django import forms
from django.contrib.auth import get_user_model

from .models import Projet, Tache

User = get_user_model()


class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ["nom", "description", "membres"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "membres": forms.SelectMultiple(attrs={"class": "form-select"}),
        }


class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = ["titre", "description", "assigne", "statut", "priorite", "date_echeance"]
        widgets = {
            "titre": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "assigne": forms.Select(attrs={"class": "form-select"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
            "priorite": forms.Select(attrs={"class": "form-select"}),
            "date_echeance": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, projet=None, **kwargs):
        super().__init__(*args, **kwargs)
        if projet is not None:
            # On ne propose que le créateur + les membres du projet comme assignables
            queryset = projet.membres.all() | User.objects.filter(pk=projet.createur_id)
            self.fields["assigne"].queryset = queryset.distinct()
