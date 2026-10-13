
from decimal import Decimal

from django.db.models import Sum

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Vendedor, Regla, Venta, ComisionCalculada
from .serializers import (
    VendedorSerializer,
    ReglaSerializer,
    VentaSerializer,
    ComisionCalculadaSerializer,
    CalcularComisionesSerializer
)


# GESTIÓN DE VENDEDORES
class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer

    @action(detail=True, methods=['get'])
    def ventas(self, request, pk=None):
        vendedor = self.get_object()
        serializer = VentaSerializer(
            vendedor.ventas.all(),
            many=True
        )
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def comisiones(self, request, pk=None):
        vendedor = self.get_object()
        ventas = vendedor.ventas.all()

        total_comisiones = Decimal('0.00')
        total_monto_ventas = Decimal('0.00')
        detalle = []

        for venta in ventas:
            datos = venta.calcular_comision()
            total_comisiones += datos['comision']
            total_monto_ventas += venta.monto

            detalle.append({
                'venta_id': venta.id,
                'fecha': venta.fecha_venta,
                'monto': venta.monto,
                'comision': datos['comision'],
                'porcentaje': datos['porcentaje']
            })

        return Response({
            'vendedor': vendedor.nombre,
            'total_ventas': len(detalle),
            'total_monto_ventas': total_monto_ventas,
            'total_comisiones': total_comisiones,
            'promedio_comision': (
                total_comisiones / len(detalle)
                if detalle else 0
            ),
            'ventas': detalle
        })


# GESTIÓN DE REGLAS
class ReglaViewSet(viewsets.ModelViewSet):
    queryset = Regla.objects.filter(
        activa=True
    ).order_by('monto_minimo')

    serializer_class = ReglaSerializer


# GESTIÓN DE VENTAS
class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

    def get_queryset(self):
        ventas = Venta.objects.all()

        vendedor = self.request.query_params.get('vendedor')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')

        if vendedor:
            ventas = ventas.filter(vendedor__id=vendedor)

        if fecha_inicio:
            ventas = ventas.filter(
                fecha_venta__gte=fecha_inicio
            )

        if fecha_fin:
            ventas = ventas.filter(
                fecha_venta__lte=fecha_fin
            )

        return ventas.order_by('-fecha_venta')


# CONSULTA DE COMISIONES ALMACENADAS
class ComisionCalculadaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ComisionCalculada.objects.all()
    serializer_class = ComisionCalculadaSerializer


# CÁLCULO DE COMISIONES POR PERÍODO
class CalcularComisionesView(APIView):

    def post(self, request):
        serializer = CalcularComisionesSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        inicio = serializer.validated_data['fecha_inicio']
        fin = serializer.validated_data['fecha_fin']

        ventas = Venta.objects.filter(
            fecha_venta__gte=inicio,
            fecha_venta__lte=fin
        ).select_related('vendedor').order_by(
            'vendedor__nombre', 'fecha_venta'
        )

        vendedores = {}

        for venta in ventas:
            nombre = venta.vendedor.nombre

            if nombre not in vendedores:
                vendedores[nombre] = {
                    'vendedor_id': venta.vendedor.id,
                    'vendedor_nombre': nombre,
                    'total_ventas': 0,
                    'total_monto_ventas': Decimal('0.00'),
                    'total_comisiones': Decimal('0.00'),
                    'ventas_detalle': [],
                    'comisiones_individuales': []
                }

            datos = venta.calcular_comision()
            grupo = vendedores[nombre]
            regla = datos['regla_aplicada']

            grupo['total_ventas'] += 1
            grupo['total_monto_ventas'] += venta.monto
            grupo['total_comisiones'] += datos['comision']

            grupo['ventas_detalle'].append({
                'venta_id': venta.id,
                'fecha': venta.fecha_venta,
                'monto': venta.monto,
                'comision': datos['comision'],
                'porcentaje': datos['porcentaje'],
                'regla_aplicada': regla.id if regla else None
            })

            descripcion = "Sin regla aplicable"

            if regla:
                porcentaje = float(datos['porcentaje']) * 100
                descripcion = (
                    f"{porcentaje:.2f}% - Min: ${regla.monto_minimo}"
                )

            grupo['comisiones_individuales'].append({
                'id': venta.id,
                'fecha': venta.fecha_venta.strftime('%d/%m/%Y'),
                'monto_venta': float(venta.monto),
                'porcentaje_aplicado': float(datos['porcentaje']),
                'monto_comision': float(datos['comision']),
                'regla_aplicada': {
                    'id': regla.id if regla else None,
                    'descripcion': descripcion
                }
            })

        for grupo in vendedores.values():
            total = grupo['total_monto_ventas']

            grupo['porcentaje_promedio'] = (
                grupo['total_comisiones'] / total
                if total > 0 else Decimal('0.0000')
            )

        resultado = sorted(
            vendedores.values(),
            key=lambda x: x['total_comisiones'],
            reverse=True
        )

        return Response({
            'fecha_inicio': inicio,
            'fecha_fin': fin,
            'total_vendedores': len(resultado),
            'total_ventas': sum(
                v['total_ventas'] for v in resultado
            ),
            'total_monto_ventas': sum(
                (v['total_monto_ventas'] for v in resultado),
                Decimal('0.00')
            ),
            'total_comisiones': sum(
                (v['total_comisiones'] for v in resultado),
                Decimal('0.00')
            ),
            'periodo_info': {
                'dias_total': (fin - inicio).days + 1,
                'fecha_inicio_formateada': inicio.strftime('%d/%m/%Y'),
                'fecha_fin_formateada': fin.strftime('%d/%m/%Y')
            },
            'vendedores': resultado
        })


# RESUMEN GENERAL DE COMISIONES
class ResumenComisionesView(APIView):

    def get(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        ventas = Venta.objects.all()

        if fecha_inicio:
            ventas = ventas.filter(
                fecha_venta__gte=fecha_inicio
            )

        if fecha_fin:
            ventas = ventas.filter(
                fecha_venta__lte=fecha_fin
            )

        cantidad = ventas.count()
        monto_total = (
            ventas.aggregate(Sum('monto'))['monto__sum']
            or Decimal('0.00')
        )

        total_comisiones = sum(
            (venta.calcular_comision()['comision']
             for venta in ventas),
            Decimal('0.00')
        )

        return Response({
            'periodo': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            },
            'resumen': {
                'total_ventas': cantidad,
                'total_monto_ventas': monto_total,
                'total_comisiones': total_comisiones,
                'promedio_comision_por_venta': (
                    total_comisiones / cantidad
                    if cantidad > 0 else 0
                ),
                'porcentaje_comision_total': (
                    total_comisiones / monto_total * 100
                    if monto_total > 0 else 0
                )
            }
        })
