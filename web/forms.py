from django import forms

from web.models import Orden

class OrdenForm(forms.ModelForm):
    METODO_PAGO = [
        ('nequi', 'Nequi'),
        ('bancolombia', 'Bancolombia'),
    ]

    metodo_pago = forms.ChoiceField(choices=METODO_PAGO, widget=forms.RadioSelect, required=True)

    class Meta:
        model = Orden
        fields = ['nombre', 'email', 'telefono', 'metodo_pago']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'munozjulian146@gmail.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu número de Teléfono'}),
        }

class CheckoutForm(forms.ModelForm):
    METODO_PAGO = [
        ('nequi', 'Nequi'),
        ('bancolombia', 'Bancolombia'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('efectivo', 'Efectivo en Entrega'),
    ]

    metodo_pago = forms.ChoiceField(choices=METODO_PAGO, widget=forms.RadioSelect, required=True)

    class Meta:
        model = Orden
        fields = ['nombre', 'email', 'telefono', 'metodo_pago']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu número de Teléfono'}),
        }

# reserva

