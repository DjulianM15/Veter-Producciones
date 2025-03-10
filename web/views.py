from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from web.forms import OrdenForm, CheckoutForm
from .models import Catalogo, CarritoItem, Datos, Orden, OrdenItem

# ============================================================
# VISTAS BÁSICAS
# ============================================================

def home(request):
    return render(request, 'home.html')

def nosotros(request):
    return render(request, 'nosotros.html')

def calendario(request):
    return render(request, 'calendario.html')

def gracias(request):
    return render(request, 'gracias.html')

# ============================================================
# VISTAS DE AUTENTICACIÓN
# ============================================================

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST.get('confirm_password')
        
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        errors = []
        if password != confirm_password:
            errors.append('Las contraseñas no coinciden.')
        if User.objects.filter(email=email).exists():
            errors.append('El correo ya está registrado.')
        if User.objects.filter(username=username).exists():
            errors.append('El nombre de Usuario ya está en uso.')
        
        if errors:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': errors})
            else:
                for error in errors:
                    messages.error(request, error)
                return render(request, 'register.html')
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    if is_ajax:
                        return JsonResponse({'success': True, 'redirect': 'home'})
                    else:
                        messages.success(request, "¡Registro exitoso! Has iniciado sesión.")
                        return redirect('home')
            except Exception as e:
                error_msg = f'Error al registrar: {str(e)}'
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': [error_msg]})
                else:
                    messages.error(request, error_msg)
                    return render(request, 'register.html')
                
    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Por favor, ingresa ambos campos.')
            return render(request, 'login.html')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'El usuario no existe.')
            return render(request, 'login.html')
        
        authenticated_user = authenticate(request, username=username, password=password)
        if authenticated_user is not None:
            auth_login(request, authenticated_user)
            return redirect('home')
        else:
            messages.error(request, "Contraseña incorrecta.")
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

# ============================================================
# VISTAS DE RECUPERACIÓN DE CONTRASEÑA
# ============================================================

def restablecer(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            try:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                enlace = request.build_absolute_uri(f"/cambiar_contraseña/{uid}/{token}/")
                send_mail(
                    "Restablecimiento de contraseña",
                    f"Haz clic en el siguiente enlace para cambiar tu contraseña: {enlace}",
                    "munozjulian146@gmail.com",
                    [email],
                    fail_silently=False,
                )
                messages.success(request, "Se ha enviado un enlace de restablecimiento a su correo.")
                return redirect("login")
            except Exception as e:
                messages.error(request, f"Ocurrió un error al enviar el correo: {e}")
                return redirect("restablecer")
        else:
            messages.error(request, "No se encontró un usuario con ese correo electrónico.")
            return redirect("restablecer")
    return render(request, "restablecer.html")

def recuperarc(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            nueva_contraseña = request.POST["password"]
            user.set_password(nueva_contraseña)
            user.save()
            return redirect("cambiada")

        return render(request, "recuperarc.html")

    return redirect("login")

def cambiada(request):
    messages.success(request, "¡Tu contraseña ha sido cambiada exitosamente!")
    return render(request, "cambiada.html")

# ============================================================
# VISTAS DE CATÁLOGO
# ============================================================

def catalogo_view(request):
    catalogos = Catalogo.objects.filter(disponible=True)
    return render(request, 'catalogo.html', {
        'catalogos': catalogos
    })

# ============================================================
# VISTAS DEL CARRITO
# ============================================================

@login_required
def ver_carrito(request):
    items_carrito = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.subtotal() for item in items_carrito)
    return render(request, 'carrito.html', {
        'items_carrito': items_carrito,
        'total': total
    })

@require_POST
@login_required
def agregar_al_carrito(request):
    """
    Agrega un producto al carrito del usuario.
    """
    if request.method == 'POST':
        try:
            catalogo_id = request.POST.get('catalogo_id')
            cantidad = int(request.POST.get('cantidad', 1))
            
            if not catalogo_id:
                print("Error: No se recibió catalogo_id")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'No se especificó el producto'}, status=400)
                else:
                    messages.error(request, 'No se especificó el producto')
                    return redirect('catalogo')
            
            catalogo = get_object_or_404(Catalogo, id=catalogo_id)
            
            carrito_item, created = CarritoItem.objects.get_or_create(
                usuario=request.user,
                catalogo=catalogo,
                defaults={'cantidad': cantidad}
            )
            
            if not created:
                carrito_item.cantidad += cantidad
                carrito_item.save()
            
            cart_count = CarritoItem.objects.filter(usuario=request.user).count()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': f'{catalogo.nombre} agregado al carrito.',
                    'cart_count': cart_count
                })
            
            messages.success(request, f'{catalogo.nombre} agregado al carrito.')
            return redirect('catalogo')
            
        except Exception as e:
            print(f"Error al agregar al carrito: {str(e)}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
            messages.error(request, f'Error al agregar al carrito: {str(e)}')
            return redirect('catalogo')
    
    return redirect('catalogo')

@login_required
def eliminar_item(request, item_id):
    """
    Elimina un item específico del carrito del usuario.
    """
    try:
        item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
        item.delete()
        
        messages.success(request, 'Producto eliminado del carrito')
        return redirect('ver_carrito')
        
    except Exception as e:
        messages.error(request, f'Error al eliminar el producto: {str(e)}')
        return redirect('ver_carrito')

@login_required
def actualizar_cantidad(request):
    """
    Actualiza la cantidad de un producto en el carrito.
    """
    if request.method == 'POST':
        try:
            item_id = request.POST.get('item_id')
            cantidad = int(request.POST.get('cantidad', 1))
            
            if not item_id:
                return JsonResponse({'success': False, 'error': 'ID de item no proporcionado'}, status=400)
                
            if cantidad < 1:
                cantidad = 1
                
            item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
            
            item.cantidad = cantidad
            item.save()
            
            items_carrito = CarritoItem.objects.filter(usuario=request.user)
            total = sum(i.subtotal() for i in items_carrito)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Cantidad actualizada',
                    'subtotal': float(item.subtotal()),
                    'total': float(total)
                })
            
            messages.success(request, 'Cantidad actualizada')
            return redirect('ver_carrito')
            
        except CarritoItem.DoesNotExist:
            error_msg = 'El item no existe en el carrito'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg}, status=404)
            messages.error(request, error_msg)
            return redirect('ver_carrito')
            
        except ValueError as e:
            error_msg = 'Valor de cantidad inválido'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('ver_carrito')
            
        except Exception as e:
            print(f"Error al actualizar cantidad: {str(e)}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
            messages.error(request, f'Error al actualizar cantidad: {str(e)}')
            return redirect('ver_carrito')
    
    return redirect('ver_carrito')

@login_required
def actualizar_carrito(request, item_id):
    """
    Actualiza la cantidad de un producto en el carrito o lo elimina si la cantidad es 0.
    """
    try:
        item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
        cantidad = int(request.POST.get('cantidad', 1))
        
        if cantidad > 0:
            item.cantidad = cantidad
            item.save()
        else:
            item.delete()
            
        messages.success(request, 'Carrito actualizado')
    except Exception as e:
        messages.error(request, f'Error al actualizar: {str(e)}')

    return redirect('ver_carrito')

# ============================================================
# VISTAS DE CHECKOUT Y PROCESAMIENTO DE ÓRDENES
# ============================================================

@login_required
def checkout(request):
    """
    Maneja el proceso de checkout para finalizar la compra.
    """
    items_carrito = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.subtotal() for item in items_carrito)
    
    if request.method == 'POST':
        # Aquí iría la lógica para procesar el pago
        
        # Limpiamos el carrito después de una compra exitosa
        items_carrito.delete()
        
        messages.success(request, '¡Compra realizada con éxito!')
        return redirect('home')
    
    return render(request, 'checkout.html', {
        'items_carrito': items_carrito,
        'total': total
    })

