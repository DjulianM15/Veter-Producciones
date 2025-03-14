from django.contrib import admin
from .models import Catalogo, CarritoItem, Datos, Orden, OrdenItem

# Configuración para el modelo Catalogo
@admin.register(Catalogo)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'disponible', 'fecha_creacion']
    list_filter = ['disponible', 'fecha_creacion']
    search_fields = ['nombre', 'description']
    list_editable = ['precio', 'disponible']

# Configuración para los items de orden (inline)
class OrdenItemInline(admin.TabularInline):
    model = OrdenItem
    extra = 0
    readonly_fields = ['catalogo', 'cantidad', 'precio', 'subtotal']
    
    def subtotal(self, obj):
        return obj.subtotal()
    subtotal.short_description = 'Subtotal'

# Configuración para el modelo Orden
@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'email', 'telefono', 'total', 'metodo_pago', 'estado', 'fecha_creacion']
    list_filter = ['estado', 'metodo_pago', 'fecha_creacion']
    search_fields = ['nombre', 'email', 'telefono']
    inlines = [OrdenItemInline]
    list_editable = ['estado']
    actions = ['marcar_como_procesando', 'marcar_como_enviado', 'marcar_como_entregado', 'marcar_como_cancelado']
    
    def marcar_como_procesando(self, request, queryset):
        queryset.update(estado='procesando')
        self.message_user(request, f"{queryset.count()} pedidos marcados como en procesamiento.")
    marcar_como_procesando.short_description = "Marcar pedidos como en procesamiento"
    
    def marcar_como_enviado(self, request, queryset):
        queryset.update(estado='enviado')
        self.message_user(request, f"{queryset.count()} pedidos marcados como enviados.")
    marcar_como_enviado.short_description = "Marcar pedidos como enviados"
    
    def marcar_como_entregado(self, request, queryset):
        queryset.update(estado='entregado')
        self.message_user(request, f"{queryset.count()} pedidos marcados como entregados.")
    marcar_como_entregado.short_description = "Marcar pedidos como entregados"
    
    def marcar_como_cancelado(self, request, queryset):
        queryset.update(estado='cancelado')
        self.message_user(request, f"{queryset.count()} pedidos marcados como cancelados.")
    marcar_como_cancelado.short_description = "Marcar pedidos como cancelados"

# Registrar otros modelos
admin.site.register(CarritoItem)
admin.site.register(Datos)