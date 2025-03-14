from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Catalogo(models.Model):  # Nombre del modelo en PascalCase
    nombre = models.CharField(max_length=200)
    description = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    foto = models.ImageField(upload_to='catalogo/')
    disponible = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Producto del Catálogo'
        verbose_name_plural = 'Productos del Catálogo'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('catalogo-detalle', kwargs={'pk': self.pk})

    def precio_formatted(self):
        return f"${self.precio:.2f}"


class CarritoItem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    catalogo = models.ForeignKey(Catalogo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.cantidad * self.catalogo.precio

class Datos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    

class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, choices=[
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('efectivo', 'Efectivo en Entrega'),
        ('nequi', 'Nequi'),
        ('bancolombia', 'Bancolombia')
    ])
    estado = models.CharField(max_length=50, default='pendiente', choices=[
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado')
    ])

    def __str__(self):
        return f"Orden #{self.id} - {self.nombre}"
    
    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-fecha_creacion']
    
class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, related_name='items', on_delete=models.CASCADE)
    catalogo = models.ForeignKey(Catalogo, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    cantidad = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = "Item de Orden"
        verbose_name_plural = "Items de Órdenes"

    def __str__(self):
        return f"{self.cantidad} x {self.catalogo.nombre}"
    
    def subtotal(self):
        return self.precio * self.cantidad