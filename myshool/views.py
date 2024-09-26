import asyncio
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from myshool.sms_client import SMSClient
from .serializers import PhoneNumberSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from .models import Academic_years, Trimestres, Roles, Admins, Classes, Profs, Matieres, Eleves, Interros, Devoirs
from .serializers import (
    AcademicYearsSerializer, TrimestresSerializer, RolesSerializer, AdminsSerializer,
    ClassesSerializer, ProfsSerializer, MatieresSerializer, ElevesSerializer, InterrosSerializer, DevoirsSerializer
)

# ViewSet pour Academic_years
class AcademicYearsViewSet(viewsets.ModelViewSet):
    queryset = Academic_years.objects.all()
    serializer_class = AcademicYearsSerializer

# ViewSet pour Trimestres
class TrimestresViewSet(viewsets.ModelViewSet):
    queryset = Trimestres.objects.all()
    serializer_class = TrimestresSerializer

# ViewSet pour Roles
class RolesViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer

# ViewSet pour Admins
class AdminsViewSet(viewsets.ModelViewSet):
    queryset = Admins.objects.all()
    serializer_class = AdminsSerializer

# ViewSet pour Classes
class ClassesViewSet(viewsets.ModelViewSet):
    queryset = Classes.objects.all()
    serializer_class = ClassesSerializer

# ViewSet pour Profs
class ProfsViewSet(viewsets.ModelViewSet):
    queryset = Profs.objects.all()
    serializer_class = ProfsSerializer

# ViewSet pour Matieres
class MatieresViewSet(viewsets.ModelViewSet):
    queryset = Matieres.objects.all()
    serializer_class = MatieresSerializer

# ViewSet pour Eleves
class ElevesViewSet(viewsets.ModelViewSet):
    queryset = Eleves.objects.all()
    serializer_class = ElevesSerializer

# ViewSet pour Interros
class InterrosViewSet(viewsets.ModelViewSet):
    queryset = Interros.objects.all()
    serializer_class = InterrosSerializer

# ViewSet pour Devoirs
class DevoirsViewSet(viewsets.ModelViewSet):
    queryset = Devoirs.objects.all()
    serializer_class = DevoirsSerializer


class RequestPhoneNumberView(APIView):
    def post(self, request):
        phone_num = request.data.get('phone_num')
        user = None
        try:
            # Vérifier si c'est un admin
            user = Admins.objects.get(phone_num=phone_num)
        except ObjectDoesNotExist:
            try:
                # Sinon vérifier si c'est un prof
                user = Profs.objects.get(phone_num=phone_num)
            except ObjectDoesNotExist:
                return Response({'error': 'Numéro de téléphone non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Générer un code de 6 chiffres
        code = str(random.randint(100000, 999999))
        # Stocker le code dans la base de données (pour Admin ou Prof)
        user.code = code
        user.save()
        print(user)
        
        # send code via sms to client
        sms_client = SMSClient()
        asyncio.run(sms_client.send_message(code, user.phone_num))

        return Response({'message': 'Code envoyé par SMS.'}, status=status.HTTP_200_OK)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyCodeView(APIView):
    def post(self, request):
        phone_num = request.data.get('phone_num')
        code = request.data.get('code')

        user = None
        try:
            # Vérifier dans la table Admins
            user = Admins.objects.get(phone_num=phone_num)
        except ObjectDoesNotExist:
            try:
                # Vérifier dans la table Profs
                user = Profs.objects.get(phone_num=phone_num)
            except ObjectDoesNotExist:
                return Response({'error': 'Numéro de téléphone non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        # Vérifier si le code correspond
        if user.code == code:
            # Générer un token d'authentification
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Code invalide.'}, status=status.HTTP_400_BAD_REQUEST)
