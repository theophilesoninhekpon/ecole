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
        
class TrimestresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trimestres
        fields = ['start_date', 'end_date', 'is_active', 'academic_year']


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
            if not Matieres.objects.filter(classe=classe, name=matiere_data['name']).exists():
                Matieres.objects.create(classe=classe, **matiere_data)

        return classe
    
    
class ClasseDetailSerializer(serializers.ModelSerializer):
    trimestres = serializers.SerializerMethodField()

    class Meta:
        model = Classes
        fields = ['id', 'name', 'trimestres']

    def get_trimestres(self, obj):
        # Récupérer les trimestres associés à l'année académique de la classe
        academic_year = obj.academic_year
        trimestres = Trimestres.objects.filter(academic_year=academic_year)

        trimestres_data = {}

        # Récupérer les matières associées à la classe
        matieres = Matieres.objects.filter(classe=obj)

        # Pour chaque trimestre, organiser les informations
        for trimestre in trimestres:
            if trimestre.numero not in trimestres_data:
                trimestres_data[trimestre.numero] = {
                    "start_date": trimestre.start_date,
                    "end_date": trimestre.end_date,
                    "matieres": []
                }

            # Pour chaque matière, récupérer les élèves et leurs notes pour le trimestre actuel
            for matiere in matieres:
                eleves = Eleves.objects.filter(classe=obj)

                interros_data = {}
                devoirs_data = {}

                for eleve in eleves:
                    # Récupérer les interros
                    interros = Interros.objects.filter(
                        matiere=matiere,
                        eleve=eleve,
                        trimestre=trimestre
                    ).order_by('numero')

                    for interro in interros:
                        interros_data[interro.numero] = interro.note

                    # Récupérer les devoirs
                    devoirs = Devoirs.objects.filter(
                        matiere=matiere,
                        eleve=eleve,
                        trimestre=trimestre
                    ).order_by('numero')

                    for devoir in devoirs:
                        devoirs_data[devoir.numero] = devoir.note

                # Ajouter les informations de la matière
                trimestres_data[trimestre.numero]["matieres"].append({
                    "matiere": {
                        "id": matiere.id,
                        "name": matiere.name,
                        "coef": matiere.coef,
                        "prof": {
                            "id": matiere.prof.id,
                            "first_name": matiere.prof.first_name,
                            "last_name": matiere.prof.last_name,
                            "phone_number": matiere.prof.phone_number
                        }
                    },
                    "eleves": [
                        {
                            "eleve_id": eleve.id,
                            "firstname": eleve.firstname,
                            "lastname": eleve.lastname,
                            "interros": interros_data,
                            "devoirs": devoirs_data,
                        } for eleve in eleves
                    ]
                })

        return trimestres_data

    trimestres = serializers.SerializerMethodField()


'''
ENREGISTREMENT D'UN PROF et D'UN ADMIN
'''
    
class AdminRegisterSerializer(serializers.ModelSerializer):
    role = serializers.HiddenField(default='admin')  # Le rôle est défini automatiquement à 'admin'

    class Meta:
        model = User
        fields = ['username', 'password', 'phone_number', 'first_name', 'last_name', 'role', 'email']

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
RECUPERATION DES DONNEES D'UN PROF
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
        # Récupérer les trimestres associés à l'année académique de la classe de l'élève
        academic_year = obj.classe.academic_year
        trimestres = Trimestres.objects.filter(academic_year=academic_year)

        trimestres_data = {}

        # Récupérer les matières de la classe de l'élève
        matieres = Matieres.objects.filter(classe=obj.classe)

        for trimestre in trimestres:
            matieres_data = []

            for matiere in matieres:
                prof = matiere.prof
                eleve = obj

                # Récupérer les interros et devoirs pour ce trimestre et les trier par numéro
                interros = Interros.objects.filter(
                    matiere=matiere,
                    eleve=eleve,
                    trimestre=trimestre
                ).order_by('numero')

                interros_notes = {interro.numero: interro.note for interro in interros}

                devoirs = Devoirs.objects.filter(
                    matiere=matiere,
                    eleve=eleve,
                    trimestre=trimestre
                ).order_by('numero')

                devoirs_notes = {devoir.numero: devoir.note for devoir in devoirs}

                # Ajouter les données de la matière dans le trimestre
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
            trimestres_data[trimestre.numero] = {
                "start_date": trimestre.start_date,
                "end_date": trimestre.end_date,
                "matieres": matieres_data
            }

        return trimestres_data



# Serializer pour un trimestre avec les élèves associés sous forme de paires clé-valeur
class TrimestreSerializer(serializers.ModelSerializer):
    eleves = serializers.SerializerMethodField()

    class Meta:
        model = Trimestres
        fields = ['numero', 'start_date', 'end_date', 'eleves']

    def get_eleves(self, obj):
        # Récupérer la classe depuis le contexte
        classe = self.context.get('classe')

        # Récupérer tous les élèves de la classe
        eleves = Eleves.objects.filter(classe=classe)

        # Récupérer les interros et devoirs de chaque élève pour le trimestre
        return EleveTrimestreSerializer(eleves, many=True, context={'trimestre': obj}).data

    def to_representation(self, instance):
        # Représentation sous forme de paires clé-valeur
        return {
            f"{instance.numero}": super().to_representation(instance)
        }



# Serializer pour les matières avec trimestres sous forme de paires clé-valeur
class MatieresSerializer(serializers.ModelSerializer):
    trimestres = serializers.SerializerMethodField()

    class Meta:
        model = Matieres
        fields = ['name', 'coef', 'classe', 'trimestres']

    def get_trimestres(self, obj):
        # Récupérer les trimestres associés à l'année académique de la classe de la matière
        academic_year = obj.classe.academic_year
        trimestres = Trimestres.objects.filter(academic_year=academic_year)

        # Retourner les trimestres en utilisant le serializer TrimestreSerializer
        return TrimestreSerializer(trimestres, many=True, context={'classe': obj.classe}).data

    def to_representation(self, instance):
        # Représentation sous forme de paires clé-valeur pour les matières avec trimestres
        representation = super().to_representation(instance)
        return {
            f"{instance.name}": representation
        }


    
    
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
    matieres = MatieresMiniSerializer(many=True)

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




'''
SYNCHRONISATION
'''
class SyncInterroSerializer(serializers.Serializer):
    numero = serializers.IntegerField()
    note = serializers.IntegerField()

class SyncDevoirSerializer(serializers.Serializer):
    numero = serializers.IntegerField()
    note = serializers.IntegerField()

class SyncTrimestreSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    interros = SyncInterroSerializer(many=True)
    devoirs = SyncDevoirSerializer(many=True)

class SyncEleveSerializer(serializers.Serializer):
    id = serializers.IntegerField()  # ID de l'élève
    trimestres = SyncTrimestreSerializer(many=True)  # Liste des trimestres avec interros et devoirs
    
class SyncMatiereSerializer(serializers.Serializer):
    id = serializers.IntegerField()  # ID de la matière
    eleves = SyncEleveSerializer(many=True)  # Liste des élèves
    
class SyncClasseSerializer(serializers.Serializer):
    id = serializers.IntegerField()  # ID de la classe
    matieres = SyncMatiereSerializer(many=True)  # Liste des matières enseignées dans la classe

class SyncDataSerializer(serializers.Serializer):
    classes = SyncClasseSerializer(many=True)  # Liste des classes


    