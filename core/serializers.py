from rest_framework import serializers
from .models import Maquina, Produccion


class MaquinaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Maquina.
    Incluye información anidada de producciones relacionadas.
    """
    total_producciones = serializers.SerializerMethodField()
    
    class Meta:
        model = Maquina
        fields = [
            'id', 
            'nombre', 
            'ubicacion', 
            'descripcion', 
            'activa',
            'total_producciones'
        ]
        read_only_fields = ['id']
    
    def get_total_producciones(self, obj):
        """Retorna el total de producciones asociadas a esta máquina"""
        return obj.producciones.count()
    
    def validate_nombre(self, value):
        """Valida que el nombre no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre de la máquina no puede estar vacío")
        return value.strip()


class ProduccionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Produccion.
    Incluye información de la máquina asociada y validaciones de negocio.
    """
    maquina_nombre = serializers.CharField(source='maquina.nombre', read_only=True)
    maquina_ubicacion = serializers.CharField(source='maquina.ubicacion', read_only=True)
    turno_display = serializers.CharField(source='get_turno_display', read_only=True)
    duracion_horas = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    
    class Meta:
        model = Produccion
        fields = [
            'id',
            'maquina',
            'maquina_nombre',
            'maquina_ubicacion',
            'codigo_lote',
            'producto',
            'fecha_inicio',
            'fecha_fin',
            'cantidad_producida',
            'turno',
            'turno_display',
            'observaciones',
            'duracion_horas',
            'estado',
        ]
        read_only_fields = ['id']
    
    def get_duracion_horas(self, obj):
        """Calcula la duración en horas si hay fecha_fin"""
        if obj.fecha_fin and obj.fecha_inicio:
            delta = obj.fecha_fin - obj.fecha_inicio
            return round(delta.total_seconds() / 3600, 2)
        return None
    
    def get_estado(self, obj):
        """Determina el estado de la producción"""
        if obj.fecha_fin:
            return "Finalizado"
        return "En Proceso"
    
    def validate_cantidad_producida(self, value):
        """Valida que la cantidad sea mayor a 0"""
        if value <= 0:
            raise serializers.ValidationError("La cantidad producida debe ser mayor a 0")
        return value
    
    def validate_codigo_lote(self, value):
        """Valida formato y unicidad del código de lote"""
        if not value or not value.strip():
            raise serializers.ValidationError("El código de lote no puede estar vacío")
        
        value = value.strip().upper()
        
        # Validar unicidad solo en creación
        if not self.instance:  # Creación
            if Produccion.objects.filter(codigo_lote=value).exists():
                raise serializers.ValidationError(f"Ya existe una producción con el código de lote '{value}'")
        
        return value
    
    def validate(self, data):
        """Validaciones que involucran múltiples campos"""
        # Validar que fecha_fin sea posterior a fecha_inicio
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if fecha_fin and fecha_inicio:
            if fecha_fin < fecha_inicio:
                raise serializers.ValidationError({
                    "fecha_fin": "La fecha de fin debe ser posterior a la fecha de inicio"
                })
        
        # Validar que la máquina esté activa
        maquina = data.get('maquina')
        if maquina and not maquina.activa:
            raise serializers.ValidationError({
                "maquina": f"La máquina '{maquina.nombre}' no está activa"
            })
        
        return data


class ProduccionListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listados (más rápido, menos datos)
    """
    maquina_nombre = serializers.CharField(source='maquina.nombre', read_only=True)
    turno_display = serializers.CharField(source='get_turno_display', read_only=True)
    
    class Meta:
        model = Produccion
        fields = [
            'id',
            'codigo_lote',
            'producto',
            'maquina_nombre',
            'fecha_inicio',
            'fecha_fin',
            'cantidad_producida',
            'turno_display',
        ]


