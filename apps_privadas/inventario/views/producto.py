from apps_privadas.inventario.views.base import BaseViewSet
from apps_privadas.inventario.models import Producto, Categoria
from apps_privadas.inventario.serializers import (
    ProductoSerializer,
    CrearProductoSerializer,
    ActualizarProductoSerializer
)


class ProductoViewSet(BaseViewSet):
    queryset = Producto.objects.select_related('categoria').all()
    model = Producto
    serializer_class = ProductoSerializer
    crear_serializer_class = CrearProductoSerializer
    actualizar_serializer_class = ActualizarProductoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        categoria_id = serializer.validated_data.pop('categoria_id')
        categoria = Categoria.objects.get(id=categoria_id)
        instance = self.model.objects.create(
            categoria=categoria,
            **serializer.validated_data
        )
        
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(self.model, pk=kwargs.get('pk'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data.copy()
        categoria_id = data.pop('categoria_id', None)
        
        if categoria_id:
            data['categoria'] = Categoria.objects.get(id=categoria_id)
        
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
