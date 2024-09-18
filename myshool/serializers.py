from rest_framework import serializers
from phonenumber_field.modelfields import PhoneNumberField
from .models import Academic_years, Trimestres, Roles, Admins, Classes, Profs, Matieres, Eleves, Interros, Devoirs

# Serializer pour le modèle Academic_years
class AcademicYearsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Academic_years
        fields = ['start', 'end', 'school_name']

# Serializer pour le modèle Trimestres
class TrimestresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trimestres
        fields = ['name']

# Serializer pour le modèle Roles
class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = ['name']

# Serializer pour le modèle Admins
class AdminsSerializer(serializers.ModelSerializer):
    role = RolesSerializer()  # Nested serializer for role

    class Meta:
        model = Admins
        fields = ['phone_num', 'role', 'code', 'firstname', 'lastname']

# Serializer pour le modèle Classes
class ClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classes
        fields = ['name']

# Serializer pour le modèle Profs
class ProfsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profs
        fields = ['phone_num', 'firstname', 'lastname']

# Serializer pour le modèle Matieres
class MatieresSerializer(serializers.ModelSerializer):
    classe = ClassesSerializer()  # Nested serializer for classe
    prof = ProfsSerializer()  # Nested serializer for prof

    class Meta:
        model = Matieres
        fields = ['name', 'coef', 'classe', 'prof']

# Serializer pour le modèle Eleves
class ElevesSerializer(serializers.ModelSerializer):
    classe = ClassesSerializer()  # Nested serializer for classe

    class Meta:
        model = Eleves
        fields = ['firstname', 'lastname', 'birth_date', 'classe']

# Serializer pour le modèle Interros
class InterrosSerializer(serializers.ModelSerializer):
    matiere = MatieresSerializer()  # Nested serializer for matiere
    eleve = ElevesSerializer()  # Nested serializer for eleve
    prof = ProfsSerializer()  # Nested serializer for prof
    trimestre = TrimestresSerializer()  # Nested serializer for trimestre

    class Meta:
        model = Interros
        fields = ['note', 'matiere', 'eleve', 'prof', 'trimestre']

# Serializer pour le modèle Devoirs
class DevoirsSerializer(serializers.ModelSerializer):
    matiere = MatieresSerializer()  # Nested serializer for matiere
    eleve = ElevesSerializer()  # Nested serializer for eleve
    prof = ProfsSerializer()  # Nested serializer for prof
    trimestre = TrimestresSerializer()  # Nested serializer for trimestre

    class Meta:
        model = Devoirs
        fields = ['note', 'matiere', 'eleve', 'prof', 'trimestre']

class PhoneNumberSerializer(serializers.Serializer):
    phone_num = PhoneNumberField()