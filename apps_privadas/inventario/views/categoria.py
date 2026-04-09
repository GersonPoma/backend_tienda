from apps_privadas.inventario.views.base import BaseViewSet
from apps_privadas.inventario.models import Categoria
from apps_privadas.inventario.serializers import (
    CategoriaSerializer,
    CrearCategoriaSerializer,
    ActualizarCategoriaSerializer
)


class CategoriaViewSet(BaseViewSet):
    queryset = Categoria.objects.all()
    model = Categoria
    serializer_class = CategoriaSerializer
    crear_serializer_class = CrearCategoriaSerializer
    actualizar_serializer_class = ActualizarCategoriaSerializer