@login_required
def finalizar_compra(request):
    """
    Vista para procesar el formulario de finalización de compra.
    Muestra el formulario, procesa los datos y crea la orden.
    """
    carrito_items = CarritoItem.objects.filter(usuario=request.user)
    
    if not carrito_items.exists():
        messages.warning(request, "No tienes productos en tu carrito.")
        return redirect('catalogo')
    
    total = sum(item.subtotal() for item in carrito_items)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.usuario = request.user
            orden.total = total
            orden.save()
            
            for item in carrito_items:
                OrdenItem.objects.create(
                    orden=orden,
                    catalogo=item.catalogo,
                    cantidad=item.cantidad,
                    precio=item.catalogo.precio
                )
            
            request.session['orden_id'] = orden.id
            
            carrito_items.delete()
            
            messages.success(request, "¡Tu pedido ha sido procesado con éxito!")
            
            return redirect('pedido_confirmado')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'nombre': request.user.first_name + ' ' + request.user.last_name,
                'email': request.user.email,
            }
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'form': form,
        'carrito_items': carrito_items,
        'total': total
    }
    
    return render(request, 'finalizar_compra.html', context)


def pasarela(request):
    """
    Vista para procesar el pago y crear la orden.
    """
    carrito_items = []
    total = 0

    # Obtener los items del carrito según si el usuario está autenticado o no
    if request.user.is_authenticated:
        carrito_items = CarritoItem.objects.filter(usuario=request.user)
    else:
        if request.session.session_key:
            carrito_items = CarritoItem.objects.filter(sesion_id=request.session.session_key)

    # Verificar si el carrito está vacío
    if not carrito_items.exists():
        messages.warning(request, "Tu carrito está vacío")
        return redirect('ver_carrito')

    # Calcular el total
    for item in carrito_items:
        total += item.subtotal()

    if request.method == 'POST':
        form = OrdenForm(request.POST)
        metodo_pago = request.POST.get('metodo_pago')

        if form.is_valid() and metodo_pago:
            # Crear la orden pero no guardarla aún
            orden = form.save(commit=False)

            # Asignar usuario o sesión según corresponda
            if request.user.is_authenticated:
                orden.usuario = request.user
            else:
                orden.sesion_id = request.session.session_key

            # Asignar total y método de pago
            orden.total = total 
            orden.metodo_pago = metodo_pago
            orden.save()

            # Crear items de la orden
            for item in carrito_items:
                OrdenItem.objects.create(
                    orden=orden,    
                    catalogo=item.catalogo,
                    precio=item.catalogo.precio,
                    cantidad=item.cantidad
                )

            # Vaciar el carrito
            carrito_items.delete()

            # Enviar correo de confirmación
            enviar_correo_confirmacion(orden)

            messages.success(request, "¡Tu pedido ha sido procesado con éxito!")
            return redirect('confirmacion', orden_id=orden.id)
        else:
            messages.error(request, "Por favor, completa todos los campos y selecciona un método de pago")
    else:
        # Preparar datos iniciales para el formulario
        initial_data = {}
        if request.user.is_authenticated:
            try:
                datos = Datos.objects.get(usuario=request.user)
                initial_data = {
                    'nombre': f"{datos.nombre} {datos.apellido}",
                    'email': request.user.email
                }
            except Datos.DoesNotExist:
                initial_data = {
                    'nombre': request.user.username,
                    'email': request.user.email
                }

        form = OrdenForm(initial=initial_data)

    return render(request, 'pasarela.html', {
        'form': form,
        'carrito_items': carrito_items,
        'total': total
    })

