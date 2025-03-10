from django.contrib import admin
from .models import Catalogo, CarritoItem, Datos

class CatalogoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'description', 'precio', 'foto')
    list_display_links = ('nombre',)
    search_fields = ('nombre', 'description')
    list_filter = ('disponible', 'fecha_creacion')
    ordering = ('-fecha_creacion',)

@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ['catalogo', 'cantidad', 'usuario', 'fecha_agregado']
    list_filter = ['catalogo', 'usuario']
    search_fields = ['catalogo__nombre', 'usuario__username']

class DatosAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nombre', 'apellido')
    list_display_links = ('usuario',)
    search_fields = ('usuario__username', 'nombre', 'apellido')

# Registrar los modelos
admin.site.register(Catalogo, CatalogoAdmin)
admin.site.register(Datos, DatosAdmin)