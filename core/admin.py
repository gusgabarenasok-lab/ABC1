from django.contrib import admin
from .models import Maquina, Produccion

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ubicacion', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre', 'ubicacion')

@admin.register(Produccion)
class ProduccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo_lote', 'producto', 'maquina', 'fecha_inicio', 'turno', 'cantidad_producida', 'estado')
    list_filter = ('maquina', 'turno', 'fecha_inicio')
    search_fields = ('codigo_lote', 'producto', 'maquina__nombre')
    date_hierarchy = 'fecha_inicio'
    readonly_fields = ('estado', 'duracion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('codigo_lote', 'producto', 'maquina', 'turno')
        }),
        ('Fechas y Tiempos', {
            'fields': ('fecha_inicio', 'fecha_fin', 'duracion')
        }),
        ('Producción', {
            'fields': ('cantidad_producida', 'estado')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
    )
    
    def estado(self, obj):
        if obj.fecha_fin:
            return "✅ Finalizado"
        return "🔄 En Proceso"
    estado.short_description = 'Estado'
    
    def duracion(self, obj):
        if obj.fecha_fin and obj.fecha_inicio:
            delta = obj.fecha_fin - obj.fecha_inicio
            horas = delta.total_seconds() / 3600
            return f"{horas:.2f} horas"
        return "-"
    duracion.short_description = 'Duración'
