from django.db.models import Avg, Min, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps_privadas.inventario.models import Multimedio, Producto, Resena, VarianteProducto
from apps_privadas.inventario.serializers.comparador import CompararProductosSerializer


class ComparadorViewSet(viewsets.ViewSet):
    """
    Compara muebles seleccionados por el cliente dentro del tenant actual.

    La seleccion se mantiene temporalmente en el frontend; el backend recibe
    los IDs y devuelve los datos estructurados para pintar la tabla comparativa.
    """

    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = CompararProductosSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        producto_ids = serializer.validated_data['producto_ids']
        productos = Producto.objects.select_related('categoria', 'marca').filter(
            id__in=producto_ids,
            activo=True,
        )
        productos_por_id = {producto.id: producto for producto in productos}
        productos_ordenados = [productos_por_id[producto_id] for producto_id in producto_ids]

        items = [self._build_item(producto) for producto in productos_ordenados]

        return Response(
            {
                'success': True,
                'total': len(items),
                'producto_ids': producto_ids,
                'columnas': [item['nombre'] for item in items],
                'caracteristicas': self._build_caracteristicas(items),
                'productos': items,
            },
            status=status.HTTP_200_OK,
        )

    def _build_item(self, producto):
        variantes = VarianteProducto.objects.filter(producto=producto)
        precio_minimo = variantes.aggregate(valor=Min('precio'))['valor']
        stock_total = variantes.aggregate(valor=Sum('cantidad'))['valor'] or 0
        imagen_principal = self._get_imagen_principal(producto)
        calificacion = Resena.objects.filter(producto=producto).aggregate(valor=Avg('calificacion'))['valor']
        total_resenas = Resena.objects.filter(producto=producto).count()
        descuento = self._get_descuento_activo(producto)

        return {
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'categoria': producto.categoria_id,
            'categoria_nombre': producto.categoria.nombre,
            'marca': producto.marca_id,
            'marca_nombre': producto.marca.nombre,
            'precio_minimo': precio_minimo,
            'stock_total': stock_total,
            'material': getattr(producto, 'material', None),
            'color': getattr(producto, 'color', None),
            'dimensiones': getattr(producto, 'dimensiones', None),
            'imagen_principal': imagen_principal,
            'variantes': list(
                variantes.values('id', 'sku', 'precio', 'cantidad', 'limite_cantidad')
            ),
            'descuento_activo': descuento,
            'calificacion_promedio': round(calificacion, 1) if calificacion is not None else None,
            'total_resenas': total_resenas,
            'acciones': {
                'ver_detalle_url': f'/api/productos-detalle/{producto.id}/',
                'agregar_carrito_producto_id': producto.id,
            },
        }

    def _build_caracteristicas(self, items):
        return [
            self._row('Precio minimo', 'precio_minimo', items),
            self._row('Marca', 'marca_nombre', items),
            self._row('Categoria', 'categoria_nombre', items),
            self._row('Stock disponible', 'stock_total', items),
            self._row('Material', 'material', items),
            self._row('Color', 'color', items),
            self._row('Dimensiones', 'dimensiones', items),
            self._row('Descripcion', 'descripcion', items),
            self._row('Descuento', 'descuento_activo', items),
            self._row('Calificacion', 'calificacion_promedio', items),
            self._row('Total resenas', 'total_resenas', items),
            self._row('Imagen principal', 'imagen_principal', items),
        ]

    def _row(self, etiqueta, campo, items):
        return {
            'etiqueta': etiqueta,
            'campo': campo,
            'valores': {
                str(item['id']): item[campo]
                for item in items
            },
        }

    def _get_imagen_principal(self, producto):
        imagen = Multimedio.objects.filter(
            producto=producto,
            tipo='imagen',
            es_principal=True,
        ).first()
        if not imagen:
            imagen = Multimedio.objects.filter(producto=producto, tipo='imagen').first()
        return imagen.archivo_url if imagen else None

    def _get_descuento_activo(self, producto):
        try:
            from apps_privadas.notificaciones.models import Promocion
        except Exception:
            return None

        ahora = timezone.now()
        promocion = Promocion.objects.filter(
            producto=producto,
            estado=Promocion.ESTADO_PUBLICADA,
            fecha_inicio__lte=ahora,
            fecha_fin__gte=ahora,
        ).order_by('-fecha_publicacion', '-fecha_creacion').first()

        if not promocion:
            return None

        return {
            'id': promocion.id,
            'titulo': promocion.titulo,
            'tipo_descuento': promocion.tipo_descuento,
            'valor_descuento': promocion.valor_descuento,
        }
