from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps_publicas.empresas.models import Empresa, Dominio

User = get_user_model()


class SuperAdminSerializer(serializers.Serializer):
    """Serializer para los datos del super admin de la empresa"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        """Validar que las contraseñas coincidan"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password': 'Las contraseñas no coinciden.'
            })
        return data


class EmpresaRegistroSerializer(serializers.Serializer):
    """Serializer para registro completo de empresa + super admin"""

    # Datos de la empresa
    nombre = serializers.CharField(max_length=100)
    correo = serializers.EmailField()

    # Datos del super admin
    super_admin = SuperAdminSerializer()

    def validate_nombre(self, value):
        """Validar que el nombre sea único y no contenga caracteres especiales"""
        if Empresa.objects.filter(nombre=value).exists():
            raise serializers.ValidationError(
                f"Ya existe una empresa con el nombre '{value}'."
            )

        # Validar que solo contenga letras, números y espacios
        if not all(c.isalnum() or c.isspace() for c in value):
            raise serializers.ValidationError(
                "El nombre solo puede contener letras, números y espacios."
            )
        return value

    def validate_correo(self, value):
        """Validar que el correo sea único"""
        if Empresa.objects.filter(correo=value).exists():
            raise serializers.ValidationError(
                f"Ya existe una empresa registrada con el correo '{value}'."
            )
        return value

    def validate_super_admin(self, value):
        """Validar datos del super admin"""
        # Nota: No validamos username único globalmente porque cada tenant
        # tiene su propio schema con sus propios usuarios.
        # El usuario "admin" puede existir en tienda_amiga y en otro tenant sin problema.

        username = value.get('username')

        # Solo validar que username no esté vacío
        if not username or len(username) < 3:
            raise serializers.ValidationError({
                'username': 'El username debe tener al menos 3 caracteres.'
            })

        return value


class EmpresaCreatedSerializer(serializers.Serializer):
    """Serializer para la respuesta de creación de empresa"""
    empresa_id = serializers.IntegerField()
    nombre = serializers.CharField()
    schema_name = serializers.CharField()
    dominio = serializers.CharField()
    super_admin_username = serializers.CharField()
    mensaje = serializers.CharField()

