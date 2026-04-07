from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


# Create your models here.
class Empresa(TenantMixin):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True, null=True)
    is_active = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    auto_create_schema = True

class Dominio(DomainMixin):
    pass