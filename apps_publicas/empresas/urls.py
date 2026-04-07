from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_publicas.empresas.views import EmpresaViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'empresas', EmpresaViewSet, basename='empresa')

app_name = 'empresas'

urlpatterns = [
    path('', include(router.urls)),
]

