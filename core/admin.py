from django.contrib import admin
from .models import Maquina, Produccion

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ubicacion', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre', 'ubicacion')

@admin.register(Produccion)
class ProduccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'maquina', 'fecha', 'cantidad_producida', 'observaciones')
    list_filter = ('maquina', 'fecha_inicio')
    search_fields = ('maquina__nombre',)

    def fecha(self, obj):
        return obj.fecha_inicio
    fecha.admin_order_field = 'fecha_inicio'
    fecha.short_description = 'fecha'
