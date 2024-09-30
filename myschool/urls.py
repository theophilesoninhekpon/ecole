from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Création du routeur
router = DefaultRouter()

# Enregistrement des ViewSets dans le routeur
router.register(r'academic_years', views.AcademicYearsViewSet)
router.register(r'classes', views.ClassesViewSet)
router.register(r'matieres', views.MatieresViewSet)
router.register(r'eleves', views.ElevesViewSet)
router.register(r'interros', views.InterrosViewSet)
router.register(r'devoirs', views.DevoirsViewSet)

# URL patterns
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/request-code', views.RequestPhoneNumberView.as_view(), name='request-phone'),
    path('api/auth/verify-code', views.VerifyCodeView.as_view(), name='verify-code'),
    path('api/classes/create', views.ClasseCreateAPIView.as_view(), name='create-classe'),
    path('api/admins/create', views.AdminRegisterAPIView.as_view(), name='register_admin'),
    path('api/profs/create', views.ProfRegisterAPIView.as_view(), name='register_prof'),
    path('api/profs/<int:prof_id>/classes', views.ProfesseurClassesDetailView.as_view(), name='prof_classes'),
    path('api/profs/<int:prof_id>', views.ProfesseurDetailView.as_view(), name='prof_detail'),
    path('api/eleves/create', views.EleveCreateAPIView.as_view(), name='eleve_create'),
    path('api/eleves/delete', views.EleveDeleteAPIView.as_view(), name='eleve_delete'),
    path('api/eleves/update', views.EleveUpdateAPIView.as_view(), name='eleve_update'),
    path('api/eleves/<int:eleve_id>/', views.EleveDetailAPIView.as_view(), name='eleve-detail'),

]
