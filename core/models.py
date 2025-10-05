from django.db import models

class Maquina(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Produccion(models.Model):
    TURNO_CHOICES = [
        ('M', 'Mañana'),
        ('T', 'Tarde'),
        ('N', 'Noche'),
    ]

    maquina = models.ForeignKey('Maquina', on_delete=models.CASCADE, related_name='producciones')
    codigo_lote = models.CharField(max_length=50, unique=True)
    producto = models.CharField(max_length=100)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)
    cantidad_producida = models.PositiveIntegerField()
    turno = models.CharField(max_length=1, choices=TURNO_CHOICES)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Lote {self.codigo_lote} - {self.producto}"
