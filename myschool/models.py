from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


# from phonenumber_field.modelfields import PhoneNumberField


class Trimestres(models.IntegerChoices):
    PREMIER = 1, 'Premier'
    DEUXIEME = 2, 'Deuxième'
    TROISIEME = 3, 'Troisième'


class Academic_years(models.Model):
    start = models.DateField()
    end = models.DateField()
    school_name = models.CharField(max_length=100)

# Un modèle d'utilisateur unique avec des rôles
class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    first_name = models.CharField(_("first name"), max_length=150, unique=True)
    last_name = models.CharField(_("last name"), max_length=150, unique=True)
    email = models.EmailField(_("email address"), unique=True)

    # Champ de rôle pour différencier admin et prof
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('prof', 'Professeur'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='prof')
    code = models.CharField(max_length=6, null=True, blank=True)
    code_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

class Classes(models.Model):
    name = models.CharField(max_length=10, unique=True)

class Matieres(models.Model):
    name = models.CharField(max_length=50)
    coef = models.IntegerField()
    classe = models.ForeignKey(Classes, on_delete=models.SET_NULL,related_name='matieres', null=True, blank=True)
    prof = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

class Eleves (models.Model):
    firstname = models.CharField(max_length=100, unique=True)
    lastname = models.CharField(max_length=100, unique=True)
    birth_date = models.DateField()
    classe = models.ForeignKey(Classes, on_delete=models.SET_NULL, null=True, blank=True)

class Interros(models.Model):
    numero = models.IntegerField()
    note = models.IntegerField()
    matiere = models.ForeignKey(Matieres, on_delete=models.CASCADE)
    eleve = models.ForeignKey(Eleves, on_delete=models.CASCADE)
    prof = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    trimestre = models.IntegerField(
        choices=Trimestres.choices,
        default=Trimestres.PREMIER
    )

class Devoirs(models.Model):
    numero = models.IntegerField()
    note = models.IntegerField()
    matiere = models.ForeignKey(Matieres, on_delete=models.CASCADE)
    eleve = models.ForeignKey(Eleves, on_delete=models.CASCADE)
    prof = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    trimestre = models.IntegerField(
        choices=Trimestres.choices,
        default=Trimestres.PREMIER
    )