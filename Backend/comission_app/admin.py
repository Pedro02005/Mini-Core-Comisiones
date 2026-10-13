
from django.contrib import admin
from .models import Vendedor, Regla, Venta, ComisionCalculada

admin.site.register(Vendedor)
admin.site.register(Regla)
admin.site.register(Venta)
admin.site.register(ComisionCalculada)
