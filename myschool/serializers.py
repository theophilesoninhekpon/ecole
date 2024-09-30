from re import U
from rest_framework import serializers
# from phonenumber_field.modelfields import PhoneNumberField
from .models import Academic_years, Trimestres, Classes, Matieres, Eleves, Interros, Devoirs, User

# Serializer pour le modèle Academic_years
class AcademicYearsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Academic_years
        fields = ['start', 'end', 'school_name']

class ClassesAllSerializer(serializers.ModelSerializer):
    class Meta:
        model= Classes
        fields = '__all__'
class MatieresAllSerializer(serializers.ModelSerializer):
    class Meta:
        model= Matieres
        fields = '__all__'
class ElevesAllSerializer(serializers.ModelSerializer):
    class Meta:
        model= Eleves 
        fields = '__all__'
        
class InterrosAllSerializer(serializers.ModelSerializer):
    class Meta:
        model= Interros
        fields = '__all__'
class DevoirsAllSerializer(serializers.ModelSerializer):
    class Meta:
        model= Devoirs
        fields = '__all__'
        
        
class ElevesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model= Eleves 
        fields = '__all__'


class EleveDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleves
        fields = ['id', 'firstname', 'lastname', 'birth_date', 'classe']

class EleveUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleves
        fields = ['firstname', 'lastname', 'birth_date', 'classe']

        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


# Serializer pour le modèle Matieres
class MatieresCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matieres
        fields = ['name', 'coef', 'prof']  # Prof peut être null ou déjà existant


'''
CREATION D'UNE CLASSE
'''
class ClasseCreateSerializer(serializers.ModelSerializer):
    matieres = MatieresCreateSerializer(many=True)  # Sérialiseur imbriqué pour créer les matières

    class Meta:
        model = Classes
        fields = ['name', 'matieres']

    def create(self, validated_data):        
        # Extraire les données des matières
        matieres_data = validated_data.pop('matieres')

        # Créer la classe
        classe = Classes.objects.create(**validated_data)

        # Créer chaque matière et lier à la classe
        for matiere_data in matieres_data:
            Matieres.objects.create(classe=classe, **matiere_data)

        return classe
    
    
        

'''
ENREGISTREMENT D'UN PROF et D'UN ADMIN
'''
    
