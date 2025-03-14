# Generated by Django 5.1.6 on 2025-03-13 00:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_orden_sesion_id_alter_orden_cancelado_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orden',
            name='cancelado',
        ),
        migrations.RemoveField(
            model_name='orden',
            name='direccion',
        ),
        migrations.RemoveField(
            model_name='orden',
            name='pagado',
        ),
        migrations.RemoveField(
            model_name='orden',
            name='sesion_id',
        ),
        migrations.AddField(
            model_name='orden',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('procesando', 'Procesando'), ('enviado', 'Enviado'), ('entregado', 'Entregado'), ('cancelado', 'Cancelado')], default='pendiente', max_length=50),
        ),
        migrations.AlterField(
            model_name='orden',
            name='metodo_pago',
            field=models.CharField(choices=[('tarjeta', 'Tarjeta de Crédito/Débito'), ('transferencia', 'Transferencia Bancaria'), ('efectivo', 'Efectivo en Entrega'), ('nequi', 'Nequi'), ('bancolombia', 'Bancolombia')], max_length=50),
        ),
        migrations.AlterField(
            model_name='orden',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='orden',
            name='usuario',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
