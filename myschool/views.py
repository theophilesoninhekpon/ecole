import asyncio
from datetime import timedelta, timezone
import datetime
import random
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from myschool.sms_client import SMSClient
from .serializers import AdminRegisterSerializer, ClasseCreateSerializer, ClasseDetailSerializer, EleveDetailSerializer, EleveUpdateSerializer, ElevesCreateSerializer, ProfRegisterSerializer, ProfesseurDetailSerializer, ProfesseurMiniDetailSerializer, SyncDataSerializer, TrimestresSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from .models import Academic_years, Trimestres, Classes, Matieres, Eleves, Interros, Devoirs, User
from .serializers import (
    AcademicYearsSerializer, ClassesAllSerializer, MatieresAllSerializer, ElevesAllSerializer, InterrosAllSerializer, DevoirsAllSerializer
)

# ViewSet pour Academic_years
class AcademicYearsViewSet(viewsets.ModelViewSet):
    queryset = Academic_years.objects.all()
    serializer_class = AcademicYearsSerializer


# ViewSet pour Classes
class ClassesViewSet(viewsets.ModelViewSet):
    queryset = Classes.objects.all()
    serializer_class = ClassesAllSerializer


# ViewSet pour Matieres
class MatieresViewSet(viewsets.ModelViewSet):
    queryset = Matieres.objects.all()
    serializer_class = MatieresAllSerializer

# ViewSet pour Eleves
class ElevesViewSet(viewsets.ModelViewSet):
    queryset = Eleves.objects.all()
    serializer_class = ElevesAllSerializer

# ViewSet pour Interros
class InterrosViewSet(viewsets.ModelViewSet):
    queryset = Interros.objects.all()
    serializer_class = InterrosAllSerializer

# ViewSet pour Devoirs
class DevoirsViewSet(viewsets.ModelViewSet):
    queryset = Devoirs.objects.all()
    serializer_class = DevoirsAllSerializer


class TrimestresViewSet(viewsets.ModelViewSet):
    queryset = Trimestres.objects.all()
    serializer_class = TrimestresSerializer

    def create(self, request, *args, **kwargs):
        # Récupérer l'année académique à partir des données
        academic_year_id = request.data.get('academic_year')
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        if start_date >= end_date:
            return JsonResponse({"error": "La date de fin doit être supérieure à la date de début."}, status=status.HTTP_400_BAD_REQUEST)
            
        print(academic_year_id)
        # Trouver le dernier trimestre actif
        last_trimester = Trimestres.objects.filter(
            academic_year=academic_year_id,
            is_active=True
        ).order_by('numero').last()  # Récupère le dernier trimestre actif
        
        # Déterminer le numéro du nouveau trimestre
        if last_trimester:
            current_number = last_trimester.numero + 1
        else:
            current_number = 1  # Si aucun trimestre n'existe, commencer par 1

        # Vérifier que le numéro ne dépasse pas 3
        if current_number > 3:
            return JsonResponse({"error": "Vous ne pouvez pas créer plus de 3 trimestres."}, status=status.HTTP_400_BAD_REQUEST)

        # Désactiver le trimestre précédent, s'il existe
        if last_trimester and last_trimester.numero == current_number - 1:
            last_trimester.is_active = False
            last_trimester.save()

        # Créer un nouveau trimestre
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ajouter le numéro du trimestre
        serializer.validated_data['numero'] = current_number
        
        self.perform_create(serializer)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)


