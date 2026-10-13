from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from comission_app.models import Regla, Vendedor, Venta


class Command(BaseCommand):
    help = 'Carga una demo de seis meses solo si vendedores, reglas y ventas están vacíos.'

    @transaction.atomic
    def handle(self, *args, **options):
        if Vendedor.objects.exists() or Regla.objects.exists() or Venta.objects.exists():
            self.stdout.write('Ya hay datos; se conserva la base existente.')
            return

        for minimo, porcentaje in [('100', '0.02'), ('500', '0.05'),
                                    ('1000', '0.08'), ('2000', '0.10'),
                                    ('5000', '0.12')]:
            Regla.objects.create(monto_minimo=Decimal(minimo), porcentaje=Decimal(porcentaje))
        # Una regla inactiva permite explicar por qué no participa del cálculo.
        Regla.objects.create(monto_minimo=Decimal('50'), porcentaje=Decimal('0.15'), activa=False)

        nombres = ['Ana Torres', 'Carlos Mendoza', 'Daniela Ruiz',
                   'Diego Salazar', 'María López', 'Pedro Castillo']
        vendedores = [Vendedor.objects.create(nombre=nombre) for nombre in nombres]
        hoy = timezone.localdate()
        mes_actual = hoy.year * 12 + hoy.month - 1
        montos = ['75', '100', '250', '500', '750', '1000', '1500',
                  '2000', '3200', '5000', '6500', '999.99']
        ventas = []
        for offset in range(6):
            anio, mes_cero = divmod(mes_actual - offset, 12)
            mes = mes_cero + 1
            ultimo_dia = hoy.day if offset == 0 else monthrange(anio, mes)[1]
            for indice, vendedor in enumerate(vendedores):
                for numero in range(4):
                    dia = min(3 + numero * 7 + indice % 3, ultimo_dia)
                    monto = Decimal(montos[(indice * 2 + numero + offset) % len(montos)])
                    ventas.append(Venta(vendedor=vendedor, fecha_venta=date(anio, mes, dia), monto=monto))
        Venta.objects.bulk_create(ventas)
        self.stdout.write(self.style.SUCCESS(
            'Demo creada: 6 vendedores, 6 reglas (5 activas) y 144 ventas en 6 meses.'
        ))
