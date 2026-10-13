
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(
    r'vendedores',
    views.VendedorViewSet
)

router.register(
    r'reglas',
    views.ReglaViewSet
)

router.register(
    r'ventas',
    views.VentaViewSet
)

router.register(
    r'comisiones-calculadas',
    views.ComisionCalculadaViewSet
)

urlpatterns = [
    path('', include(router.urls)),

    path(
        'comisiones/calcular/',
        views.CalcularComisionesView.as_view(),
        name='calcular-comisiones'
    ),

    path(
        'comisiones/resumen/',
        views.ResumenComisionesView.as_view(),
        name='resumen-comisiones'
    ),

    path('api-auth/', include('rest_framework.urls')),
]