class AdminRegisterSerializer(serializers.ModelSerializer):
    role = serializers.HiddenField(default='admin')  # Le rôle est défini automatiquement à 'admin'

    class Meta:
        model = User
        fields = ['username', 'password', 'phone_number', 'first_name', 'last_name', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.role = 'admin'  # Assigner le rôle admin
        user.save()
        return user
    
    
class ProfRegisterSerializer(serializers.ModelSerializer):
    role = serializers.HiddenField(default='prof')  # Le rôle est défini automatiquement à 'prof'
    matieres = serializers.PrimaryKeyRelatedField(queryset=Matieres.objects.all(), many=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'phone_number', 'first_name', 'last_name', 'role', 'matieres']

    def create(self, validated_data):
        matieres_data = validated_data.pop('matieres', [])  # On récupère les IDs des matières
        user = User.objects.create_user(**validated_data)  # Créer le professeur
        user.role = 'prof'
        user.save()

        # Assigner les matières au professeur si des IDs sont fournis
        if matieres_data:
            for matiere in matieres_data:
                matiere.prof = user  # Assigner le professeur à chaque matière
                matiere.save()

        return user
    

'''
RECUPERATION DES DONNES D'UN PROF
'''

# Serializer pour les interros sous forme de paires clé-valeur
class InterroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interros
        fields = ['numero', 'note']

    def to_representation(self, instance):
        return {instance.numero: instance.note}

# Serializer pour les devoirs sous forme de paires clé-valeur
class DevoirSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devoirs
        fields = ['numero', 'note']

    def to_representation(self, instance):
        return {instance.numero: instance.note}


# Serializer pour les élèves, leurs interros et devoirs dans un trimestre donné
class EleveTrimestreSerializer(serializers.ModelSerializer):
    interros = serializers.SerializerMethodField()
    devoirs = serializers.SerializerMethodField()

    class Meta:
        model = Eleves
        fields = ['firstname', 'lastname', 'interros', 'devoirs']

    def get_interros(self, obj):
        trimestre = self.context.get('trimestre')
        interros = Interros.objects.filter(eleve=obj, trimestre=trimestre).order_by('numero')
        return InterroSerializer(interros, many=True).data

    def get_devoirs(self, obj):
        trimestre = self.context.get('trimestre')
        devoirs = Devoirs.objects.filter(eleve=obj, trimestre=trimestre).order_by('numero')
        return DevoirSerializer(devoirs, many=True).data
    
    
class EleveDetailSerializer(serializers.ModelSerializer):
    trimestres = serializers.SerializerMethodField()

    class Meta:
        model = Eleves
        fields = ['id', 'firstname', 'lastname', 'birth_date', 'classe', 'trimestres']

    def get_trimestres(self, obj):
        # Créer un dictionnaire vide pour les trimestres
        trimestres_data = {}

        # Récupérer les matières de la classe de l'élève
        classe = obj.classe
        matieres = Matieres.objects.filter(classe=classe)

        # Pour chaque trimestre (1, 2, 3)
        for trimestre_num in [1, 2, 3]:
            matieres_data = []

            for matiere in matieres:
                prof = matiere.prof
                eleve = obj

                # Récupérer les interros pour ce trimestre et les trier par numéro
                interros = Interros.objects.filter(
                    matiere=matiere,
                    eleve=eleve,
                    trimestre=trimestre_num
                ).order_by('numero')

                interros_notes = {interro.numero: interro.note for interro in interros}

                # Récupérer les devoirs pour ce trimestre et les trier par numéro
                devoirs = Devoirs.objects.filter(
                    matiere=matiere,
                    eleve=eleve,
                    trimestre=trimestre_num
                ).order_by('numero')

                devoirs_notes = {devoir.numero: devoir.note for devoir in devoirs}

                # Ajouter les données de la matière dans ce trimestre
                matieres_data.append({
                    "matiere": matiere.name,
                    "coef": matiere.coef,
                    "prof": {
                        "id": prof.id if prof else None,
                        "username": prof.username if prof else None,
                        "first_name": prof.first_name if prof else None,
                        "last_name": prof.last_name if prof else None,
                    },
                    "interros": interros_notes,
                    "devoirs": devoirs_notes
                })

            # Ajouter les matières dans l'objet du trimestre
            trimestres_data[trimestre_num] = {
                "matieres": matieres_data
            }

        return trimestres_data



# Serializer pour un trimestre avec les élèves associés, sous forme de paires clé-valeur
class TrimestreSerializer(serializers.Serializer):
    trimestre = serializers.IntegerField()  # Numéro du trimestre
    eleves = serializers.SerializerMethodField()

    def get_eleves(self, obj):
        # Récupérer les élèves de la classe
        classe = self.context.get('classe')
        eleves = Eleves.objects.filter(classe=classe)

        # Récupérer les interros et devoirs de chaque élève pour le trimestre
        return EleveTrimestreSerializer(eleves, many=True, context={'trimestre': obj}).data

    def to_representation(self, instance):
        return {instance: super().to_representation(instance)}


# Serializer pour les matières avec trimestres, sous forme de paires clé-valeur
class MatieresSerializer(serializers.ModelSerializer):
    trimestres = serializers.SerializerMethodField()

    class Meta:
        model = Matieres
        fields = ['name', 'coef', 'classe', 'trimestres']

    def get_trimestres(self, obj):
        trimestres_data = [1, 2, 3]  # Les trois trimestres (Premier, Deuxième, Troisième)
        classe = obj.classe  # Récupérer la classe associée à la matière
        return TrimestreSerializer(trimestres_data, many=True, context={'classe': classe}).data
    
    
class MatieresMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matieres
        fields = ['name', 'coef']

# Serializer pour les classes associées au professeur
class ClassesSerializer(serializers.ModelSerializer):
    matieres = MatieresSerializer(many=True)

    class Meta:
        model = Classes
        fields = ['name', 'matieres']
        
# Serializer pour les classes associées au professeur
class ClassesMiniSerializer(serializers.ModelSerializer):
    matieres = MatieresSerializer(many=True)

    class Meta:
        model = Classes
        fields = ['name', 'matieres']


# Serializer pour le professeur avec ses classes, matières, trimestres, élèves, interros, et devoirs
class ProfesseurDetailSerializer(serializers.ModelSerializer):
    classes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'phone_number', 'first_name', 'last_name', 'classes']

    def get_classes(self, obj):
        # Récupérer les classes où le professeur enseigne
        classes = Classes.objects.filter(matieres__prof=obj)
        return ClassesSerializer(classes, many=True).data

class ProfesseurMiniDetailSerializer(serializers.ModelSerializer):
    classes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'phone_number', 'first_name', 'last_name', 'classes']

    def get_classes(self, obj):
        # Récupérer les classes où le professeur enseigne
        classes = Classes.objects.filter(matieres__prof=obj)
        return ClassesMiniSerializer(classes, many=True).data
