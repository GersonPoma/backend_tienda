from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_privadas.inventario.views import CategoriaViewSet, ProductoViewSet, MultimedioViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'multimedios', MultimedioViewSet, basename='multimedio')

app_name = 'inventario'

urlpatterns = [
    path('', include(router.urls)),
]
