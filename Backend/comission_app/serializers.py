
from rest_framework import serializers
from .models import Vendedor, Regla, Venta, ComisionCalculada


class VendedorSerializer(serializers.ModelSerializer):
    total_ventas = serializers.SerializerMethodField()
    total_comisiones = serializers.SerializerMethodField()

    class Meta:
        model = Vendedor
        fields = [
            'id', 'nombre', 'fecha_creacion',
            'total_ventas', 'total_comisiones'
        ]
        read_only_fields = ['fecha_creacion']

    def get_total_ventas(self, obj):
        return obj.ventas.count()

    def get_total_comisiones(self, obj):
        total = sum(
            venta.calcular_comision()['comision']
            for venta in obj.ventas.all()
        )
        return float(total)


class ReglaSerializer(serializers.ModelSerializer):
    porcentaje_display = serializers.SerializerMethodField()

    class Meta:
        model = Regla
        fields = [
            'id', 'porcentaje', 'porcentaje_display',
            'monto_minimo', 'fecha_creacion', 'activa'
        ]
        read_only_fields = ['fecha_creacion']

    def get_porcentaje_display(self, obj):
        return f"{float(obj.porcentaje) * 100:.2f}%"


class VentaSerializer(serializers.ModelSerializer):
    vendedor_nombre = serializers.CharField(
        source='vendedor.nombre',
        read_only=True
    )
    comision_calculada = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = [
            'id', 'vendedor', 'vendedor_nombre',
            'fecha_venta', 'monto', 'comision_calculada',
            'fecha_creacion', 'fecha_modificacion'
        ]
        read_only_fields = [
            'fecha_creacion', 'fecha_modificacion'
        ]

    def get_comision_calculada(self, obj):
        datos = obj.calcular_comision()
        regla = datos['regla_aplicada']

        return {
            'monto': float(datos['comision']),
            'porcentaje': float(datos['porcentaje']),
            'regla_id': regla.id if regla else None
        }


class ComisionCalculadaSerializer(serializers.ModelSerializer):
    venta_info = serializers.SerializerMethodField()

    class Meta:
        model = ComisionCalculada
        fields = [
            'id', 'venta', 'venta_info',
            'regla_aplicada', 'monto_comision',
            'porcentaje_aplicado', 'fecha_calculo'
        ]
        read_only_fields = ['fecha_calculo']

    def get_venta_info(self, obj):
        return {
            'vendedor': obj.venta.vendedor.nombre,
            'fecha': obj.venta.fecha_venta,
            'monto': float(obj.venta.monto)
        }


class CalcularComisionesSerializer(serializers.Serializer):
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()

    def validate(self, data):
        if data['fecha_inicio'] > data['fecha_fin']:
            raise serializers.ValidationError(
                "La fecha de inicio no puede ser mayor que la fecha de fin"
            )
        return data
