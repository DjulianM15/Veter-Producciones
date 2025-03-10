from django.db import models
from django.contrib.auth.models import User

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
        return f"${self.precio:,.2f}"


class CarritoItem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    catalogo = models.ForeignKey(Catalogo, on_delete=models.CASCADE)  # Campo relacionado con el producto
    cantidad = models.IntegerField(default=1)
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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    sesion_id = models.CharField(max_length=100, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=0)
    metodo_pago = models.CharField(max_length=20, choices=[('nequi', 'Nequi',), ('bancolombia', 'Bancolombia')])
    pagado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Orden #{self.id} - {self.nombre}"
    
class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, related_name='items', on_delete=models.CASCADE)
    catalogo = models.ForeignKey(Catalogo, on_delete=models.CASCADE)  # Corregido a Catalogo con mayúscula
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    cantidad = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.catalogo.nombre}"
    
    def subtotal(self):
        return self.precio * self.cantidad
    

# reserva

