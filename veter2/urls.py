"""
URL configuration for veter2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from web import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # URLs administrativas
    path('admin/', admin.site.urls),
    
    # URLs principales
    path('', views.home, name='home'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('catalogo/', views.catalogo_view, name='catalogo'),
    path('calendario/', views.calendario, name='calendario'),
    
    # URLs de autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='home', http_method_names=['post', 'get']), name='logout'),
    
    # URLs de recuperación de contraseña
    path('restablecer/', views.restablecer, name='restablecer'),
    path('cambiar_contraseña/<str:uidb64>/<str:token>/', views.recuperarc, name='recuperarc'),
    path('cambiada/', views.cambiada, name='cambiada'),
    
    # URLs de contacto
    path('gracias/', views.gracias, name='gracias'),
    path('contacto/', views.contacto, name='formulario'),
    
    # URLs del carrito
    path('carrito/', login_required(views.ver_carrito), name='ver_carrito'),
    path('agregar-al-carrito/', login_required(views.agregar_al_carrito), name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', login_required(views.eliminar_item), name='eliminar_item'),
    # Añade esta línea a tus patrones de URL existentes
    path('carrito/actualizar-cantidad/', login_required(views.actualizar_cantidad), name='actualizar_cantidad'),
    path('finalizar_compra/', views.finalizar_compra, name='finalizar_compra'),
    path('pedido_confirmado/', views.pedido_confirmado, name='pedido_confirmado'),
    # URL de checkout (nueva)
    path('checkout/', login_required(views.checkout), name='checkout'),

    # historal de pedidos
    path('historial-pedidos/', views.historial_pedidos, name='historial_pedidos'),
    path('cancelar-pedido/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)