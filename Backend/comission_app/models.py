
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


# MODELO VENDEDOR
class Vendedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# MODELO REGLA
class Regla(models.Model):
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))]
    )

    monto_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Regla de Comisión"
        verbose_name_plural = "Reglas de Comisión"
        ordering = ['monto_minimo']

    def __str__(self):
        return f"Regla {self.id}: {self.porcentaje_display()} - Min: ${self.monto_minimo}"

    def porcentaje_display(self):
        return f"{self.porcentaje * 100:.2f}%"


# MODELO VENTA
class Venta(models.Model):
    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.CASCADE,
        related_name='ventas'
    )

    fecha_venta = models.DateField()

    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta', 'fecha_creacion']

    def __str__(self):
        return f"{self.vendedor.nombre} - ${self.monto} ({self.fecha_venta})"

    def calcular_comision(self):
        reglas = Regla.objects.filter(
            activa=True
        ).order_by('-monto_minimo')

        for regla in reglas:
            if self.monto >= regla.monto_minimo:
                comision = self.monto * regla.porcentaje

                return {
                    'comision': comision,
                    'regla_aplicada': regla,
                    'porcentaje': regla.porcentaje
                }

        return {
            'comision': Decimal('0.00'),
            'regla_aplicada': None,
            'porcentaje': Decimal('0.0000')
        }
class ComisionCalculada(models.Model):
    venta = models.OneToOneField(
        Venta,
        on_delete=models.CASCADE,
        related_name='comision_calculada'
    )

    regla_aplicada = models.ForeignKey(
        Regla,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    monto_comision = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    porcentaje_aplicado = models.DecimalField(
        max_digits=5,
        decimal_places=4
    )

    fecha_calculo = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comisión Calculada"
        verbose_name_plural = "Comisiones Calculadas"
        ordering = ['-fecha_calculo']

    def __str__(self):
        return f"Comisión: {self.venta.vendedor.nombre} - ${self.monto_comision}"