class RequestPhoneNumberView(APIView):
    def post(self, request):
        phone_num = request.data.get('phone_number')
        
        # Essayer de récupérer l'utilisateur par son numéro de téléphone
        try:
            user = User.objects.get(phone_number=phone_num)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Numéro de téléphone non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Générer un code de vérification à 6 chiffres
        code = str(random.randint(100000, 999999))
        
        # Stocker le code dans le profil utilisateur (sans modifier le mot de passe)
        user.code = code
        user.code_created_at = datetime.datetime.now()

        user.save()

        # Envoyer le code par SMS
        sms_client = SMSClient()
        try:
            asyncio.run(sms_client.send_message(code, user.phone_number))
        except Exception as e:
            return JsonResponse({'error': 'Échec de l\'envoi du SMS: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({'message': 'Code envoyé par SMS.'}, status=status.HTTP_200_OK)



class VerifyCodeView(APIView):
    def post(self, request):
        phone_num = request.data.get('phone_number')
        code = request.data.get('code')

        try:
            user = User.objects.get(phone_number=phone_num)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Numéro de téléphone non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        # Vérifier si le code a expiré (10 minutes d'expiration par exemple)
        if user.code and user.code_created_at:
            if timezone.now() - user.code_created_at > timedelta(minutes=1):
                return JsonResponse({'error': 'Le code a expiré.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.code == code:
            # Générer un token d'authentification
            token, created = Token.objects.get_or_create(user=user)

            # Réinitialiser le code et l'heure de création
            user.code = None
            user.code_created_at = None
            user.save()

            return JsonResponse({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': 'Code invalide.'}, status=status.HTTP_400_BAD_REQUEST)
   
        
'''
Création d'une classe
'''
class ClasseCreateAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = ClasseCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()  # Création de la classe avec les matières
                return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return JsonResponse({"detail": "Erreur :" + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ClasseDetailAPIView(APIView):
    def get(self, request, classe_id, *args, **kwargs):
        try:
            # Récupérer la classe en fonction de l'ID
            classe = get_object_or_404(Classes, id=classe_id)

            # Sérialiser les données de la classe
            serializer = ClasseDetailSerializer(classe)

            # Retourner la réponse avec les données sérialisées
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"detail": "Erreur :" + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        

class AdminRegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = AdminRegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()  # Création de l'utilisateur admin
                
                if user:
                    # Générer un code de vérification à 6 chiffres
                    code = str(random.randint(100000, 999999))
                    
                    # Stocker le code dans le profil utilisateur (sans modifier le mot de passe)
                    user.code = code
                    user.code_created_at = datetime.datetime.now()

                    user.save()

                    # Envoyer le code par SMS
                    sms_client = SMSClient()
                    try:
                        asyncio.run(sms_client.send_message(code, user.phone_number))
                    except Exception as e:
                        return JsonResponse({'error': 'Échec de l\'envoi du SMS: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return JsonResponse({'message': 'Code envoyé par SMS.'}, status=status.HTTP_200_OK)
                # return JsonResponse({"message": f"Admin {user.username} created successfully."}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"detail": "Erreur :" + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class ProfRegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = ProfRegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()  # Création de l'utilisateur prof et assignation des matières
                return JsonResponse({"message": f"Prof {user.username} created successfully."}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"detail": "Erreur :" + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


'''
ELEVE
'''
class EleveCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = ElevesCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                eleve = serializer.save()  # Créer l'élève avec les données validées
                return JsonResponse({"message": f"Élève {eleve.firstname} {eleve.lastname} créé avec succès."}, status=status.HTTP_201_CREATED)
            
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"detail": "Erreur :" + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class EleveDetailAPIView(APIView):
    def get(self, request, eleve_id, *args, **kwargs):
        try:
            # Récupérer l'élève par son ID
            eleve = get_object_or_404(Eleves, id=eleve_id)

            # Sérialiser les données de l'élève avec les matières, profs et notes
            serializer = EleveDetailSerializer(eleve)

            # Retourner la réponse avec les données sérialisées
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"detail": "Erreur :" + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        
class EleveUpdateAPIView(APIView):
    def put(self, request, eleve_id, *args, **kwargs):
        try:
            eleve = get_object_or_404(Eleves, id=eleve_id)  # Récupérer l'élève
            serializer = EleveUpdateSerializer(eleve, data=request.data)

            if serializer.is_valid():
                eleve = serializer.save()  # Mettre à jour l'élève avec les nouvelles données
                return JsonResponse({"message": f"Élève {eleve.firstname} {eleve.lastname} mis à jour avec succès."}, status=status.HTTP_200_OK)
            
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"detail": "Erreur :" + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class EleveDeleteAPIView(APIView):
    def delete(self, request, eleve_id, *args, **kwargs):
        try:
            eleve = get_object_or_404(Eleves, id=eleve_id)  # Récupérer l'élève par ID
            eleve.delete()  # Supprimer l'élève
            return JsonResponse({"message": f"Élève {eleve.firstname} {eleve.lastname} supprimé avec succès."}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"detail": "Erreur :" + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

'''
RECUPERATION D'UN PROFESSEUR
'''
class ProfesseurClassesDetailView(APIView):
    def get(self, request, prof_id):
        # Récupérer le professeur par ID
        professeur = get_object_or_404(User, id=prof_id, role='prof')

        # Sérialiser les informations du professeur, y compris les matières avec les trimestres
        serializer = ProfesseurDetailSerializer(professeur)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    
class ProfesseurDetailView(APIView):
    def get(self, request, prof_id):
        # Récupérer le professeur par ID
        professeur = get_object_or_404(User, id=prof_id, role='prof')

        # Sérialiser les informations du professeur, y compris les matières avec les trimestres
        serializer = ProfesseurMiniDetailSerializer(professeur)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        

class SynchronisationView(APIView):
    
    def post(self, request):
        # Désérialisation des données du payload
        serializer = SyncDataSerializer(data=request.data)
        
        if serializer.is_valid():
            # Récupérer l'ID du professeur depuis le payload
            prof_id = serializer.validated_data.get('prof_id')
            prof = get_object_or_404(User, id=prof_id, role='prof')  # S'assurer que c'est bien un prof

            # Parcourir chaque classe
            for classe_data in serializer.validated_data['classes']:
                classe_id = classe_data['id']
                classe = get_object_or_404(Classes, id=classe_id)  # Récupérer la classe

                # Parcourir chaque matière dans la classe
                for matiere_data in classe_data['matieres']:
                    matiere_id = matiere_data['id']
                    matiere = get_object_or_404(Matieres, id=matiere_id, prof=prof)  # Récupérer la matière

                    # Parcourir chaque élève dans la matière
                    for eleve_data in matiere_data['eleves']:
                        eleve_id = eleve_data['id']
                        eleve = get_object_or_404(Eleves, id=eleve_id)  # Récupérer l'élève

                        # Parcourir chaque trimestre de l'élève
                        for trimestre_data in eleve_data['trimestres']:
                            trimestre_id = trimestre_data['id']
                            trimestre = get_object_or_404(Trimestres, id=trimestre_id)  # Récupérer le trimestre

                            # Parcourir chaque interro pour le trimestre
                            for interro_data in trimestre_data['interros']:
                                interro_numero = interro_data['numero']
                                note_interro = interro_data['note']

                                # Créer ou mettre à jour l'interro avec l'association au prof
                                interro, created = Interros.objects.update_or_create(
                                    numero=interro_numero,
                                    matiere=matiere,
                                    eleve=eleve,
                                    trimestre=trimestre,
                                    defaults={
                                        'note': note_interro,
                                        'prof': prof  # Associer l'interro au professeur
                                    }
                                )

                            # Parcourir chaque devoir pour le trimestre
                            for devoir_data in trimestre_data['devoirs']:
                                devoir_numero = devoir_data['numero']
                                note_devoir = devoir_data['note']

                                # Créer ou mettre à jour le devoir avec l'association au prof
                                devoir, created = Devoirs.objects.update_or_create(
                                    numero=devoir_numero,
                                    matiere=matiere,
                                    eleve=eleve,
                                    trimestre=trimestre,
                                    defaults={
                                        'note': note_devoir,
                                        'prof': prof  # Associer le devoir au professeur
                                    }
                                )
            
            return JsonResponse({"message": "Données synchronisées avec succès"}, status=status.HTTP_200_OK)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