def confirmacion(request, orden_id):
    """
    Vista para mostrar la confirmación de un pedido.
    """
    try:
        # Obtener la orden según si el usuario está autenticado o no
        if request.user.is_authenticated:
            orden = Orden.objects.get(id=orden_id, usuario=request.user)
        else:
            orden = Orden.objects.get(id=orden_id, sesion_id=request.session.session_key)

        # Obtener los items de la orden
        items = OrdenItem.objects.filter(orden=orden)

        return render(request, 'pedido_confirmado.html', {
            'orden': orden,
            'items': items
        })
    except Orden.DoesNotExist:
        messages.error(request, "Orden no encontrada")
        return redirect('catalogo')

def pedido_confirmado(request):
    """
    Vista que muestra la página de confirmación después de finalizar un pedido.
    """
    orden = None
    items = []
    
    # Intentar obtener el ID de la orden de la sesión
    orden_id = request.session.get('orden_id')
    
    if orden_id:
        try:
            # Obtener la orden y sus items
            orden = Orden.objects.get(id=orden_id)
            items = OrdenItem.objects.filter(orden=orden)
            
            # Enviar correo de confirmación
            enviar_correo_confirmacion(orden)
            
            # Limpiar la sesión después de mostrar la confirmación
            if 'orden_id' in request.session:
                del request.session['orden_id']
                
        except Exception as e:
            # Si hay algún error al obtener la orden, simplemente mostrar la confirmación genérica
            print(f"Error al obtener la orden: {e}")
    
    return render(request, 'pedido_confirmado.html', {
        'orden': orden,
        'items': items
    })

# ============================================================
# VISTAS DE CONTACTO
# ============================================================

def contacto(request):
    """
    Vista de formulario de contacto
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        mensaje = request.POST.get('mensaje')
        
        try:
            # Correo para ti (administrador)
            send_mail(
                subject=f'Nuevo mensaje de contacto de {nombre}',
                message=f'De: {nombre}\nEmail: {email}\nMensaje: {mensaje}',
                from_email='munozjulian146@gmail.com',
                recipient_list=['munozjulian146@gmail.com'],
                fail_silently=False,
            )
            
            # Correo de confirmación para el remitente
            send_mail(
                subject='Confirmación de mensaje recibido',
                message=f'Hola {nombre},\n\nGracias por contactarnos. Hemos recibido tu mensaje y nos pondremos en contacto contigo lo antes posible.\n\nResumen de tu mensaje:\n{mensaje}\n\nSaludos cordiales,\nEl equipo de soporte',
                from_email='munozjulian146@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )
            
            messages.success(request, '¡Mensaje enviado correctamente!')
            return redirect('gracias')
        except Exception as e:
            messages.error(request, f'Error al enviar el mensaje: {str(e)}')
            return redirect('formulario')
            
    return render(request, 'formulario.html')


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def enviar_correo_confirmacion(orden):
    """
    Envía un correo de confirmación al usuario con los detalles de su orden.
    """
    subject = f'Confirmación de tu pedido #{orden.id}'
    html_message = render_to_string('email_confirmacion.html', {'orden': orden})
    plain_message = strip_tags(html_message)
    from_email = 'munozjulian146@gmail.com'
    to_email = orden.email

    send_mail(
        subject,
        plain_message,
        from_email,
        [to_email],
        html_message=html_message,
        fail_silently=False,
    )


# reversa

