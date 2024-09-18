from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Création du routeur
router = DefaultRouter()

# Enregistrement des ViewSets dans le routeur
router.register(r'academic_years', views.AcademicYearsViewSet)
router.register(r'trimestres', views.TrimestresViewSet)
router.register(r'roles', views.RolesViewSet)
router.register(r'admins', views.AdminsViewSet)
router.register(r'classes', views.ClassesViewSet)
router.register(r'profs', views.ProfsViewSet)
router.register(r'matieres', views.MatieresViewSet)
router.register(r'eleves', views.ElevesViewSet)
router.register(r'interros', views.InterrosViewSet)
router.register(r'devoirs', views.DevoirsViewSet)

# URL patterns
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/request-phone/', views.RequestPhoneNumberView.as_view(), name='request-phone'),
    path('api/auth/verify-code/', views.VerifyCodeView.as_view(), name='verify-code'),
]
