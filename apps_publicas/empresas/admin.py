from django.contrib import admin
from apps_publicas.empresas.models import Empresa, Dominio
from django.db import connection


# Solo registrar Empresa y Dominio en el esquema público
# No deben aparecer en los tenants
try:
    current_schema = connection.get_schema()
    # Si estamos en un tenant (no en public), no registrar
    if current_schema and current_schema != 'public':
        # No registrar en tenants
        pass
    else:
        # Registrar en public
        @admin.register(Empresa)
        class EmpresaAdmin(admin.ModelAdmin):
            list_display = ('nombre', 'schema_name', 'correo', 'is_active', 'fecha_creacion')
            list_filter = ('is_active', 'fecha_creacion')
            search_fields = ('nombre', 'schema_name', 'correo')
            readonly_fields = ('schema_name', 'fecha_creacion')

        @admin.register(Dominio)
        class DominioAdmin(admin.ModelAdmin):
            list_display = ('domain', 'tenant', 'is_primary')
            list_filter = ('is_primary', 'tenant')
            search_fields = ('domain',)
except:
    # Si hay error al detectar tenant, registrar normalmente (en migraciones iniciales)
    @admin.register(Empresa)
    class EmpresaAdmin(admin.ModelAdmin):
        list_display = ('nombre', 'schema_name', 'correo', 'is_active', 'fecha_creacion')
        list_filter = ('is_active', 'fecha_creacion')
        search_fields = ('nombre', 'schema_name', 'correo')
        readonly_fields = ('schema_name', 'fecha_creacion')

    @admin.register(Dominio)
    class DominioAdmin(admin.ModelAdmin):
        list_display = ('domain', 'tenant', 'is_primary')
        list_filter = ('is_primary', 'tenant')
        search_fields = ('domain',)
