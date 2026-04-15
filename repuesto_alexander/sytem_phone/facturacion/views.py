from django.shortcuts import render, redirect, get_object_or_404
from .models import EntradaProducto, Proveedor,  Cliente, Caja, Venta, DetalleVenta, MovimientoStock, CuentaPorCobrar, PagoCuentaPorCobrar, CierreCaja, ComprobantePago, Rol, CuentaPorPagar, DetalleCuentaPorPagar, Devolucion
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.template.loader import get_template
from django.http import JsonResponse
from django.db import models
from django.core.validators import ValidationError
from django.db import transaction
from decimal import Decimal
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from datetime import datetime, time as datetime_time
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.apps import apps
import pytz
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.pagesizes import mm
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os
from django.conf import settings
import random
import string
from django.core.mail import send_mail
# hola
from django.urls import reverse
# import time

from django.db.models import Max
from django.db.models import Sum, Q, F, Avg, Count, ExpressionWrapper, DecimalField, Value
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncDate, ExtractMonth
from datetime import datetime, timedelta, time
import pandas as pd
from decimal import Decimal, InvalidOperation
import logging

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User, Group, Permission
import csv
from reportlab.pdfgen import canvas
import traceback
from django.http import JsonResponse
from functools import wraps

# from weasyprint import HTML
from django.template.loader import render_to_string
from functools import wraps
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from xhtml2pdf import pisa
from decimal import Decimal
from datetime import date

from reportlab.lib.units import cm

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.management.base import BaseCommand
from celery import shared_task

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal
import json

from django.core.mail import EmailMessage
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
import csv
from django.db import IntegrityError
from django.db.models.signals import post_migrate

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
import json
from django.contrib.auth import authenticate, logout, login as auth_login

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
import json


# ==============================================================================================
# ==============================Funciones de control de acceso=================================
# ==============================================================================================
def is_superuser_or_usuario_normal(user):
    return user.is_superuser or user.groups.filter(name='Usuario Normal').exists()

# ==============================================================================================
# ==============================Funciones de control de acceso=================================
# ==============================================================================================


def is_superuser(user):
    return user.is_superuser
# ==============================================================================================
# ==============================Funciones de control de acceso=================================
# ==============================================================================================


def is_superuser_or_almacen(user):
    return user.is_superuser or user.groups.filter(name='Almacén').exists()

# ==============================================================================================
# ==============================Funciones de control de acceso=================================
# ==============================================================================================


def check_module_access(module_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Superusuarios tienen acceso total
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Verificar si el usuario tiene acceso al módulo
            user_groups = request.user.groups.values_list('name', flat=True)

            # Módulos permitidos por defecto para todos los usuarios
            allowed_modules = ['ventas', 'inventario']

            if module_name in allowed_modules:
                return view_func(request, *args, **kwargs)

            # Si no tiene acceso, redirigir
            messages.error(
                request, 'No tienes permiso para acceder a este módulo.')
            return redirect('ventas')

        return wrapper
    return decorator


# ==============================================================================================
# ==============================inicio de seccion===============================================
# ==============================================================================================
@ensure_csrf_cookie
@never_cache
def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 1) Super user -> dashboard
            if user.is_superuser:
                return redirect('dashboard')

            # 2) Normalizar nombres de grupos para evitar problemas con mayúsculas/acentos
            grupos = set()
            for g in user.groups.values_list('name', flat=True):
                nombre = (g or '').strip().lower()
                nombre = nombre.replace('á', 'a').replace('é', 'e').replace(
                    'í', 'i').replace('ó', 'o').replace('ú', 'u')
                grupos.add(nombre)

            # 3) Almacén -> entrada de mercancía
            if 'almacen' in grupos:
                return redirect('entrada')

            # 4) Usuario normal -> caja
            # Si tu "caja" real es ventas, cambia 'cierredecaja' por 'ventas'
            if 'usuario normal' in grupos:
                return redirect('ventas')

            # 5) Cualquier otro rol -> dashboard
            return redirect('dashboard')

        messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'facturacion/index.html')


def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    request.session.flush()
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('index')

# ==============================================================================================
# ==============================Dashboard - Vista principal con KPIs y gráficos=================
# ==============================================================================================


@user_passes_test(is_superuser, login_url='/')
@login_required
def dashboard(request):
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    inicio_semana = hoy - timedelta(days=hoy.weekday())

    try:
        # Ventas al contado (total de ventas contado)
        ventas_contado_hoy = Venta.objects.filter(
            fecha_venta__date=hoy,
            anulada=False,
            tipo_venta='contado'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        # Ventas a crédito (solo monto_pagado)
        ventas_credito_hoy = CuentaPorCobrar.objects.filter(
            venta__fecha_venta__date=hoy,
            venta__anulada=False,
            venta__tipo_venta='credito',
            anulada=False
        ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

        # Total ventas hoy
        ventas_hoy = ventas_contado_hoy + ventas_credito_hoy

        # Ventas al contado (mes)
        ventas_contado_mes = Venta.objects.filter(
            fecha_venta__date__gte=inicio_mes,
            anulada=False,
            tipo_venta='contado'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        # Ventas a crédito (mes)
        ventas_credito_mes = CuentaPorCobrar.objects.filter(
            venta__fecha_venta__date__gte=inicio_mes,
            venta__anulada=False,
            venta__tipo_venta='credito',
            anulada=False
        ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

        # Total ventas mes
        ventas_mes = ventas_contado_mes + ventas_credito_mes

        # Ventas de la semana
        ventas_semana = []
        dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

        for i in range(7):
            dia = inicio_semana + timedelta(days=i)

            # Ventas contado del día
            ventas_contado_dia = Venta.objects.filter(
                fecha_venta__date=dia,
                anulada=False,
                tipo_venta='contado'
            ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

            # Ventas crédito del día
            ventas_credito_dia = CuentaPorCobrar.objects.filter(
                venta__fecha_venta__date=dia,
                venta__anulada=False,
                venta__tipo_venta='credito',
                anulada=False
            ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

            # Total del día
            total_dia = float(ventas_contado_dia + ventas_credito_dia)
            ventas_semana.append(total_dia)

        # Tendencia mensual real (enero-diciembre del anio actual)
        monthly_trend = [0.0] * 12

        ventas_contado_por_mes = Venta.objects.filter(
            fecha_venta__year=hoy.year,
            anulada=False,
            tipo_venta='contado'
        ).annotate(
            mes=ExtractMonth('fecha_venta')
        ).values('mes').annotate(
            total=Sum('total')
        )

        ventas_credito_por_mes = CuentaPorCobrar.objects.filter(
            venta__fecha_venta__year=hoy.year,
            venta__anulada=False,
            venta__tipo_venta='credito',
            anulada=False
        ).annotate(
            mes=ExtractMonth('venta__fecha_venta')
        ).values('mes').annotate(
            total=Sum('monto_pagado')
        )

        for item in ventas_contado_por_mes:
            mes = item.get('mes')
            if mes:
                monthly_trend[mes - 1] += float(item.get('total') or 0)

        for item in ventas_credito_por_mes:
            mes = item.get('mes')
            if mes:
                monthly_trend[mes - 1] += float(item.get('total') or 0)

        # Inventario
        total_stock = EntradaProducto.objects.filter(
            activo=True).aggregate(total=Sum('cantidad'))['total'] or 0
        productos_bajo_stock = EntradaProducto.objects.filter(
            activo=True, cantidad__lte=F('cantidad_minima')
        ).count()

        # Top productos últimos 30 días - CORREGIDO: usar 'descripcion' en lugar de 'nombre_producto'
        fecha_30_dias = hoy - timedelta(days=30)
        top_productos = DetalleVenta.objects.filter(
            venta__anulada=False,
            venta__fecha_venta__date__gte=fecha_30_dias
        ).values(
            'producto__descripcion'  # CAMBIO AQUÍ
        ).annotate(
            total_vendido=Sum('cantidad')
        ).order_by('-total_vendido')[:5]

        # Convertir a la estructura correcta para el template
        top_productos_list = [{
            'nombre_producto': item['producto__descripcion'],  # CAMBIO AQUÍ
            'total_vendido': item['total_vendido']
        } for item in top_productos]

        # Últimas ventas
        ultimas_ventas = Venta.objects.filter(
            anulada=False
        ).select_related('cliente').order_by('-fecha_venta')[:8]

        # Productos inventario - CORREGIDO: usar 'descripcion' en lugar de 'nombre_producto'
        productos_inventario = list(
            EntradaProducto.objects.filter(activo=True)
            # CAMBIOS AQUÍ
            .values('descripcion', 'marca', 'cantidad', 'precio')[:10]
        )

        # Alertas de stock bajo - CORREGIDO
        alertas = [
            f"{p['descripcion']} - Solo {p['cantidad']} unidades restantes (mínimo: {p['cantidad_minima']})"
            for p in EntradaProducto.objects.filter(
                activo=True, cantidad__lte=F('cantidad_minima')
            ).values('descripcion', 'cantidad', 'cantidad_minima')  # CAMBIO AQUÍ
        ]

        # Cuentas vencidas
        cuentas_vencidas = CuentaPorCobrar.objects.filter(
            fecha_vencimiento__lt=hoy,
            estado__in=['pendiente', 'parcial'],
            anulada=False
        ).count()

        context = {
            'ventas_hoy': float(ventas_hoy),
            'ventas_mes': float(ventas_mes),
            'total_stock': total_stock,
            'productos_bajo_stock': productos_bajo_stock,
            'cuentas_vencidas': cuentas_vencidas,
            'ventas_semana': json.dumps(ventas_semana),
            'dias_semana': json.dumps(dias_semana),
            'top_productos': json.dumps(top_productos_list),
            'ultimas_ventas': ultimas_ventas,
            'productos_inventario': productos_inventario,
            'alertas': json.dumps(alertas[:5]),
        }
        return render(request, "facturacion/dashboard.html", context)

    except Exception as e:
        print(f"Error en dashboard: {e}")
        import traceback
        traceback.print_exc()
        return dashboard_tradicional(request)

# ==============================================================================================
# ==============================Dashboard - Datos para gráficos=================================
# ==============================================================================================


def dashboard_data(request):
    try:
        # Zona horaria República Dominicana para mostrar horas en el dashboard
        tz_rd = pytz.timezone('America/Santo_Domingo')
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)
        inicio_semana = hoy - timedelta(days=hoy.weekday())

        # Ventas al contado (total de ventas contado)
        ventas_contado_hoy = Venta.objects.filter(
            fecha_venta__date=hoy,
            anulada=False,
            tipo_venta='contado'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        # Ventas a crédito (solo monto_pagado)
        ventas_credito_hoy = CuentaPorCobrar.objects.filter(
            venta__fecha_venta__date=hoy,
            venta__anulada=False,
            venta__tipo_venta='credito',
            anulada=False
        ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

        # Total ventas hoy
        ventas_hoy = ventas_contado_hoy + ventas_credito_hoy

        # Ventas al contado (mes)
        ventas_contado_mes = Venta.objects.filter(
            fecha_venta__date__gte=inicio_mes,
            anulada=False,
            tipo_venta='contado'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        # Ventas a crédito (mes)
        ventas_credito_mes = CuentaPorCobrar.objects.filter(
            venta__fecha_venta__date__gte=inicio_mes,
            venta__anulada=False,
            venta__tipo_venta='credito',
            anulada=False
        ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

        # Total ventas mes
        ventas_mes = ventas_contado_mes + ventas_credito_mes

        # Ventas de la semana
        ventas_semana = []
        dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

        for i in range(7):
            dia = inicio_semana + timedelta(days=i)

            # Ventas contado del día
            ventas_contado_dia = Venta.objects.filter(
                fecha_venta__date=dia,
                anulada=False,
                tipo_venta='contado'
            ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

            # Ventas crédito del día
            ventas_credito_dia = CuentaPorCobrar.objects.filter(
                venta__fecha_venta__date=dia,
                venta__anulada=False,
                venta__tipo_venta='credito',
                anulada=False
            ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

            # Total del día
            total_dia = float(ventas_contado_dia + ventas_credito_dia)
            ventas_semana.append(total_dia)

        # Tendencia mensual real (enero-diciembre del anio actual)
        monthly_trend = [0.0] * 12

        ventas_contado_por_mes = Venta.objects.filter(
            fecha_venta__year=hoy.year,
            anulada=False,
            tipo_venta='contado'
        ).annotate(
            mes=ExtractMonth('fecha_venta')
        ).values('mes').annotate(
            total=Sum('total')
        )

        ventas_credito_por_mes = CuentaPorCobrar.objects.filter(
            venta__fecha_venta__year=hoy.year,
            venta__anulada=False,
            venta__tipo_venta='credito',
            anulada=False
        ).annotate(
            mes=ExtractMonth('venta__fecha_venta')
        ).values('mes').annotate(
            total=Sum('monto_pagado')
        )

        for item in ventas_contado_por_mes:
            mes = item.get('mes')
            if mes:
                monthly_trend[mes - 1] += float(item.get('total') or 0)

        for item in ventas_credito_por_mes:
            mes = item.get('mes')
            if mes:
                monthly_trend[mes - 1] += float(item.get('total') or 0)

        # Inventario
        total_stock = EntradaProducto.objects.filter(
            activo=True).aggregate(total=Sum('cantidad'))['total'] or 0
        productos_bajo_stock = EntradaProducto.objects.filter(
            activo=True, cantidad__lte=F('cantidad_minima')
        ).count()

        # Top productos últimos 30 días - CORREGIDO
        fecha_30_dias = hoy - timedelta(days=30)
        top_productos = DetalleVenta.objects.filter(
            venta__anulada=False,
            venta__fecha_venta__date__gte=fecha_30_dias
        ).values(
            'producto__descripcion'
        ).annotate(
            total_vendido=Sum('cantidad')
        ).order_by('-total_vendido')[:5]

        # Últimas ventas
        ultimas_ventas = Venta.objects.filter(
            anulada=False
        ).select_related('cliente').order_by('-fecha_venta')[:8]

        # Inventario detalle - CORREGIDO
        productos_inventario = list(
            EntradaProducto.objects.filter(activo=True)
            .values('descripcion', 'marca', 'cantidad', 'precio', 'cantidad_minima')[:10]
        )

        # Alertas - CORREGIDO
        alertas = [
            f"{p['descripcion']} - Solo {p['cantidad']} unidades restantes (mínimo: {p['cantidad_minima']})"
            for p in EntradaProducto.objects.filter(
                activo=True, cantidad__lte=F('cantidad_minima')
            ).values('descripcion', 'cantidad', 'cantidad_minima')
        ]

        # Cuentas vencidas
        cuentas_vencidas = CuentaPorCobrar.objects.filter(
            fecha_vencimiento__lt=hoy,
            estado__in=['pendiente', 'parcial'],
            anulada=False
        ).count()

        # =============================================
        # CÁLCULOS DEL VALOR DEL INVENTARIO (OPTIMIZADOS)
        # =============================================
        productos_activos = EntradaProducto.objects.filter(activo=True)

        valor_expr = ExpressionWrapper(
            F('costo') * F('cantidad'),
            output_field=DecimalField(max_digits=18, decimal_places=2)
        )
        inversion_expr = ExpressionWrapper(
            Coalesce(F('precio_con_itbis'), F('precio')) * F('cantidad'),
            output_field=DecimalField(max_digits=18, decimal_places=2)
        )

        inventario_totales = productos_activos.aggregate(
            total_value=Coalesce(Sum(valor_expr), Value(
                0), output_field=DecimalField(max_digits=18, decimal_places=2)),
            total_investment=Coalesce(Sum(inversion_expr), Value(
                0), output_field=DecimalField(max_digits=18, decimal_places=2))
        )

        valor_total_inventario = float(inventario_totales['total_value'] or 0)
        inversion_total = float(inventario_totales['total_investment'] or 0)
        ganancia_potencial = inversion_total - valor_total_inventario

        marcas_map = dict(EntradaProducto.MARCAS)

        valores_por_marca_qs = (
            productos_activos
            .values('marca')
            .annotate(
                valor_total=Coalesce(
                    Sum(valor_expr),
                    Value(0),
                    output_field=DecimalField(max_digits=18, decimal_places=2)
                )
            )
            .order_by('-valor_total')
        )

        valores_por_marca = [
            {
                'marca': marcas_map.get(item['marca'], item['marca']),
                'valorTotal': round(float(item['valor_total'] or 0), 2)
            }
            for item in valores_por_marca_qs
        ]

        productos_mayor_valor_qs = (
            productos_activos
            .annotate(valor_total=valor_expr)
            .values('descripcion', 'marca', 'cantidad', 'cantidad_minima', 'costo', 'precio', 'valor_total')
            .order_by('-valor_total')[:10]
        )

        productos_mayor_valor = [
            {
                'descripcion': item['descripcion'],
                'marca': marcas_map.get(item['marca'], item['marca']),
                'cantidad': item['cantidad'],
                'cantidad_minima': item['cantidad_minima'],
                'costo': float(item['costo'] or 0),
                'precio': float(item['precio'] or 0),
                'valorTotal': round(float(item['valor_total'] or 0), 2)
            }
            for item in productos_mayor_valor_qs
        ]

        data = {
            'sales': {
                'daily': float(ventas_hoy),
                'monthly': float(ventas_mes),
                'weekly': ventas_semana,
                'weekLabels': dias_semana,
                'monthlyTrend': monthly_trend,
                'monthLabels': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            },
            'inventory': {
                'totalStock': total_stock,
                'totalSold': 0,
                'lowStockItems': productos_bajo_stock,
                'categories': [
                    {'name': 'SuperGato', 'count': 75},
                    {'name': 'Zusuki', 'count': 45},
                    {'name': 'CG300', 'count': 25},
                    {'name': 'Tauro', 'count': 11}
                ]
            },
            'topProducts': [{
                'nombre_producto': item['producto__descripcion'],
                'total_vendido': item['total_vendido']
            } for item in top_productos],
            'recentSales': [{
                'id': venta.id,
                'producto': f"{venta.cliente_nombre} - {venta.numero_factura}",
                'monto': float(venta.total),
                'fecha': venta.fecha_venta.strftime('%d-%m-%Y'),
                'hora': timezone.localtime(venta.fecha_venta, tz_rd).strftime('%I:%M'),
                'estado': 'completada',
                'cantidad': 1
            } for venta in ultimas_ventas],
            'inventoryItems': productos_inventario,
            'lowStockAlerts': alertas[:5],
            'overdueAccounts': cuentas_vencidas,
            # =============================================
            # NUEVO: DATOS DEL VALOR DEL INVENTARIO
            # =============================================
            'inventoryValue': {
                'totalValue': round(valor_total_inventario, 2),
                'totalInvestment': round(inversion_total, 2),
                'potentialProfit': round(ganancia_potencial, 2),
                'brandValues': valores_por_marca,
                'highValueProducts': productos_mayor_valor
            }
        }
        return JsonResponse(data)

    except Exception as e:
        print(f"Error en dashboard_data: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


def dashboard_tradicional(request):
    """Versión tradicional sin pandas"""
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    inicio_semana = hoy - timedelta(days=hoy.weekday())

    # Ventas al contado (total de ventas contado)
    ventas_contado_hoy = Venta.objects.filter(
        fecha_venta__date=hoy,
        anulada=False,
        tipo_venta='contado'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

    # Ventas a crédito (solo monto_pagado)
    ventas_credito_hoy = CuentaPorCobrar.objects.filter(
        venta__fecha_venta__date=hoy,
        venta__anulada=False,
        venta__tipo_venta='credito',
        anulada=False
    ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

    # Total ventas hoy
    ventas_hoy = ventas_contado_hoy + ventas_credito_hoy

    # Ventas al contado (mes)
    ventas_contado_mes = Venta.objects.filter(
        fecha_venta__date__gte=inicio_mes,
        anulada=False,
        tipo_venta='contado'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

    # Ventas a crédito (mes)
    ventas_credito_mes = CuentaPorCobrar.objects.filter(
        venta__fecha_venta__date__gte=inicio_mes,
        venta__anulada=False,
        venta__tipo_venta='credito',
        anulada=False
    ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

    # Total ventas mes
    ventas_mes = ventas_contado_mes + ventas_credito_mes

    # Ventas de la semana
    ventas_semana = []
    dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    for i in range(7):
        dia = inicio_semana + timedelta(days=i)

        # Ventas contado del día
        ventas_contado_dia = Venta.objects.filter(
            fecha_venta__date=dia,
            anulada=False,
            tipo_venta='contado'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        # Ventas crédito del día
        ventas_credito_dia = CuentaPorCobrar.objects.filter(
            venta__fecha_venta__date=dia,
            venta__anulada=False,
            venta__tipo_venta='credito',
            anulada=False
        ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

        # Total del día
        total_dia = float(ventas_contado_dia + ventas_credito_dia)
        ventas_semana.append(total_dia)

    # Tendencia mensual real (enero-diciembre del anio actual)
    monthly_trend = [0.0] * 12

    ventas_contado_por_mes = Venta.objects.filter(
        fecha_venta__year=hoy.year,
        anulada=False,
        tipo_venta='contado'
    ).annotate(
        mes=ExtractMonth('fecha_venta')
    ).values('mes').annotate(
        total=Sum('total')
    )

    ventas_credito_por_mes = CuentaPorCobrar.objects.filter(
        venta__fecha_venta__year=hoy.year,
        venta__anulada=False,
        venta__tipo_venta='credito',
        anulada=False
    ).annotate(
        mes=ExtractMonth('venta__fecha_venta')
    ).values('mes').annotate(
        total=Sum('monto_pagado')
    )

    for item in ventas_contado_por_mes:
        mes = item.get('mes')
        if mes:
            monthly_trend[mes - 1] += float(item.get('total') or 0)

    for item in ventas_credito_por_mes:
        mes = item.get('mes')
        if mes:
            monthly_trend[mes - 1] += float(item.get('total') or 0)

    # Inventario
    total_stock = EntradaProducto.objects.filter(activo=True).aggregate(
        total=Sum('cantidad')
    )['total'] or 0

    productos_bajo_stock = EntradaProducto.objects.filter(
        activo=True,
        cantidad__lte=F('cantidad_minima')
    ).count()

    # Top productos últimos 30 días - CORREGIDO
    fecha_30_dias = hoy - timedelta(days=30)
    top_productos = DetalleVenta.objects.filter(
        venta__anulada=False,
        venta__fecha_venta__date__gte=fecha_30_dias
    ).values(
        'producto__descripcion'  # CAMBIO AQUÍ
    ).annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]

    # Convertir a la estructura correcta
    top_productos_list = [{
        'nombre_producto': item['producto__descripcion'],  # CAMBIO AQUÍ
        'total_vendido': item['total_vendido']
    } for item in top_productos]

    # Últimas ventas
    ultimas_ventas = Venta.objects.filter(
        anulada=False
    ).select_related('cliente').order_by('-fecha_venta')[:8]

    # Productos en inventario - CORREGIDO
    productos_inventario = EntradaProducto.objects.filter(
        activo=True
    ).values('descripcion', 'marca', 'cantidad', 'precio')[:10]  # CAMBIOS AQUÍ

    # Alertas de stock bajo - CORREGIDO
    alertas_stock = EntradaProducto.objects.filter(
        activo=True,
        cantidad__lte=F('cantidad_minima')
    ).values('descripcion', 'cantidad', 'cantidad_minima')  # CAMBIO AQUÍ

    alertas = [
        f"{p['descripcion']} - Solo {p['cantidad']} unidades restantes (mínimo: {p['cantidad_minima']})"
        for p in alertas_stock
    ]

    # Cuentas por cobrar vencidas
    cuentas_vencidas = CuentaPorCobrar.objects.filter(
        fecha_vencimiento__lt=hoy,
        estado__in=['pendiente', 'parcial'],
        anulada=False
    ).count()

    context = {
        'ventas_hoy': float(ventas_hoy),
        'ventas_mes': float(ventas_mes),
        'total_stock': total_stock,
        'productos_bajo_stock': productos_bajo_stock,
        'cuentas_vencidas': cuentas_vencidas,
        'ventas_semana': json.dumps(ventas_semana),
        'dias_semana': json.dumps(dias_semana),
        'top_productos': json.dumps(top_productos_list),
        'ultimas_ventas': ultimas_ventas,
        'productos_inventario': productos_inventario,
        'alertas': json.dumps(alertas[:5]),
    }

    return render(request, "facturacion/dashboard.html", context)

# ==============================================================================================
# ==============================Dashboard - Datos para gráficos (versión tradicional)===============
# ==============================================================================================


def dashboard_data_tradicional(request):
    """Versión tradicional sin pandas para JSON"""
    # Zona horaria República Dominicana para mostrar horas en el dashboard
    tz_rd = pytz.timezone('America/Santo_Domingo')
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    inicio_semana = hoy - timedelta(days=hoy.weekday())

    # Ventas al contado (total de ventas contado)
    ventas_contado_hoy = Venta.objects.filter(
        fecha_venta__date=hoy,
        anulada=False,
        tipo_venta='contado'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

    # Ventas a crédito (solo monto_pagado)
    ventas_credito_hoy = CuentaPorCobrar.objects.filter(
        venta__fecha_venta__date=hoy,
        venta__anulada=False,
        venta__tipo_venta='credito',
        anulada=False
    ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

    # Total ventas hoy
    ventas_hoy = ventas_contado_hoy + ventas_credito_hoy

    # Ventas al contado (mes)
    ventas_contado_mes = Venta.objects.filter(
        fecha_venta__date__gte=inicio_mes,
        anulada=False,
        tipo_venta='contado'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

    # Ventas a crédito (mes)
    ventas_credito_mes = CuentaPorCobrar.objects.filter(
        venta__fecha_venta__date__gte=inicio_mes,
        venta__anulada=False,
        venta__tipo_venta='credito',
        anulada=False
    ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

    # Total ventas mes
    ventas_mes = ventas_contado_mes + ventas_credito_mes

    # Ventas de la semana
    ventas_semana = []
    dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    for i in range(7):
        dia = inicio_semana + timedelta(days=i)

        # Ventas contado del día
        ventas_contado_dia = Venta.objects.filter(
            fecha_venta__date=dia,
            anulada=False,
            tipo_venta='contado'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        # Ventas crédito del día
        ventas_credito_dia = CuentaPorCobrar.objects.filter(
            venta__fecha_venta__date=dia,
            venta__anulada=False,
            venta__tipo_venta='credito',
            anulada=False
        ).aggregate(total=Sum('monto_pagado'))['total'] or Decimal('0.00')

        # Total del día
        total_dia = float(ventas_contado_dia + ventas_credito_dia)
        ventas_semana.append(total_dia)

    # Tendencia mensual (enero-diciembre del año actual)
    monthly_trend = [0.0] * 12

    ventas_contado_por_mes = Venta.objects.filter(
        fecha_venta__year=hoy.year,
        anulada=False,
        tipo_venta='contado'
    ).annotate(
        mes=ExtractMonth('fecha_venta')
    ).values('mes').annotate(
        total=Sum('total')
    )

    ventas_credito_por_mes = CuentaPorCobrar.objects.filter(
        venta__fecha_venta__year=hoy.year,
        venta__anulada=False,
        venta__tipo_venta='credito',
        anulada=False
    ).annotate(
        mes=ExtractMonth('venta__fecha_venta')
    ).values('mes').annotate(
        total=Sum('monto_pagado')
    )

    for item in ventas_contado_por_mes:
        mes = item.get('mes')
        if mes:
            monthly_trend[mes - 1] += float(item.get('total') or 0)

    for item in ventas_credito_por_mes:
        mes = item.get('mes')
        if mes:
            monthly_trend[mes - 1] += float(item.get('total') or 0)

    # Inventario
    total_stock = EntradaProducto.objects.filter(activo=True).aggregate(
        total=Sum('cantidad')
    )['total'] or 0

    productos_bajo_stock = EntradaProducto.objects.filter(
        activo=True,
        cantidad__lte=F('cantidad_minima')
    ).count()

    # Top productos últimos 30 días
    fecha_30_dias = hoy - timedelta(days=30)
    top_productos = DetalleVenta.objects.filter(
        venta__anulada=False,
        venta__fecha_venta__date__gte=fecha_30_dias
    ).values(
        'producto__descripcion'
    ).annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]

    # Últimas ventas
    ultimas_ventas = Venta.objects.filter(
        anulada=False
    ).select_related('cliente').order_by('-fecha_venta')[:8]

    # Inventario
    productos_inventario = list(EntradaProducto.objects.filter(
        activo=True
    ).values('descripcion', 'marca', 'cantidad', 'precio', 'cantidad_minima')[:10])

    # Alertas
    alertas_stock = EntradaProducto.objects.filter(
        activo=True,
        cantidad__lte=F('cantidad_minima')
    ).values('descripcion', 'cantidad', 'cantidad_minima')

    alertas = [
        f"{p['descripcion']} - Solo {p['cantidad']} unidades restantes (mínimo: {p['cantidad_minima']})"
        for p in alertas_stock
    ]

    # Cuentas por cobrar vencidas
    cuentas_vencidas = CuentaPorCobrar.objects.filter(
        fecha_vencimiento__lt=hoy,
        estado__in=['pendiente', 'parcial'],
        anulada=False
    ).count()

    data = {
        'sales': {
            'daily': float(ventas_hoy),
            'monthly': float(ventas_mes),
            'weekly': ventas_semana,
            'weekLabels': dias_semana,
            'monthlyTrend': monthly_trend,
            'monthLabels': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        },
        'inventory': {
            'totalStock': total_stock,
            'totalSold': 0,
            'lowStockItems': productos_bajo_stock,
            'categories': [
                {'name': 'Supergato', 'count': 75},
                {'name': 'Accesorios', 'count': 45},
                {'name': 'Repuestos', 'count': 25},
                {'name': 'Tablets', 'count': 11}
            ]
        },
        'topProducts': [{
            'nombre_producto': item['producto__descripcion'],
            'total_vendido': item['total_vendido']
        } for item in top_productos],
        'recentSales': [{
            'id': venta.id,
            'producto': f"{venta.cliente_nombre} - {venta.numero_factura}",
            'monto': float(venta.total),
            'fecha': venta.fecha_venta.strftime('%d-%m-%Y'),
            'hora': timezone.localtime(venta.fecha_venta, tz_rd).strftime('%I:%M'),
            'estado': 'completada',
            'cantidad': 1
        } for venta in ultimas_ventas],
        'inventoryItems': productos_inventario,
        'lowStockAlerts': alertas[:5],
        'overdueAccounts': cuentas_vencidas
    }

    return JsonResponse(data)


def movimientos_stock(request):
    """API para obtener movimientos de stock - INCLUYENDO VENTAS Y ENTRADAS"""
    try:
        movimientos_data = []
        limite_total = 300
        limite_fuente = 200
        tz_rd = pytz.timezone('America/Santo_Domingo')

        def format_rd_datetime(dt):
            if not dt:
                return "Fecha no disponible"
            try:
                return timezone.localtime(dt, tz_rd).strftime('%d-%m-%Y %I:%M')
            except Exception:
                return dt.strftime('%d-%m-%Y %I:%M')

        # =============================================
        # 1. OBTENER ENTRADAS DE PRODUCTOS (COMPRAS)
        # =============================================
        # El error indica que EntradaProducto tiene solo 'proveedor' como relación
        # Probablemente EntradaProducto ES el producto en sí mismo, no tiene relación con otro modelo Producto

        print("=== DEBUG: Obteniendo entradas de productos ===")

        # Definir entradas sin slicing para poder filtrar correctamente por fecha.
        try:
            entradas = EntradaProducto.objects.select_related(
                'proveedor').all().order_by('-fecha_entrada')
            campo_fecha_entrada = 'fecha_entrada'
        except Exception:
            try:
                entradas = EntradaProducto.objects.select_related(
                    'proveedor').all().order_by('-fecha_registro')
                campo_fecha_entrada = 'fecha_registro'
            except Exception:
                entradas = EntradaProducto.objects.select_related(
                    'proveedor').all().order_by('-id')
                campo_fecha_entrada = None

        # =============================================
        # 2. OBTENER MOVIMIENTOS DE STOCK (AJUSTES, ETC.)
        # =============================================
        movimientos = MovimientoStock.objects.select_related(
            'producto', 'usuario').order_by('-fecha_movimiento')

        # =============================================
        # 3. OBTENER VENTAS (DETALLES DE VENTA)
        # =============================================
        ventas = DetalleVenta.objects.select_related(
            'venta', 'producto', 'venta__vendedor'
        ).filter(
            venta__anulada=False
        ).order_by('-venta__fecha_venta')

        # =============================================
        # 4. APLICAR FILTROS
        # =============================================
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        tipo_movimiento = request.GET.get('tipo_movimiento')

        print(
            f"Filtros recibidos: fecha_desde={fecha_desde}, fecha_hasta={fecha_hasta}, tipo={tipo_movimiento}")

        # Aplicar filtros a entradas
        if fecha_desde:
            try:
                if campo_fecha_entrada == 'fecha_entrada':
                    entradas = entradas.filter(fecha_entrada__gte=fecha_desde)
                elif campo_fecha_entrada == 'fecha_registro':
                    entradas = entradas.filter(
                        fecha_registro__date__gte=fecha_desde)
            except Exception as e:
                print(f"Error filtrando fecha_desde en entradas: {e}")

        if fecha_hasta:
            try:
                if campo_fecha_entrada == 'fecha_entrada':
                    entradas = entradas.filter(fecha_entrada__lte=fecha_hasta)
                elif campo_fecha_entrada == 'fecha_registro':
                    entradas = entradas.filter(
                        fecha_registro__date__lte=fecha_hasta)
            except Exception as e:
                print(f"Error filtrando fecha_hasta en entradas: {e}")

        if tipo_movimiento and tipo_movimiento != 'entrada':
            entradas = entradas.none()

        # Aplicar filtros a movimientos de stock
        if fecha_desde:
            movimientos = movimientos.filter(
                fecha_movimiento__date__gte=fecha_desde)
        if fecha_hasta:
            movimientos = movimientos.filter(
                fecha_movimiento__date__lte=fecha_hasta)
        if tipo_movimiento and tipo_movimiento not in ['entrada', 'venta']:
            movimientos = movimientos.filter(tipo_movimiento=tipo_movimiento)

        # Aplicar filtros a ventas
        if fecha_desde:
            ventas = ventas.filter(venta__fecha_venta__date__gte=fecha_desde)
        if fecha_hasta:
            ventas = ventas.filter(venta__fecha_venta__date__lte=fecha_hasta)
        if tipo_movimiento == 'venta':
            # Si solo se quiere ver ventas
            pass
        elif tipo_movimiento and tipo_movimiento != 'venta':
            # Si se filtra por otro tipo, excluir ventas
            ventas = ventas.none()

        # Limitar registros por fuente después de aplicar filtros
        entradas = entradas[:limite_fuente]
        movimientos = movimientos[:limite_fuente]
        ventas = ventas[:limite_fuente]

        # =============================================
        # 5. PROCESAR ENTRADAS DE PRODUCTOS
        # =============================================
        print("Procesando entradas...")

        for entrada in entradas:
            try:
                # Obtener nombre del producto directamente de EntradaProducto
                # EntradaProducto probablemente tiene campos como 'descripcion', 'nombre_producto', etc.
                producto_nombre = ""

                if hasattr(entrada, 'descripcion') and entrada.descripcion:
                    producto_nombre = entrada.descripcion
                elif hasattr(entrada, 'nombre_producto') and entrada.nombre_producto:
                    producto_nombre = entrada.nombre_producto
                elif hasattr(entrada, 'nombre') and entrada.nombre:
                    producto_nombre = entrada.nombre
                else:
                    producto_nombre = f"Producto ID: {entrada.id}"

                # Obtener usuario que hizo la entrada
                usuario_nombre = "Sistema"

                # Intentar obtener usuario de diferentes maneras
                if hasattr(entrada, 'usuario') and entrada.usuario:
                    usuario_nombre = entrada.usuario.username
                elif hasattr(entrada, 'vendedor') and entrada.vendedor:
                    usuario_nombre = entrada.vendedor.username
                elif hasattr(entrada, 'creado_por') and entrada.creado_por:
                    usuario_nombre = entrada.creado_por.username
                elif hasattr(entrada, 'proveedor') and entrada.proveedor:
                    # Si no hay usuario, al menos mostrar el proveedor
                    usuario_nombre = f"Proveedor: {entrada.proveedor}"

                # Obtener fecha
                fecha_str = "Fecha no disponible"
                if hasattr(entrada, 'fecha_entrada') and entrada.fecha_entrada:
                    fecha_str = entrada.fecha_entrada.strftime(
                        '%d-%m-%Y %I:%M')
                elif hasattr(entrada, 'fecha_registro') and entrada.fecha_registro:
                    fecha_str = format_rd_datetime(entrada.fecha_registro)
                elif hasattr(entrada, 'created_at') and entrada.created_at:
                    fecha_str = format_rd_datetime(entrada.created_at)

                # Obtener cantidad
                cantidad = 0
                if hasattr(entrada, 'cantidad') and entrada.cantidad:
                    cantidad = entrada.cantidad
                elif hasattr(entrada, 'cantidad_entrada') and entrada.cantidad_entrada:
                    cantidad = entrada.cantidad_entrada

                # Obtener motivo/referencia
                motivo = "Entrada de mercancía"
                if hasattr(entrada, 'observaciones') and entrada.observaciones:
                    motivo = entrada.observaciones
                elif hasattr(entrada, 'notas') and entrada.notas:
                    motivo = entrada.notas

                referencia = ""
                if hasattr(entrada, 'numero_factura') and entrada.numero_factura:
                    referencia = entrada.numero_factura
                elif hasattr(entrada, 'referencia') and entrada.referencia:
                    referencia = entrada.referencia

                movimientos_data.append({
                    'fecha_movimiento': fecha_str,
                    'producto': producto_nombre,
                    'tipo_movimiento': 'entrada',
                    'tipo_operacion': 'entrada',
                    'cantidad': cantidad,
                    'cantidad_anterior': 0,
                    'cantidad_nueva': cantidad,
                    'motivo': motivo,
                    'usuario': usuario_nombre,
                    'referencia': referencia,
                    'origen': 'entrada_producto'
                })

            except Exception as e:
                print(f"Error procesando entrada ID {entrada.id}: {e}")
                import traceback
                traceback.print_exc()
                continue

        # =============================================
        # 6. PROCESAR MOVIMIENTOS DE STOCK
        # =============================================
        print("Procesando movimientos de stock...")

        for mov in movimientos:
            try:
                # Determinar tipo_operacion basado en el tipo y signo
                if mov.tipo_movimiento == 'entrada':
                    tipo_operacion = "entrada"
                elif mov.tipo_movimiento in ['salida', 'venta']:
                    tipo_operacion = "salida"
                elif mov.tipo_movimiento == 'ajuste':
                    tipo_operacion = "entrada" if mov.cantidad > 0 else "salida"
                elif mov.tipo_movimiento == 'devolucion':
                    tipo_operacion = "entrada" if mov.cantidad > 0 else "salida"
                else:
                    tipo_operacion = "entrada" if mov.cantidad > 0 else "salida"

                # Obtener nombre del producto
                producto_nombre = ""
                if hasattr(mov.producto, 'descripcion'):
                    producto_nombre = mov.producto.descripcion
                elif hasattr(mov.producto, 'nombre_producto'):
                    producto_nombre = mov.producto.nombre_producto
                elif hasattr(mov.producto, 'nombre'):
                    producto_nombre = mov.producto.nombre
                else:
                    producto_nombre = str(mov.producto)

                movimientos_data.append({
                    'fecha_movimiento': format_rd_datetime(mov.fecha_movimiento),
                    'producto': producto_nombre,
                    'tipo_movimiento': mov.tipo_movimiento,
                    'tipo_operacion': tipo_operacion,
                    'cantidad': mov.cantidad,
                    'cantidad_anterior': mov.cantidad_anterior,
                    'cantidad_nueva': mov.cantidad_nueva,
                    'motivo': mov.motivo,
                    'usuario': mov.usuario.username if mov.usuario else 'Sistema',
                    'referencia': mov.referencia or '',
                    'origen': 'movimiento_stock'
                })
            except Exception as e:
                print(f"Error procesando movimiento ID {mov.id}: {e}")
                continue

        # =============================================
        # 7. PROCESAR VENTAS
        # =============================================
        print("Procesando ventas...")

        for detalle_venta in ventas:
            try:
                venta = detalle_venta.venta
                producto = detalle_venta.producto

                # Para ventas, la cantidad siempre es negativa (es una salida)
                cantidad = -detalle_venta.cantidad

                # Obtener nombre del producto
                producto_nombre = ""
                if hasattr(producto, 'descripcion'):
                    producto_nombre = producto.descripcion
                elif hasattr(producto, 'nombre_producto'):
                    producto_nombre = producto.nombre_producto
                elif hasattr(producto, 'nombre'):
                    producto_nombre = producto.nombre
                else:
                    producto_nombre = str(producto)

                movimientos_data.append({
                    'fecha_movimiento': format_rd_datetime(venta.fecha_venta),
                    'producto': producto_nombre,
                    'tipo_movimiento': 'venta',
                    'tipo_operacion': 'salida',
                    'cantidad': cantidad,
                    'cantidad_anterior': 0,
                    'cantidad_nueva': 0,
                    'motivo': f"Venta #{venta.numero_factura} - {venta.cliente_nombre}",
                    'usuario': venta.vendedor.username if venta.vendedor else 'Sistema',
                    'referencia': venta.numero_factura,
                    'origen': 'venta'
                })
            except Exception as e:
                print(f"Error procesando venta ID {detalle_venta.id}: {e}")
                continue

        # =============================================
        # 8. ORDENAR Y LIMITAR
        # =============================================
        # Ordenar por fecha de movimiento (más reciente primero)
        movimientos_data.sort(
            key=lambda x: x['fecha_movimiento'], reverse=True)

        # Limitar el tamaño total de la respuesta
        movimientos_data = movimientos_data[:limite_total]

        # Eliminar campo 'origen' antes de enviar al frontend
        for mov in movimientos_data:
            mov.pop('origen', None)

        # DEBUG: Mostrar resumen
        print(f"=== RESUMEN FINAL ===")
        print(f"Total movimientos procesados: {len(movimientos_data)}")
        print(
            f"Entradas: {len([m for m in movimientos_data if m['tipo_movimiento'] == 'entrada'])}")
        print(
            f"Ventas: {len([m for m in movimientos_data if m['tipo_movimiento'] == 'venta'])}")
        print(
            f"Otros movimientos: {len([m for m in movimientos_data if m['tipo_movimiento'] not in ['entrada', 'venta']])}")

        data = {
            'movimientos': movimientos_data
        }
        return JsonResponse(data)

    except Exception as e:
        print(f"Error en movimientos_stock: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


def movimientos_stock_pdf(request):
    """Generar PDF de movimientos de stock - INCLUYENDO VENTAS"""
    try:
        # =============================================
        # 1. OBTENER MOVIMIENTOS DE STOCK
        # =============================================
        movimientos_stock = MovimientoStock.objects.select_related(
            'producto', 'usuario'
        ).order_by('-fecha_movimiento')

        # =============================================
        # 2. OBTENER VENTAS (DETALLES DE VENTA)
        # =============================================
        ventas_detalles = DetalleVenta.objects.select_related(
            'venta', 'producto', 'venta__vendedor'
        ).filter(
            venta__anulada=False
        ).order_by('-venta__fecha_venta')

        # =============================================
        # 3. APLICAR FILTROS A AMBAS FUENTES
        # =============================================
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        tipo_movimiento = request.GET.get('tipo_movimiento')

        # Filtros para movimientos de stock
        if fecha_desde:
            try:
                movimientos_stock = movimientos_stock.filter(
                    fecha_movimiento__date__gte=fecha_desde
                )
            except Exception as e:
                print(f"Error filtrando fecha_desde en movimientos_stock: {e}")

        if fecha_hasta:
            try:
                movimientos_stock = movimientos_stock.filter(
                    fecha_movimiento__date__lte=fecha_hasta
                )
            except Exception as e:
                print(f"Error filtrando fecha_hasta en movimientos_stock: {e}")

        if tipo_movimiento and tipo_movimiento != 'venta':
            movimientos_stock = movimientos_stock.filter(
                tipo_movimiento=tipo_movimiento
            )

        # Filtros para ventas
        if fecha_desde:
            try:
                ventas_detalles = ventas_detalles.filter(
                    venta__fecha_venta__date__gte=fecha_desde
                )
            except Exception as e:
                print(f"Error filtrando fecha_desde en ventas: {e}")

        if fecha_hasta:
            try:
                ventas_detalles = ventas_detalles.filter(
                    venta__fecha_venta__date__lte=fecha_hasta
                )
            except Exception as e:
                print(f"Error filtrando fecha_hasta en ventas: {e}")

        if tipo_movimiento == 'venta':
            # Si solo se quiere ver ventas, excluir movimientos de stock
            movimientos_stock = movimientos_stock.none()
        elif tipo_movimiento and tipo_movimiento != 'venta':
            # Si se filtra por otro tipo, excluir ventas
            ventas_detalles = ventas_detalles.none()

        # Limitar resultados para evitar PDFs demasiado grandes
        movimientos_stock = movimientos_stock[:500]
        ventas_detalles = ventas_detalles[:500]

        # DEBUG: Verificar qué datos se están obteniendo
        print(f"=== DATOS PARA PDF ===")
        print(f"Movimientos de stock encontrados: {movimientos_stock.count()}")
        print(f"Ventas encontradas: {ventas_detalles.count()}")
        print(
            f"Filtros aplicados: desde={fecha_desde}, hasta={fecha_hasta}, tipo={tipo_movimiento}")

        # =============================================
        # 4. COMBINAR Y PREPARAR DATOS
        # =============================================
        all_movements = []

        # Procesar movimientos de stock
        for mov in movimientos_stock:
            # Determinar tipo de operación
            if mov.tipo_movimiento == 'entrada':
                tipo_operacion = "ENTRADA"
                es_entrada = True
            elif mov.tipo_movimiento in ['salida', 'venta']:
                tipo_operacion = "SALIDA"
                es_entrada = False
            elif mov.tipo_movimiento == 'ajuste':
                if mov.cantidad > 0:
                    tipo_operacion = "AJUSTE ENTRADA"
                    es_entrada = True
                else:
                    tipo_operacion = "AJUSTE SALIDA"
                    es_entrada = False
            elif mov.tipo_movimiento == 'devolucion':
                if mov.cantidad > 0:
                    tipo_operacion = "DEVOLUCIÓN ENTRADA"
                    es_entrada = True
                else:
                    tipo_operacion = "DEVOLUCIÓN SALIDA"
                    es_entrada = False
            else:
                tipo_operacion = mov.tipo_movimiento.upper()
                es_entrada = mov.cantidad > 0

            all_movements.append({
                'fecha': mov.fecha_movimiento,
                'producto': mov.producto.descripcion,
                'tipo_movimiento': mov.tipo_movimiento,
                'tipo_operacion': tipo_operacion,
                'es_entrada': es_entrada,
                'cantidad': mov.cantidad,
                'cantidad_anterior': mov.cantidad_anterior,
                'cantidad_nueva': mov.cantidad_nueva,
                'motivo': mov.motivo,
                'usuario': mov.usuario.username if mov.usuario else 'Sistema',
                'referencia': mov.referencia or '',
                'origen': 'movimiento_stock'
            })

        # Procesar ventas
        for detalle_venta in ventas_detalles:
            venta = detalle_venta.venta
            producto = detalle_venta.producto

            # Para ventas, la cantidad siempre es negativa (es una salida)
            cantidad = -detalle_venta.cantidad

            # Calcular stock aproximado
            # Nota: Esto es aproximado porque no tenemos el stock exacto en el momento de la venta
            # Podríamos usar el stock actual como referencia
            try:
                # Intentar obtener el stock actual del producto
                cantidad_actual = producto.cantidad if hasattr(
                    producto, 'cantidad') else 0
                cantidad_anterior = cantidad_actual + detalle_venta.cantidad
                cantidad_nueva = cantidad_actual
            except:
                cantidad_anterior = 0
                cantidad_nueva = 0

            all_movements.append({
                'fecha': venta.fecha_venta,
                'producto': producto.descripcion,
                'tipo_movimiento': 'venta',
                'tipo_operacion': 'VENTA',
                'es_entrada': False,  # Las ventas siempre son salidas
                'cantidad': cantidad,
                'cantidad_anterior': cantidad_anterior,
                'cantidad_nueva': cantidad_nueva,
                'motivo': f"Venta #{venta.numero_factura} - {venta.cliente_nombre}",
                'usuario': venta.vendedor.username if venta.vendedor else 'Sistema',
                'referencia': venta.numero_factura,
                'origen': 'venta'
            })

        # Ordenar por fecha descendente
        all_movements.sort(key=lambda x: x['fecha'], reverse=True)

        # Limitar a 1000 registros para el PDF
        all_movements = all_movements[:1000]

        # =============================================
        # 5. CREAR RESPONSE PDF
        # =============================================
        # Crear respuesta HTTP con tipo PDF
        response = HttpResponse(content_type='application/pdf')

        # Nombre del archivo
        filename = "reporte_movimientos.pdf"
        if fecha_desde and fecha_hasta:
            filename = f"movimientos_{fecha_desde}_a_{fecha_hasta}.pdf"

        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # Crear el documento PDF
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from io import BytesIO

        # Usar página horizontal para más espacio
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Contenedor para los elementos del PDF
        elements = []

        # Estilos
        styles = getSampleStyleSheet()

        # Estilo para título personalizado
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor=colors.HexColor('#333333')
        )

        # Estilo para subtítulo
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=20,
            alignment=1,
            textColor=colors.HexColor('#666666')
        )

        # =============================================
        # 6. ENCABEZADO Y INFORMACIÓN
        # =============================================
        # Título principal
        title = Paragraph("REPORTE DE MOVIMIENTOS DE INVENTARIO", title_style)
        elements.append(title)

        # Información del reporte
        info_style = styles['Normal']
        fecha_reporte = timezone.now().strftime('%d/%m/%Y %H:%M')
        empresa = "Super Bestia"

        info_text = f"""
        <b>Empresa:</b> {empresa}<br/>
        <b>Fecha de reporte:</b> {fecha_reporte}
        """

        if fecha_desde and fecha_hasta:
            info_text += f"<br/><b>Período:</b> {fecha_desde} al {fecha_hasta}"

        if tipo_movimiento:
            # Traducir tipo de movimiento
            tipo_display = {
                'entrada': 'Entradas',
                'salida': 'Salidas',
                'venta': 'Ventas',
                'ajuste': 'Ajustes',
                'devolucion': 'Devoluciones',
                'todos': 'Todos los tipos'
            }.get(tipo_movimiento, tipo_movimiento.capitalize())

            info_text += f"<br/><b>Tipo de movimiento:</b> {tipo_display}"

        info_paragraph = Paragraph(info_text, info_style)
        elements.append(info_paragraph)
        elements.append(Spacer(1, 20))

        # =============================================
        # 7. CALCULAR ESTADÍSTICAS
        # =============================================
        total_movimientos = len(all_movements)
        total_entradas = 0
        total_salidas = 0

        for mov in all_movements:
            if mov['es_entrada']:
                total_entradas += abs(mov['cantidad'])
            else:
                total_salidas += abs(mov['cantidad'])

        saldo_neto = total_entradas - total_salidas

        # Mostrar estadísticas rápidas
        stats_text = f"""
        <b>Estadísticas del Reporte:</b><br/>
        Total de movimientos: <b>{total_movimientos}</b> |
        Total entradas: <b>{total_entradas}</b> unidades |
        Total salidas: <b>{total_salidas}</b> unidades |
        Saldo neto: <b>{saldo_neto}</b> unidades
        """

        stats_paragraph = Paragraph(stats_text, info_style)
        elements.append(stats_paragraph)
        elements.append(Spacer(1, 15))

        # =============================================
        # 8. TABLA DE MOVIMIENTOS
        # =============================================
        if total_movimientos > 0:
            # Preparar datos para la tabla
            table_data = [['Fecha', 'Producto', 'Tipo', 'Cantidad',
                           'Stock Anterior', 'Stock Nuevo', 'Motivo', 'Usuario', 'Referencia']]

            for mov in all_movements:
                # Formatear fecha
                fecha_str = mov['fecha'].strftime('%d/%m/%Y %H:%M')

                # Formatear tipo
                tipo_display = mov['tipo_operacion']

                # Formatear cantidad (color y signo)
                cantidad_str = f"+{mov['cantidad']}" if mov['es_entrada'] else f"{mov['cantidad']}"

                # Acortar texto si es muy largo
                producto_display = mov['producto']
                if len(producto_display) > 30:
                    producto_display = producto_display[:27] + "..."

                motivo_display = mov['motivo']
                if len(motivo_display) > 35:
                    motivo_display = motivo_display[:32] + "..."

                table_data.append([
                    fecha_str,
                    producto_display,
                    tipo_display,
                    cantidad_str,
                    str(mov['cantidad_anterior']),
                    str(mov['cantidad_nueva']),
                    motivo_display,
                    mov['usuario'],
                    mov['referencia']
                ])

            # Crear tabla
            table = Table(
                table_data,
                colWidths=[
                    1.2*inch,  # Fecha
                    1.5*inch,  # Producto
                    0.9*inch,  # Tipo
                    0.7*inch,  # Cantidad
                    0.9*inch,  # Stock Anterior
                    0.9*inch,  # Stock Nuevo
                    1.5*inch,  # Motivo
                    0.8*inch,  # Usuario
                    0.9*inch   # Referencia
                ]
            )

            # Estilo de la tabla
            table.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                # Filas de datos
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                # Producto alineado a la izquierda
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                # Motivo alineado a la izquierda
                ('ALIGN', (6, 1), (6, -1), 'LEFT'),

                # Colores para cantidades
                ('TEXTCOLOR', (3, 1), (3, -1), lambda row, col, cell, cellvalue:
                    colors.HexColor('#28a745') if cellvalue.startswith('+') else colors.HexColor('#dc3545')),

                # Alternar colores de filas
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                 [colors.white, colors.HexColor('#f2f2f2')]),
            ]))

            elements.append(table)
        else:
            # Mensaje cuando no hay datos
            no_data_style = ParagraphStyle(
                'NoData',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=20,
                alignment=1,
                textColor=colors.HexColor('#6c757d')
            )

            no_data = Paragraph(
                "No hay movimientos que mostrar con los filtros seleccionados", no_data_style)
            elements.append(Spacer(1, 50))
            elements.append(no_data)

        # =============================================
        # 9. RESUMEN DETALLADO
        # =============================================
        elements.append(Spacer(1, 30))

        # Título del resumen
        summary_title = Paragraph(
            "<b>RESUMEN DETALLADO</b>", styles['Heading2'])
        elements.append(summary_title)
        elements.append(Spacer(1, 10))

        # Estilo para resumen
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=5,
            textColor=colors.HexColor('#495057')
        )

        # Información del resumen
        summary_text = f"""
        <b>Total de registros:</b> {total_movimientos}<br/>
        <b>Total entradas:</b> {total_entradas} unidades<br/>
        <b>Total salidas:</b> {total_salidas} unidades<br/>
        <b>Saldo neto (entradas - salidas):</b> {saldo_neto} unidades<br/>
        <b>Porcentaje de entradas:</b> {round((total_entradas / (total_entradas + total_salidas) * 100), 2) if (total_entradas + total_salidas) > 0 else 0}%<br/>
        <b>Porcentaje de salidas:</b> {round((total_salidas / (total_entradas + total_salidas) * 100), 2) if (total_entradas + total_salidas) > 0 else 0}%
        """

        summary_paragraph = Paragraph(summary_text, summary_style)
        elements.append(summary_paragraph)

        # Desglose por tipo de movimiento
        if total_movimientos > 0:
            elements.append(Spacer(1, 15))

            # Contar por tipo
            tipos_count = {}
            for mov in all_movements:
                tipo = mov['tipo_movimiento']
                if tipo in tipos_count:
                    tipos_count[tipo] += 1
                else:
                    tipos_count[tipo] = 1

            # Crear texto de desglose
            tipos_text = "<b>Desglose por tipo de movimiento:</b><br/>"
            for tipo, count in tipos_count.items():
                porcentaje = round((count / total_movimientos) * 100, 1)
                tipos_text += f"• {tipo.capitalize()}: {count} registros ({porcentaje}%)<br/>"

            tipos_paragraph = Paragraph(tipos_text, summary_style)
            elements.append(tipos_paragraph)

        # =============================================
        # 10. PIE DE PÁGINA
        # =============================================
        elements.append(Spacer(1, 30))

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=1,
            textColor=colors.HexColor('#6c757d')
        )

        footer_text = f"""
        <i>Reporte generado automáticamente por el sistema de Super Bestia<br/>
        Fecha de generación: {fecha_reporte}<br/>
        Este documento es confidencial y para uso interno.</i>
        """

        footer_paragraph = Paragraph(footer_text, footer_style)
        elements.append(footer_paragraph)

        # =============================================
        # 11. GENERAR PDF
        # =============================================
        # Construir el documento
        doc.build(elements)

        # DEBUG: Mostrar información final
        print(f"=== PDF GENERADO ===")
        print(f"Total movimientos en PDF: {total_movimientos}")
        print(f"Total entradas: {total_entradas}")
        print(f"Total salidas: {total_salidas}")
        print(
            f"Tipos encontrados: {set([m['tipo_movimiento'] for m in all_movements])}")

        return response

    except Exception as e:
        print(f"Error en movimientos_stock_pdf: {e}")
        import traceback
        traceback.print_exc()

        # En caso de error, devolver respuesta JSON en lugar de PDF
        return JsonResponse({
            'error': str(e),
            'mensaje': 'Error al generar el PDF. Por favor, intente nuevamente.'
        }, status=500)


@login_required
def get_cuadres(request):
    """Obtener cuadres de caja con filtros por rango de fechas"""
    try:
        print("=== GET_CUADRES LLAMADO ===")

        # Iniciar con todos los cuadres
        cuadres = CierreCaja.objects.all().order_by('-fecha_cierre')

        # Aplicar filtros
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        usuario_id = request.GET.get('usuario')

        print(
            f"Filtros recibidos: desde={fecha_desde}, hasta={fecha_hasta}, usuario={usuario_id}")

        if fecha_desde:
            try:
                cuadres = cuadres.filter(fecha_cierre__date__gte=fecha_desde)
                print(f"Filtrando desde: {fecha_desde}")
            except Exception as e:
                print(f"Error filtrando fecha_desde: {e}")

        if fecha_hasta:
            try:
                cuadres = cuadres.filter(fecha_cierre__date__lte=fecha_hasta)
                print(f"Filtrando hasta: {fecha_hasta}")
            except Exception as e:
                print(f"Error filtrando fecha_hasta: {e}")

        if usuario_id:
            try:
                # Ajusta según cómo está relacionado el usuario con el cierre de caja
                # Si hay un campo usuario directo en CierreCaja, usa:
                # cuadres = cuadres.filter(usuario_id=usuario_id)

                # Si está a través de Caja:
                cuadres = cuadres.filter(caja__usuario_id=usuario_id)
                print(f"Filtrando por usuario: {usuario_id}")
            except Exception as e:
                print(f"Error filtrando usuario: {e}")

        print(f"Total cuadres encontrados: {cuadres.count()}")

        data = []
        for cuadre in cuadres:
            try:
                # Obtener el nombre de usuario según tu estructura
                username = "Sistema"
                if cuadre.caja and cuadre.caja.usuario:
                    username = cuadre.caja.usuario.username
                elif hasattr(cuadre, 'usuario') and cuadre.usuario:
                    username = cuadre.usuario.username

                # Crear diccionario con los datos
                cuadre_data = {
                    'id': cuadre.id,
                    'fecha_cierre': cuadre.fecha_cierre.strftime('%d/%m/%Y %H:%M'),
                    'usuario': username,
                    'monto_inicial': float(getattr(cuadre, 'monto_inicial', 0)),
                    'monto_final': float(getattr(cuadre, 'monto_final', 0)),
                    'monto_efectivo_real': float(cuadre.monto_efectivo_real),
                    'monto_tarjeta_real': float(cuadre.monto_tarjeta_real),
                    'total_esperado': float(cuadre.total_esperado),
                    'diferencia': float(cuadre.diferencia),
                    'estado': getattr(cuadre, 'estado', 'cerrada'),
                    'observaciones': cuadre.observaciones or '',
                }
                data.append(cuadre_data)

            except Exception as e:
                print(f"Error procesando cuadre {cuadre.id}: {e}")
                continue

        print(f"Datos preparados: {len(data)} registros")
        return JsonResponse({'cuadres': data})

    except Exception as e:
        print(f"Error en get_cuadres: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def generar_pdf_todos_cuadres(request):
    """Generar PDF con todos los cuadres del rango seleccionado"""
    try:
        cuadres = CierreCaja.objects.select_related(
            'caja__usuario').all().order_by('fecha_cierre')

        # Aplicar filtros
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        usuario_id = request.GET.get('usuario')

        if fecha_desde:
            cuadres = cuadres.filter(fecha_cierre__date__gte=fecha_desde)
        if fecha_hasta:
            cuadres = cuadres.filter(fecha_cierre__date__lte=fecha_hasta)
        if usuario_id:
            cuadres = cuadres.filter(caja__usuario_id=usuario_id)

        # Crear el PDF
        from django.http import HttpResponse
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from io import BytesIO

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Encabezado
        p.setFont("Helvetica-Bold", 16)
        p.drawString(1 * inch, height - 1 * inch, "Reporte de Cuadres de Caja")

        # Información del rango de fechas
        p.setFont("Helvetica", 10)
        fecha_reporte = f"Fecha del reporte: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        p.drawString(1 * inch, height - 1.25 * inch, fecha_reporte)

        if fecha_desde and fecha_hasta:
            rango_fechas = f"Rango: {fecha_desde} al {fecha_hasta}"
            p.drawString(1 * inch, height - 1.5 * inch, rango_fechas)

        # Tabla de cuadres
        y_position = height - 2 * inch
        p.setFont("Helvetica-Bold", 10)

        # Encabezados de tabla
        headers = ['Fecha', 'Usuario', 'Monto Inicial', 'Monto Final',
                   'Efectivo Real', 'Tarjeta Real', 'Total Esperado', 'Diferencia']
        col_widths = [1.2, 1, 0.8, 0.8, 0.8, 0.8, 0.9, 0.8]
        x_positions = [1 * inch]

        for i in range(1, len(headers)):
            x_positions.append(x_positions[i-1] + col_widths[i-1] * inch)

        for i, header in enumerate(headers):
            p.drawString(x_positions[i], y_position, header)

        # Línea separadora
        p.line(1 * inch, y_position - 0.1 * inch,
               sum(col_widths) * inch, y_position - 0.1 * inch)

        # Datos de cuadres
        p.setFont("Helvetica", 8)
        y_position -= 0.25 * inch

        total_cuadres = 0
        total_diferencia = 0

        for cuadre in cuadres:
            if y_position < 1 * inch:
                p.showPage()
                y_position = height - 1 * inch
                # Redibujar encabezados en nueva página
                p.setFont("Helvetica-Bold", 10)
                for i, header in enumerate(headers):
                    p.drawString(x_positions[i], y_position, header)
                p.line(1 * inch, y_position - 0.1 * inch,
                       sum(col_widths) * inch, y_position - 0.1 * inch)
                p.setFont("Helvetica", 8)
                y_position -= 0.25 * inch

            # Datos del cuadre
            p.drawString(x_positions[0], y_position,
                         cuadre.fecha_cierre.strftime('%d/%m/%Y'))
            p.drawString(x_positions[1], y_position,
                         cuadre.caja.usuario.username[:10])
            p.drawString(x_positions[2], y_position,
                         f"${cuadre.caja.monto_inicial:,.2f}")
            p.drawString(x_positions[3], y_position,
                         f"${cuadre.caja.monto_final or 0:,.2f}")
            p.drawString(x_positions[4], y_position,
                         f"${cuadre.monto_efectivo_real:,.2f}")
            p.drawString(x_positions[5], y_position,
                         f"${cuadre.monto_tarjeta_real:,.2f}")
            p.drawString(x_positions[6], y_position,
                         f"${cuadre.total_esperado:,.2f}")

            # Diferencia (rojo si es negativa, verde si es positiva)
            if cuadre.diferencia >= 0:
                p.drawString(x_positions[7], y_position,
                             f"${cuadre.diferencia:,.2f}")
            else:
                p.drawString(x_positions[7], y_position,
                             f"-${abs(cuadre.diferencia):,.2f}")

            total_cuadres += 1
            total_diferencia += cuadre.diferencia
            y_position -= 0.2 * inch

        # Totales
        y_position -= 0.3 * inch
        p.setFont("Helvetica-Bold", 10)
        p.drawString(1 * inch, y_position,
                     f"Total de cuadres: {total_cuadres}")
        p.drawString(4 * inch, y_position,
                     f"Diferencia total: ${total_diferencia:,.2f}")

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="cuadres_completos.pdf"'

        return response

    except Exception as e:
        print(f"Error en generar_pdf_todos_cuadres: {e}")
        return HttpResponse(f"Error al generar PDF: {str(e)}", status=500)


@login_required
def generar_pdf_cuadre(request, cuadre_id):
    """Generar PDF del cuadre de caja"""
    # Aquí implementarías la generación del PDF
    # Por ahora redirigimos a una página simple
    from django.shortcuts import get_object_or_404, render
    cuadre = get_object_or_404(CierreCaja, id=cuadre_id)

    context = {
        'cuadre': cuadre,
        'caja': cuadre.caja
    }
    return render(request, "facturacion/reporte_cuadre.html", context)


# ============================================================================================
# ======================== VENTAS POR USUARIO  (OJO )===============================
# ============================================================================================
@login_required
def ventas_por_usuario(request):
    """
    Vista para obtener ventas agrupadas por usuario (AJAX)
    Incluye:
    - Total ventas (contado + crédito)
    - Total contado
    - Total crédito (monto total de facturas a crédito)
    - Total cobros registrados (pagos a cuentas por cobrar)
    Vista para obtener ventas y cobros agrupadas por usuario (AJAX).
    Incluye usuarios que tengan ventas o cobros en el período.
    (arreglo de anlacion, dashbor y descuebto en cuenta por cobrar)
    """
    try:
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        usuario_id = request.GET.get('usuario')

        # Ventas no anuladas

        ventas = Venta.objects.filter(anulada=False)
        if fecha_desde:
            ventas = ventas.filter(fecha_venta__date__gte=fecha_desde)
        if fecha_hasta:
            ventas = ventas.filter(fecha_venta__date__lte=fecha_hasta)

        if usuario_id:
            ventas = ventas.filter(vendedor_id=usuario_id)

        dinero_field = DecimalField(max_digits=18, decimal_places=2)

        ventas_agrupadas = list(
            ventas.values('vendedor_id', 'vendedor__username').annotate(
                cantidad_ventas=Count('id'),
                total_contado=Coalesce(
                    Sum('total', filter=Q(tipo_venta='contado')),
                    Value(Decimal('0.00')),
                    output_field=dinero_field
                ),
                total_credito=Coalesce(
                    Sum('total', filter=Q(tipo_venta='credito')),
                    Value(Decimal('0.00')),
                    output_field=dinero_field
                ),
                total_efectivo=Coalesce(
                    Sum('total', filter=Q(
                        tipo_venta='contado', metodo_pago='efectivo')),
                    Value(Decimal('0.00')),
                    output_field=dinero_field
                ),
                total_tarjeta=Coalesce(
                    Sum('total', filter=Q(
                        tipo_venta='contado', metodo_pago='tarjeta')),
                    Value(Decimal('0.00')),
                    output_field=dinero_field
                ),
                total_transferencia=Coalesce(
                    Sum('total', filter=Q(tipo_venta='contado',
                        metodo_pago='transferencia')),
                    Value(Decimal('0.00')),
                    output_field=dinero_field
                ),
            )
        )

        # Pagos (cobros) no anulados
        pagos = PagoCuentaPorCobrar.objects.filter(anulado=False)
        if fecha_desde:
            pagos = pagos.filter(fecha_pago__date__gte=fecha_desde)
        if fecha_hasta:
            pagos = pagos.filter(fecha_pago__date__lte=fecha_hasta)

        if usuario_id:
            pagos = pagos.filter(usuario_id=usuario_id)

        cobros_por_usuario = {
            item['usuario_id']: item['total_cobros']
            for item in pagos.values('usuario_id').annotate(
                total_cobros=Coalesce(
                    Sum('monto'),
                    Value(Decimal('0.00')),
                    output_field=dinero_field
                )
            )
        }

        ventas_por_usuario = []
        for item in ventas_agrupadas:
            total_contado = item['total_contado'] or Decimal('0.00')
            total_credito = item['total_credito'] or Decimal('0.00')
            total_general = total_contado + total_credito
            cantidad_ventas = item['cantidad_ventas'] or 0
            total_cobros = cobros_por_usuario.get(
                item['vendedor_id'], Decimal('0.00'))
            promedio_venta = (
                total_general / cantidad_ventas) if cantidad_ventas > 0 else Decimal('0.00')

        # Usuarios con actividad (ventas o cobros)
        usuarios_con_ventas = set(ventas.values_list(
            'vendedor_id', flat=True).distinct())
        usuarios_con_cobros = set(pagos.values_list(
            'usuario_id', flat=True).distinct())
        usuarios_con_actividad = usuarios_con_ventas | usuarios_con_cobros

        if not usuarios_con_actividad:
            return JsonResponse({'ventas': []})

        usuarios = User.objects.filter(
            id__in=usuarios_con_actividad).order_by('username')
        if usuario_id:
            usuarios = usuarios.filter(id=usuario_id)

        ventas_por_usuario = []
        for item in ventas_agrupadas:
            total_contado = item['total_contado'] or Decimal('0.00')
            total_credito = item['total_credito'] or Decimal('0.00')
            total_general = total_contado + total_credito
            cantidad_ventas = item['cantidad_ventas'] or 0
            total_cobros = cobros_por_usuario.get(
                item['vendedor_id'], Decimal('0.00'))
            promedio_venta = (
                total_general / cantidad_ventas) if cantidad_ventas > 0 else Decimal('0.00')

        for usuario in usuarios:
            ventas_usuario = ventas.filter(vendedor=usuario)
            pagos_usuario = pagos.filter(usuario=usuario)

            cantidad_ventas = ventas_usuario.count()
            ventas_contado = ventas_usuario.filter(tipo_venta='contado').aggregate(
                total=Sum('total'))['total'] or Decimal('0.00')
            ventas_credito = ventas_usuario.filter(tipo_venta='credito').aggregate(
                total=Sum('total'))['total'] or Decimal('0.00')
            total_general = ventas_contado + ventas_credito

            ventas_efectivo = ventas_usuario.filter(tipo_venta='contado', metodo_pago='efectivo').aggregate(
                total=Sum('total'))['total'] or Decimal('0.00')
            ventas_tarjeta = ventas_usuario.filter(tipo_venta='contado', metodo_pago='tarjeta').aggregate(
                total=Sum('total'))['total'] or Decimal('0.00')
            ventas_transferencia = ventas_usuario.filter(tipo_venta='contado', metodo_pago='transferencia').aggregate(
                total=Sum('total'))['total'] or Decimal('0.00')

            promedio_venta = total_general / cantidad_ventas if cantidad_ventas > 0 else 0
            total_cobros = pagos_usuario.aggregate(total=Sum('monto'))[
                'total'] or Decimal('0.00')
            ventas_por_usuario.append({
                'usuario_id': item['vendedor_id'],
                'usuario': item['vendedor__username'],
                'cantidad_ventas': cantidad_ventas,
                'total_ventas': float(total_general),

                'total_contado': float(total_contado),
                'total_credito': float(total_credito),
                'total_efectivo': float(item['total_efectivo'] or Decimal('0.00')),
                'total_tarjeta': float(item['total_tarjeta'] or Decimal('0.00')),
                'total_transferencia': float(item['total_transferencia'] or Decimal('0.00')),
                'total_contado': float(ventas_contado),
                'total_credito': float(ventas_credito),
                'total_efectivo': float(ventas_efectivo),
                'total_tarjeta': float(ventas_tarjeta),
                'total_transferencia': float(ventas_transferencia),

                'total_cobros': float(total_cobros),
                'promedio_venta': float(promedio_venta)
            })

        if usuario_id and not ventas_por_usuario:
            usuario = User.objects.filter(
                id=usuario_id).values('id', 'username').first()
            if usuario:
                ventas_por_usuario.append({
                    'usuario_id': usuario['id'],
                    'usuario': usuario['username'],
                    'cantidad_ventas': 0,
                    'total_ventas': 0.0,
                    'total_contado': 0.0,
                    'total_credito': 0.0,
                    'total_efectivo': 0.0,
                    'total_tarjeta': 0.0,
                    'total_transferencia': 0.0,
                    'total_cobros': float(cobros_por_usuario.get(usuario['id'], Decimal('0.00'))),
                    'promedio_venta': 0.0
                })

        ventas_por_usuario.sort(key=lambda x: x['total_ventas'], reverse=True)
        return JsonResponse({'ventas': ventas_por_usuario})

    except Exception as e:
        print(f"Error en ventas_por_usuario: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


# ================================================================================================
# ======================== APARTADO DE REPORTE DE VENTAS CUADRE ===================================
# ================================================================================================
@login_required
def ventas_por_usuario_pdf(request):
    """
    Genera PDF con detalle de ventas y cobros por usuario.
    El descuento se muestra siempre como monto en RD$ (nunca como porcentaje).
    """
    import io
    import pytz
    from django.http import HttpResponse
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib.units import inch
    from django.utils import timezone
    from django.contrib.auth.models import User
    from django.db.models import Sum
    from decimal import Decimal
    from collections import defaultdict
    from .models import Venta, PagoCuentaPorCobrar, Devolucion

    try:
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        usuario_id = request.GET.get('usuario')

        tz_rd = pytz.timezone('America/Santo_Domingo')
        ahora_local = timezone.now().astimezone(tz_rd)
        fecha_reporte = ahora_local.strftime('%d/%m/%Y %I:%M %p')

        ventas = Venta.objects.all()
        if fecha_desde:
            ventas = ventas.filter(fecha_venta__date__gte=fecha_desde)
        if fecha_hasta:
            ventas = ventas.filter(fecha_venta__date__lte=fecha_hasta)

        usuarios_excluidos = ['derej', 'soft']
        usuarios_activos = User.objects.filter(
            is_active=True).exclude(username__in=usuarios_excluidos)

        usuarios_con_ventas = ventas.filter(vendedor__in=usuarios_activos).values_list(
            'vendedor_id', flat=True).distinct()

        pagos_raw = PagoCuentaPorCobrar.objects.filter(anulado=False)
        if fecha_desde:
            pagos_raw = pagos_raw.filter(fecha_pago__date__gte=fecha_desde)
        if fecha_hasta:
            pagos_raw = pagos_raw.filter(fecha_pago__date__lte=fecha_hasta)

        usuarios_con_cobros = pagos_raw.filter(usuario__is_active=True).exclude(
            usuario__username__in=usuarios_excluidos).values_list('usuario_id', flat=True).distinct()

        usuarios_con_actividad_ids = set(
            usuarios_con_ventas) | set(usuarios_con_cobros)

        if usuario_id:
            usuario_obj = User.objects.filter(id=usuario_id, is_active=True).exclude(
                username__in=usuarios_excluidos).first()
            if usuario_obj and usuario_obj.id in usuarios_con_actividad_ids:
                usuarios_con_actividad_ids = {usuario_obj.id}
            else:
                usuarios_con_actividad_ids = set()

        ventas = ventas.filter(vendedor_id__in=usuarios_con_actividad_ids)
        pagos = pagos_raw.filter(usuario_id__in=usuarios_con_actividad_ids)

        # ========== Asociar descuento de pagos con monto 0 al pago principal ==========
        # ✅ CORREGIDO: usar descuento_monto en lugar de descuento_porcentaje
        descuentos_por_factura = defaultdict(
            lambda: {'monto': Decimal('0.00')})
        for pago in pagos.filter(monto=0):
            if pago.cuenta and pago.cuenta.venta:
                factura_num = pago.cuenta.venta.numero_factura
                key = (factura_num, pago.fecha_pago.date())
                if pago.descuento_monto:
                    descuentos_por_factura[key]['monto'] = pago.descuento_monto

        pagos_principales = pagos.filter(monto__gt=0)

        rows = []
        total_ventas_general = Decimal('0.00')
        total_efectivo = Decimal('0.00')
        total_transferencias = Decimal('0.00')
        total_credito = Decimal('0.00')
        total_cobros_efectivo = Decimal('0.00')
        total_cobros_transf = Decimal('0.00')
        total_descuentos_ventas = Decimal('0.00')
        total_descuentos_cobros = Decimal('0.00')

        # ---------- VENTAS ----------
        for venta in ventas.select_related('vendedor', 'cliente').iterator():
            es_anulada = venta.anulada
            devoluciones = Devolucion.objects.filter(venta=venta)
            tiene_devolucion = devoluciones.exists()
            monto_devuelto = devoluciones.aggregate(total=Sum('monto'))[
                'total'] or Decimal('0.00')
            usuarios_dev = devoluciones.values_list(
                'usuario__username', flat=True).distinct()
            quien_devuelve = ", ".join(usuarios_dev) if usuarios_dev else ""

            if not es_anulada:
                total_ventas_general += venta.total
                total_descuentos_ventas += venta.descuento_monto
                if venta.tipo_venta == 'contado':
                    if venta.metodo_pago == 'efectivo':
                        total_efectivo += venta.total
                    elif venta.metodo_pago == 'transferencia':
                        total_transferencias += venta.total
                elif venta.tipo_venta == 'credito':
                    total_credito += venta.total

            if venta.tipo_venta == 'contado':
                tipo = 'contado'
                metodo = venta.metodo_pago if venta.metodo_pago else 'efectivo'
            else:
                tipo = 'credito'
                metodo = 'credito'

            estado_texto = ""
            if es_anulada:
                estado_texto = "Anulada"
            elif tiene_devolucion:
                estado_texto = f"Devuelto: RD${float(monto_devuelto):,.2f} ({quien_devuelve})"

            descuento_texto = ""
            if venta.descuento_monto and venta.descuento_monto > 0:
                descuento_texto = f"V: RD${float(venta.descuento_monto):,.2f}"

            rows.append({
                'fecha': venta.fecha_venta.date(),
                'factura': venta.numero_factura,
                'usuario': venta.vendedor.username,
                'cliente': venta.cliente_nombre if venta.cliente_nombre else 'N/A',
                'tipo': tipo,
                'metodo': metodo,
                'valor': venta.total,
                'descuento': descuento_texto,
                'estado': estado_texto,
                'es_anulada': es_anulada,
                'tiene_devolucion': tiene_devolucion,
            })

        # ---------- COBROS ----------
        for pago in pagos_principales.select_related('usuario', 'cuenta', 'cuenta__venta').iterator():
            cliente_nombre = 'N/A'
            if pago.cuenta and pago.cuenta.venta:
                if pago.cuenta.venta.cliente:
                    cliente_nombre = pago.cuenta.venta.cliente.full_name
                elif pago.cuenta.venta.cliente_nombre:
                    cliente_nombre = pago.cuenta.venta.cliente_nombre

            if pago.metodo_pago == 'efectivo':
                metodo = 'cobro/efectivo'
                total_cobros_efectivo += pago.monto
            elif pago.metodo_pago == 'transferencia':
                metodo = 'cobro/transferencia'
                total_cobros_transf += pago.monto
            else:
                metodo = pago.metodo_pago

            descuento_texto = ""
            factura_num = pago.cuenta.venta.numero_factura if pago.cuenta and pago.cuenta.venta else None
            if factura_num:
                key = (factura_num, pago.fecha_pago.date())
                if key in descuentos_por_factura:
                    desc_info = descuentos_por_factura[key]
                    if desc_info['monto'] and desc_info['monto'] > 0:
                        descuento_texto = f"C: RD${float(desc_info['monto']):,.2f}"
                        total_descuentos_cobros += desc_info['monto']

            rows.append({
                'fecha': pago.fecha_pago.date(),
                'factura': factura_num or 'N/A',
                'usuario': pago.usuario.username if pago.usuario else 'Sistema',
                'cliente': cliente_nombre,
                'tipo': 'Cobros',
                'metodo': metodo,
                'valor': pago.monto,
                'descuento': descuento_texto,
                'estado': '',
                'es_anulada': False,
                'tiene_devolucion': False,
            })

        rows.sort(key=lambda x: (x['fecha'], x['factura']), reverse=True)

        total_cobros = total_cobros_efectivo + total_cobros_transf
        total_contado = total_efectivo + total_cobros_efectivo
        total_registros = len(rows)
        total_descuentos = total_descuentos_ventas + total_descuentos_cobros

        # ========== GENERACIÓN DEL PDF (REPORTLAB) ==========
        HEADER_BG = (0.25, 0.25, 0.25)
        HEADER_TEXT = (1, 1, 1)
        ROW_ALT = (0.93, 0.93, 0.93)
        ROW_WHITE = (1, 1, 1)
        CARD_BG = (0.20, 0.20, 0.20)
        CARD_TEXT = (1, 1, 1)
        BORDER = (0.60, 0.60, 0.60)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=landscape(letter))
        width, height = landscape(letter)

        def draw_page_header(p, height, fecha_reporte, periodo):
            p.setFillColorRGB(0.15, 0.15, 0.15)
            p.setFont("Helvetica-Bold", 15)
            p.drawString(1 * inch, height - 0.75 * inch,
                         "Reporte Detallado de Ventas y Cobros por Usuario")
            p.setFont("Helvetica", 9)
            p.setFillColorRGB(0.35, 0.35, 0.35)
            p.drawString(1 * inch, height - 1.05 * inch,
                         f"Generado: {fecha_reporte}    |    Período: {periodo}")
            p.setStrokeColorRGB(*BORDER)
            p.setLineWidth(0.8)
            p.line(1 * inch, height - 1.20 * inch,
                   width - 1 * inch, height - 1.20 * inch)

        periodo = "Todos los tiempos"
        if fecha_desde and fecha_hasta:
            periodo = f"{fecha_desde} al {fecha_hasta}"
        elif fecha_desde:
            periodo = f"Desde {fecha_desde}"
        elif fecha_hasta:
            periodo = f"Hasta {fecha_hasta}"

        draw_page_header(p, height, fecha_reporte, periodo)

        # Tarjetas de resumen
        cards_data = [
            ("Total Vendido",
             f"RD${float(total_ventas_general):,.2f}", None),
            ("Transacciones",    str(total_registros), None),
            ("Efectivo",         f"RD${float(total_efectivo):,.2f}",
             f"({sum(1 for r in rows if r['metodo'] in ('efectivo', 'cobro/efectivo') and not r['es_anulada'])} ventas)"),
            ("Transferencias",   f"RD${float(total_transferencias):,.2f}",
             f"({sum(1 for r in rows if r['metodo'] in ('transferencia', 'cobro/transferencia') and not r['es_anulada'])} trans.)"),
            ("Total Descuentos", f"RD${float(total_descuentos):,.2f}", None),
            ("Cobros",           f"RD${float(total_cobros):,.2f}",
             f"({sum(1 for r in rows if r['tipo'] == 'Cobros')} cobros)"),
            ("Contado",          f"RD${float(total_contado):,.2f}",
             f"({sum(1 for r in rows if r['tipo'] == 'contado' and not r['es_anulada'])} ventas)"),
            ("Crédito",          f"RD${float(total_credito):,.2f}",
             f"({sum(1 for r in rows if r['metodo'] == 'credito' and not r['es_anulada'])} ventas)"),
        ]

        n_cards = len(cards_data)
        total_card_area = width - 2 * inch
        card_spacing = 0.12 * inch
        card_width = (total_card_area - (n_cards - 1) * card_spacing) / n_cards
        card_height = 0.70 * inch
        card_y_top = height - 1.45 * inch
        card_y_bottom = card_y_top - card_height

        x = 1 * inch
        for label, value, sub in cards_data:
            p.setFillColorRGB(*CARD_BG)
            p.setStrokeColorRGB(*BORDER)
            p.setLineWidth(0.5)
            p.roundRect(x, card_y_bottom, card_width,
                        card_height, 4, fill=1, stroke=1)
            p.setFillColorRGB(0.75, 0.75, 0.75)
            p.setFont("Helvetica", 7)
            p.drawCentredString(
                x + card_width / 2, card_y_bottom + card_height - 0.20 * inch, label.upper())
            p.setFillColorRGB(*CARD_TEXT)
            font_size = 10 if len(value) > 14 else 11
            p.setFont("Helvetica-Bold", font_size)
            p.drawCentredString(x + card_width / 2,
                                card_y_bottom + card_height * 0.38, value)
            if sub:
                p.setFillColorRGB(0.65, 0.65, 0.65)
                p.setFont("Helvetica", 6.5)
                p.drawCentredString(x + card_width / 2,
                                    card_y_bottom + 0.10 * inch, sub)
            x += card_width + card_spacing

        # Tabla
        y_position = card_y_bottom - 0.30 * inch

        headers = ['Fecha', 'Factura', 'Usuario', 'Cliente',
                   'Tipo', 'Método', 'Valor (RD$)', 'Descuento', 'Estado']
        col_x = [
            1.00 * inch,   # Fecha
            2.00 * inch,   # Factura
            3.20 * inch,   # Usuario
            4.30 * inch,   # Cliente
            5.80 * inch,   # Tipo
            6.60 * inch,   # Método
            7.50 * inch,   # Valor
            8.50 * inch,   # Descuento
            9.20 * inch,   # Estado
        ]
        col_widths = [
            0.95 * inch,
            1.15 * inch,
            1.05 * inch,
            1.45 * inch,
            0.75 * inch,
            0.85 * inch,
            0.95 * inch,
            0.65 * inch,
            0.80 * inch,
        ]
        table_right = col_x[-1] + col_widths[-1]
        table_left = col_x[0]
        row_height = 0.22 * inch

        def draw_table_header(p, y, col_x, col_widths, headers, table_left, table_right, row_height):
            p.setFillColorRGB(*HEADER_BG)
            p.setStrokeColorRGB(*BORDER)
            p.setLineWidth(0.4)
            p.rect(table_left, y - row_height, table_right -
                   table_left, row_height, fill=1, stroke=0)
            p.setFillColorRGB(*HEADER_TEXT)
            p.setFont("Helvetica-Bold", 9)
            for i, header in enumerate(headers):
                p.drawString(col_x[i] + 0.05 * inch, y -
                             row_height + 0.07 * inch, header)
            p.setStrokeColorRGB(*BORDER)
            p.line(table_left, y - row_height, table_right, y - row_height)
            return y - row_height

        y_position = draw_table_header(
            p, y_position, col_x, col_widths, headers, table_left, table_right, row_height)
        p.setFont("Helvetica", 8)

        def draw_table_border(p, top_y, bottom_y, table_left, table_right, col_x, col_widths, BORDER):
            p.setStrokeColorRGB(*BORDER)
            p.setLineWidth(0.4)
            p.rect(table_left, bottom_y, table_right -
                   table_left, top_y - bottom_y, fill=0, stroke=1)
            for i in range(1, len(col_x)):
                p.line(col_x[i], bottom_y, col_x[i], top_y)

        table_top_y = y_position

        for idx, row in enumerate(rows):
            if y_position < 1.2 * inch:
                draw_table_border(
                    p, table_top_y, y_position, table_left, table_right, col_x, col_widths, BORDER)
                p.showPage()
                draw_page_header(p, height, fecha_reporte, periodo)
                y_position = height - 1.50 * inch
                y_position = draw_table_header(
                    p, y_position, col_x, col_widths, headers, table_left, table_right, row_height)
                table_top_y = y_position
                p.setFont("Helvetica", 8)

            if idx % 2 == 0:
                p.setFillColorRGB(*ROW_WHITE)
            else:
                p.setFillColorRGB(*ROW_ALT)
            p.rect(table_left, y_position - row_height, table_right -
                   table_left, row_height, fill=1, stroke=0)

            p.setStrokeColorRGB(*BORDER)
            p.setLineWidth(0.2)
            p.line(table_left, y_position - row_height,
                   table_right, y_position - row_height)

            p.setFillColorRGB(0.10, 0.10, 0.10)
            text_y = y_position - row_height + 0.065 * inch

            fecha_str = row['fecha'].strftime('%d/%m/%Y')
            factura = str(row['factura'])[:16]
            usuario = str(row['usuario'])[:14]
            cliente = str(row['cliente'])[:20]
            tipo = str(row['tipo'])[:15]
            metodo = str(row['metodo'])[:25]
            valor_str = f"RD${float(row['valor']):,.2f}"
            descuento_str = row['descuento'][:15]
            estado = str(row['estado'])[:30]

            cells = [
                (col_x[0], fecha_str, False),
                (col_x[1], factura, False),
                (col_x[2], usuario, False),
                (col_x[3], cliente, False),
                (col_x[4], tipo, False),
                (col_x[5], metodo, False),
                (col_x[6], valor_str, True),
                (col_x[7], descuento_str, False),
                (col_x[8], estado, False),
            ]

            for cx, text, right_align in cells:
                if right_align:
                    p.drawRightString(
                        cx + col_widths[6] - 0.05 * inch, text_y, text)
                else:
                    p.drawString(cx + 0.05 * inch, text_y, text)

            # Subrayado para devoluciones y anuladas
            if row.get('tiene_devolucion') and not row.get('es_anulada'):
                p.setStrokeColorRGB(1, 1, 0)
                p.setLineWidth(1.2)
                p.line(table_left, y_position - row_height + 0.02 * inch,
                       table_right, y_position - row_height + 0.02 * inch)
            elif row.get('es_anulada'):
                p.setStrokeColorRGB(1, 0, 0)
                p.setLineWidth(1.2)
                p.line(table_left, y_position - row_height + 0.02 * inch,
                       table_right, y_position - row_height + 0.02 * inch)

            y_position -= row_height

        draw_table_border(p, table_top_y, y_position, table_left,
                          table_right, col_x, col_widths, BORDER)

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        filename = f"reporte-ventas-cuadre-{ahora_local.strftime('%d%m%Y-%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error al generar el reporte: {str(e)}", status=500)

# ============================================================================================
# ======================== REPORTE DE VENTAS POR CADA  USUARIO (PDF) INDIVIDUAL===============================
# ============================================================================================


@login_required
def ventas_usuario_pdf(request, usuario_id):
    """
    Genera PDF con el detalle de ventas (incluyendo anuladas) y cobros realizados por un usuario específico.
    Las ventas anuladas NO se suman a los totales, pero se muestran en la tabla con estado 'Anulada'.
    """
    try:
        from io import BytesIO
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from django.shortcuts import get_object_or_404
        from django.db.models import Sum, Q
        from decimal import Decimal
        from django.utils import timezone
        from .models import Venta, PagoCuentaPorCobrar, Devolucion

        usuario = get_object_or_404(User, id=usuario_id)

        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')

        # ---------- 1. VENTAS (TODAS, incluyendo anuladas) ----------
        ventas = Venta.objects.filter(
            vendedor=usuario).select_related('cliente')
        if fecha_desde:
            ventas = ventas.filter(fecha_venta__date__gte=fecha_desde)
        if fecha_hasta:
            ventas = ventas.filter(fecha_venta__date__lte=fecha_hasta)
        ventas = ventas.order_by('-fecha_venta')

        # ---------- 2. COBROS ----------
        pagos = PagoCuentaPorCobrar.objects.filter(
            usuario=usuario,
            anulado=False
        ).select_related('cuenta__venta', 'cuenta__cliente').order_by('-fecha_pago')
        if fecha_desde:
            pagos = pagos.filter(fecha_pago__date__gte=fecha_desde)
        if fecha_hasta:
            pagos = pagos.filter(fecha_pago__date__lte=fecha_hasta)

        # ---------- CÁLCULO DE TOTALES (excluyendo anuladas) ----------
        ventas_no_anuladas = ventas.filter(anulada=False)
        total_ventas = ventas_no_anuladas.aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')
        total_contado = ventas_no_anuladas.filter(tipo_venta='contado').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')
        total_credito = ventas_no_anuladas.filter(tipo_venta='credito').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')
        total_cobros = pagos.aggregate(total=Sum('monto'))[
            'total'] or Decimal('0.00')
        cantidad_ventas = ventas_no_anuladas.count()

        entrada_dia = float(total_contado) + float(total_cobros)

        # ---------- CONFIGURACIÓN DEL PDF ----------
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=landscape(letter))
        width, height = landscape(letter)

        # ---------- ENCABEZADO ----------
        p.setFont("Helvetica-Bold", 18)
        p.drawString(1 * inch, height - 0.75 * inch,
                     "Reporte de Actividad del Usuario")
        p.setFont("Helvetica-Bold", 14)
        nombre_usuario = usuario.get_full_name() or usuario.username
        p.drawString(1 * inch, height - 1.25 * inch, nombre_usuario)

        p.setFont("Helvetica", 10)
        fecha_reporte = timezone.now().strftime('%d/%m/%Y %H:%M')
        p.drawString(1 * inch, height - 1.6 * inch,
                     f"Generado: {fecha_reporte}")

        periodo = "Todos los tiempos"
        if fecha_desde and fecha_hasta:
            periodo = f"Desde {fecha_desde} hasta {fecha_hasta}"
        elif fecha_desde:
            periodo = f"Desde {fecha_desde}"
        elif fecha_hasta:
            periodo = f"Hasta {fecha_hasta}"
        p.drawString(1 * inch, height - 1.8 * inch, f"Período: {periodo}")

        y_position = height - 2.3 * inch

        # ---------- RESUMEN GENERAL ----------
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1 * inch, y_position, "RESUMEN GENERAL")
        y_position -= 0.2 * inch

        p.setFont("Helvetica", 10)
        p.drawString(1.2 * inch, y_position,
                     f"Cantidad de ventas (no anuladas): {cantidad_ventas}")
        y_position -= 0.15 * inch
        p.drawString(1.2 * inch, y_position,
                     f"Total ventas (no anuladas): RD${float(total_ventas):,.2f}")
        y_position -= 0.15 * inch
        p.drawString(1.2 * inch, y_position,
                     f"Total contado: RD${float(total_contado):,.2f}")
        y_position -= 0.15 * inch
        p.drawString(1.2 * inch, y_position,
                     f"Total crédito: RD${float(total_credito):,.2f}")
        y_position -= 0.15 * inch
        p.drawString(1.2 * inch, y_position,
                     f"Total cobros registrados: RD${float(total_cobros):,.2f}")
        y_position -= 0.15 * inch
        p.drawString(1.2 * inch, y_position,
                     f"Entrada del día (contado + cobros): RD${entrada_dia:,.2f}")
        y_position -= 0.2 * inch

        p.line(1 * inch, y_position, 9.5 * inch, y_position)
        y_position -= 0.3 * inch

        # ---------- SECCIÓN 1: VENTAS (DETALLE, incluyendo anuladas) ----------
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1 * inch, y_position,
                     "VENTAS REALIZADAS (incluye anuladas)")
        y_position -= 0.3 * inch

        # Encabezados de tabla de ventas (6 columnas)
        p.setFont("Helvetica-Bold", 9)
        p.drawString(1.0 * inch, y_position, "Fecha")
        p.drawString(2.0 * inch, y_position, "Factura")
        p.drawString(3.5 * inch, y_position, "Cliente")
        p.drawString(5.5 * inch, y_position, "Tipo")
        p.drawString(6.7 * inch, y_position, "Total (RD$)")
        p.drawString(8.0 * inch, y_position, "Estado")
        p.line(1.0 * inch, y_position - 0.1 * inch,
               9.5 * inch, y_position - 0.1 * inch)
        y_position -= 0.25 * inch
        p.setFont("Helvetica", 8)

        for venta in ventas:   # todas las ventas (anuladas incluidas)
            if y_position < 1.5 * inch:
                p.showPage()
                y_position = height - 1 * inch
                p.setFont("Helvetica-Bold", 12)
                p.drawString(1 * inch, y_position, "VENTAS (continuación)")
                y_position -= 0.3 * inch
                p.setFont("Helvetica-Bold", 9)
                p.drawString(1.0 * inch, y_position, "Fecha")
                p.drawString(2.0 * inch, y_position, "Factura")
                p.drawString(3.5 * inch, y_position, "Cliente")
                p.drawString(5.5 * inch, y_position, "Tipo")
                p.drawString(6.7 * inch, y_position, "Total (RD$)")
                p.drawString(8.0 * inch, y_position, "Estado")
                p.line(1.0 * inch, y_position - 0.1 * inch,
                       9.5 * inch, y_position - 0.1 * inch)
                y_position -= 0.25 * inch
                p.setFont("Helvetica", 8)

            # Datos de la venta
            fecha_str = venta.fecha_venta.strftime('%d/%m/%Y')
            factura = venta.numero_factura[:14]
            cliente = venta.cliente_nombre or "N/A"
            if len(cliente) > 20:
                cliente = cliente[:20] + "..."

            tipo = venta.tipo_venta.capitalize()
            total_str = f"RD${float(venta.total):,.2f}"
            estado = "Anulada" if venta.anulada else "Activa"

            # Color para el total si está anulada
            p.setFillColorRGB(0, 0, 0)  # negro normal
            if venta.anulada:
                p.setFillColorRGB(0.8, 0, 0)  # rojo para anuladas

            p.drawString(1.0 * inch, y_position, fecha_str)
            p.drawString(2.0 * inch, y_position, factura)
            p.drawString(3.5 * inch, y_position, cliente)
            p.drawString(5.5 * inch, y_position, tipo)
            p.drawRightString(7.5 * inch, y_position, total_str)
            p.drawString(8.0 * inch, y_position, estado)

            # Restaurar color negro para la siguiente fila
            p.setFillColorRGB(0, 0, 0)

            y_position -= 0.15 * inch

        # Separador después de ventas
        y_position -= 0.2 * inch
        p.line(1.0 * inch, y_position, 9.5 * inch, y_position)
        y_position -= 0.3 * inch

        # ---------- SECCIÓN 2: COBROS REGISTRADOS ----------
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1 * inch, y_position,
                     "COBROS REGISTRADOS (Pagos a Cuentas por Cobrar)")
        y_position -= 0.3 * inch

        p.setFont("Helvetica-Bold", 9)
        p.drawString(1.0 * inch, y_position, "Fecha Pago")
        p.drawString(2.2 * inch, y_position, "Factura")
        p.drawString(3.8 * inch, y_position, "Cliente")
        p.drawString(5.5 * inch, y_position, "Monto (RD$)")
        p.drawString(6.8 * inch, y_position, "Método")
        p.drawString(8.0 * inch, y_position, "Saldo Pendiente")
        p.line(1.0 * inch, y_position - 0.1 * inch,
               9.5 * inch, y_position - 0.1 * inch)
        y_position -= 0.25 * inch
        p.setFont("Helvetica", 8)

        for pago in pagos:
            if y_position < 1.5 * inch:
                p.showPage()
                y_position = height - 1 * inch
                p.setFont("Helvetica-Bold", 12)
                p.drawString(1 * inch, y_position,
                             "COBROS REGISTRADOS (continuación)")
                y_position -= 0.3 * inch
                p.setFont("Helvetica-Bold", 9)
                p.drawString(1.0 * inch, y_position, "Fecha Pago")
                p.drawString(2.2 * inch, y_position, "Factura")
                p.drawString(3.8 * inch, y_position, "Cliente")
                p.drawString(5.5 * inch, y_position, "Monto (RD$)")
                p.drawString(6.8 * inch, y_position, "Método")
                p.drawString(8.0 * inch, y_position, "Saldo Pendiente")
                p.line(1.0 * inch, y_position - 0.1 * inch,
                       9.5 * inch, y_position - 0.1 * inch)
                y_position -= 0.25 * inch
                p.setFont("Helvetica", 8)

            fecha_pago = pago.fecha_pago.strftime('%d/%m/%Y')
            factura_num = pago.cuenta.venta.numero_factura if pago.cuenta and pago.cuenta.venta else "N/A"
            cliente_nombre = "N/A"
            if pago.cuenta:
                if pago.cuenta.cliente:
                    cliente_nombre = pago.cuenta.cliente.full_name
                elif pago.cuenta.venta and pago.cuenta.venta.cliente_nombre:
                    cliente_nombre = pago.cuenta.venta.cliente_nombre
            cliente = (
                cliente_nombre[:20] + "...") if len(cliente_nombre) > 20 else cliente_nombre
            monto_str = f"RD${float(pago.monto):,.2f}"
            metodo = pago.get_metodo_pago_display() or pago.metodo_pago or "N/A"
            saldo = pago.cuenta.saldo_pendiente if pago.cuenta else Decimal(
                '0')
            saldo_str = f"RD${float(saldo):,.2f}"

            p.drawString(1.0 * inch, y_position, fecha_pago)
            p.drawString(2.2 * inch, y_position, factura_num[:12])
            p.drawString(3.8 * inch, y_position, cliente)
            p.drawRightString(6.2 * inch, y_position, monto_str)
            p.drawString(6.8 * inch, y_position, metodo[:10])
            p.drawRightString(9.5 * inch, y_position, saldo_str)

            y_position -= 0.15 * inch

        # ---------- FIRMAS ----------
        y_position = 1.5 * inch
        p.line(1 * inch, y_position, 3.5 * inch, y_position)
        p.setFont("Helvetica", 9)
        p.drawString(1.2 * inch, y_position - 0.2 * inch, "Firma del Usuario")
        p.line(6 * inch, y_position, 9.5 * inch, y_position)
        p.drawString(6.7 * inch, y_position - 0.2 *
                     inch, "Firma del Administrador")

        p.showPage()
        p.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        filename = f"actividad_{usuario.username}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error al generar el PDF: {str(e)}", status=500)
 # ================================================================================================
 # ========================== Obtener lista de usuarios para filtros =============================
 # ================================================================================================

# ============================================================================================
# ======================== Obtener lista de usuarios para filtros =============================
# ============================================================================================


@login_required
def get_usuarios(request):
    """Obtener lista de usuarios para filtros"""
    try:
        usuarios = User.objects.all().values('id', 'username')
        return JsonResponse({'usuarios': list(usuarios)})
    except Exception as e:
        print(f"Error en get_usuarios: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# ================================================================================================
# ================================= VENTAS POR USUARIO ACTUAL ===================================
# ================================================================================================


@login_required
def reporte_ventas_usuario_actual(request):
    """Vista para mostrar reporte de ventas del usuario actual"""
    try:
        # Obtener filtros de fecha del request
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')

        # Query base de ventas del usuario actual no anuladas
        ventas = Venta.objects.filter(
            anulada=False,
            vendedor=request.user
        ).order_by('-fecha_venta')

        # Aplicar filtros de fecha
        if fecha_desde:
            ventas = ventas.filter(fecha_venta__date__gte=fecha_desde)
        if fecha_hasta:
            ventas = ventas.filter(fecha_venta__date__lte=fecha_hasta)

        # Calcular totales
        total_ventas = ventas.aggregate(total=Sum('total'))[
            'total'] or Decimal('0.00')
        cantidad_ventas = ventas.count()

        # Ventas por tipo
        ventas_contado = ventas.filter(tipo_venta='contado').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')
        ventas_credito = ventas.filter(tipo_venta='credito').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')

        # Ventas por método de pago
        ventas_efectivo = ventas.filter(
            tipo_venta='contado',
            metodo_pago='efectivo'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        ventas_tarjeta = ventas.filter(
            tipo_venta='contado',
            metodo_pago='tarjeta'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        ventas_transferencia = ventas.filter(
            tipo_venta='contado',
            metodo_pago='transferencia'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        # Promedio por venta
        promedio_venta = total_ventas / cantidad_ventas if cantidad_ventas > 0 else 0

        # Preparar datos para la respuesta
        data = {
            'success': True,
            'usuario': request.user.username,
            'usuario_id': request.user.id,
            'cantidad_ventas': cantidad_ventas,
            'total_ventas': float(total_ventas),
            'total_contado': float(ventas_contado),
            'total_credito': float(ventas_credito),
            'total_efectivo': float(ventas_efectivo),
            'total_tarjeta': float(ventas_tarjeta),
            'total_transferencia': float(ventas_transferencia),
            'promedio_venta': float(promedio_venta),
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }

        # Si se solicita HTML (para modal), devolver template
        if request.GET.get('format') == 'html':
            ventas_list = list(ventas[:50])  # Últimas 50 ventas
            return render(request, 'facturacion/reporte_ventas_usuario_modal.html', {
                'usuario': request.user,
                'ventas': ventas_list,
                'resumen': data,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
            })

        # Si es AJAX, devolver JSON
        return JsonResponse(data)

    except Exception as e:
        print(f"Error en reporte_ventas_usuario_actual: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def reporte_ventas_usuario_actual_pdf(request):
    """Generar PDF con reporte de ventas del usuario actual"""
    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        from io import BytesIO
        from datetime import datetime

        # Obtener filtros
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')

        # Query de ventas del usuario actual
        ventas = Venta.objects.filter(
            anulada=False,
            vendedor=request.user
        ).order_by('-fecha_venta')

        if fecha_desde:
            ventas = ventas.filter(fecha_venta__date__gte=fecha_desde)
        if fecha_hasta:
            ventas = ventas.filter(fecha_venta__date__lte=fecha_hasta)

        # Calcular totales
        total_ventas = ventas.aggregate(total=Sum('total'))[
            'total'] or Decimal('0.00')
        cantidad_ventas = ventas.count()

        # Ventas por tipo
        ventas_contado = ventas.filter(tipo_venta='contado').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')
        ventas_credito = ventas.filter(tipo_venta='credito').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')

        # Ventas por método de pago
        ventas_efectivo = ventas.filter(tipo_venta='contado', metodo_pago='efectivo').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')
        ventas_tarjeta = ventas.filter(tipo_venta='contado', metodo_pago='tarjeta').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')
        ventas_transferencia = ventas.filter(tipo_venta='contado', metodo_pago='transferencia').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')

        # Crear PDF en orientación vertical
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # ============================================
        # ENCABEZADO
        # ============================================
        # Título
        p.setFont("Helvetica-Bold", 18)
        p.drawString(1 * inch, height - 1 * inch, "REPORTE DE VENTAS")

        # Usuario
        p.setFont("Helvetica-Bold", 14)
        p.drawString(1 * inch, height - 1.5 * inch,
                     f"Usuario: {request.user.get_full_name() or request.user.username}")

        # Fecha del reporte
        p.setFont("Helvetica", 10)
        fecha_reporte = timezone.now().strftime('%d/%m/%Y %H:%M')
        p.drawString(1 * inch, height - 1.8 * inch,
                     f"Fecha de generación: {fecha_reporte}")

        # Período
        periodo = "Todos los tiempos"
        if fecha_desde and fecha_hasta:
            periodo = f"{fecha_desde} al {fecha_hasta}"
        elif fecha_desde:
            periodo = f"Desde {fecha_desde}"
        elif fecha_hasta:
            periodo = f"Hasta {fecha_hasta}"

        p.setFont("Helvetica-Bold", 11)
        p.drawString(1 * inch, height - 2.1 * inch, f"Período: {periodo}")

        # Línea separadora
        p.line(1 * inch, height - 2.3 * inch, 7.5 * inch, height - 2.3 * inch)

        # ============================================
        # RESUMEN
        # ============================================
        y_position = height - 2.8 * inch

        # Tarjeta de resumen
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1 * inch, y_position, "RESUMEN DE VENTAS:")
        y_position -= 0.3 * inch

        # Cuadro de resumen
        p.setFont("Helvetica", 10)
        p.drawString(1.2 * inch, y_position, f"Cantidad de ventas:")
        p.drawRightString(3.5 * inch, y_position, f"{cantidad_ventas}")
        y_position -= 0.2 * inch

        p.drawString(1.2 * inch, y_position, f"Total ventas:")
        p.drawRightString(3.5 * inch, y_position,
                          f"RD${float(total_ventas):,.2f}")
        y_position -= 0.2 * inch

        if cantidad_ventas > 0:
            promedio = float(total_ventas) / cantidad_ventas
            p.drawString(1.2 * inch, y_position, f"Promedio por venta:")
            p.drawRightString(3.5 * inch, y_position, f"RD${promedio:,.2f}")
            y_position -= 0.2 * inch

        # Línea separadora
        p.line(1 * inch, y_position - 0.1 * inch,
               7.5 * inch, y_position - 0.1 * inch)
        y_position -= 0.3 * inch

        # Desglose por tipo
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1 * inch, y_position, "DESGLOSE POR TIPO DE VENTA:")
        y_position -= 0.25 * inch

        p.setFont("Helvetica", 10)
        p.drawString(1.2 * inch, y_position, f"Ventas al contado:")
        p.drawRightString(3.5 * inch, y_position,
                          f"RD${float(ventas_contado):,.2f}")
        y_position -= 0.2 * inch

        p.drawString(1.2 * inch, y_position, f"Ventas a crédito:")
        p.drawRightString(3.5 * inch, y_position,
                          f"RD${float(ventas_credito):,.2f}")
        y_position -= 0.2 * inch

        # Línea separadora
        p.line(1 * inch, y_position - 0.1 * inch,
               7.5 * inch, y_position - 0.1 * inch)
        y_position -= 0.3 * inch

        # Desglose por método de pago
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1 * inch, y_position,
                     "DESGLOSE POR MÉTODO DE PAGO (CONTADO):")
        y_position -= 0.25 * inch

        p.setFont("Helvetica", 10)
        p.drawString(1.2 * inch, y_position, f"Efectivo:")
        p.drawRightString(3.5 * inch, y_position,
                          f"RD${float(ventas_efectivo):,.2f}")
        y_position -= 0.2 * inch

        p.drawString(1.2 * inch, y_position, f"Tarjeta:")
        p.drawRightString(3.5 * inch, y_position,
                          f"RD${float(ventas_tarjeta):,.2f}")
        y_position -= 0.2 * inch

        p.drawString(1.2 * inch, y_position, f"Transferencia:")
        p.drawRightString(3.5 * inch, y_position,
                          f"RD${float(ventas_transferencia):,.2f}")
        y_position -= 0.2 * inch

        # Línea separadora
        p.line(1 * inch, y_position - 0.1 * inch,
               7.5 * inch, y_position - 0.1 * inch)
        y_position -= 0.3 * inch

        # ============================================
        # LISTADO DE VENTAS (últimas 20)
        # ============================================
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1 * inch, y_position, "ÚLTIMAS VENTAS:")
        y_position -= 0.3 * inch

        # Encabezados de tabla
        p.setFont("Helvetica-Bold", 9)
        p.drawString(1 * inch, y_position, "Fecha")
        p.drawString(2.2 * inch, y_position, "Factura")
        p.drawString(3.8 * inch, y_position, "Cliente")
        p.drawString(5.5 * inch, y_position, "Tipo")
        p.drawString(6.3 * inch, y_position, "Total")

        p.line(1 * inch, y_position - 0.1 * inch,
               7.5 * inch, y_position - 0.1 * inch)
        y_position -= 0.2 * inch

        p.setFont("Helvetica", 8)
        ventas_recientes = ventas[:20]  # Mostrar solo las últimas 20 ventas

        for venta in ventas_recientes:
            if y_position < 1 * inch:
                p.showPage()
                y_position = height - 1 * inch
                p.setFont("Helvetica-Bold", 9)
                p.drawString(1 * inch, y_position, "Fecha")
                p.drawString(2.2 * inch, y_position, "Factura")
                p.drawString(3.8 * inch, y_position, "Cliente")
                p.drawString(5.5 * inch, y_position, "Tipo")
                p.drawString(6.3 * inch, y_position, "Total")
                p.line(1 * inch, y_position - 0.1 * inch,
                       7.5 * inch, y_position - 0.1 * inch)
                y_position -= 0.2 * inch
                p.setFont("Helvetica", 8)

            fecha_str = venta.fecha_venta.strftime('%d/%m/%Y')
            p.drawString(1 * inch, y_position, fecha_str)
            p.drawString(2.2 * inch, y_position, venta.numero_factura[:12])

            cliente = venta.cliente_nombre[:18] + "..." if len(
                venta.cliente_nombre) > 18 else venta.cliente_nombre
            p.drawString(3.8 * inch, y_position, cliente)

            tipo = "Contado" if venta.tipo_venta == 'contado' else "Crédito"
            p.drawString(5.5 * inch, y_position, tipo)
            p.drawRightString(7.5 * inch, y_position,
                              f"RD${float(venta.total):,.2f}")

            y_position -= 0.15 * inch

        # ============================================
        # FIRMAS
        # ============================================
        y_position = 2 * inch
        p.line(1 * inch, y_position, 3.5 * inch, y_position)
        p.setFont("Helvetica", 9)
        p.drawString(1.2 * inch, y_position - 0.2 * inch, "Firma del Vendedor")

        p.line(5 * inch, y_position, 7.5 * inch, y_position)
        p.drawString(5.7 * inch, y_position - 0.2 *
                     inch, "Firma del Administrador")

        # ============================================
        # FINALIZAR PDF
        # ============================================
        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        filename = f"reporte_ventas_{request.user.username}_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        print(f"Error en reporte_ventas_usuario_actual_pdf: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error al generar PDF: {str(e)}", status=500)


# ================================================================================================
# =======================Decorador personalizado para requerir superusuario =====================
# ================================================================================================
def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        print(f"Usuario autenticado: {request.user.is_authenticated}")  # Debug
        print(f"Es superusuario: {request.user.is_superuser}")  # Debug
        print(f"Usuario: {request.user}")  # Debug

        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required', 'status': 401}, status=401)
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Superuser privileges required', 'status': 403}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ================================================================================================
# ============================ Vista para renderizar la página de inventario ============================
# ================================================================================================


@login_required
@check_module_access('inventario')
def inventario(request):
    return render(request, "facturacion/inventario.html", {'user': request.user})

# ================================================================================================
# ============================ Vista para obtener los datos del inventario (JSON) ============================
# ================================================================================================


def inventario_datos(request):
    try:
        productos = list(EntradaProducto.objects.all().values(
            'id',
            'codigo_producto',
            'descripcion',
            'marca',
            'compatibilidad',
            'color',
            'cantidad',
            'costo',
            'precio',  # Añade este campo
            'precio_por_mayor',  # Añade este campo
            'precio_con_itbis',
            'precio_por_mayor_con_itbis',
            'imagen',
            'observaciones'
        ))
        # Construir la URL completa para las imágenes
        for producto in productos:
            if producto['imagen']:
                producto['imagen'] = request.build_absolute_uri(
                    settings.MEDIA_URL + producto['imagen'])
            else:
                producto['imagen'] = None
        proveedores = list(Proveedor.objects.all().values())
        return JsonResponse({
            'productos': productos,
            'proveedores': proveedores,
            'user': {
                'is_superuser': request.user.is_superuser,
                'username': request.user.username
            }
        })
    except Exception as e:
        return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)


# ================================================================================================
# ================ Vista para editar un producto (solo superusuarios) ===========================
# ================================================================================================
@csrf_exempt
@superuser_required
def inventario_editar(request, id):
    if request.method not in ['PUT', 'POST']:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        producto = EntradaProducto.objects.get(id=id)

        is_multipart = request.content_type and 'multipart' in request.content_type

        if is_multipart:
            # Actualizar campos del formulario
            producto.descripcion = request.POST.get(
                'descripcion', producto.descripcion)
            producto.marca = request.POST.get('marca', producto.marca)
            producto.compatibilidad = request.POST.get(
                'compatibilidad', producto.compatibilidad) or None
            producto.color = request.POST.get('color', producto.color) or None
            producto.costo = Decimal(request.POST.get('costo', producto.costo))

            # Manejar precios con ITBIS - CAMBIO IMPORTANTE
            precio_con_itbis = request.POST.get('precio_con_itbis')
            if precio_con_itbis:
                # Convertir a precio base
                producto.precio = Decimal(precio_con_itbis) / Decimal('1.18')

            precio_por_mayor_con_itbis = request.POST.get(
                'precio_por_mayor_con_itbis')
            if precio_por_mayor_con_itbis:
                producto.precio_por_mayor = Decimal(
                    precio_por_mayor_con_itbis) / Decimal('1.18')  # Convertir a precio base

            producto.observaciones = request.POST.get(
                'observaciones', producto.observaciones) or None

            # Procesar la imagen si se envió una nueva
            if 'imagen' in request.FILES:
                if producto.imagen:
                    try:
                        old_image_path = producto.imagen.path
                        if os.path.isfile(old_image_path):
                            os.remove(old_image_path)
                    except Exception as e:
                        print(f"Error al eliminar imagen anterior: {str(e)}")
                producto.imagen = request.FILES['imagen']

        else:  # Si es JSON (sin imagen)
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'JSON inválido'}, status=400)

            producto.descripcion = data.get(
                'descripcion', producto.descripcion)
            producto.marca = data.get('marca', producto.marca)
            producto.compatibilidad = data.get(
                'compatibilidad', producto.compatibilidad) or None
            producto.color = data.get('color', producto.color) or None
            producto.costo = Decimal(str(data.get('costo', producto.costo)))

            # Manejar precios con ITBIS - CAMBIO IMPORTANTE
            precio_con_itbis = data.get('precio_con_itbis')
            if precio_con_itbis:
                # Convertir a precio base
                producto.precio = Decimal(
                    str(precio_con_itbis)) / Decimal('1.18')

            precio_por_mayor_con_itbis = data.get('precio_por_mayor_con_itbis')
            if precio_por_mayor_con_itbis:
                producto.precio_por_mayor = Decimal(
                    str(precio_por_mayor_con_itbis)) / Decimal('1.18')  # Convertir a precio base

            producto.observaciones = data.get(
                'observaciones', producto.observaciones) or None

        # Guardar el producto (esto recalculará los precios con ITBIS automáticamente)
        producto.save()

        # Construir URL completa para la imagen
        imagen_url = None
        if producto.imagen:
            imagen_url = request.build_absolute_uri(producto.imagen.url)

        # Preparar la respuesta con los datos actualizados
        producto_actualizado = {
            'id': producto.id,
            'codigo_producto': producto.codigo_producto,
            'descripcion': producto.descripcion,
            'marca': producto.marca,
            'compatibilidad': producto.compatibilidad,
            'color': producto.color,
            'cantidad': producto.cantidad,
            'costo': float(producto.costo),
            'precio': float(producto.precio),
            'precio_por_mayor': float(producto.precio_por_mayor) if producto.precio_por_mayor else None,
            'precio_con_itbis': float(producto.precio_con_itbis) if producto.precio_con_itbis else None,
            'precio_por_mayor_con_itbis': float(producto.precio_por_mayor_con_itbis) if producto.precio_por_mayor_con_itbis else None,
            'imagen': imagen_url,
            'observaciones': producto.observaciones,
        }

        return JsonResponse(producto_actualizado)

    except EntradaProducto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except ValueError as e:
        return JsonResponse({'error': f'Valor inválido: {str(e)}'}, status=400)
    except Exception as e:
        print(f"Error en inventario_editar: {str(e)}")
        return JsonResponse({'error': f'Error al actualizar el producto: {str(e)}'}, status=500)

# ================================================================================================
# ============= Vista para eliminar un producto (solo superusuarios) ==============================
# ================================================================================================


@csrf_exempt
@superuser_required
def inventario_eliminar(request, id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        producto = EntradaProducto.objects.get(id=id)

        # Eliminar imagen si existe
        if producto.imagen:
            try:
                if os.path.isfile(producto.imagen.path):
                    os.remove(producto.imagen.path)
                    print(f"Imagen eliminada: {producto.imagen.path}")
            except Exception as e:
                print(f"Error al eliminar imagen: {str(e)}")

        producto.delete()
        return JsonResponse({'success': True, 'message': 'Producto eliminado correctamente'})

    except EntradaProducto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except Exception as e:
        print(f"Error en inventario_eliminar: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# ================================================================================================
# ============================ Vista para renderizar la página de ventas ============================
# ================================================================================================
@user_passes_test(is_superuser_or_usuario_normal, login_url='/')
@login_required
@check_module_access('ventas')
def ventas(request):

    if request.method == 'POST':
        return procesar_venta(request)

    clientes = Cliente.objects.filter(status=True)
    productos = EntradaProducto.objects.filter(activo=True, cantidad__gt=0)

    return render(request, "facturacion/ventas.html", {
        'user': request.user,
        'clientes': clientes,
        'productos': productos
    })


# ================================================================================================
# ====================================== Funciones auxiliares ======================================
# ================================================================================================
def safe_decimal(value, default=0):
    """
    Convierte de forma segura un valor a Decimal.
    Maneja strings, números, y valores nulos/vacíos.
    """
    if value is None:
        return Decimal(default)

    # Si ya es Decimal, devolverlo
    if isinstance(value, Decimal):
        return value

    # Convertir a string y limpiar
    value_str = str(value).strip()

    # Si está vacío, retornar default
    if not value_str:
        return Decimal(default)

    try:
        # Reemplazar comas por puntos
        value_str = value_str.replace(',', '.')

        # Eliminar caracteres no numéricos excepto punto, signo negativo y exponente
        # Permitir formato científico si es necesario
        cleaned_chars = []
        for c in value_str:
            if c.isdigit() or c in ['.', '-']:
                cleaned_chars.append(c)
        value_str = ''.join(cleaned_chars)

        # Si después de limpiar está vacío, retornar default
        if not value_str or value_str == '-':
            return Decimal(default)

        return Decimal(value_str)
    except (InvalidOperation, ValueError, TypeError):
        # Log del error para debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"No se pudo convertir a Decimal: '{value}' (tipo: {type(value)})")
        return Decimal(default)


def safe_int(value, default=0):
    """
    Convierte de forma segura un valor a entero.
    Maneja strings vacíos, None, y valores inválidos.
    """
    if value is None:
        return default

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    value_str = str(value).strip()
    if not value_str:
        return default

    try:
        # Eliminar caracteres no numéricos excepto signo negativo
        cleaned_str = ''.join(c for c in value_str if c.isdigit() or c == '-')
        if cleaned_str and cleaned_str != '-':
            return int(cleaned_str)
        return default
    except (ValueError, TypeError):
        return default

# ================================================================================================
# ============================ Vista para procesar la venta ============================
# ================================================================================================


@csrf_exempt
@require_POST
@transaction.atomic
@login_required
def procesar_venta(request):
    try:
        data = request.POST
        user = request.user

        print("=== INICIANDO PROCESO DE VENTA ===")
        print(f"Usuario: {user.username} (Superusuario: {user.is_superuser})")

        # ============================================
        # DATOS DE LA VENTA - USANDO safe_decimal
        # ============================================
        payment_type = data.get('payment_type', 'contado')
        payment_method = data.get('payment_method', 'efectivo')

        subtotal_sin_itbis = safe_decimal(data.get('subtotal'), 0)
        itbis_monto = safe_decimal(data.get('itbis_monto'), 0)
        itbis_porcentaje = safe_decimal(data.get('itbis_porcentaje', 18.00))
        total = safe_decimal(data.get('total'), 0)
        total_a_pagar = safe_decimal(data.get('total_a_pagar'), 0)
        cash_received = safe_decimal(data.get('cash_received'), 0)
        change_amount = safe_decimal(data.get('change_amount'), 0)

        print(
            f"Datos recibidos - Subtotal: {subtotal_sin_itbis}, ITBIS: {itbis_monto}, Total: {total}")

        # ============================================
        # VALIDACIÓN DE DESCUENTO - SOLO PARA SUPERUSUARIOS
        # ============================================
        if not user.is_superuser:
            discount_percentage = Decimal('0.00')
            discount_amount = Decimal('0.00')
            received_discount = safe_decimal(
                data.get('discount_percentage', 0))
            if received_discount > 0:
                return JsonResponse({
                    'success': False,
                    'message': 'No tiene permisos para aplicar descuentos. Solo el administrador puede hacerlo.'
                })
        else:
            discount_percentage = safe_decimal(
                data.get('discount_percentage', 0))
            discount_amount = safe_decimal(data.get('discount_amount', 0))

        print(
            f"Descuento - Porcentaje: {discount_percentage}%, Monto: {discount_amount}")

        # ============================================
        # VALIDACIONES BÁSICAS
        # ============================================
        if payment_type not in ['contado', 'credito']:
            return JsonResponse({'success': False, 'message': 'Tipo de pago inválido'})

        if payment_method not in ['efectivo', 'tarjeta', 'transferencia']:
            return JsonResponse({'success': False, 'message': 'Método de pago inválido'})

        if subtotal_sin_itbis < 0:
            return JsonResponse({'success': False, 'message': 'El subtotal debe ser mayor o igual a 0'})

        if total <= 0:
            return JsonResponse({'success': False, 'message': 'El total debe ser mayor a 0'})

        if user.is_superuser and (discount_percentage < 0 or discount_percentage > 100):
            return JsonResponse({
                'success': False,
                'message': 'El porcentaje de descuento debe estar entre 0 y 100'
            })

        # ============================================
        # CÁLCULO Y VALIDACIÓN DE ITBIS
        # ============================================
        subtotal_con_itbis = subtotal_sin_itbis + itbis_monto

        itbis_calculado = subtotal_sin_itbis * \
            (itbis_porcentaje / Decimal('100.00'))
        if abs(itbis_monto - itbis_calculado) > Decimal('0.01'):
            print(
                f"Advertencia: ITBIS inconsistente. Recibido: {itbis_monto}, Calculado: {itbis_calculado}")
            itbis_monto = itbis_calculado
            subtotal_con_itbis = subtotal_sin_itbis + itbis_monto

        print(
            f"ITBIS - Porcentaje: {itbis_porcentaje}%, Monto: {itbis_monto}, Calculado: {itbis_calculado}")

        # ============================================
        # VALIDACIÓN DE DESCUENTO (CÁLCULO)
        # ============================================
        if user.is_superuser:
            discount_amount_calculado = (
                subtotal_con_itbis * discount_percentage) / Decimal('100.00')
            total_calculado = subtotal_con_itbis - discount_amount_calculado

            if abs(discount_amount - discount_amount_calculado) > Decimal('0.01'):
                print(
                    f"Advertencia: Descuento inconsistente. Recibido: {discount_amount}, Calculado: {discount_amount_calculado}")
                discount_amount = discount_amount_calculado

            if abs(total - total_calculado) > Decimal('0.01'):
                print(
                    f"Advertencia: Total inconsistente. Recibido: {total}, Calculado: {total_calculado}")
                total = total_calculado
        else:
            discount_amount = Decimal('0.00')
            discount_percentage = Decimal('0.00')
            total = subtotal_con_itbis

        if abs(total_a_pagar - total) > Decimal('0.01'):
            total_a_pagar = total

        print(
            f"Totales - Subtotal con ITBIS: {subtotal_con_itbis}, Total: {total}, Total a pagar: {total_a_pagar}")

        # ============================================
        # PROCESAR CLIENTE
        # ============================================
        client_id = data.get('client_id')
        client_name = data.get('client_name', '').strip()
        client_document = data.get('client_document', '').strip()
        cliente = None

        if payment_type == 'credito':
            if not client_id:
                return JsonResponse({'success': False, 'message': 'Debe seleccionar un cliente para ventas a crédito'})
            try:
                from .models import Cliente, CuentaPorCobrar
                cliente = Cliente.objects.get(id=client_id, status=True)

                cuentas_pendientes = CuentaPorCobrar.objects.filter(
                    cliente=cliente,
                    anulada=False,
                    eliminada=False
                ).exclude(estado='pagada')

                total_deuda = sum(safe_decimal(cuenta.saldo_pendiente)
                                  for cuenta in cuentas_pendientes)
                total_con_nueva_venta = total_deuda + total

                if total_con_nueva_venta > safe_decimal(cliente.credit_limit):
                    return JsonResponse({
                        'success': False,
                        'message': f'El cliente {cliente.full_name} ha excedido su límite de crédito. Límite: RD${safe_decimal(cliente.credit_limit):.2f}, Deuda actual: RD${total_deuda:.2f}, Nueva deuda: RD${total_con_nueva_venta:.2f}'
                    })

            except Cliente.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Cliente no válido o no encontrado'})
        else:
            if not client_name:
                return JsonResponse({'success': False, 'message': 'Debe ingresar el nombre del cliente'})

        # ============================================
        # PROCESAR ITEMS DE LA VENTA
        # ============================================
        sale_items_json = data.get('sale_items')
        if not sale_items_json:
            return JsonResponse({'success': False, 'message': 'No hay productos en la venta'})

        try:
            sale_items = json.loads(sale_items_json)
        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'message': f'Formato de productos no válido: {str(e)}'})

        if not sale_items:
            return JsonResponse({'success': False, 'message': 'No hay productos en la venta'})

        from .models import EntradaProducto
        productos_validados = []

        for item in sale_items:
            try:
                producto_id = item.get('id')
                producto_nombre = item.get('name', 'Producto Desconocido')
                cantidad_solicitada = safe_int(item.get('quantity', 0))
                precio_unitario = safe_decimal(item.get('price', 0))

                if not producto_id:
                    return JsonResponse({'success': False, 'message': f'Producto sin ID: {producto_nombre}'})

                if cantidad_solicitada <= 0:
                    return JsonResponse({'success': False, 'message': f'Cantidad inválida para {producto_nombre}'})

                producto = EntradaProducto.objects.get(
                    id=producto_id, activo=True)

                if safe_int(producto.cantidad) < cantidad_solicitada:
                    nombre_producto = getattr(producto, 'descripcion', getattr(
                        producto, 'nombre', 'Producto Desconocido'))
                    return JsonResponse({
                        'success': False,
                        'message': f'Stock insuficiente para {nombre_producto}. Disponible: {producto.cantidad}, Solicitado: {cantidad_solicitada}'
                    })

                productos_validados.append({
                    'producto': producto,
                    'cantidad': cantidad_solicitada,
                    'precio_unitario': precio_unitario,
                    'subtotal': safe_decimal(item.get('subtotal', 0)),
                    'nombre': producto_nombre
                })

            except EntradaProducto.DoesNotExist:
                return JsonResponse({'success': False, 'message': f'Producto no encontrado: {item.get("name", "Desconocido")}'})
            except (ValueError, KeyError) as e:
                return JsonResponse({'success': False, 'message': f'Datos inválidos para producto: {item.get("name", "Desconocido")}. Error: {str(e)}'})

        print(f"Productos validados: {len(productos_validados)} items")

        # ============================================
        # CREAR LA VENTA
        # ============================================
        from .models import Venta, DetalleVenta
        venta = Venta(
            vendedor=user,
            cliente=cliente,
            cliente_nombre=client_name,
            cliente_documento=client_document,
            tipo_venta=payment_type,
            metodo_pago=payment_method,
            subtotal=subtotal_sin_itbis,
            itbis_porcentaje=itbis_porcentaje,
            itbis_monto=itbis_monto,
            descuento_porcentaje=discount_percentage,
            descuento_monto=discount_amount,
            total=total,
            total_a_pagar=total_a_pagar,
            montoinicial=Decimal('0.00'),
            efectivo_recibido=cash_received,
            cambio=change_amount,
            completada=True,
            fecha_venta=timezone.now(),
        )
        venta.save()

        print(f"=== VENTA CREADA ===")
        print(f"Factura: {venta.numero_factura}")
        print(f"Total: RD${venta.total:.2f}")

        # ============================================
        # PROCESAR DETALLES Y DESCONTAR STOCK
        # ============================================
        productos_para_cuenta = []
        for item_data in productos_validados:
            producto = item_data['producto']
            cantidad = item_data['cantidad']
            precio_unitario = item_data['precio_unitario']
            subtotal_item = item_data['subtotal']

            calculated_subtotal = precio_unitario * cantidad
            if abs(calculated_subtotal - subtotal_item) > Decimal('0.01'):
                subtotal_item = calculated_subtotal

            producto.cantidad -= cantidad
            producto.save(update_fields=['cantidad'])

            nombre_producto = getattr(producto, 'descripcion', getattr(
                producto, 'nombre', 'Producto Desconocido'))
            print(
                f"Stock actualizado: {nombre_producto} -{cantidad} (Nuevo stock: {producto.cantidad})")

            detalle = DetalleVenta(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal_item
            )
            detalle.save()

            productos_para_cuenta.append(
                f"{nombre_producto} x{cantidad} - RD${precio_unitario:.2f}")

        # ============================================
        # CREAR CUENTA POR COBRAR SI ES VENTA A CRÉDITO
        # ============================================
        if payment_type == 'credito' and cliente:
            try:
                from .models import CuentaPorCobrar
                from datetime import datetime

                # MODIFICACIÓN: leer fecha del input del formulario
                fecha_vencimiento_str = data.get('fecha_vencimiento')
                if fecha_vencimiento_str:
                    fecha_vencimiento = datetime.strptime(
                        fecha_vencimiento_str, '%Y-%m-%d').date()
                else:
                    # fallback: 30 días si por alguna razón no llega la fecha
                    fecha_vencimiento = timezone.now().date() + timezone.timedelta(days=30)

                productos_str = "\n".join(productos_para_cuenta)

                cuenta_por_cobrar = CuentaPorCobrar(
                    venta=venta,
                    cliente=cliente,
                    monto_total=total,
                    monto_pagado=Decimal('0.00'),
                    fecha_vencimiento=fecha_vencimiento,
                    productos=productos_str,
                    estado='pendiente',
                    observaciones=f"""Venta a crédito - Factura: {venta.numero_factura}
Cliente: {cliente.full_name}
Productos:
{productos_str}"""
                )
                cuenta_por_cobrar.save()

                print(f"Cuenta por cobrar creada: {cuenta_por_cobrar.id}")
                print(f"Fecha vencimiento: {fecha_vencimiento}")
                print(f"Monto total: RD${total:.2f}")

            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'success': False, 'message': f'Error al crear cuenta por cobrar: {str(e)}'})

        # ============================================
        # GENERAR Y ENVIAR PDF POR CORREO
        # ============================================
        try:
            from django.core.mail import EmailMessage
            from django.conf import settings

            email_configured = hasattr(
                settings, 'EMAIL_HOST') and settings.EMAIL_HOST

            if email_configured:
                recipient_list = []

                if user.email:
                    recipient_list.append(user.email)

                if payment_type == 'credito' and cliente and hasattr(cliente, 'email') and cliente.email:
                    recipient_list.append(cliente.email)

                recipient_list.append('superbestiard16@gmail.com')
                recipient_list = list(set(recipient_list))

                if recipient_list:
                    try:
                        pdf_buffer = generar_pdf_venta(venta)

                        subject = f'Factura de Venta - {venta.numero_factura}'
                        message = f'''
Se ha procesado una nueva venta en el sistema.

Detalles de la venta:
- Número de Factura: {venta.numero_factura}
- Cliente: {client_name if client_name else cliente.full_name if cliente else "N/A"}
- Documento: {client_document if client_document else cliente.identification_number if cliente else "N/A"}
- Tipo de Venta: {payment_type.title()}
- Método de Pago: {payment_method.title()}
- Subtotal: RD${subtotal_sin_itbis:.2f}
- ITBIS ({itbis_porcentaje}%): RD${itbis_monto:.2f}
- Descuento: {discount_percentage}% (RD${discount_amount:.2f})
- Total: RD${total:.2f}
- Fecha: {venta.fecha_venta.strftime("%d/%m/%Y %H:%M")}
- Vendedor: {user.get_full_name() or user.username}

Se adjunta el comprobante en PDF.

Saludos,
Sistema de Ventas - Super Bestia
'''
                        email = EmailMessage(
                            subject=subject,
                            body=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=recipient_list,
                        )
                        email.attach(
                            filename=f'factura_{venta.numero_factura}.pdf',
                            content=pdf_buffer.getvalue(),
                            mimetype='application/pdf'
                        )
                        email.send(fail_silently=False)
                        print(f"✓ Correo enviado a {recipient_list}")

                    except ImportError as e:
                        print(
                            f"✗ Error: generar_pdf_venta no encontrada: {str(e)}")
                    except Exception as e:
                        print(f"✗ Error al enviar correo: {str(e)}")
                else:
                    print("ℹ️ No hay destinatarios para enviar el correo")
            else:
                print("ℹ️ Configuración de correo no encontrada en settings.py")

        except Exception as e:
            print(f"⚠️ Advertencia: Error en envío de correo: {str(e)}")

        # ============================================
        # RESPUESTA EXITOSA
        # ============================================
        return JsonResponse({
            'success': True,
            'message': 'Venta procesada correctamente',
            'venta_id': venta.id,
            'numero_factura': venta.numero_factura,
            'descuento_aplicado': user.is_superuser,
            'detalles': {
                'subtotal_sin_itbis': float(venta.subtotal),
                'itbis_porcentaje': float(venta.itbis_porcentaje),
                'itbis_monto': float(venta.itbis_monto),
                'subtotal_con_itbis': float(venta.subtotal + venta.itbis_monto),
                'descuento_porcentaje': float(venta.descuento_porcentaje),
                'descuento_monto': float(venta.descuento_monto),
                'total': float(venta.total),
                'total_a_pagar': float(venta.total_a_pagar),
                'efectivo_recibido': float(venta.efectivo_recibido),
                'cambio': float(venta.cambio),
                'items_count': len(sale_items)
            }
        })

    except Exception as e:
        transaction.set_rollback(True)
        import traceback
        error_traceback = traceback.format_exc()
        print(f"✗ Error completo: {error_traceback}")
        return JsonResponse({
            'success': False,
            'message': f'Error al procesar la venta: {str(e)}',
            'error_type': str(type(e).__name__),
            'traceback': error_traceback if settings.DEBUG else None
        })

# ========================================================================================
# =========================== FUNCIÓN PARA GENERAR PDF (SIN CAMBIOS) ========================
# ============================================================================================


def generar_pdf_venta(venta):
    """Genera un PDF con los detalles de la venta"""
    buffer = BytesIO()

    # Crear el documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )

    # Estilos
    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    estilo_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        leading=12
    )

    estilo_negrita = ParagraphStyle(
        'Bold',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        fontName='Helvetica-Bold'
    )

    # Contenido del PDF
    contenido = []

    # Título
    contenido.append(Paragraph("FACTURA DE VENTA", estilo_titulo))
    contenido.append(Spacer(1, 20))

    # Información de la empresa
    info_empresa = [
        ["<b>SUPER BESTIA</b>", f"<b>Factura No:</b> {venta.numero_factura}"],
        ["<b>Venta de Repuestos para Motos</b>",
            f"<b>Fecha:</b> {venta.fecha_venta.strftime('%d/%m/%Y %H:%M')}"],
        ["Tel: (809) 123-4567",
         f"<b>Vendedor:</b> {venta.vendedor.get_full_name() or venta.vendedor.username}"],
        ["Email: info@superbestia.com", ""]
    ]

    tabla_info = Table(info_empresa, colWidths=[3*inch, 3*inch])
    tabla_info.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    contenido.append(tabla_info)
    contenido.append(Spacer(1, 20))

    # Información del cliente
    contenido.append(
        Paragraph("<b>INFORMACIÓN DEL CLIENTE</b>", estilo_negrita))
    cliente_nombre = venta.cliente_nombre or (
        venta.cliente.full_name if venta.cliente else "Cliente General")
    cliente_doc = venta.cliente_documento or (
        venta.cliente.identification_number if venta.cliente else "N/A")

    info_cliente = [
        ["Nombre:", cliente_nombre],
        ["Documento:", cliente_doc],
        ["Tipo de Venta:", venta.tipo_venta.title()],
        ["Método de Pago:", venta.metodo_pago.title()]
    ]

    tabla_cliente = Table(info_cliente, colWidths=[1.5*inch, 4.5*inch])
    tabla_cliente.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    contenido.append(tabla_cliente)
    contenido.append(Spacer(1, 20))

    # Detalles de los productos
    contenido.append(Paragraph("<b>DETALLES DE LA VENTA</b>", estilo_negrita))

    # Encabezados de la tabla de productos
    encabezados = ['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']
    datos_productos = [encabezados]

    # Obtener detalles de la venta
    detalles = venta.detalles.all()
    for detalle in detalles:
        nombre_producto = detalle.producto.descripcion if hasattr(
            detalle.producto, 'descripcion') else str(detalle.producto)
        if len(nombre_producto) > 40:
            nombre_producto = nombre_producto[:37] + "..."

        fila = [
            nombre_producto,
            str(detalle.cantidad),
            f"RD${detalle.precio_unitario:.2f}",
            f"RD${detalle.subtotal:.2f}"
        ]
        datos_productos.append(fila)

    tabla_productos = Table(datos_productos, colWidths=[
                            3*inch, 1*inch, 1.2*inch, 1.2*inch])
    tabla_productos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    contenido.append(tabla_productos)
    contenido.append(Spacer(1, 20))

    # Resumen financiero
    contenido.append(Paragraph("<b>RESUMEN FINANCIERO</b>", estilo_negrita))

    resumen = [
        ["Subtotal (sin ITBIS):", f"RD${venta.subtotal:.2f}"],
        [f"ITBIS ({venta.itbis_porcentaje}%):", f"RD${venta.itbis_monto:.2f}"],
        ["Subtotal (con ITBIS):",
         f"RD${venta.subtotal + venta.itbis_monto:.2f}"],
        [f"Descuento ({venta.descuento_porcentaje}%):",
         f"RD${venta.descuento_monto:.2f}"],
        ["<b>TOTAL:</b>", f"<b>RD${venta.total:.2f}</b>"]
    ]

    if venta.tipo_venta == 'contado' and venta.metodo_pago == 'efectivo':
        resumen.extend([
            ["Efectivo Recibido:", f"RD${venta.efectivo_recibido:.2f}"],
            ["<b>Cambio:</b>", f"<b>RD${venta.cambio:.2f}</b>"]
        ])

    tabla_resumen = Table(resumen, colWidths=[3*inch, 2*inch])
    tabla_resumen.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
    ]))

    contenido.append(tabla_resumen)
    contenido.append(Spacer(1, 30))

    # Mensaje de agradecimiento
    contenido.append(Paragraph("¡Gracias por su compra!", estilo_negrita))
    contenido.append(Paragraph(
        "Para reclamos o devoluciones, presente esta factura.", estilo_normal))

    # Nota sobre descuento (solo si fue aplicado)
    if venta.descuento_porcentaje > 0:
        contenido.append(Spacer(1, 10))
        contenido.append(Paragraph(
            f"<i>Nota: Se aplicó un descuento del {venta.descuento_porcentaje}% autorizado por el administrador.</i>", estilo_normal))

    # Construir el PDF
    doc.build(contenido)

    # Obtener el valor del buffer
    pdf = buffer.getvalue()
    buffer.close()

    return BytesIO(pdf)

# =========================================================================================
# ============================ Vista para renderizar el comprobante de venta ============================
# =========================================================================================


@login_required
def comprobante_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = venta.detalles.all()
    total_articulos = sum(detalle.cantidad for detalle in detalles)

    # Obtener fecha de vencimiento si es venta a crédito
    fecha_vencimiento = None
    if venta.tipo_venta == 'credito' and hasattr(venta, 'cuenta_por_cobrar'):
        fecha_vencimiento = venta.cuenta_por_cobrar.fecha_vencimiento

    # Calcular los totales correctamente
    subtotal_sin_itbis = venta.subtotal
    itbis_monto = venta.itbis_monto
    subtotal_con_itbis = subtotal_sin_itbis + itbis_monto
    descuento_monto = venta.descuento_monto
    total_final = venta.total

    return render(request, 'facturacion/comprobante_venta.html', {
        'venta': venta,
        'detalles': detalles,
        'total_articulos': total_articulos,
        'subtotal_sin_itbis': subtotal_sin_itbis,
        'subtotal_con_itbis': subtotal_con_itbis,
        'itbis_monto': itbis_monto,
        'descuento_monto': descuento_monto,
        'total_final': total_final,
        'fecha_vencimiento': fecha_vencimiento,  # pasar al template
        'now': timezone.now().strftime('%d/%m/%Y')
    })


@login_required
def buscar_productos(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'success': False, 'message': 'Término de búsqueda vacío'})
    try:
        productos = EntradaProducto.objects.filter(
            Q(activo=True) & Q(cantidad__gt=0) & (
                Q(descripcion__icontains=query) |
                Q(codigo_producto__icontains=query) |
                Q(marca__icontains=query)
            )
        ).select_related('proveedor')[:20]
        productos_data = []
        for producto in productos:
            productos_data.append({
                'id': producto.id,
                'codigo_producto': producto.codigo_producto,
                'descripcion': producto.descripcion,
                'precio': float(producto.precio),
                'precio_con_itbis': float(producto.precio_con_itbis) if producto.precio_con_itbis else 0.0,
                'precio_por_mayor': float(producto.precio_por_mayor) if producto.precio_por_mayor else 0.0,
                'precio_por_mayor_con_itbis': float(producto.precio_por_mayor_con_itbis) if producto.precio_por_mayor_con_itbis else 0.0,
                'cantidad': producto.cantidad,
                'imagen': producto.imagen.url if producto.imagen else '/static/image/default-product.png',
                # AGREGAR ESTOS CAMPOS:
                'compatibilidad': producto.compatibilidad or '',
                'marca': producto.marca or '',
                'color': producto.color or '',
            })
        return JsonResponse({
            'success': True,
            'productos': productos_data,
            'total': len(productos_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error en la búsqueda: {str(e)}'
        })


# Vista para ver los detalles de una venta
@login_required
def detalle_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Verificar que la venta pertenece al usuario actual
    if venta.caja.usuario != request.user:
        messages.error(request, 'No tienes permisos para ver esta venta.')
        return redirect('historial_ventas')

    return render(request, "facturacion/detalle_venta.html", {
        'venta': venta,
        'detalles': venta.detalles.all()
    })


@user_passes_test(is_superuser_or_usuario_normal, login_url='/')
@login_required
def listadecliente(request):
    return render(request, "facturacion/listadecliente.html")


@require_GET
def obtener_clientes(request):
    try:
        # Obtener todos los clientes activos
        clientes = Cliente.objects.filter(status=True).values(
            'id', 'full_name', 'identification_number',
            'address', 'primary_phone', 'secondary_phone',
            'credit_limit', 'fecha_registro'   # 👈 corregido
        )

        # Convertir a lista y formatear fechas
        clientes_list = list(clientes)
        for cliente in clientes_list:
            cliente['fecha_registro'] = cliente['fecha_registro'].isoformat()

        return JsonResponse({
            'success': True,
            'clientes': clientes_list
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener clientes: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["DELETE"])
@superuser_required  # 👈 Nuevo decorador agregado
def eliminar_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)

        # En lugar de eliminar físicamente, cambiamos el estado
        cliente.status = False
        cliente.save()

        return JsonResponse({
            'success': True,
            'message': 'Cliente eliminado exitosamente'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar cliente: {str(e)}'
        })


@csrf_exempt
@require_POST
@superuser_required  # 👈 Nuevo decorador agregado
def editar_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        data = json.loads(request.body)

        # Validar campos requeridos
        campos_requeridos = ['fullName',
                             'identificationNumber', 'address', 'primaryPhone']
        for campo in campos_requeridos:
            if campo not in data or not data[campo].strip():
                return JsonResponse({
                    'success': False,
                    'message': f'El campo {campo} es requerido'
                })

        # Verificar si ya existe otro cliente con el mismo número de identificación
        if Cliente.objects.filter(identification_number=data['identificationNumber']).exclude(id=cliente_id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Ya existe otro cliente con este número de identificación'
            })

        # Actualizar los datos del cliente
        cliente.full_name = data['fullName']
        cliente.identification_number = data['identificationNumber']
        cliente.address = data['address']
        cliente.primary_phone = data['primaryPhone']
        cliente.secondary_phone = data.get('secondaryPhone', '')

        # Procesar el límite de crédito
        credit_limit = data.get('creditLimit', '0')
        try:
            credit_limit = Decimal(credit_limit)
        except (InvalidOperation, ValueError):
            credit_limit = Decimal('0')

        if credit_limit < Decimal('0') or credit_limit > Decimal('99999999.99'):
            return JsonResponse({
                'success': False,
                'message': 'El límite de crédito debe estar entre RD$ 0.00 y RD$ 99,999,999.99'
            })
        cliente.credit_limit = credit_limit

        cliente.save()

        return JsonResponse({
            'success': True,
            'message': 'Cliente actualizado exitosamente'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al editar cliente: {str(e)}'
        })


@user_passes_test(is_superuser_or_usuario_normal, login_url='/')
@login_required
def registrodecliente(request):
    return render(request, "facturacion/registrodecliente.html")


@csrf_exempt
@require_POST
def guardar_cliente(request):
    try:
        # Parsear los datos JSON recibidos
        data = json.loads(request.body)

        # Validar campos requeridos
        campos_requeridos = ['fullName',
                             'identificationNumber', 'address', 'primaryPhone']
        for campo in campos_requeridos:
            if campo not in data or not data[campo].strip():
                return JsonResponse({
                    'success': False,
                    'message': f'El campo {campo} es requerido'
                })

        # Verificar si ya existe un cliente con el mismo número de identificación
        if Cliente.objects.filter(identification_number=data['identificationNumber']).exists():
            return JsonResponse({
                'success': False,
                'message': 'Ya existe un cliente con este número de identificación'
            })

        # Procesar el límite de crédito (valor por defecto 0 si no se proporciona)
        credit_limit = data.get('creditLimit', '0')
        try:
            credit_limit = Decimal(credit_limit)
        except (InvalidOperation, ValueError):
            credit_limit = Decimal('0')

        if credit_limit < Decimal('0') or credit_limit > Decimal('99999999.99'):
            return JsonResponse({
                'success': False,
                'message': 'El límite de crédito debe estar entre RD$ 0.00 y RD$ 99,999,999.99'
            })

        # Crear y guardar el nuevo cliente
        cliente = Cliente(
            full_name=data['fullName'],
            identification_number=data['identificationNumber'],
            address=data['address'],
            primary_phone=data['primaryPhone'],
            secondary_phone=data.get('secondaryPhone', ''),
            credit_limit=credit_limit
        )
        cliente.save()

        return JsonResponse({
            'success': True,
            'message': 'Cliente registrado exitosamente',
            'client_id': cliente.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error en el servidor: {str(e)}'
        })


@csrf_exempt
def obtener_datos_entrada(request, entrada_id):
    """Obtiene datos de una entrada existente para autocompletar el formulario"""
    if request.method == 'GET':
        try:
            entrada = EntradaProducto.objects.get(id=entrada_id)
            data = {
                'success': True,
                'entrada': {
                    'marca': entrada.marca,
                    'compatibilidad': entrada.compatibilidad or '',
                    'color': entrada.color or '',
                    'costo': float(entrada.costo),
                    'precio': float(entrada.precio),
                    'precio_por_mayor': float(entrada.precio_por_mayor) if entrada.precio_por_mayor else 0,
                    'porcentaje_itbis': float(entrada.porcentaje_itbis),
                    'precio_con_itbis': float(entrada.precio_con_itbis) if entrada.precio_con_itbis else 0,
                    'precio_por_mayor_con_itbis': float(entrada.precio_por_mayor_con_itbis) if entrada.precio_por_mayor_con_itbis else 0,
                    'descripcion': entrada.descripcion,
                    'imagen_url': entrada.imagen.url if entrada.imagen else None,
                }
            }
            return JsonResponse(data)
        except EntradaProducto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Entrada no encontrada'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# Vista para obtener productos disponibles (plantillas)
@csrf_exempt
def obtener_productos_disponibles(request):
    """Obtiene plantillas de productos para el dropdown"""
    try:
        plantillas = EntradaProducto.objects.filter(
            es_producto_base=True,
            activo=True
        ).order_by('descripcion', 'marca')
        plantillas_data = []
        for plantilla in plantillas:
            plantillas_data.append({
                'id': plantilla.id,
                'texto_completo': f"{plantilla.descripcion} - {plantilla.get_marca_display()}",
                'descripcion': plantilla.descripcion,
                'marca': plantilla.marca,
                'marca_display': plantilla.get_marca_display(),
                'compatibilidad': plantilla.compatibilidad or '',
                'color': plantilla.color or 'negro',
                'costo': float(plantilla.costo),
                'precio': float(plantilla.precio),
                'precio_por_mayor': float(plantilla.precio_por_mayor) if plantilla.precio_por_mayor else 0,
            })
        return JsonResponse({'success': True, 'plantillas': plantillas_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Vista para obtener datos de una plantilla
@csrf_exempt
def obtener_datos_plantilla(request, plantilla_id):
    """Obtiene datos de una plantilla para autocompletar campos"""
    if request.method == 'GET':
        try:
            plantilla = EntradaProducto.objects.get(
                id=plantilla_id, es_producto_base=True, activo=True)
            data = {
                'success': True,
                'data': {
                    'marca': plantilla.marca,
                    'compatibilidad': plantilla.compatibilidad or '',
                    'color': plantilla.color or '',
                    'costo': float(plantilla.costo),
                    'precio': float(plantilla.precio),
                    'precio_por_mayor': float(plantilla.precio_por_mayor) if plantilla.precio_por_mayor else 0,
                    'porcentaje_itbis': float(plantilla.porcentaje_itbis),
                }
            }
            return JsonResponse(data)
        except EntradaProducto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Plantilla no encontrada'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# Vista para agregar una nueva plantilla de producto


@csrf_exempt
@require_POST
def agregar_nuevo_producto(request):
    """Crea una nueva plantilla de producto con datos mínimos para el modal"""
    try:
        nombre = request.POST.get('newProductName', '').strip()
        marca = request.POST.get('newProductBrand', '').strip()

        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre del producto es requerido'})
        if not marca:
            return JsonResponse({'success': False, 'error': 'La marca es requerida'})

        existe = EntradaProducto.objects.filter(
            descripcion__iexact=nombre,
            marca=marca,
            es_producto_base=True,
            activo=True
        ).exists()

        if existe:
            return JsonResponse({
                'success': False,
                'error': 'Ya existe una plantilla con este nombre y marca'
            })

        # BUSCAR O CREAR PROVEEDOR CORRECTAMENTE
        try:
            proveedor_default = Proveedor.objects.filter(activo=True).first()
            if not proveedor_default:
                # CREAR PROVEEDOR CON TODOS LOS CAMPOS OBLIGATORIOS
                proveedor_default = Proveedor.objects.create(
                    nombre_empresa="Proveedor General",
                    rnc="00000000000",
                    nombre_contacto="Contacto General",
                    email="proveedor@general.com",
                    telefono="000-000-0000",
                    pais="DO",
                    ciudad="Ciudad General",
                    direccion="Dirección general",
                    activo=True
                )
        except Exception as e:
            print(f"Error al crear proveedor: {e}")
            proveedor_default = Proveedor.objects.filter(activo=True).first()
            if not proveedor_default:
                return JsonResponse({
                    'success': False,
                    'error': 'No hay proveedores disponibles y no se pudo crear uno automáticamente.'
                })

        # Generar número de factura único usando timestamp
        import datetime
        timestamp = int(datetime.datetime.now().timestamp())

        # Crear la nueva plantilla
        nueva_plantilla = EntradaProducto(
            numero_factura=f"PLANTILLA-{timestamp}",
            fecha_entrada=timezone.now().date(),
            proveedor=proveedor_default,
            descripcion=nombre,
            marca=marca,
            compatibilidad=nombre,
            color="negro",
            cantidad=1,
            cantidad_minima=2,
            costo=Decimal('0.00'),
            precio=Decimal('0.00'),
            porcentaje_itbis=Decimal('18.00'),
            observaciones="Plantilla creada mediante modal rápido",
            activo=True,
            es_producto_base=True
        )

        nueva_plantilla.save()

        return JsonResponse({
            'success': True,
            'plantilla_id': nueva_plantilla.id,
            'nombre_producto': nueva_plantilla.descripcion,
            'marca': nueva_plantilla.get_marca_display(),
            'marca_valor': nueva_plantilla.marca,
            'mensaje': 'Plantilla creada exitosamente.'
        })

    except Exception as e:
        # Mejor logging del error
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error completo en agregar_nuevo_producto:\n{error_trace}")
        return JsonResponse({
            'success': False,
            'error': f'Error al crear la plantilla: {str(e)}'
        })


@user_passes_test(is_superuser_or_almacen, login_url='/')
@csrf_exempt
def entrada(request):
    """Vista principal para registro de entradas de productos (inventario)"""
    if request.method == 'POST':
        try:
            print("Datos POST recibidos:", request.POST)

            # Obtener datos del formulario
            numero_factura = request.POST.get('numero_factura', '').strip()
            fecha_entrada = request.POST.get('fecha_entrada', '')
            proveedor_id = request.POST.get('proveedor', '')
            ncf = request.POST.get('ncf', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            marca = request.POST.get('marca', '').strip()
            compatibilidad = request.POST.get('compatibilidad', '').strip()
            color = request.POST.get('color', '')
            imagen = request.FILES.get('imagen')
            codigo_producto = request.POST.get('codigo_producto', '').strip()
            producto_existente_id = request.POST.get(
                'producto_existente_id', '').strip()

            # Manejar valores numéricos CON Decimal
            try:
                cantidad = int(request.POST.get('cantidad', 1))
            except (ValueError, TypeError):
                cantidad = 1

            try:
                costo = Decimal(str(request.POST.get('costo', 0)))
            except (ValueError, TypeError):
                costo = Decimal('0.00')

            try:
                precio = Decimal(str(request.POST.get('precio', 0)))
            except (ValueError, TypeError):
                precio = Decimal('0.00')

            try:
                precio_por_mayor_val = request.POST.get('precio_por_mayor')
                precio_por_mayor = Decimal(
                    str(precio_por_mayor_val)) if precio_por_mayor_val else None
            except (ValueError, TypeError):
                precio_por_mayor = None

            try:
                porcentaje_itbis = Decimal(
                    str(request.POST.get('porcentaje_itbis', 18.00)))
            except (ValueError, TypeError):
                porcentaje_itbis = Decimal('18.00')

            # Validar campos requeridos
            required_fields = [
                ('numero_factura', numero_factura, 'Número de factura'),
                ('fecha_entrada', fecha_entrada, 'Fecha de entrada'),
                ('proveedor', proveedor_id, 'Proveedor'),
                ('descripcion', descripcion, 'Descripción'),
                ('marca', marca, 'Marca'),
                ('costo', costo, 'Costo'),
                ('precio', precio, 'Precio')
            ]

            for field_name, field_value, field_display in required_fields:
                if not field_value:
                    error_msg = f'{field_display} es requerido'
                    messages.error(request, error_msg)
                    return JsonResponse({'success': False, 'error': error_msg})

            if cantidad <= 0:
                error_msg = 'La cantidad debe ser mayor a 0'
                messages.error(request, error_msg)
                return JsonResponse({'success': False, 'error': error_msg})

            if costo <= Decimal('0'):
                error_msg = 'El costo debe ser mayor a 0'
                messages.error(request, error_msg)
                return JsonResponse({'success': False, 'error': error_msg})

            if precio <= Decimal('0'):
                error_msg = 'El precio debe ser mayor a 0'
                messages.error(request, error_msg)
                return JsonResponse({'success': False, 'error': error_msg})

            # Obtener el proveedor
            try:
                proveedor = Proveedor.objects.get(id=proveedor_id, activo=True)
            except Proveedor.DoesNotExist:
                error_msg = 'Proveedor no válido'
                messages.error(request, error_msg)
                return JsonResponse({'success': False, 'error': error_msg})

            # CALCULAR PORCENTAJES EN EL BACKEND
            if costo > 0:
                porcentaje_minorista_real = (
                    (precio - costo) / costo * 100).quantize(Decimal('0.01'))
            else:
                porcentaje_minorista_real = Decimal('0.00')

            if precio_por_mayor and costo > 0:
                porcentaje_mayor_real = (
                    (precio_por_mayor - costo) / costo * 100).quantize(Decimal('0.01'))
            else:
                porcentaje_mayor_real = None

            # VERIFICAR SI EL PRODUCTO EXISTE - PRIORIDAD POR producto_existente_id
            producto_existente = None

            # 1. Buscar por producto_existente_id (si viene del formulario)
            if producto_existente_id:
                try:
                    producto_existente = EntradaProducto.objects.get(
                        id=producto_existente_id, activo=True)
                    print(
                        f"Producto encontrado por ID: {producto_existente_id}")
                except EntradaProducto.DoesNotExist:
                    print(
                        f"Producto no encontrado por ID: {producto_existente_id}")
                    # Si no se encuentra por ID, tratar como producto nuevo
                    producto_existente_id = ''

            # 2. Si no se encontró por ID, intentar por código de producto
            if not producto_existente and codigo_producto:
                try:
                    producto_existente = EntradaProducto.objects.get(
                        codigo_producto=codigo_producto, activo=True)
                    print(f"Producto encontrado por código: {codigo_producto}")
                except EntradaProducto.DoesNotExist:
                    print(
                        f"Producto no encontrado por código: {codigo_producto}")

            # SI EL PRODUCTO EXISTE, ACTUALIZARLO
            if producto_existente:
                print(
                    f"Actualizando producto existente: {producto_existente.codigo_producto}")

                # Si es un producto base, convertirlo a producto de inventario normal
                if producto_existente.es_producto_base:
                    producto_existente.es_producto_base = False
                    producto_existente.observaciones = "Convertido de plantilla a producto de inventario"

                # Actualizar los campos del producto existente
                producto_existente.numero_factura = numero_factura
                producto_existente.fecha_entrada = fecha_entrada
                producto_existente.proveedor = proveedor
                producto_existente.ncf = ncf
                producto_existente.descripcion = descripcion
                producto_existente.marca = marca
                producto_existente.compatibilidad = compatibilidad
                producto_existente.color = color
                producto_existente.cantidad += cantidad
                producto_existente.costo = costo
                producto_existente.precio = precio
                producto_existente.precio_por_mayor = precio_por_mayor
                producto_existente.porcentaje_itbis = porcentaje_itbis
                producto_existente.porcentaje_minorista = porcentaje_minorista_real
                producto_existente.porcentaje_mayor = porcentaje_mayor_real

                # Si se sube una nueva imagen, actualizarla
                if imagen:
                    producto_existente.imagen = imagen

                producto_existente.save()

                messages.success(
                    request, f'Producto actualizado exitosamente - Código: {producto_existente.codigo_producto}')
                return JsonResponse({
                    'success': True,
                    'message': f'Producto actualizado exitosamente - Código: {producto_existente.codigo_producto}',
                    'producto_actualizado': True,
                    'codigo_producto': producto_existente.codigo_producto,
                    'porcentajes_calculados': {
                        'minorista': float(porcentaje_minorista_real),
                        'mayor': float(porcentaje_mayor_real) if porcentaje_mayor_real else None
                    }
                })

            # SI EL PRODUCTO NO EXISTE, CREAR UNO NUEVO
            else:
                print("Creando nuevo producto desde formulario principal")

                # Crear la entrada de producto como producto normal (no base)
                entrada_producto = EntradaProducto(
                    numero_factura=numero_factura,
                    fecha_entrada=fecha_entrada,
                    proveedor=proveedor,
                    ncf=ncf,
                    descripcion=descripcion,
                    marca=marca,
                    compatibilidad=compatibilidad,
                    color=color,
                    cantidad=cantidad,
                    cantidad_minima=2,
                    costo=costo,
                    precio=precio,
                    precio_por_mayor=precio_por_mayor,
                    porcentaje_itbis=porcentaje_itbis,
                    imagen=imagen,
                    porcentaje_minorista=porcentaje_minorista_real,
                    porcentaje_mayor=porcentaje_mayor_real,
                    es_producto_base=False,  # Asegurar que no sea producto base
                )
                entrada_producto.save()

                messages.success(
                    request, f'Producto registrado exitosamente - Código: {entrada_producto.codigo_producto}')
                return JsonResponse({
                    'success': True,
                    'message': f'Producto registrado exitosamente - Código: {entrada_producto.codigo_producto}',
                    'producto_actualizado': False,
                    'codigo_producto': entrada_producto.codigo_producto,
                    'porcentajes_calculados': {
                        'minorista': float(porcentaje_minorista_real),
                        'mayor': float(porcentaje_mayor_real) if porcentaje_mayor_real else None
                    }
                })

        except Exception as e:
            error_msg = f'Error al procesar el producto: {str(e)}'
            print(f"Error completo: {e}")
            messages.error(request, error_msg)
            return JsonResponse({'success': False, 'error': error_msg})

    # GET request - mostrar el formulario
    proveedores = Proveedor.objects.filter(activo=True)
    fecha_actual = timezone.now().date().isoformat()
    return render(request, 'facturacion/entrada.html', {
        'proveedores': proveedores,
        'fecha_actual': fecha_actual
    })


@csrf_exempt
def buscar_productos_similares(request):
    """Busca productos similares para autocompletar"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()

        if not query or len(query) < 2:
            return JsonResponse({'success': True, 'productos': []})

        try:
            # Buscar productos por código, descripción o marca
            productos = EntradaProducto.objects.filter(
                Q(codigo_producto__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(marca__icontains=query),
                activo=True
            ).distinct().order_by('-fecha_actualizacion', 'marca', 'descripcion')[:15]

            resultados = []
            for producto in productos:
                # Determinar el tipo de producto
                tipo = "Base" if producto.es_producto_base else "Inventario"

                resultados.append({
                    'id': producto.id,
                    'codigo_producto': producto.codigo_producto,
                    'descripcion': producto.descripcion,
                    'marca': producto.marca,
                    'marca_display': producto.get_marca_display(),
                    'compatibilidad': producto.compatibilidad or '',
                    'color': producto.color or '',
                    'cantidad': producto.cantidad,
                    'costo': float(producto.costo) if producto.costo else 0.0,
                    'precio': float(producto.precio) if producto.precio else 0.0,
                    'precio_por_mayor': float(producto.precio_por_mayor) if producto.precio_por_mayor else 0.0,
                    'porcentaje_itbis': float(producto.porcentaje_itbis) if producto.porcentaje_itbis else 18.0,
                    'es_producto_base': producto.es_producto_base,
                    'tipo': tipo,
                    'fecha_actualizacion': producto.fecha_actualizacion.strftime('%d/%m/%Y') if producto.fecha_actualizacion else ''
                })

            return JsonResponse({'success': True, 'productos': resultados})

        except Exception as e:
            print(f"Error en buscar_productos_similares: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@require_GET
@login_required
def generar_comprobante_pdf(request, comprobante_id):
    try:
        comprobante = get_object_or_404(ComprobantePago, id=comprobante_id)

        # Crear respuesta HTTP con tipo PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="comprobante_{comprobante.numero_comprobante}.pdf"'

        # Configurar el PDF en tamaño A4 (595 x 842 puntos)
        width, height = A4
        p = canvas.Canvas(response, pagesize=A4)

        # Ruta absoluta del logo en STATIC_ROOT
        logo_path = os.path.join(settings.STATIC_ROOT,
                                 'image', 'favicon12.ico')

        # Verifica si el archivo existe
        if not os.path.exists(logo_path):
            raise FileNotFoundError(
                f"No se encontró el logo en la ruta: {logo_path}")

        # Márgenes y posiciones iniciales
        margin_left = 50
        y_position = height - 50  # Iniciar 50 puntos desde el borde superior
        line_height = 14
        small_line_height = 10

        # Función para centrar texto
        def draw_centered_text(text, y, font_size=12, bold=False):
            if bold:
                p.setFont("Helvetica-Bold", font_size)
            else:
                p.setFont("Helvetica", font_size)
            text_width = p.stringWidth(text, "Helvetica", font_size)
            x = (width - text_width) / 2
            p.drawString(x, y, text)
            return y - line_height

        # Función para texto alineado a la izquierda
        def draw_left_text(text, y, font_size=10, bold=False):
            if bold:
                p.setFont("Helvetica-Bold", font_size)
            else:
                p.setFont("Helvetica", font_size)
            p.drawString(margin_left, y, text)
            return y - line_height

        # Insertar logo en el encabezado
        logo_width = 150
        logo_height = 80
        logo_x = (width - logo_width) / 2
        logo_y = y_position - logo_height
        p.drawImage(logo_path, logo_x, logo_y, width=logo_width,
                    height=logo_height, preserveAspectRatio=True)
        y_position = logo_y - 20  # Espacio después del logo

        # Encabezado del comprobante
        y_position = draw_centered_text(
            "REPUESTO SUPER BESTIA", y_position, 16, True)
        y_position = draw_centered_text(
            "COMPROBANTE DE PAGO", y_position, 14, True)
        y_position -= line_height / 2

        # Línea separadora
        p.line(margin_left, y_position, width - margin_left, y_position)
        y_position -= line_height

        # Información del comprobante
        y_position = draw_left_text(
            f"Comprobante: {comprobante.numero_comprobante}", y_position, 10)
        y_position = draw_left_text(
            f"Fecha: {comprobante.fecha_emision.strftime('%d/%m/%Y %H:%M')}", y_position, 10)
        y_position = draw_left_text(
            f"Cliente: {comprobante.cliente.full_name}", y_position, 10)
        if comprobante.cuenta.venta:
            y_position = draw_left_text(
                f"Factura: {comprobante.cuenta.venta.numero_factura}", y_position, 10)
        y_position -= line_height / 2

        # Línea separadora
        p.line(margin_left, y_position, width - margin_left, y_position)
        y_position -= line_height

        # Información del pago
        y_position = draw_centered_text(
            "DETALLE DEL PAGO", y_position, 12, True)
        y_position -= small_line_height
        y_position = draw_left_text(
            f"Monto Pagado: RD$ {comprobante.pago.monto:,.2f}", y_position, 10, True)
        y_position = draw_left_text(
            f"Método: {comprobante.pago.get_metodo_pago_display()}", y_position, 10)
        if comprobante.pago.referencia:
            y_position = draw_left_text(
                f"Referencia: {comprobante.pago.referencia}", y_position, 9)
        y_position -= line_height / 2

        # Línea separadora
        p.line(margin_left, y_position, width - margin_left, y_position)
        y_position -= line_height

        # Cálculo de montos
        monto_total_original = Decimal(
            str(comprobante.cuenta.venta.total_a_pagar))
        monto_total_con_itbis = comprobante.cuenta.venta.total if comprobante.cuenta.venta else comprobante.cuenta.monto_total
        saldo_pendiente = monto_total_original - \
            Decimal(str(comprobante.cuenta.monto_pagado))

        # Resumen de cuenta
        y_position = draw_centered_text(
            "RESUMEN DE CUENTA", y_position, 12, True)
        y_position -= small_line_height
        y_position = draw_left_text(
            f"Monto Original: RD$ {monto_total_original:,.2f}", y_position, 10)
        y_position = draw_left_text(
            f"Pagado Acumulado: RD$ {comprobante.cuenta.monto_pagado:,.2f}", y_position, 10)
        y_position = draw_left_text(
            f"Saldo Pendiente: RD$ {saldo_pendiente:,.2f}", y_position, 10, True)
        y_position -= line_height

        # Línea separadora
        p.line(margin_left, y_position, width - margin_left, y_position)
        y_position -= line_height * 2

        # Sección de firmas
        y_position = draw_centered_text(
            "FIRMA DEL CLIENTE", y_position, 10, True)
        y_position -= small_line_height
        p.line(margin_left + 40, y_position,
               width - margin_left - 40, y_position)
        y_position -= line_height * 1.2
        y_position = draw_left_text(
            "Cédula: _________________________", y_position, 9)
        y_position -= line_height * 1.5

        y_position = draw_centered_text(
            "FIRMA DE LA EMPRESA", y_position, 10, True)
        y_position -= small_line_height
        p.line(margin_left + 40, y_position,
               width - margin_left - 40, y_position)
        y_position -= line_height

        # Pie de página
        y_position = draw_centered_text(
            "REPUESTO SUPER BESTIA", y_position, 10, True)
        y_position -= line_height
        y_position = draw_centered_text(
            "¡Gracias por su pago!", y_position, 12, True)
        y_position -= small_line_height
        y_position = draw_centered_text("Tel: (849) 353-5344", y_position, 9)
        y_position = draw_centered_text(
            f"Ref: {comprobante.numero_comprobante}", y_position, 8)

        # Finalizar el PDF
        p.showPage()
        p.save()
        return response

    except FileNotFoundError as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}. Asegúrate de que el logo esté en la carpeta correcta y de que hayas ejecutado `collectstatic`.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al generar comprobante: {str(e)}'
        })


@require_POST
@login_required
def eliminar_cuenta_pagada(request, cuenta_id):
    if request.method == 'POST':
        try:
            cuenta = get_object_or_404(CuentaPorCobrar, id=cuenta_id)

            # Verificar que la cuenta esté pagada
            if cuenta.estado != 'pagada':
                return JsonResponse({
                    'success': False,
                    'message': 'Solo se pueden eliminar cuentas que estén completamente pagadas'
                })

            # Verificar que no esté ya eliminada
            if cuenta.eliminada:
                return JsonResponse({
                    'success': False,
                    'message': 'Esta cuenta ya ha sido eliminada'
                })

            # Realizar soft delete
            cuenta.eliminar_cuenta()

            return JsonResponse({
                'success': True,
                'message': f'Cuenta #{cuenta.id} - Factura {cuenta.venta.numero_factura} eliminada exitosamente'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar cuenta: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Método no permitido'})


# =========================================================================================
#                          ===== VISTA PARA LISTAR COMPROBANTES =====
# =========================================================================================
@login_required
def lista_comprobantes(request):
    comprobantes = ComprobantePago.objects.select_related(
        'pago', 'cuenta', 'cliente'
    ).order_by('-fecha_emision')

    # Filtros opcionales
    search = request.GET.get('search', '')
    if search:
        comprobantes = comprobantes.filter(
            Q(numero_comprobante__icontains=search) |
            Q(cliente__full_name__icontains=search) |
            Q(cuenta__venta__numero_factura__icontains=search)
        )

    context = {
        'comprobantes': comprobantes,
        'search': search,
    }

    return render(request, 'facturacion/lista_comprobantes.html', context)


ventas


@user_passes_test(is_superuser_or_usuario_normal, login_url='/')
@login_required
def cuentaporcobrar(request):
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # ===== ACTUALIZAR ESTADOS VENCIDOS AUTOMÁTICAMENTE =====
    hoy = timezone.now().date()
    # Obtener todas las cuentas pendientes o parciales que no estén anuladas/eliminadas
    cuentas_pendientes = CuentaPorCobrar.objects.filter(
        anulada=False,
        eliminada=False,
        estado__in=['pendiente', 'parcial']
    )
    for cuenta in cuentas_pendientes:
        if cuenta.fecha_vencimiento and hoy > cuenta.fecha_vencimiento:
            saldo = Decimal(str(cuenta.monto_total)) - \
                Decimal(str(cuenta.monto_pagado))
            if saldo > 0:
                cuenta.estado = 'vencida'
                cuenta.save(update_fields=['estado'])
    # =====================================================

    # Obtener todas las cuentas (excluyendo anuladas y eliminadas) para los filtros
    cuentas = CuentaPorCobrar.objects.select_related('venta', 'cliente').filter(
        anulada=False,
        eliminada=False
    )

    # Aplicar filtros
    if search:
        cuentas = cuentas.filter(
            Q(cliente__full_name__icontains=search) |
            Q(venta__numero_factura__icontains=search) |
            Q(cliente__identification_number__icontains=search)
        )
    if status_filter:
        cuentas = cuentas.filter(estado=status_filter)
    if date_from:
        cuentas = cuentas.filter(venta__fecha_venta__gte=date_from)
    if date_to:
        cuentas = cuentas.filter(venta__fecha_venta__lte=date_to)

    # Calcular estadísticas
    total_pendiente = Decimal('0.00')
    total_vencido = Decimal('0.00')
    total_por_cobrar = Decimal('0.00')

    for cuenta in cuentas:
        monto_total_original = Decimal(str(cuenta.monto_total))
        saldo_pendiente = monto_total_original - \
            Decimal(str(cuenta.monto_pagado))

        if saldo_pendiente < 0:
            saldo_pendiente = Decimal('0.00')
            if cuenta.monto_pagado > monto_total_original:
                cuenta.monto_pagado = monto_total_original
                cuenta.save()

        if cuenta.estado in ['pendiente', 'parcial']:
            total_pendiente += saldo_pendiente
        elif cuenta.estado == 'vencida':
            total_vencido += saldo_pendiente

        if cuenta.estado != 'pagada':
            total_por_cobrar += saldo_pendiente

    # Pagos del mes actual
    mes_actual = timezone.now().month
    año_actual = timezone.now().year
    pagos_mes = PagoCuentaPorCobrar.objects.filter(
        fecha_pago__month=mes_actual,
        fecha_pago__year=año_actual,
        cuenta__anulada=False,
        cuenta__eliminada=False
    ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

    # Preparar datos para el template
    cuentas_data = []
    for cuenta in cuentas:
        monto_total_original = float(cuenta.monto_total)
        monto_pagado = float(cuenta.monto_pagado)
        # Asegurar que el monto pagado no exceda el total
        if monto_pagado >= monto_total_original:
            monto_pagado = monto_total_original
        saldo_pendiente = max(0.0, monto_total_original - monto_pagado)

        # Productos de la venta
        productos = []
        if cuenta.venta and hasattr(cuenta.venta, 'detalles'):
            for detalle in cuenta.venta.detalles.all():
                nombre_producto = 'Servicio'
                precio_sin_itbis = float(detalle.precio_unitario)
                if hasattr(detalle, 'producto') and detalle.producto:
                    nombre_producto = detalle.producto.descripcion
                elif hasattr(detalle, 'servicio') and detalle.servicio:
                    nombre_producto = detalle.servicio.nombre
                elif hasattr(detalle, 'descripcion') and detalle.descripcion:
                    nombre_producto = detalle.descripcion
                cantidad = 1
                if hasattr(detalle, 'cantidad'):
                    cantidad = float(detalle.cantidad)
                productos.append({
                    'nombre': nombre_producto,
                    'cantidad': cantidad,
                    'precio': precio_sin_itbis,
                })

        client_name = cuenta.cliente.full_name if cuenta.cliente else 'Cliente no disponible'
        client_phone = cuenta.cliente.primary_phone if cuenta.cliente else 'N/A'
        invoice_number = cuenta.venta.numero_factura if cuenta.venta else 'N/A'
        # CORRECCIÓN: usar fecha_venta en lugar de fecha_vencimiento
        sale_date = cuenta.venta.fecha_venta.strftime(
            '%Y-%m-%d') if cuenta.venta and cuenta.venta.fecha_venta else ''
        due_date = cuenta.fecha_vencimiento.strftime(
            '%Y-%m-%d') if cuenta.fecha_vencimiento else ''
        puede_eliminar = cuenta.estado == 'pagada'

        # ===== CÁLCULO DE DÍAS VENCIDO =====
        dias_vencido = None
        if cuenta.fecha_vencimiento and hoy > cuenta.fecha_vencimiento and saldo_pendiente > 0:
            dias_vencido = (hoy - cuenta.fecha_vencimiento).days
        # ===================================

        cuentas_data.append({
            'id': cuenta.id,
            'clientId': cuenta.cliente.id if cuenta.cliente else None,
            'invoiceNumber': invoice_number,
            'clientName': client_name,
            'clientPhone': client_phone,
            'products': productos,
            'saleDate': sale_date,
            'dueDate': due_date,
            'totalAmount': monto_total_original,
            'paidAmount': monto_pagado,
            'pendingBalance': saldo_pendiente,
            'status': cuenta.estado,
            'observations': cuenta.observaciones or '',
            'puede_eliminar': puede_eliminar,
            'totalConItbis': float(cuenta.venta.total) if cuenta.venta else 0,
            'dias_vencido': dias_vencido,  # Nuevo campo
        })

    cuentas_json = json.dumps(cuentas_data)

    context = {
        'cuentas_json': cuentas_json,
        'total_pendiente': float(total_pendiente),
        'total_vencido': float(total_vencido),
        'pagos_mes': float(pagos_mes),
        'total_por_cobrar': float(total_por_cobrar),
        'search': search,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(request, "facturacion/cuentaporcobrar.html", context)


def sincronizar_cuentas_ventas():
    """
    Sincroniza todas las cuentas por cobrar con sus ventas correspondientes.
    Corrige inconsistencias después de devoluciones o pagos mal registrados.
    """
    cuentas = CuentaPorCobrar.objects.filter(anulada=False, eliminada=False)

    for cuenta in cuentas:
        if cuenta.venta:
            cuenta.monto_total = cuenta.venta.total_a_pagar
            saldo_pendiente = cuenta.monto_total - cuenta.monto_pagado

            if saldo_pendiente <= 0:
                cuenta.estado = 'pagada'
                # ✅ CORRECCIÓN: ajustar monto_pagado si excede el total,
                # evitando que quede registrado un pago mayor al total de la factura.
                cuenta.monto_pagado = cuenta.monto_total
            elif cuenta.monto_pagado > 0:
                cuenta.estado = 'parcial'
            else:
                cuenta.estado = 'pendiente'

            if cuenta.esta_vencida:
                cuenta.estado = 'vencida'

            cuenta.save()

    return f"Sincronizadas {cuentas.count()} cuentas"


@login_required
def registrar_pago(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cuenta_id = data.get('cuenta_id')
            # Dinero real recibido
            monto = Decimal(str(data.get('monto')))
            descuento_monto = Decimal(
                str(data.get('descuento_monto', 0)))   # <-- NUEVO
            metodo_pago = data.get('metodo_pago')
            referencia = data.get('referencia', '')
            observaciones = data.get('observaciones', '')

            cuenta = get_object_or_404(CuentaPorCobrar, id=cuenta_id)

            if cuenta.anulada:
                return JsonResponse({'success': False, 'message': 'No se puede registrar pago en una cuenta anulada'})

            monto_total_original = Decimal(
                str(cuenta.monto_total)).quantize(Decimal('0.01'))
            monto_ya_pagado = Decimal(
                str(cuenta.monto_pagado)).quantize(Decimal('0.01'))
            saldo_pendiente = (monto_total_original -
                               monto_ya_pagado).quantize(Decimal('0.01'))

            # Si hay descuento, se suma al monto_pagado (reduce la deuda)
            # pero no ingresa dinero real, así que el monto real pagado puede ser menor.
            # El total a aplicar al saldo = monto (real) + descuento_monto
            total_a_aplicar = monto + descuento_monto

            if total_a_aplicar <= 0:
                return JsonResponse({'success': False, 'message': 'El monto + descuento debe ser mayor a cero'})

            if total_a_aplicar > saldo_pendiente + Decimal('0.01'):
                return JsonResponse({
                    'success': False,
                    'message': f'El total a aplicar (RD${total_a_aplicar}) excede el saldo pendiente de RD${saldo_pendiente}'
                })

            # ✅ CORRECCIÓN: usar cuenta.monto_total como fuente de verdad,
            # no venta.total_a_pagar, para evitar inconsistencias.
            monto_total_original = Decimal(
                str(cuenta.monto_total)).quantize(Decimal('0.01'))
            monto_ya_pagado = Decimal(
                str(cuenta.monto_pagado)).quantize(Decimal('0.01'))
            saldo_pendiente = (monto_total_original -
                               monto_ya_pagado).quantize(Decimal('0.01'))

            # ✅ CORRECCIÓN: si el saldo ya es <= 0, la cuenta está pagada.
            # Corregir estado en BD si hace falta y rechazar el pago.
            if saldo_pendiente <= Decimal('0.00'):
                if cuenta.estado != 'pagada':
                    cuenta.estado = 'pagada'
                    cuenta.monto_pagado = monto_total_original
                    cuenta.save()
                return JsonResponse({
                    'success': False,
                    'message': 'Esta cuenta ya está completamente pagada'
                })

            monto = monto.quantize(Decimal('0.01'))

            if monto <= 0:
                return JsonResponse({
                    'success': False,
                    'message': 'El monto del pago debe ser mayor a cero'
                })

            if monto > saldo_pendiente + Decimal('0.01'):
                return JsonResponse({
                    'success': False,
                    'message': f'El monto (RD${monto}) excede el saldo pendiente de RD${saldo_pendiente}'
                })

            # Si el monto es muy cercano al saldo pendiente (diferencia <= 1 centavo), ajustarlo
            if abs(monto - saldo_pendiente) <= Decimal('0.01'):
                monto = saldo_pendiente

            # Ajuste fino por centavos
            if abs(total_a_aplicar - saldo_pendiente) <= Decimal('0.01'):
                total_a_aplicar = saldo_pendiente

            # Crear el pago, ahora incluyendo descuento_monto

            pago = PagoCuentaPorCobrar(
                cuenta=cuenta,
                monto=monto,                         # Dinero real recibido
                descuento_monto=descuento_monto,     # <-- AHORA SE GUARDA
                metodo_pago=metodo_pago,
                referencia=referencia,
                observaciones=observaciones,
                usuario=request.user
            )
            pago.save()

            # Actualizar la cuenta: se suma el total aplicado (real + descuento)
            nuevo_monto_pagado = (
                monto_ya_pagado + total_a_aplicar).quantize(Decimal('0.01'))
            if nuevo_monto_pagado > monto_total_original:
                nuevo_monto_pagado = monto_total_original
            cuenta.monto_pagado = nuevo_monto_pagado

            # Recalcular estado
            if cuenta.monto_pagado >= cuenta.monto_total:
                cuenta.estado = 'pagada'
                cuenta.monto_pagado = cuenta.monto_total
            elif cuenta.monto_pagado > 0:
                cuenta.estado = 'parcial'
            else:
                # Si no hay pagos, determinar pendiente o vencida
                hoy = timezone.now().date()
                if cuenta.fecha_vencimiento and hoy > cuenta.fecha_vencimiento:
                    cuenta.estado = 'vencida'
                else:
                    cuenta.estado = 'pendiente'

            cuenta.save()

            # Generar comprobante (si existe el modelo)

            comprobante = ComprobantePago(
                pago=pago,
                cuenta=cuenta,
                cliente=cuenta.cliente,
                tipo_comprobante='recibo'
            )
            comprobante.save()

            nuevo_saldo = max(cuenta.monto_total -
                              cuenta.monto_pagado, Decimal('0.00'))

            return JsonResponse({
                'success': True,
                'message': f'Pago registrado exitosamente. Comprobante: {comprobante.numero_comprobante}',
                'comprobante_numero': comprobante.numero_comprobante,
                'comprobante_id': comprobante.id,
                'nuevo_saldo_pendiente': float(nuevo_saldo),
                'monto_total_original': float(monto_total_original),
                'monto_pagado_total': float(cuenta.monto_pagado),
                'estado_actual': cuenta.estado
            })

        except Exception as e:

            return JsonResponse({
                'success': False,
                'message': f'Error al registrar pago: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@require_GET
@login_required
def generar_comprobante_pdf(request, comprobante_id):
    try:
        comprobante = get_object_or_404(ComprobantePago, id=comprobante_id)

        # Crear respuesta HTTP con tipo PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="comprobante_{comprobante.numero_comprobante}.pdf"'

        # Configurar el PDF en tamaño A4 (595 x 842 puntos)
        width, height = A4
        p = canvas.Canvas(response, pagesize=A4)

        # Ruta absoluta del logo en STATIC_ROOT
        logo_path = os.path.join(settings.STATIC_ROOT,
                                 'image', 'favicon12.ico')

        # Verifica si el archivo existe
        if not os.path.exists(logo_path):
            raise FileNotFoundError(
                f"No se encontró el logo en la ruta: {logo_path}")

        # Márgenes y posiciones iniciales
        margin_left = 50
        y_position = height - 50  # Iniciar 50 puntos desde el borde superior
        line_height = 14
        small_line_height = 10

        # Función para centrar texto
        def draw_centered_text(text, y, font_size=12, bold=False):
            if bold:
                p.setFont("Helvetica-Bold", font_size)
            else:
                p.setFont("Helvetica", font_size)
            text_width = p.stringWidth(text, "Helvetica", font_size)
            x = (width - text_width) / 2
            p.drawString(x, y, text)
            return y - line_height

        # Función para texto alineado a la izquierda
        def draw_left_text(text, y, font_size=10, bold=False):
            if bold:
                p.setFont("Helvetica-Bold", font_size)
            else:
                p.setFont("Helvetica", font_size)
            p.drawString(margin_left, y, text)
            return y - line_height

        # Insertar logo en el encabezado
        logo_width = 150
        logo_height = 80
        logo_x = (width - logo_width) / 2
        logo_y = y_position - logo_height
        p.drawImage(logo_path, logo_x, logo_y, width=logo_width,
                    height=logo_height, preserveAspectRatio=True)
        y_position = logo_y - 20  # Espacio después del logo

        # Encabezado del comprobante
        y_position = draw_centered_text(
            "REPUESTO SUPER BESTIA", y_position, 16, True)
        y_position = draw_centered_text(
            "COMPROBANTE DE PAGO", y_position, 14, True)
        y_position -= line_height / 2

        # Línea separadora
        p.line(margin_left, y_position, width - margin_left, y_position)
        y_position -= line_height

        # Información del comprobante
        y_position = draw_left_text(
            f"Comprobante: {comprobante.numero_comprobante}", y_position, 10)
        y_position = draw_left_text(
            f"Fecha: {comprobante.fecha_emision.strftime('%d/%m/%Y %H:%M')}", y_position, 10)
        y_position = draw_left_text(
            f"Cliente: {comprobante.cliente.full_name}", y_position, 10)
        if comprobante.cuenta.venta:
            y_position = draw_left_text(
                f"Factura: {comprobante.cuenta.venta.numero_factura}", y_position, 10)

        y_position -= line_height / 2

        # Línea separadora
        p.line(margin_left, y_position, width - margin_left, y_position)
        y_position -= line_height

        # Información del pago
        y_position = draw_centered_text(
            "DETALLE DEL PAGO", y_position, 12, True)
        y_position -= small_line_height
        y_position = draw_left_text(
            f"Monto Pagado: RD$ {comprobante.pago.monto:,.2f}", y_position, 10, True)
        y_position = draw_left_text(
            f"Método: {comprobante.pago.get_metodo_pago_display()}", y_position, 10)
        if comprobante.pago.referencia:
            y_position = draw_left_text(
                f"Referencia: {comprobante.pago.referencia}", y_position, 9)

        y_position -= line_height / 2

        # Línea separadora
        p.line(margin_left, y_position, width - margin_left, y_position)
        y_position -= line_height

        # Cálculo de montos
        monto_total_original = Decimal(
            str(comprobante.cuenta.venta.total_a_pagar))
        monto_total_con_itbis = comprobante.cuenta.venta.total if comprobante.cuenta.venta else comprobante.cuenta.monto_total
        saldo_pendiente = monto_total_original - \
            Decimal(str(comprobante.cuenta.monto_pagado))

        # Resumen de cuenta
        y_position = draw_centered_text(
            "RESUMEN DE CUENTA", y_position, 12, True)
        y_position -= small_line_height
        y_position = draw_left_text(
            f"Monto Original: RD$ {monto_total_original:,.2f}", y_position, 10)
        y_position = draw_left_text(
            f"Pagado Acumulado: RD$ {comprobante.cuenta.monto_pagado:,.2f}", y_position, 10)
        y_position = draw_left_text(
            f"Saldo Pendiente: RD$ {saldo_pendiente:,.2f}", y_position, 10, True)

        y_position -= line_height

        # Línea separadora
        p.line(margin_left, y_position, width - margin_left, y_position)
        y_position -= line_height * 2

        # Sección de firmas
        y_position = draw_centered_text(
            "FIRMA DEL CLIENTE", y_position, 10, True)
        y_position -= small_line_height
        p.line(margin_left + 40, y_position,
               width - margin_left - 40, y_position)
        y_position -= line_height * 1.2
        y_position = draw_left_text(
            "Cédula: _________________________", y_position, 9)

        y_position -= line_height * 1.5
        y_position = draw_centered_text(
            "FIRMA DE LA EMPRESA", y_position, 10, True)
        y_position -= small_line_height
        p.line(margin_left + 40, y_position,
               width - margin_left - 40, y_position)
        y_position -= line_height

        # Pie de página
        y_position = draw_centered_text(
            "REPUESTO SUPER BESTIA", y_position, 10, True)
        y_position -= line_height
        y_position = draw_centered_text(
            "¡Gracias por su pago!", y_position, 12, True)
        y_position -= small_line_height
        y_position = draw_centered_text("Tel: (849) 353-5344", y_position, 9)
        y_position = draw_centered_text(
            f"Ref: {comprobante.numero_comprobante}", y_position, 8)

        # Finalizar el PDF
        p.showPage()
        p.save()

        return response

    except FileNotFoundError as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}. Asegúrate de que el logo esté en la carpeta correcta y de que hayas ejecutado `collectstatic`.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al generar comprobante: {str(e)}'
        })
    return JsonResponse({'success': False, 'message': f'Error al registrar pago: {str(e)}'})


@require_POST
@login_required
def eliminar_cuenta_pagada(request, cuenta_id):
    if request.method == 'POST':
        try:
            cuenta = get_object_or_404(CuentaPorCobrar, id=cuenta_id)

            # Verificar que la cuenta esté pagada
            if cuenta.estado != 'pagada':
                return JsonResponse({
                    'success': False,
                    'message': 'Solo se pueden eliminar cuentas que estén completamente pagadas'
                })

            # Verificar que no esté ya eliminada
            if cuenta.eliminada:
                return JsonResponse({
                    'success': False,
                    'message': 'Esta cuenta ya ha sido eliminada'
                })

            # Realizar soft delete
            cuenta.eliminar_cuenta()

            return JsonResponse({
                'success': True,
                'message': f'Cuenta #{cuenta.id} - Factura {cuenta.venta.numero_factura} eliminada exitosamente'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar cuenta: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@require_POST
@login_required
def anular_cuenta(request, cuenta_id):
    if request.method == 'POST':
        try:
            # Verificar que el usuario sea superusuario
            if not request.user.is_superuser:
                return JsonResponse({
                    'success': False,
                    'message': 'No tiene permisos para anular cuentas. Solo el superusuario puede realizar esta acción.'
                })

            cuenta = get_object_or_404(CuentaPorCobrar, id=cuenta_id)

            # Verificar que la cuenta no esté anulada
            if cuenta.anulada:
                return JsonResponse({
                    'success': False,
                    'message': 'Esta cuenta ya se encuentra anulada'
                })

            # Verificar que no tenga pagos
            if cuenta.monto_pagado > 0:
                return JsonResponse({
                    'success': False,
                    'message': 'No se puede anular una cuenta que tiene pagos registrados'
                })

            # Anular la cuenta
            cuenta.anulada = True
            cuenta.estado = 'anulada'
            cuenta.save()

            return JsonResponse({
                'success': True,
                'message': f'Cuenta #{cuenta.id} - Factura {cuenta.venta.numero_factura} anulada exitosamente'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al anular cuenta: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def detalle_cuenta(request, cuenta_id):
    cuenta = get_object_or_404(
        CuentaPorCobrar.objects.select_related('venta', 'cliente'),
        id=cuenta_id
    )

    pagos = PagoCuentaPorCobrar.objects.filter(
        cuenta=cuenta).order_by('-fecha_pago')

    # CAMBIO: Usar total_a_pagar y total_con_interes
    monto_original = cuenta.venta.total_a_pagar if cuenta.venta and cuenta.venta.total_a_pagar else cuenta.monto_total
    monto_con_interes = cuenta.venta.total_con_interes if cuenta.venta and cuenta.venta.total_con_interes else monto_original
    saldo_pendiente = monto_con_interes - cuenta.monto_pagado

    data = {
        'id': cuenta.id,
        'factura': cuenta.venta.numero_factura,
        'cliente': cuenta.cliente.full_name,
        'telefono': cuenta.cliente.primary_phone or 'N/A',
        'productos': [
            {
                'nombre': item.producto.nombre if hasattr(item, 'producto') else 'Servicio',
                'cantidad': item.cantidad,
                'precio': item.precio
            }
            for item in cuenta.venta.detalles.all()
        ] if cuenta.venta else [],
        'fecha_venta': cuenta.venta.fecha_venta.strftime('%Y-%m-%d') if cuenta.venta else '',
        'fecha_vencimiento': cuenta.fecha_vencimiento.strftime('%Y-%m-%d') if cuenta.fecha_vencimiento else '',
        'monto_total_original': float(monto_original),  # total_a_pagar
        # total_con_interes
        'monto_total_con_interes': float(monto_con_interes),
        'monto_pagado': float(cuenta.monto_pagado),
        # basado en total_con_interes
        'saldo_pendiente': float(saldo_pendiente),
        'estado': cuenta.get_estado_display(),
        'observaciones': cuenta.observaciones or 'N/A',
        'pagos': [
            {
                'fecha': pago.fecha_pago.strftime('%Y-%m-%d %H:%M'),
                'monto': float(pago.monto),
                'metodo': pago.get_metodo_pago_display(),
                'referencia': pago.referencia or 'N/A',
                'observaciones': pago.observaciones or 'N/A'
            }
            for pago in pagos
        ]
    }

    return JsonResponse(data)


@login_required
@xframe_options_exempt
def generar_reporte_deudas_pdf(request):
    """
    Genera un reporte PDF de deudas por cliente
    """
    try:
        # Obtener parámetros de filtrado (si existen)
        search = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')

        # Filtrar cuentas por cobrar (excluir anuladas y eliminadas)
        cuentas = CuentaPorCobrar.objects.select_related('venta', 'cliente').filter(
            anulada=False,
            eliminada=False
        ).order_by('cliente__full_name')

        # Aplicar filtros si existen
        if search:
            cuentas = cuentas.filter(
                Q(cliente__full_name__icontains=search) |
                Q(venta__numero_factura__icontains=search) |
                Q(cliente__identification_number__icontains=search)
            )

        if status_filter:
            cuentas = cuentas.filter(estado=status_filter)

        if date_from:
            cuentas = cuentas.filter(venta__fecha_venta__gte=date_from)

        if date_to:
            cuentas = cuentas.filter(venta__fecha_venta__lte=date_to)

        # Agrupar por cliente
        clientes_dict = {}

        for cuenta in cuentas:
            cliente = cuenta.cliente
            if not cliente:
                continue

            cliente_id = cliente.id
            if cliente_id not in clientes_dict:
                clientes_dict[cliente_id] = {
                    'nombre': cliente.full_name or 'Sin nombre',
                    'cedula': cliente.identification_number or 'N/A',
                    'telefono': cliente.primary_phone or 'N/A',
                    'facturas_pendientes': 0,
                    'monto_total_pendiente': Decimal('0.00'),
                    'estado_general': 'pagada',  # Empezamos asumiendo pagada
                    'detalle_facturas': []
                }

            # Calcular saldo pendiente
            monto_total_original = Decimal(str(cuenta.venta.total_a_pagar))
            saldo_pendiente = monto_total_original - \
                Decimal(str(cuenta.monto_pagado))

            # Solo considerar si tiene saldo pendiente
            if saldo_pendiente > 0:
                clientes_dict[cliente_id]['facturas_pendientes'] += 1
                clientes_dict[cliente_id]['monto_total_pendiente'] += saldo_pendiente

                # Actualizar estado general
                if cuenta.estado == 'vencida' and clientes_dict[cliente_id]['estado_general'] != 'vencida':
                    clientes_dict[cliente_id]['estado_general'] = 'vencida'
                elif cuenta.estado == 'pendiente' and clientes_dict[cliente_id]['estado_general'] not in ['vencida']:
                    clientes_dict[cliente_id]['estado_general'] = 'pendiente'
                elif cuenta.estado == 'parcial' and clientes_dict[cliente_id]['estado_general'] == 'pagada':
                    clientes_dict[cliente_id]['estado_general'] = 'parcial'

                # Agregar detalle de factura
                clientes_dict[cliente_id]['detalle_facturas'].append({
                    'factura': cuenta.venta.numero_factura if cuenta.venta else 'N/A',
                    'monto_pendiente': saldo_pendiente,
                    'estado': cuenta.estado,
                    'fecha_vencimiento': cuenta.fecha_vencimiento.strftime('%d/%m/%Y') if cuenta.fecha_vencimiento else 'N/A'
                })

        # Filtrar solo clientes con deuda
        clientes_con_deuda = []
        total_deuda_general = Decimal('0.00')

        for cliente_info in clientes_dict.values():
            if cliente_info['monto_total_pendiente'] > 0:
                clientes_con_deuda.append(cliente_info)
                total_deuda_general += cliente_info['monto_total_pendiente']

        # Crear el PDF
        response = HttpResponse(content_type='application/pdf')
        tz_rd = pytz.timezone('America/Santo_Domingo')
        ahora_local = timezone.now().astimezone(tz_rd)
        fecha_reporte = ahora_local.strftime('%d/%m/%Y %I:%M ')
        fecha_archivo = ahora_local.strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="reporte_deudas_{fecha_archivo}.pdf"'

        # Configurar el documento A4
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=portrait(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )

        # Estilos
        styles = getSampleStyleSheet()

        # Título principal
        titulo_style = ParagraphStyle(
            'Titulo',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=20,
            alignment=1  # Centrado
        )

        # Subtítulo
        subtitulo_style = ParagraphStyle(
            'Subtitulo',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=15,
            alignment=1
        )

        # Estilo para encabezados de tabla
        encabezado_style = ParagraphStyle(
            'Encabezado',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.white,
            alignment=1
        )

        # Estilo para datos de tabla
        datos_style = ParagraphStyle(
            'Datos',
            parent=styles['Normal'],
            fontSize=8,
            alignment=0  # Izquierda
        )

        # Contenido del PDF
        contenido = []

        # Título
        contenido.append(
            Paragraph("REPORTE DE DEUDAS POR CLIENTE", titulo_style))

        # Información del reporte
        fecha_actual = fecha_reporte
        filtros = []
        if search:
            filtros.append(f"Búsqueda: {search}")
        if status_filter:
            filtros.append(f"Estado: {status_filter}")
        if date_from:
            filtros.append(f"Desde: {date_from}")
        if date_to:
            filtros.append(f"Hasta: {date_to}")

        info_filtros = " | ".join(
            filtros) if filtros else "Todos los registros"
        contenido.append(
            Paragraph(f"Generado: {fecha_actual}", subtitulo_style))
        contenido.append(
            Paragraph(f"Filtros: {info_filtros}", subtitulo_style))
        contenido.append(Spacer(1, 15))

        # Datos de resumen
        resumen_data = [
            ["Total Clientes con Deuda:", len(clientes_con_deuda)],
            ["Deuda Total:", f"RD$ {total_deuda_general:,.2f}"],
            ["Fecha de Reporte:", fecha_actual]
        ]

        resumen_table = Table(resumen_data, colWidths=[4*cm, 4*cm])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))

        contenido.append(resumen_table)
        contenido.append(Spacer(1, 20))

        # Tabla principal de deudas
        if clientes_con_deuda:
            # Encabezados de la tabla
            encabezados = [
                Paragraph("Cliente", encabezado_style),
                Paragraph("Cédula", encabezado_style),
                Paragraph("Teléfono", encabezado_style),
                Paragraph("Facturas Pendientes", encabezado_style),
                Paragraph("Monto Total Pendiente", encabezado_style),
                Paragraph("Estado General", encabezado_style)
            ]

            datos_tabla = [encabezados]

            # Agregar datos de cada cliente
            for cliente in clientes_con_deuda:
                # Determinar color del estado
                estado_texto = {
                    'vencida': 'VENCIDA',
                    'pendiente': 'PENDIENTE',
                    'parcial': 'PAGO PARCIAL',
                    'pagada': 'PAGADA'
                }.get(cliente['estado_general'], cliente['estado_general'].upper())

                fila = [
                    Paragraph(cliente['nombre'], datos_style),
                    Paragraph(cliente['cedula'], datos_style),
                    Paragraph(cliente['telefono'], datos_style),
                    Paragraph(
                        str(cliente['facturas_pendientes']), datos_style),
                    Paragraph(
                        f"RD$ {cliente['monto_total_pendiente']:,.2f}", datos_style),
                    Paragraph(estado_texto, datos_style)
                ]
                datos_tabla.append(fila)

            # Crear tabla
            tabla = Table(datos_tabla, colWidths=[
                          4.5*cm, 2.5*cm, 3*cm, 3*cm, 4*cm, 3*cm])

            # Estilos de la tabla
            tabla.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8a8178')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                # Filas alternas
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (2, -1), 'LEFT'),
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),
                ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
                ('ALIGN', (5, 1), (5, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 6),

                # Bordes
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),

                # Resaltar montos
                ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),

                # Colorear estados
                ('TEXTCOLOR', (5, 1), (5, -1), lambda r, c:
                    colors.red if datos_tabla[r][5].text == 'VENCIDA'
                    else colors.orange if datos_tabla[r][5].text == 'PENDIENTE'
                    else colors.blue if datos_tabla[r][5].text == 'PAGO PARCIAL'
                    else colors.green)
            ]))

            contenido.append(tabla)
            contenido.append(Spacer(1, 20))

            # Pie de página con totales
            pie_data = [
                ["TOTAL GENERAL:", f"RD$ {total_deuda_general:,.2f}"]
            ]

            pie_table = Table(pie_data, colWidths=[15*cm, 5*cm])
            pie_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ]))

            contenido.append(pie_table)

        else:
            # Si no hay deudas
            contenido.append(
                Paragraph("No hay deudas pendientes para mostrar.", styles['Heading3']))
            contenido.append(Spacer(1, 20))

        # Nota al pie
        nota = Paragraph(
            "Este reporte fue generado automáticamente por el sistema de gestión Super Bestia. "
            "Los montos están expresados en pesos dominicanos (RD$).",
            ParagraphStyle(
                'Nota',
                parent=styles['Normal'],
                fontSize=7,
                textColor=colors.grey,
                alignment=1
            )
        )
        contenido.append(Spacer(1, 30))
        contenido.append(nota)

        # Construir el PDF
        doc.build(contenido)

        # Obtener el valor del buffer
        pdf = buffer.getvalue()
        buffer.close()

        response.write(pdf)
        return response

    except Exception as e:
        # En caso de error, devolver una respuesta de error
        error_message = f"Error al generar el reporte: {str(e)}"
        return HttpResponse(error_message, content_type='text/plain')


@login_required
def generar_historial_cliente_pdf(request, client_id):
    """
    Genera un PDF con el historial detallado de un cliente.
    Ya usa cuenta.monto_total, por lo que refleja descuentos.
    """
    try:
        from .models import Cliente, CuentaPorCobrar, PagoCuentaPorCobrar
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from decimal import Decimal
        from datetime import datetime
        import io
        import pytz

        tz_rd = pytz.timezone('America/Santo_Domingo')

        def formato_hora_rd(dt):
            """Convierte un datetime UTC a hora RD (UTC-4) en formato 12h"""
            if dt is None:
                return 'N/A'
            if timezone.is_aware(dt):
                dt = dt.astimezone(tz_rd)
            else:
                dt = pytz.utc.localize(dt).astimezone(tz_rd)
            return dt.strftime('%d/%m/%Y %I:%M %p')

        User = get_user_model()
        cliente = get_object_or_404(Cliente, id=client_id)

        cuentas = CuentaPorCobrar.objects.filter(
            cliente=cliente,
            anulada=False,
            eliminada=False
        ).select_related(
            'venta',
            'venta__vendedor'
        ).prefetch_related(
            'pagos',
            'pagos__usuario',
            'pagos__comprobante'
        ).order_by('venta__fecha_venta')

        if not cuentas.exists():
            return HttpResponse("El cliente no tiene cuentas registradas.", content_type='text/plain')

        response = HttpResponse(content_type='application/pdf')
        fecha_reporte = datetime.now(tz_rd).strftime('%Y%m%d_%H%M%S')
        nombre_limpio = "".join(
            c for c in cliente.full_name if c.isalnum() or c in "._- ").strip()
        response['Content-Disposition'] = f'attachment; filename="historial_{nombre_limpio}_{fecha_reporte}.pdf"'

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        styles = getSampleStyleSheet()
        contenido = []

        titulo_style = ParagraphStyle(
            'Titulo',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=10,
            alignment=1
        )
        contenido.append(
            Paragraph("HISTORIAL DE CUENTAS POR CLIENTE", titulo_style))
        contenido.append(Spacer(1, 0.5*cm))

        info_style = ParagraphStyle(
            'Info', parent=styles['Normal'], fontSize=10)
        contenido.append(
            Paragraph(f"<b>Cliente:</b> {cliente.full_name}", info_style))
        contenido.append(Paragraph(
            f"<b>Cédula/RNC:</b> {cliente.identification_number or 'N/A'}", info_style))
        contenido.append(
            Paragraph(f"<b>Teléfono:</b> {cliente.primary_phone or 'N/A'}", info_style))

        fecha_reporte_str = datetime.now(tz_rd).strftime('%d/%m/%Y %I:%M %p')
        contenido.append(
            Paragraph(f"<b>Fecha del reporte:</b> {fecha_reporte_str}", info_style))
        contenido.append(Spacer(1, 0.5*cm))

        # Calcular totales con clamp (usando cuenta.monto_total)
        total_deuda = Decimal('0.00')
        total_pagado = Decimal('0.00')
        for cuenta in cuentas:
            monto_total = Decimal(str(cuenta.monto_total))
            monto_pagado_real = min(
                Decimal(str(cuenta.monto_pagado)), monto_total)
            saldo = max(monto_total - monto_pagado_real, Decimal('0.00'))
            if saldo > 0:
                total_deuda += saldo
            total_pagado += monto_pagado_real

        resumen_data = [
            ["Total deuda pendiente:",   f"RD$ {total_deuda:,.2f}"],
            ["Total pagado (histórico):", f"RD$ {total_pagado:,.2f}"],
        ]
        resumen_table = Table(resumen_data, colWidths=[6*cm, 4*cm])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR',     (0, 0), (-1, -1), colors.black),
            ('ALIGN',         (0, 0), (0, -1),  'LEFT'),
            ('ALIGN',         (1, 0), (1, -1),  'RIGHT'),
            ('FONTNAME',      (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOX',           (0, 0), (-1, -1), 1, colors.black),
        ]))
        contenido.append(resumen_table)
        contenido.append(Spacer(1, 0.7*cm))

        # Recorrer cada cuenta
        for cuenta in cuentas:
            factura_text = f"<b>Factura N°:</b> {cuenta.venta.numero_factura if cuenta.venta else 'N/A'}"
            if cuenta.venta and cuenta.venta.vendedor:
                vendedor = cuenta.venta.vendedor
                factura_text += f" | <b>Vendedor:</b> {vendedor.get_full_name() or vendedor.username}"
            contenido.append(Paragraph(factura_text, styles['Heading4']))

            fecha_venta_local = formato_hora_rd(
                cuenta.venta.fecha_venta) if cuenta.venta and cuenta.venta.fecha_venta else 'N/A'
            fecha_venc = cuenta.fecha_vencimiento.strftime(
                '%d/%m/%Y') if cuenta.fecha_vencimiento else 'N/A'
            estado = cuenta.get_estado_display()

            # ✅ Usar cuenta.monto_total
            monto_total = Decimal(str(cuenta.monto_total))
            monto_pagado_real = min(
                Decimal(str(cuenta.monto_pagado)), monto_total)
            saldo = max(monto_total - monto_pagado_real, Decimal('0.00'))

            info_factura = [
                ["Campo",            "Valor"],
                ["Fecha venta",      fecha_venta_local],
                ["Vencimiento",      fecha_venc],
                ["Monto total",      f"RD$ {monto_total:,.2f}"],
                ["Monto pagado",     f"RD$ {monto_pagado_real:,.2f}"],
                ["Saldo pendiente",  f"RD$ {saldo:,.2f}"],
                ["Estado",           estado],
            ]
            tabla_factura = Table(info_factura, colWidths=[4.2*cm, 7.8*cm])
            tabla_factura.setStyle(TableStyle([
                ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#6c757d')),
                ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
                ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME',      (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME',      (1, 1), (1, -1), 'Helvetica'),
                ('FONTSIZE',      (0, 0), (-1, -1), 9),
                ('ALIGN',         (0, 0), (-1, 0),  'CENTER'),
                ('ALIGN',         (0, 1), (0, -1),  'LEFT'),
                ('ALIGN',         (1, 1), (1, -1),  'LEFT'),
                ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID',          (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND',    (0, 1), (-1, -1), colors.whitesmoke),
                ('TOPPADDING',    (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            contenido.append(tabla_factura)

            pagos = cuenta.pagos.all().order_by('-fecha_pago')
            if pagos:
                contenido.append(
                    Paragraph("<b>Pagos realizados:</b>", styles['Normal']))

                encabezado_pagos_style = ParagraphStyle(
                    'EncabezadoPagos',
                    parent=styles['Normal'],
                    fontSize=8,
                    leading=9,
                    alignment=1,
                    textColor=colors.white
                )
                celda_pagos_style = ParagraphStyle(
                    'CeldaPagos',
                    parent=styles['Normal'],
                    fontSize=7,
                    leading=8,
                    alignment=0,
                    wordWrap='CJK'
                )
                monto_pagos_style = ParagraphStyle(
                    'MontoPagos',
                    parent=celda_pagos_style,
                    alignment=2
                )

                # Cabecera con 7 columnas (incluye Observaciones)
                pago_data = [[
                    Paragraph("Fecha", encabezado_pagos_style),
                    Paragraph("Monto", encabezado_pagos_style),
                    Paragraph("Metodo", encabezado_pagos_style),
                    Paragraph("Referencia", encabezado_pagos_style),
                    Paragraph("Comprobante", encabezado_pagos_style),
                    Paragraph("Cobro", encabezado_pagos_style),
                    Paragraph("Observaciones", encabezado_pagos_style),
                ]]

                pago_data = [["Fecha", "Monto", "Método", "Referencia",
                              "Comprobante", "Cobró", "Observaciones"]]

                suma_pagos = Decimal('0.00')
                for pago in pagos:
                    suma_pagos += Decimal(str(pago.monto))

                factor_ajuste = None
                if suma_pagos > monto_total:
                    factor_ajuste = monto_total / suma_pagos

                for pago in pagos:
                    fecha_pago_local = formato_hora_rd(pago.fecha_pago)
                    comprobante = getattr(pago, 'comprobante', None)
                    comp_num = comprobante.numero_comprobante if comprobante else 'N/A'
                    usuario = pago.usuario.get_full_name(
                    ) or pago.usuario.username if pago.usuario else 'N/A'

                    monto_pago = Decimal(str(pago.monto))
                    if factor_ajuste is not None:
                        monto_pago = (
                            monto_pago * factor_ajuste).quantize(Decimal('0.01'))

                    observaciones = pago.observaciones.strip() if pago.observaciones else 'N/A'

                    pago_data.append([

                        Paragraph(fecha_pago_local, celda_pagos_style),
                        Paragraph(f"RD$ {monto_pago:,.2f}", monto_pagos_style),
                        Paragraph(pago.get_metodo_pago_display(),
                                  celda_pagos_style),
                        Paragraph(pago.referencia or 'N/A', celda_pagos_style),
                        Paragraph(comp_num, celda_pagos_style),
                        Paragraph(usuario, celda_pagos_style),
                        Paragraph(observaciones, celda_pagos_style),
                    ])

                # Anchos de columna para 7 columnas (total 18 cm, aprovecha mejor A4)
                tabla_pagos = Table(
                    pago_data,
                    colWidths=[
                        2.9*cm,   # Fecha
                        2.1*cm,   # Monto
                        2.0*cm,   # Metodo
                        2.3*cm,   # Referencia
                        2.5*cm,   # Comprobante
                        2.0*cm,   # Cobro
                        4.2*cm,    # Observaciones

                        fecha_pago_local,
                        f"RD$ {monto_pago:,.2f}",
                        pago.get_metodo_pago_display(),
                        pago.referencia or 'N/A',
                        comp_num,
                        usuario,
                        observaciones,
                    ])

                tabla_pagos = Table(
                    pago_data,
                    colWidths=[
                        2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.8*cm

                    ]
                )
                tabla_pagos.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8a8178')),
                    ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
                    ('ALIGN',      (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN',      (0, 1), (-1, -1), 'LEFT'),
                    ('ALIGN',      (1, 1), (1, -1), 'RIGHT'),
                    ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE',   (0, 0), (-1, 0), 8),
                    ('FONTSIZE',   (0, 1), (-1, -1), 7),
                    ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),

                    ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),

                    ('WORDWRAP', (6, 1), (6, -1), True),

                ]))
                contenido.append(tabla_pagos)
            else:
                contenido.append(Paragraph(
                    "<i>No hay pagos registrados para esta factura.</i>", styles['Italic']))

            contenido.append(Spacer(1, 0.5*cm))
            contenido.append(Paragraph("<hr/>", styles['Normal']))
            contenido.append(Spacer(1, 0.3*cm))

        nota = Paragraph(
            "Reporte generado automáticamente por el sistema Super Bestia.",
            ParagraphStyle(
                'Nota', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
        )
        contenido.append(Spacer(1, 1*cm))
        contenido.append(nota)

        doc.build(contenido)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    except Exception as e:
        return HttpResponse(f"Error al generar el historial: {str(e)}", content_type='text/plain')


@login_required
def generar_reporte_vencidas_pdf(request):
    """
    Genera un PDF con todas las facturas vencidas, mostrando días de atraso.
    Usa los montos actuales de la cuenta (incluyendo descuentos).
    """
    try:
        from datetime import date
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from decimal import Decimal
        import io

        # Zona horaria República Dominicana
        tz_rd = pytz.timezone('America/Santo_Domingo')
        ahora_local = timezone.now().astimezone(tz_rd)
        fecha_reporte = ahora_local.strftime('%d/%m/%Y %I:%M %p')

        hoy = ahora_local.date()

        # Obtener solo cuentas realmente vencidas (1 día o más de atraso)
        cuentas = CuentaPorCobrar.objects.filter(
            estado='vencida',
            anulada=False,
            eliminada=False,
            fecha_vencimiento__lt=hoy
        ).select_related('cliente', 'venta').order_by('fecha_vencimiento')

        if not cuentas.exists():
            return HttpResponse("No hay facturas vencidas en este momento.", content_type='text/plain')

        data = []
        total_vencido = Decimal('0.00')
        for cuenta in cuentas:
            # ✅ Usar cuenta.monto_total (ya incluye descuentos)
            monto_pendiente = Decimal(
                str(cuenta.monto_total)) - Decimal(str(cuenta.monto_pagado))
            if monto_pendiente < 0:
                monto_pendiente = Decimal('0.00')
            dias_vencido = (
                hoy - cuenta.fecha_vencimiento).days if cuenta.fecha_vencimiento else 0
            if dias_vencido < 1:
                continue
            total_vencido += monto_pendiente
            data.append({
                'cliente': cuenta.cliente.full_name if cuenta.cliente else 'Cliente no disponible',
                'telefono': cuenta.cliente.primary_phone if cuenta.cliente else 'N/A',
                'factura': cuenta.venta.numero_factura if cuenta.venta else 'N/A',
                'fecha_vencimiento': cuenta.fecha_vencimiento.strftime('%d/%m/%Y') if cuenta.fecha_vencimiento else 'N/A',
                'dias_vencido': dias_vencido,
                'monto_pendiente': monto_pendiente,
            })

        if not data:
            return HttpResponse("No hay facturas vencidas en este momento.", content_type='text/plain')

        # Crear PDF
        response = HttpResponse(content_type='application/pdf')
        fecha_reporte_archivo = ahora_local.strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="facturas_vencidas_{fecha_reporte_archivo}.pdf"'

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        styles = getSampleStyleSheet()
        contenido = []

        # Título
        titulo_style = ParagraphStyle(
            'Titulo',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=10,
            alignment=1
        )
        contenido.append(
            Paragraph("REPORTE DE FACTURAS VENCIDAS", titulo_style))
        contenido.append(Spacer(1, 0.5*cm))

        # Subtítulo con fecha de generación
        contenido.append(
            Paragraph(f"Generado: {fecha_reporte}", styles['Normal']))
        contenido.append(Spacer(1, 0.5*cm))

        # Resumen en 2 columnas (arriba)
        resumen_data = [
            ["Total deuda vencida", "Total registros"],
            [f"RD$ {total_vencido:,.2f}", str(len(data))]
        ]
        tabla_resumen = Table(resumen_data, colWidths=[7*cm, 7*cm])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, 1), colors.whitesmoke),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        contenido.append(tabla_resumen)
        contenido.append(Spacer(1, 0.5*cm))

        # Tabla de facturas vencidas
        encabezado_style = ParagraphStyle(
            'EncabezadoVencidas',
            parent=styles['Normal'],
            fontSize=8,
            leading=9,
            alignment=1,
            textColor=colors.white
        )
        encabezados = [
            Paragraph("Cliente", encabezado_style),
            Paragraph("Teléfono", encabezado_style),
            Paragraph("Factura", encabezado_style),
            Paragraph("Fecha. Venc.", encabezado_style),
            Paragraph("Días", encabezado_style),
            Paragraph("Monto Pendiente", encabezado_style)
        ]
        datos_tabla = [encabezados]

        for item in data:
            cliente_corto = item['cliente'] if len(
                item['cliente']) <= 22 else f"{item['cliente'][:19]}..."
            fila = [
                cliente_corto,
                item['telefono'],
                item['factura'],
                item['fecha_vencimiento'],
                str(item['dias_vencido']),
                f"RD$ {item['monto_pendiente']:,.2f}"
            ]
            datos_tabla.append(fila)

        col_widths = [4.5*cm, 2.8*cm, 2.5*cm, 2.8*cm, 2.2*cm, 3*cm]
        tabla = Table(datos_tabla, colWidths=col_widths)

        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),
            ('ALIGN', (5, 1), (5, -1), 'RIGHT'),
        ]))

        contenido.append(tabla)
        contenido.append(Spacer(1, 0.7*cm))

        # Nota
        nota = Paragraph(
            "Este reporte incluye todas las facturas que actualmente están vencidas, "
            "considerando los descuentos aplicados a cada cuenta.",
            ParagraphStyle(
                'Nota', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
        )
        contenido.append(Spacer(1, 1*cm))
        contenido.append(nota)

        doc.build(contenido)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    except Exception as e:
        return HttpResponse(f"Error al generar reporte: {str(e)}", content_type='text/plain')


@login_required
@require_POST
def aplicar_descuento_factura(request, cuenta_id):
    try:
        data = json.loads(request.body)
        porcentaje = Decimal(str(data.get('porcentaje', 0)))

        if porcentaje <= 0 or porcentaje > 100:
            return JsonResponse({'success': False, 'message': 'El porcentaje debe estar entre 1 y 100'})

        cuenta = get_object_or_404(
            CuentaPorCobrar, id=cuenta_id, anulada=False, eliminada=False)

        if cuenta.estado == 'pagada':
            return JsonResponse({'success': False, 'message': 'Esta factura ya está pagada'})

        saldo_actual = cuenta.saldo_pendiente
        if saldo_actual <= 0:
            return JsonResponse({'success': False, 'message': 'Esta factura no tiene saldo pendiente'})

        factor_descuento = porcentaje / Decimal('100')
        descuento = (saldo_actual * factor_descuento).quantize(Decimal('0.01'))

        if descuento <= 0:
            return JsonResponse({'success': False, 'message': 'El descuento no genera reducción significativa'})

        # --- NUEVO: Crear un registro de pago con descuento ---
        pago = PagoCuentaPorCobrar.objects.create(
            cuenta=cuenta,
            monto=Decimal('0.00'),                     # No hay dinero real
            descuento_monto=descuento,                 # Aquí se guarda el descuento
            # Puedes poner 'descuento' si agregas esa opción
            metodo_pago='efectivo',
            referencia=f'DESC_{porcentaje}%',
            observaciones=f'Descuento del {porcentaje}% aplicado sobre saldo pendiente',
            usuario=request.user,
            fecha_pago=timezone.now()
        )
        # ------------------------------------------------

        # Actualizar la cuenta sumando el descuento al monto pagado
        nuevo_monto_pagado = min(
            cuenta.monto_total, cuenta.monto_pagado + descuento)
        cuenta.monto_pagado = nuevo_monto_pagado

        # Recalcular estado
        if cuenta.monto_pagado >= cuenta.monto_total:
            cuenta.estado = 'pagada'
            cuenta.monto_pagado = cuenta.monto_total
        elif cuenta.monto_pagado > 0:
            cuenta.estado = 'parcial'
        else:
            hoy = timezone.now().date()
            if cuenta.fecha_vencimiento and hoy > cuenta.fecha_vencimiento:
                cuenta.estado = 'vencida'
            else:
                cuenta.estado = 'pendiente'

        # Registrar en observaciones de la cuenta (opcional, ya que el pago ya tiene su observación)
        usuario = request.user
        fecha_hora = timezone.now().strftime('%d/%m/%Y %H:%M')
        obs_original = cuenta.observaciones or ''
        obs_nueva = f"\n[DESCUENTO] {porcentaje}% aplicado sobre saldo pendiente por {usuario.get_full_name() or usuario.username} el {fecha_hora}. Descuento: RD$ {descuento}."
        if len(obs_original) + len(obs_nueva) > 500:
            obs_original = obs_original[:400]
        cuenta.observaciones = obs_original + obs_nueva
        cuenta.save()

        return JsonResponse({
            'success': True,
            'message': f'Descuento del {porcentaje}% aplicado. Se redujo RD$ {descuento:,.2f} del saldo pendiente. Pago de descuento registrado con ID {pago.id}.'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


@login_required
def generar_historial_cliente_pdf(request, client_id):
    """
    Genera un PDF con el historial detallado de un cliente.
    Incluye clamp en monto_pagado para evitar que supere monto_total.
    Horas en zona horaria de República Dominicana (UTC-4) en formato 12h.
    Ahora muestra las observaciones de cada pago en una columna adicional.
    """
    try:
        from .models import Cliente, CuentaPorCobrar, PagoCuentaPorCobrar
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from decimal import Decimal
        from datetime import datetime
        import io
        import pytz

        tz_rd = pytz.timezone('America/Santo_Domingo')

        def formato_hora_rd(dt):
            """Convierte un datetime UTC a hora RD (UTC-4) en formato 12h"""
            if dt is None:
                return 'N/A'
            if timezone.is_aware(dt):
                dt = dt.astimezone(tz_rd)
            else:
                dt = pytz.utc.localize(dt).astimezone(tz_rd)
            return dt.strftime('%d/%m/%Y %I:%M %p')

        User = get_user_model()
        cliente = get_object_or_404(Cliente, id=client_id)

        cuentas = CuentaPorCobrar.objects.filter(
            cliente=cliente,
            anulada=False,
            eliminada=False
        ).select_related(
            'venta',
            'venta__vendedor'
        ).prefetch_related(
            'pagos',
            'pagos__usuario',
            'pagos__comprobante'
        ).order_by('venta__fecha_venta')

        if not cuentas.exists():
            return HttpResponse("El cliente no tiene cuentas registradas.", content_type='text/plain')

        response = HttpResponse(content_type='application/pdf')
        fecha_reporte = datetime.now(tz_rd).strftime('%Y%m%d_%H%M%S')
        nombre_limpio = "".join(
            c for c in cliente.full_name if c.isalnum() or c in "._- ").strip()
        response['Content-Disposition'] = f'attachment; filename="historial_{nombre_limpio}_{fecha_reporte}.pdf"'

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        styles = getSampleStyleSheet()
        contenido = []

        titulo_style = ParagraphStyle(
            'Titulo',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=10,
            alignment=1
        )
        contenido.append(
            Paragraph("HISTORIAL DE CUENTAS POR CLIENTE", titulo_style))
        contenido.append(Spacer(1, 0.5*cm))

        info_style = ParagraphStyle(
            'Info', parent=styles['Normal'], fontSize=10)
        contenido.append(
            Paragraph(f"<b>Cliente:</b> {cliente.full_name}", info_style))
        contenido.append(Paragraph(
            f"<b>Cédula/RNC:</b> {cliente.identification_number or 'N/A'}", info_style))
        contenido.append(
            Paragraph(f"<b>Teléfono:</b> {cliente.primary_phone or 'N/A'}", info_style))

        fecha_reporte_str = datetime.now(tz_rd).strftime('%d/%m/%Y %I:%M %p')
        contenido.append(
            Paragraph(f"<b>Fecha del reporte:</b> {fecha_reporte_str}", info_style))
        contenido.append(Spacer(1, 0.5*cm))

        # Calcular totales con clamp
        total_deuda = Decimal('0.00')
        total_pagado = Decimal('0.00')
        for cuenta in cuentas:
            monto_total = Decimal(str(cuenta.monto_total))
            monto_pagado_real = min(
                Decimal(str(cuenta.monto_pagado)), monto_total)
            saldo = max(monto_total - monto_pagado_real, Decimal('0.00'))
            if saldo > 0:
                total_deuda += saldo
            total_pagado += monto_pagado_real

        resumen_data = [
            ["Total deuda pendiente:",   f"RD$ {total_deuda:,.2f}"],
            ["Total pagado (histórico):", f"RD$ {total_pagado:,.2f}"],
        ]
        resumen_table = Table(resumen_data, colWidths=[6*cm, 4*cm])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR',     (0, 0), (-1, -1), colors.black),
            ('ALIGN',         (0, 0), (0, -1),  'LEFT'),
            ('ALIGN',         (1, 0), (1, -1),  'RIGHT'),
            ('FONTNAME',      (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOX',           (0, 0), (-1, -1), 1, colors.black),
        ]))
        contenido.append(resumen_table)
        contenido.append(Spacer(1, 0.7*cm))

        # Recorrer cada cuenta
        for cuenta in cuentas:
            factura_text = f"<b>Factura N°:</b> {cuenta.venta.numero_factura if cuenta.venta else 'N/A'}"
            if cuenta.venta and cuenta.venta.vendedor:
                vendedor = cuenta.venta.vendedor
                factura_text += f" | <b>Vendedor:</b> {vendedor.get_full_name() or vendedor.username}"
            contenido.append(Paragraph(factura_text, styles['Heading4']))

            fecha_venta_local = formato_hora_rd(
                cuenta.venta.fecha_venta) if cuenta.venta and cuenta.venta.fecha_venta else 'N/A'
            fecha_venc = cuenta.fecha_vencimiento.strftime(
                '%d/%m/%Y') if cuenta.fecha_vencimiento else 'N/A'
            estado = cuenta.get_estado_display()

            monto_total = Decimal(str(cuenta.monto_total))
            monto_pagado_real = min(
                Decimal(str(cuenta.monto_pagado)), monto_total)
            saldo = max(monto_total - monto_pagado_real, Decimal('0.00'))

            info_factura = [
                ["Campo",            "Valor"],
                ["Fecha venta",      fecha_venta_local],
                ["Vencimiento",      fecha_venc],
                ["Monto total",      f"RD$ {monto_total:,.2f}"],
                ["Monto pagado",     f"RD$ {monto_pagado_real:,.2f}"],
                ["Saldo pendiente",  f"RD$ {saldo:,.2f}"],
                ["Estado",           estado],
            ]
            tabla_factura = Table(info_factura, colWidths=[4.2*cm, 7.8*cm])
            tabla_factura.setStyle(TableStyle([
                ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#6c757d')),
                ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
                ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME',      (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME',      (1, 1), (1, -1), 'Helvetica'),
                ('FONTSIZE',      (0, 0), (-1, -1), 9),
                ('ALIGN',         (0, 0), (-1, 0),  'CENTER'),
                ('ALIGN',         (0, 1), (0, -1),  'LEFT'),
                ('ALIGN',         (1, 1), (1, -1),  'LEFT'),
                ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID',          (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND',    (0, 1), (-1, -1), colors.whitesmoke),
                ('TOPPADDING',    (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            contenido.append(tabla_factura)

            pagos = cuenta.pagos.all().order_by('-fecha_pago')
            if pagos:
                contenido.append(
                    Paragraph("<b>Pagos realizados:</b>", styles['Normal']))
                encabezado_pagos_style = ParagraphStyle(
                    'EncabezadoPagos',
                    parent=styles['Normal'],
                    fontSize=8,
                    leading=9,
                    alignment=1,
                    textColor=colors.white
                )
                celda_pagos_style = ParagraphStyle(
                    'CeldaPagos',
                    parent=styles['Normal'],
                    fontSize=7,
                    leading=8,
                    alignment=0,
                    wordWrap='CJK'
                )
                monto_pagos_style = ParagraphStyle(
                    'MontoPagos',
                    parent=celda_pagos_style,
                    alignment=2
                )

                # Cabecera con 7 columnas (incluye Observaciones)
                pago_data = [[
                    Paragraph("Fecha", encabezado_pagos_style),
                    Paragraph("Monto", encabezado_pagos_style),
                    Paragraph("Metodo", encabezado_pagos_style),
                    Paragraph("Referencia", encabezado_pagos_style),
                    Paragraph("Comprobante", encabezado_pagos_style),
                    Paragraph("Cobro", encabezado_pagos_style),
                    Paragraph("Observaciones", encabezado_pagos_style),
                ]]

                suma_pagos = Decimal('0.00')
                for pago in pagos:
                    suma_pagos += Decimal(str(pago.monto))

                factor_ajuste = None
                if suma_pagos > monto_total:
                    factor_ajuste = monto_total / suma_pagos

                for pago in pagos:
                    fecha_pago_local = formato_hora_rd(pago.fecha_pago)
                    comprobante = getattr(pago, 'comprobante', None)
                    comp_num = comprobante.numero_comprobante if comprobante else 'N/A'
                    usuario = pago.usuario.get_full_name(
                    ) or pago.usuario.username if pago.usuario else 'N/A'

                    monto_pago = Decimal(str(pago.monto))
                    if factor_ajuste is not None:
                        monto_pago = (
                            monto_pago * factor_ajuste).quantize(Decimal('0.01'))

                    observaciones = pago.observaciones.strip() if pago.observaciones else 'N/A'

                    pago_data.append([
                        Paragraph(fecha_pago_local, celda_pagos_style),
                        Paragraph(f"RD$ {monto_pago:,.2f}", monto_pagos_style),
                        Paragraph(pago.get_metodo_pago_display(),
                                  celda_pagos_style),
                        Paragraph(pago.referencia or 'N/A', celda_pagos_style),
                        Paragraph(comp_num, celda_pagos_style),
                        Paragraph(usuario, celda_pagos_style),
                        Paragraph(observaciones, celda_pagos_style),
                    ])

                # Anchos de columna para 7 columnas (total 18 cm, aprovecha mejor A4)
                tabla_pagos = Table(
                    pago_data,
                    colWidths=[
                        2.9*cm,   # Fecha
                        2.1*cm,   # Monto
                        2.0*cm,   # Metodo
                        2.3*cm,   # Referencia
                        2.5*cm,   # Comprobante
                        2.0*cm,   # Cobro
                        4.2*cm    # Observaciones
                    ]
                )
                tabla_pagos.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8a8178')),
                    ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
                    ('ALIGN',      (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN',      (0, 1), (-1, -1), 'LEFT'),
                    ('ALIGN',      (1, 1), (1, -1), 'RIGHT'),
                    ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE',   (0, 0), (-1, 0), 8),
                    ('FONTSIZE',   (0, 1), (-1, -1), 7),
                    ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                contenido.append(tabla_pagos)
            else:
                contenido.append(Paragraph(
                    "<i>No hay pagos registrados para esta factura.</i>", styles['Italic']))

            contenido.append(Spacer(1, 0.5*cm))
            contenido.append(Paragraph("<hr/>", styles['Normal']))
            contenido.append(Spacer(1, 0.3*cm))

        nota = Paragraph(
            "Reporte generado automáticamente por el sistema Super Bestia.",
            ParagraphStyle(
                'Nota', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
        )
        contenido.append(Spacer(1, 1*cm))
        contenido.append(nota)

        doc.build(contenido)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    except Exception as e:
        return HttpResponse(f"Error al generar el historial: {str(e)}", content_type='text/plain')


@login_required
def generar_reporte_vencidas_pdf(request):
    """
    Genera un PDF con todas las facturas vencidas, mostrando días de atraso.
    """
    try:
        from datetime import date
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from decimal import Decimal
        import io

        # Zona horaria República Dominicana
        tz_rd = pytz.timezone('America/Santo_Domingo')
        ahora_local = timezone.now().astimezone(tz_rd)
        fecha_reporte = ahora_local.strftime('%d/%m/%Y %I:%M %p')

        hoy = ahora_local.date()

        # Obtener solo cuentas realmente vencidas (1 día o más de atraso)
        cuentas = CuentaPorCobrar.objects.filter(
            estado='vencida',
            anulada=False,
            eliminada=False,
            fecha_vencimiento__lt=hoy
        ).select_related('cliente', 'venta').order_by('fecha_vencimiento')

        if not cuentas.exists():
            return HttpResponse("No hay facturas vencidas en este momento.", content_type='text/plain')

        data = []
        total_vencido = Decimal('0.00')
        for cuenta in cuentas:
            monto_pendiente = Decimal(
                str(cuenta.monto_total)) - Decimal(str(cuenta.monto_pagado))
            if monto_pendiente < 0:
                monto_pendiente = Decimal('0.00')
            dias_vencido = (
                hoy - cuenta.fecha_vencimiento).days if cuenta.fecha_vencimiento else 0
            if dias_vencido < 1:
                continue
            total_vencido += monto_pendiente
            data.append({
                'cliente': cuenta.cliente.full_name if cuenta.cliente else 'Cliente no disponible',
                'telefono': cuenta.cliente.primary_phone if cuenta.cliente else 'N/A',
                'factura': cuenta.venta.numero_factura if cuenta.venta else 'N/A',
                'fecha_vencimiento': cuenta.fecha_vencimiento.strftime('%d/%m/%Y') if cuenta.fecha_vencimiento else 'N/A',
                'dias_vencido': dias_vencido,
                'monto_pendiente': monto_pendiente,
            })

        if not data:
            return HttpResponse("No hay facturas vencidas en este momento.", content_type='text/plain')

        # Crear PDF
        response = HttpResponse(content_type='application/pdf')
        fecha_reporte_archivo = ahora_local.strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="facturas_vencidas_{fecha_reporte_archivo}.pdf"'

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        styles = getSampleStyleSheet()
        contenido = []

        # Título
        titulo_style = ParagraphStyle(
            'Titulo',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=10,
            alignment=1
        )
        contenido.append(
            Paragraph("REPORTE DE FACTURAS VENCIDAS", titulo_style))
        contenido.append(Spacer(1, 0.5*cm))

        # Subtítulo con fecha de generación
        contenido.append(
            Paragraph(f"Generado: {fecha_reporte}", styles['Normal']))
        contenido.append(Spacer(1, 0.5*cm))

        # Resumen en 2 columnas (arriba)
        resumen_data = [
            ["Total deuda vencida", "Total registros"],
            [f"RD$ {total_vencido:,.2f}", str(len(data))]
        ]
        tabla_resumen = Table(resumen_data, colWidths=[7*cm, 7*cm])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, 1), colors.whitesmoke),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        contenido.append(tabla_resumen)
        contenido.append(Spacer(1, 0.5*cm))

        # Tabla de facturas vencidas
        encabezado_style = ParagraphStyle(
            'EncabezadoVencidas',
            parent=styles['Normal'],
            fontSize=8,
            leading=9,
            alignment=1,
            textColor=colors.white
        )
        encabezados = [
            Paragraph("Cliente", encabezado_style),
            Paragraph("Teléfono", encabezado_style),
            Paragraph("Factura", encabezado_style),
            Paragraph("Fecha. Venc.", encabezado_style),
            Paragraph("Días", encabezado_style),
            Paragraph("Monto Pendiente", encabezado_style)
        ]
        datos_tabla = [encabezados]

        for item in data:
            cliente_corto = item['cliente'] if len(
                item['cliente']) <= 22 else f"{item['cliente'][:19]}..."
            fila = [
                cliente_corto,
                item['telefono'],
                item['factura'],
                item['fecha_vencimiento'],
                str(item['dias_vencido']),
                f"RD$ {item['monto_pendiente']:,.2f}"
            ]
            datos_tabla.append(fila)

        # Calcular ancho de columnas
        col_widths = [4.5*cm, 2.8*cm, 2.5*cm, 2.8*cm, 2.2*cm, 3*cm]
        tabla = Table(datos_tabla, colWidths=col_widths)

        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),
            ('ALIGN', (5, 1), (5, -1), 'RIGHT'),
        ]))

        contenido.append(tabla)
        contenido.append(Spacer(1, 0.7*cm))

        # Nota
        nota = Paragraph(
            "Este reporte incluye todas las facturas que actualmente están vencidas.",
            ParagraphStyle(
                'Nota', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
        )
        contenido.append(Spacer(1, 1*cm))
        contenido.append(nota)

        doc.build(contenido)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    except Exception as e:
        return HttpResponse(f"Error al generar reporte: {str(e)}", content_type='text/plain')

# ==================================================================================================
# ==============================Gestión de Suplidores (Proveedores)=================================
# ==================================================================================================


@user_passes_test(is_superuser_or_almacen, login_url='/')
@login_required
def gestiondesuplidores(request):
    proveedores = Proveedor.objects.all().order_by('nombre_empresa')
    paises = Proveedor.PAIS_CHOICES
    terminos_pago = Proveedor.TERMINOS_PAGO_CHOICES

    context = {
        'proveedores': proveedores,
        'paises': paises,
        'terminos_pago': terminos_pago,
        'user': request.user,  # Asegurar que el usuario esté en el contexto
    }
    return render(request, "facturacion/gestiondesuplidores.html", context)


def agregar_proveedor(request):
    if request.method == 'POST':
        try:
            Proveedor.objects.create(
                nombre_empresa=request.POST.get('companyName'),
                rnc=request.POST.get('rnc'),
                nombre_contacto=request.POST.get('contactName'),
                email=request.POST.get('email'),
                telefono=request.POST.get('phone'),
                whatsapp=request.POST.get('whatsapp', ''),
                pais=request.POST.get('country'),
                ciudad=request.POST.get('city'),
                direccion=request.POST.get('address', ''),
                terminos_pago=request.POST.get('paymentTerms', ''),
                limite_credito=request.POST.get('creditLimit', 0) or 0,
                notas=request.POST.get('notes', ''),
                activo=request.POST.get('isActive') == 'on'
            )
            messages.success(request, 'Proveedor agregado exitosamente')
            return redirect('gestiondesuplidores')
        except Exception as e:
            messages.error(request, f'Error al agregar proveedor: {str(e)}')
            return redirect('gestiondesuplidores')

    return redirect('gestiondesuplidores')


@csrf_exempt
def editar_proveedor(request):
    if request.method == 'POST':
        # Verificar si el usuario es superusuario
        if not request.user.is_superuser:
            error_msg = 'No tiene permisos para editar suplidores. Solo el superusuario puede realizar esta acción.'

            # Si es una petición AJAX, retornar JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_msg})
            else:
                messages.error(request, error_msg)
                return redirect('gestiondesuplidores')

        try:
            # Debug: ver qué datos están llegando
            print("Datos recibidos en editar_proveedor:")
            for key, value in request.POST.items():
                print(f"{key}: {value}")

            proveedor = get_object_or_404(
                Proveedor, id=request.POST.get('supplierId'))

            # Actualizar campos con los nombres correctos
            proveedor.nombre_empresa = request.POST.get('nombre_empresa')
            proveedor.rnc = request.POST.get('rnc')
            proveedor.nombre_contacto = request.POST.get('nombre_contacto')
            proveedor.email = request.POST.get('email')
            proveedor.telefono = request.POST.get('telefono')
            proveedor.whatsapp = request.POST.get('whatsapp', '')
            proveedor.pais = request.POST.get('pais')
            proveedor.ciudad = request.POST.get('ciudad')
            proveedor.direccion = request.POST.get('direccion', '')
            proveedor.terminos_pago = request.POST.get('terminos_pago', '')

            # Manejar límite de crédito (puede estar vacío)
            limite_credito = request.POST.get('limite_credito', '0')
            proveedor.limite_credito = float(
                limite_credito) if limite_credito else 0.0

            proveedor.notas = request.POST.get('notas', '')
            proveedor.activo = request.POST.get('activo') == 'on'

            proveedor.save()

            messages.success(request, 'Proveedor actualizado exitosamente')

            # Si es una petición AJAX, retornar JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Proveedor actualizado exitosamente'})
            else:
                return redirect('gestiondesuplidores')

        except Exception as e:
            error_msg = f'Error al actualizar proveedor: {str(e)}'
            print(error_msg)
            messages.error(request, error_msg)

            # Si es AJAX, retornar error en JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_msg})
            else:
                return redirect('gestiondesuplidores')

    # Si no es POST, redirigir
    return redirect('gestiondesuplidores')


@require_POST
def eliminar_proveedor(request):
    try:
        # Verificar si el usuario es superusuario
        if not request.user.is_superuser:
            messages.error(
                request, 'No tiene permisos para eliminar suplidores. Solo el superusuario puede realizar esta acción.')
            return redirect('gestiondesuplidores')

        proveedor = get_object_or_404(
            Proveedor, id=request.POST.get('supplierId'))
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado exitosamente')
    except Exception as e:
        messages.error(request, f'Error al eliminar proveedor: {str(e)}')

    return redirect('gestiondesuplidores')


def get_proveedor_data(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    data = {
        'id': proveedor.id,
        'nombre_empresa': proveedor.nombre_empresa,
        'rnc': proveedor.rnc,
        'nombre_contacto': proveedor.nombre_contacto,
        'email': proveedor.email,
        'telefono': proveedor.telefono,
        'whatsapp': proveedor.whatsapp or '',
        'pais': proveedor.pais,
        'ciudad': proveedor.ciudad,
        'direccion': proveedor.direccion or '',
        'terminos_pago': proveedor.terminos_pago or '',
        'limite_credito': str(proveedor.limite_credito),
        'notas': proveedor.notas or '',
        'activo': proveedor.activo
    }
    return JsonResponse(data)


@user_passes_test(is_superuser_or_almacen, login_url='/')
@login_required
def registrosuplidores(request):
    if request.method == 'POST':
        # Crear el proveedor directamente desde los datos del request
        try:
            proveedor = Proveedor(
                nombre_empresa=request.POST.get('nombre_empresa'),
                rnc=request.POST.get('rnc'),
                nombre_contacto=request.POST.get('nombre_contacto'),
                email=request.POST.get('email'),
                telefono=request.POST.get('telefono'),
                whatsapp=request.POST.get('whatsapp', ''),  # Campo opcional
                pais=request.POST.get('pais'),
                ciudad=request.POST.get('ciudad'),
                # categoria=request.POST.get('categoria'),
                direccion=request.POST.get('direccion', ''),  # Campo opcional
                terminos_pago=request.POST.get(
                    'terminos_pago', ''),  # Campo opcional
                limite_credito=request.POST.get(
                    'limite_credito', 0) or 0,  # Valor por defecto 0
                notas=request.POST.get('notas', ''),  # Campo opcional
                activo=request.POST.get('activo') == 'on'  # Checkbox
            )
            proveedor.full_clean()  # Validar los datos según las reglas del modelo
            proveedor.save()
            messages.success(request, 'Suplidor registrado exitosamente')
            return redirect('registrosuplidores')

        except Exception as e:
            # Manejar errores de validación
            messages.error(
                request, f'Error al registrar el suplidor: {str(e)}')
            # Pasar los valores ingresados de vuelta al template para mantenerlos en el formulario
            context = {
                'valores': request.POST,
                'error': str(e)
            }
            return render(request, "facturacion/registrosuplidores.html", context)

    # Si es GET, mostrar el formulario vacío
    return render(request, "facturacion/registrosuplidores.html")

    # ESTE ES EL NUEVO DE CIEERE DE CAJA


# ==================================================================================================
# views.py
logger = logging.getLogger(__name__)


@login_required
def cierredecaja(request):
    # Verificar si hay una caja abierta HOY
    today = timezone.localtime(timezone.now()).date()
    caja_abierta = Caja.objects.filter(
        usuario=request.user,
        estado='abierta',
        fecha_apertura__date=today
    ).first()

    if not caja_abierta:
        messages.error(
            request, 'No hay una caja abierta hoy. Debe abrir una caja primero.')
        return redirect('iniciocaja')

    # Obtener ventas desde la apertura de caja para el usuario actual
    ventas_periodo = Venta.objects.filter(
        vendedor=request.user,
        fecha_venta__gte=caja_abierta.fecha_apertura,
        completada=True,
        anulada=False
    )

    # VENTAS AL CONTADO - Usamos el TOTAL FINAL
    ventas_contado_efectivo = ventas_periodo.filter(
        tipo_venta='contado',
        metodo_pago='efectivo'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

    ventas_contado_tarjeta = ventas_periodo.filter(
        tipo_venta='contado',
        metodo_pago='tarjeta'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

    ventas_contado_transferencia = ventas_periodo.filter(
        tipo_venta='contado',
        metodo_pago='transferencia'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

    # VENTAS A CRÉDITO - Usamos solo el MONTO INICIAL
    ventas_credito_efectivo = ventas_periodo.filter(
        tipo_venta='credito',
        metodo_pago='efectivo'
    ).aggregate(total=Sum('montoinicial'))['total'] or Decimal('0.00')

    ventas_credito_tarjeta = ventas_periodo.filter(
        tipo_venta='credito',
        metodo_pago='tarjeta'
    ).aggregate(total=Sum('montoinicial'))['total'] or Decimal('0.00')

    ventas_credito_transferencia = ventas_periodo.filter(
        tipo_venta='credito',
        metodo_pago='transferencia'
    ).aggregate(total=Sum('montoinicial'))['total'] or Decimal('0.00')

    # CALCULAR TOTALES AJUSTADOS
    ventas_efectivo_ajustado = ventas_contado_efectivo + ventas_credito_efectivo
    ventas_tarjeta_ajustado = ventas_contado_tarjeta + ventas_credito_tarjeta
    ventas_transferencia_ajustado = ventas_contado_transferencia + \
        ventas_credito_transferencia

    total_ventas_ajustado = (ventas_contado_efectivo + ventas_contado_tarjeta + ventas_contado_transferencia +
                             ventas_credito_efectivo + ventas_credito_tarjeta + ventas_credito_transferencia)

    # Verificar hora actual
    now = timezone.localtime(timezone.now())
    hora_actual = now.time()
    hora_limite = time(17, 30, 0)  # 5:30 PM
    es_despues_de_limite = hora_actual > hora_limite

    context = {
        'caja_abierta': caja_abierta,
        'total_ventas': total_ventas_ajustado,
        'ventas_efectivo': ventas_efectivo_ajustado,
        'ventas_tarjeta': ventas_tarjeta_ajustado,
        'ventas_transferencia': ventas_transferencia_ajustado,
        'total_ventas_contado': ventas_contado_efectivo + ventas_contado_tarjeta + ventas_contado_transferencia,
        'total_ventas_credito': ventas_credito_efectivo + ventas_credito_tarjeta + ventas_credito_transferencia,
        'cantidad_ventas': ventas_periodo.count(),
        'hoy': today,
        'current_time': hora_actual.strftime('%H:%M'),
        'is_after_cutoff': es_despues_de_limite,
    }

    return render(request, "facturacion/cierredecaja.html", context)


@login_required
def procesar_cierre_caja(request):
    if request.method == 'POST':
        logger.info(f"==== INICIANDO PROCESO DE CIERRE ====")
        logger.info(f"Usuario: {request.user.username}")
        logger.info(f"Datos POST: {dict(request.POST)}")

        # Verificar si es un cierre automático
        es_automatico = request.POST.get('es_automatico') == 'true'
        logger.info(f"Es cierre automático: {es_automatico}")

        # Obtener la caja abierta actual
        caja_abierta = Caja.objects.filter(
            usuario=request.user, estado='abierta').first()

        if not caja_abierta:
            error_msg = 'No hay una caja abierta para cerrar.'
            logger.error(error_msg)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or es_automatico:
                return JsonResponse({
                    'success': False,
                    'message': error_msg
                })
            messages.error(request, error_msg)
            return redirect('cierredecaja')

        logger.info(
            f"Caja encontrada: ID={caja_abierta.id}, Fecha apertura={caja_abierta.fecha_apertura}")

        # Obtener ventas desde la apertura de caja
        ventas_periodo = Venta.objects.filter(
            vendedor=request.user,
            fecha_venta__gte=caja_abierta.fecha_apertura,
            completada=True,
            anulada=False
        )

        logger.info(f"Total ventas en período: {ventas_periodo.count()}")

        # VENTAS AL CONTADO - Usamos el TOTAL FINAL
        ventas_contado_efectivo = ventas_periodo.filter(
            tipo_venta='contado',
            metodo_pago='efectivo'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        ventas_contado_tarjeta = ventas_periodo.filter(
            tipo_venta='contado',
            metodo_pago='tarjeta'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        ventas_contado_transferencia = ventas_periodo.filter(
            tipo_venta='contado',
            metodo_pago='transferencia'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        # VENTAS A CRÉDITO - Usamos solo el MONTO INICIAL
        ventas_credito_efectivo = ventas_periodo.filter(
            tipo_venta='credito',
            metodo_pago='efectivo'
        ).aggregate(total=Sum('montoinicial'))['total'] or Decimal('0.00')

        ventas_credito_tarjeta = ventas_periodo.filter(
            tipo_venta='credito',
            metodo_pago='tarjeta'
        ).aggregate(total=Sum('montoinicial'))['total'] or Decimal('0.00')

        ventas_credito_transferencia = ventas_periodo.filter(
            tipo_venta='credito',
            metodo_pago='transferencia'
        ).aggregate(total=Sum('montoinicial'))['total'] or Decimal('0.00')

        # Calcular total esperado (igual que en cierredecaja)
        total_esperado = (ventas_contado_efectivo + ventas_contado_tarjeta + ventas_contado_transferencia +
                          ventas_credito_efectivo + ventas_credito_tarjeta + ventas_credito_transferencia)

        logger.info(f"Total esperado calculado: RD${total_esperado}")

        # Si es cierre automático, usar montos de ventas
        if es_automatico:
            monto_efectivo_real = ventas_contado_efectivo + ventas_credito_efectivo
            monto_tarjeta_real = ventas_contado_tarjeta + ventas_credito_tarjeta
            observaciones = f"Cierre automático a las {timezone.localtime(timezone.now()).strftime('%H:%M:%S')}"
            logger.info(
                f"Cierre automático - Montos: Efectivo={monto_efectivo_real}, Tarjeta={monto_tarjeta_real}")
        else:
            # Obtener datos del formulario
            monto_efectivo_real = request.POST.get('cash-amount', '0')
            monto_tarjeta_real = request.POST.get('card-amount', '0')
            observaciones = request.POST.get('observations', '')

            logger.info(
                f"Cierre manual - Montos recibidos: Efectivo={monto_efectivo_real}, Tarjeta={monto_tarjeta_real}")

            # Convertir a Decimal
            try:
                monto_efectivo_real = Decimal(monto_efectivo_real)
                monto_tarjeta_real = Decimal(monto_tarjeta_real)
            except (ValueError, InvalidOperation) as e:
                error_msg = f'Los montos deben ser valores numéricos válidos. Error: {str(e)}'
                logger.error(error_msg)

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_msg
                    })
                messages.error(request, error_msg)
                return redirect('cierredecaja')

        # Calcular total real y diferencia
        total_real = monto_efectivo_real + monto_tarjeta_real
        diferencia = total_real - total_esperado

        logger.info(
            f"Total real: RD${total_real}, Diferencia: RD${diferencia}")

        # Actualizar la caja
        now = timezone.now()
        hora_actual = timezone.localtime(now).time()

        caja_abierta.monto_final = total_real
        caja_abierta.fecha_cierre = now
        caja_abierta.estado = 'cerrada'
        caja_abierta.tipo_cierre = 'automatico' if es_automatico else 'manual'
        caja_abierta.observaciones = observaciones
        caja_abierta.hora_cierre_exacta = hora_actual

        logger.info(
            f"Actualizando caja: Estado=cerrada, Tipo={caja_abierta.tipo_cierre}, Hora={hora_actual}")

        try:
            caja_abierta.save()
            logger.info(
                f"Caja actualizada exitosamente. ID: {caja_abierta.id}")
        except Exception as e:
            error_msg = f'Error al actualizar la caja: {str(e)}'
            logger.error(error_msg, exc_info=True)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_msg
                })
            messages.error(request, error_msg)
            return redirect('cierredecaja')

        # Crear registro de cierre en la tabla CierreCaja
        logger.info(f"Creando registro en CierreCaja...")

        try:
            cierre = CierreCaja.objects.create(
                caja=caja_abierta,
                monto_efectivo_real=monto_efectivo_real,
                monto_tarjeta_real=monto_tarjeta_real,
                total_esperado=total_esperado,
                diferencia=diferencia,
                observaciones=observaciones,
                tipo_cierre='automatico' if es_automatico else 'manual',
                hora_cierre_exacta=hora_actual
            )

            logger.info(f"¡CierreCaja creado exitosamente! ID: {cierre.id}")
            logger.info(f"Datos guardados: Efectivo=RD${monto_efectivo_real}, "
                        f"Tarjeta=RD${monto_tarjeta_real}, "
                        f"Esperado=RD${total_esperado}, "
                        f"Diferencia=RD${diferencia}")

        except Exception as e:
            error_msg = f'Error al crear registro de cierre: {str(e)}'
            logger.error(error_msg, exc_info=True)

            # Aunque falle el registro detallado, la caja ya está cerrada
            # Continuamos pero registramos el error

        # Si es cierre automático o petición AJAX, responder con JSON
        if es_automatico or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response_data = {
                'success': True,
                'message': 'Caja cerrada exitosamente',
                'redirect_url': reverse('iniciocaja')
            }
            logger.info(f"Respondiendo con JSON: {response_data}")
            return JsonResponse(response_data)

        # Para cierre manual normal, crear información para la sesión
        request.session['cierre_info'] = {
            'fecha': now.date().strftime('%d/%m/%Y'),
            'hora_cierre': now.strftime('%H:%M:%S'),
            'monto_efectivo_real': float(monto_efectivo_real),
            'monto_tarjeta_real': float(monto_tarjeta_real),
            'total_esperado': float(total_esperado),
            'diferencia': float(diferencia),
            'observaciones': observaciones,
            'ventas_count': ventas_periodo.count(),
            'clientes_count': Cliente.objects.filter(
                venta__in=ventas_periodo
            ).distinct().count()
        }

        success_msg = f'Caja cerrada exitosamente. Diferencia: RD${diferencia:,.2f}'
        logger.info(success_msg)
        messages.success(request, success_msg)
        return redirect('cuadre')

    logger.warning("Intento de acceso a procesar_cierre_caja con método GET")
    return redirect('cierredecaja')


def cerrar_caja_individual(caja, cutoff_time, today):
    """
    Cierra una caja individual automáticamente
    """
    try:
        usuario = caja.usuario

        # Obtener ventas desde la apertura de caja
        ventas_periodo = Venta.objects.filter(
            vendedor=usuario,
            fecha_venta__gte=caja.fecha_apertura,
            completada=True,
            anulada=False
        )

        # VENTAS AL CONTADO
        ventas_contado_efectivo = ventas_periodo.filter(
            tipo_venta='contado',
            metodo_pago='efectivo'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        ventas_contado_tarjeta = ventas_periodo.filter(
            tipo_venta='contado',
            metodo_pago='tarjeta'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        ventas_contado_transferencia = ventas_periodo.filter(
            tipo_venta='contado',
            metodo_pago='transferencia'
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        # VENTAS A CRÉDITO (solo monto inicial)
        ventas_credito_efectivo = ventas_periodo.filter(
            tipo_venta='credito',
            metodo_pago='efectivo'
        ).aggregate(total=Sum('montoinicial'))['total'] or Decimal('0.00')

        ventas_credito_tarjeta = ventas_periodo.filter(
            tipo_venta='credito',
            metodo_pago='tarjeta'
        ).aggregate(total=Sum('montoinicial'))['total'] or Decimal('0.00')

        ventas_credito_transferencia = ventas_periodo.filter(
            tipo_venta='credito',
            metodo_pago='transferencia'
        ).aggregate(total=Sum('montoinicial'))['total'] or Decimal('0.00')

        # Calcular totales
        total_efectivo_vendido = ventas_contado_efectivo + ventas_credito_efectivo
        total_tarjeta_vendido = ventas_contado_tarjeta + ventas_credito_tarjeta
        total_transferencia_vendido = ventas_contado_transferencia + \
            ventas_credito_transferencia

        total_esperado = total_efectivo_vendido + \
            total_tarjeta_vendido + total_transferencia_vendido

        # Usar montos de ventas como montos reales
        monto_efectivo_real = total_efectivo_vendido
        monto_tarjeta_real = total_tarjeta_vendido
        total_real = monto_efectivo_real + monto_tarjeta_real

        # Diferencia (debería ser 0)
        diferencia = total_real - total_esperado

        # Crear fecha y hora de cierre
        hora_cierre_exacta = cutoff_time
        fecha_cierre_completa = datetime.combine(today, hora_cierre_exacta)
        fecha_cierre_completa = timezone.make_aware(fecha_cierre_completa)

        # Actualizar la caja
        caja.monto_final = total_real
        caja.fecha_cierre = fecha_cierre_completa
        caja.hora_cierre_exacta = hora_cierre_exacta
        caja.estado = 'cerrada'
        caja.tipo_cierre = 'automatico'

        observaciones = (
            f'Cierre automático ejecutado a las {hora_cierre_exacta.strftime("%H:%M")} PM por el sistema. '
            f'Montos basados en ventas reales. '
            f'Total ventas: RD${total_esperado:,.2f}. '
            f'Efectivo: RD${monto_efectivo_real:,.2f}, Tarjeta: RD${monto_tarjeta_real:,.2f}, '
            f'Transferencia: RD${total_transferencia_vendido:,.2f}.'
        )
        caja.observaciones = observaciones
        caja.save()

        # Crear registro de cierre
        cierre = CierreCaja.objects.create(
            caja=caja,
            monto_efectivo_real=monto_efectivo_real,
            monto_tarjeta_real=monto_tarjeta_real,
            total_esperado=total_esperado,
            diferencia=diferencia,
            observaciones=observaciones,
            tipo_cierre='automatico',
            hora_cierre_exacta=hora_cierre_exacta
        )

        return {
            'success': True,
            'message': f'Caja cerrada. Total: RD${total_real:,.2f}, Ventas: {ventas_periodo.count()}',
            'cierre_id': cierre.id
        }

    except Exception as e:
        logger.error(
            f"Error al cerrar caja individual {caja.id}: {str(e)}", exc_info=True)
        return {
            'success': False,
            'message': str(e)
        }


def cerrar_todas_cajas_automaticamente():
    """
    Cierra TODAS las cajas abiertas automáticamente a las 5:30 PM
    """
    try:
        now = timezone.localtime(timezone.now())
        today = now.date()

        # Buscar todas las cajas abiertas (sin importar la fecha)
        cajas_abiertas = Caja.objects.filter(estado='abierta')

        if not cajas_abiertas.exists():
            logger.info(
                f"[{now}] No hay cajas abiertas para cerrar automáticamente")
            return {
                'success': True,
                'message': 'No hay cajas abiertas',
                'cajas_cerradas': 0
            }

        exitosos = 0
        fallidos = 0
        detalles = []
        cutoff_time = time(17, 30, 0)  # 5:30 PM

        for caja in cajas_abiertas:
            try:
                # Obtener ventas desde la apertura de caja
                ventas_periodo = Venta.objects.filter(
                    vendedor=caja.usuario,
                    fecha_venta__gte=caja.fecha_apertura,
                    completada=True,
                    anulada=False
                )

                # Calcular totales
                total_efectivo_vendido = ventas_periodo.filter(
                    metodo_pago='efectivo'
                ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

                total_tarjeta_vendido = ventas_periodo.filter(
                    metodo_pago='tarjeta'
                ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

                total_transferencia_vendido = ventas_periodo.filter(
                    metodo_pago='transferencia'
                ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

                total_esperado = total_efectivo_vendido + \
                    total_tarjeta_vendido + total_transferencia_vendido

                # Crear fecha y hora de cierre
                hora_cierre_exacta = cutoff_time
                fecha_cierre_completa = datetime.combine(
                    today, hora_cierre_exacta)
                fecha_cierre_completa = timezone.make_aware(
                    fecha_cierre_completa)

                # Actualizar la caja
                caja.monto_final = total_esperado
                caja.fecha_cierre = fecha_cierre_completa
                caja.hora_cierre_exacta = hora_cierre_exacta
                caja.estado = 'cerrada'
                caja.tipo_cierre = 'automatico'
                observaciones = f'Cierre automático a las {hora_cierre_exacta.strftime("%H:%M")} PM'
                caja.observaciones = observaciones
                caja.save()

                # Crear registro de cierre
                cierre = CierreCaja.objects.create(
                    caja=caja,
                    monto_efectivo_real=total_efectivo_vendido,
                    monto_tarjeta_real=total_tarjeta_vendido,
                    total_esperado=total_esperado,
                    diferencia=Decimal('0.00'),
                    observaciones=observaciones,
                    tipo_cierre='automatico',
                    hora_cierre_exacta=hora_cierre_exacta
                )

                exitosos += 1
                detalles.append(
                    f"✓ {caja.usuario.username}: Cerrada automáticamente")
                logger.info(
                    f"Caja {caja.id} cerrada automáticamente para {caja.usuario.username}")

            except Exception as e:
                fallidos += 1
                detalles.append(f"✗ {caja.usuario.username}: Error: {str(e)}")
                logger.error(f"Error al cerrar caja {caja.id}: {str(e)}")

        # Resumen
        resumen = f"Proceso completado. {exitosos} exitoso(s), {fallidos} fallido(s)"
        logger.info(f"CIERRE AUTOMÁTICO MASIVO: {resumen}")

        return True, {
            'exitosos': exitosos,
            'fallidos': fallidos,
            'resumen': resumen,
            'detalles': detalles
        }

    except Exception as e:
        logger.error(f"Error en cierre automático masivo: {str(e)}")
        return False, f"Error: {str(e)}"


@shared_task
def cerrar_cajas_5_30_pm():
    """
    Tarea que se ejecuta automáticamente todos los días a las 5:30 PM
    """
    logger.info("Iniciando cierre automático de cajas a las 5:30 PM...")
    success, result = cerrar_todas_cajas_automaticamente()
    return {
        'success': success,
        'result': result
    }


@login_required
def cuadre(request):
    # Obtener la caja abierta actual o la última cerrada
    caja_actual = Caja.objects.filter(
        usuario=request.user, estado='abierta').first()

    if not caja_actual:
        caja_actual = Caja.objects.filter(
            usuario=request.user, estado='cerrada').order_by('-fecha_cierre').first()

    context = {'caja': None, 'ventas': {}, 'cierre': None}

    if caja_actual:
        # Obtener ventas de esta caja
        ventas = Venta.objects.filter(
            vendedor=request.user,
            fecha_venta__gte=caja_actual.fecha_apertura,
            completada=True,
            anulada=False
        )

        if caja_actual.fecha_cierre:
            ventas = ventas.filter(fecha_venta__lte=caja_actual.fecha_cierre)

        cierre = CierreCaja.objects.filter(caja=caja_actual).first()

        # CORRECCIÓN: Calcular por método de pago sumando contado + monto inicial créditos
        # Efectivo: ventas al contado en efectivo + monto inicial créditos en efectivo
        ventas_contado_efectivo = ventas.filter(tipo_venta='contado', metodo_pago='efectivo').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')
        ventas_credito_efectivo = ventas.filter(
            tipo_venta='credito', metodo_pago='efectivo')
        montoinicial_credito_efectivo = ventas_credito_efectivo.aggregate(
            total=Sum('montoinicial'))['total'] or Decimal('0.00')
        total_efectivo_mostrar = ventas_contado_efectivo + montoinicial_credito_efectivo

        # Tarjeta: ventas al contado con tarjeta + monto inicial créditos con tarjeta
        ventas_contado_tarjeta = ventas.filter(tipo_venta='contado', metodo_pago='tarjeta').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')
        ventas_credito_tarjeta = ventas.filter(
            tipo_venta='credito', metodo_pago='tarjeta')
        montoinicial_credito_tarjeta = ventas_credito_tarjeta.aggregate(
            total=Sum('montoinicial'))['total'] or Decimal('0.00')
        total_tarjeta_mostrar = ventas_contado_tarjeta + montoinicial_credito_tarjeta

        # Transferencia: ventas al contado con transferencia + monto inicial créditos con transferencia
        ventas_contado_transferencia = ventas.filter(tipo_venta='contado', metodo_pago='transferencia').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')
        ventas_credito_transferencia = ventas.filter(
            tipo_venta='credito', metodo_pago='transferencia')
        montoinicial_credito_transferencia = ventas_credito_transferencia.aggregate(
            total=Sum('montoinicial'))['total'] or Decimal('0.00')
        total_transferencia_mostrar = ventas_contado_transferencia + \
            montoinicial_credito_transferencia

        # Monto inicial total de todos los créditos (para el cuadre de caja)
        ventas_credito = ventas.filter(tipo_venta='credito')
        montoinicial_credito_total = ventas_credito.aggregate(
            total=Sum('montoinicial'))['total'] or Decimal('0.00')

        # Ventas totales al contado (para el Total General)
        ventas_contado_total = ventas.filter(tipo_venta='contado').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')

        # CORRECCIÓN FINAL: TOTAL GENERAL = ventas al contado (TOTAL) + monto inicial créditos (TOTAL)
        total_general = ventas_contado_total + montoinicial_credito_total

        # EFECTIVO para cuadre de caja = solo montos iniciales de créditos
        total_efectivo_cuadre = montoinicial_credito_total

        # CALCULAR MONTO CONTADO REAL
        monto_contado = caja_actual.monto_inicial + total_efectivo_cuadre

        # DEBUG: Verificar cálculos
        print("=== CÁLCULOS FINALES CORREGIDOS ===")
        print(
            f"Efectivo mostrar: {total_efectivo_mostrar} (contado: {ventas_contado_efectivo} + crédito: {montoinicial_credito_efectivo})")
        print(
            f"Tarjeta mostrar: {total_tarjeta_mostrar} (contado: {ventas_contado_tarjeta} + crédito: {montoinicial_credito_tarjeta})")
        print(
            f"Transferencia mostrar: {total_transferencia_mostrar} (contado: {ventas_contado_transferencia} + crédito: {montoinicial_credito_transferencia})")
        print(f"Ventas al contado total: {ventas_contado_total}")
        print(f"Monto inicial créditos total: {montoinicial_credito_total}")
        print(f"Total general: {total_general}")
        print(f"Efectivo cuadre: {total_efectivo_cuadre}")

        context = {
            'caja': caja_actual,
            'ventas': {
                'efectivo_cuadre': total_efectivo_cuadre,  # Solo para cuadre de caja
                # Para mostrar: contado + crédito efectivo
                'efectivo_mostrar': total_efectivo_mostrar,
                # Para mostrar: contado + crédito tarjeta
                'tarjeta_mostrar': total_tarjeta_mostrar,
                # Para mostrar: contado + crédito transferencia
                'transferencia_mostrar': total_transferencia_mostrar,
                'ventas_contado_total': ventas_contado_total,  # Total ventas al contado
                # Total monto inicial créditos
                'montoinicial_credito_total': montoinicial_credito_total,
                'total': total_general,
                # Detalles para desglose
                'contado_efectivo': ventas_contado_efectivo,
                'credito_efectivo': montoinicial_credito_efectivo,
                'contado_tarjeta': ventas_contado_tarjeta,
                'credito_tarjeta': montoinicial_credito_tarjeta,
                'contado_transferencia': ventas_contado_transferencia,
                'credito_transferencia': montoinicial_credito_transferencia,
            },
            'cierre': cierre
        }

    return render(request, 'facturacion/cuadre.html', context)
# ========================================================================================


@user_passes_test(is_superuser, login_url='/')
@login_required
def reavastecer(request):
    # Obtener todos los productos activos
    productos = EntradaProducto.objects.filter(activo=True)

    # Preparar datos para el template
    productos_data = []
    for producto in productos:
        # Obtener URL de la imagen si existe
        imagen_url = producto.imagen.url if producto.imagen and hasattr(
            producto.imagen, 'url') else None

        productos_data.append({
            'id': producto.id,
            'name': producto.descripcion,
            'brand': producto.get_marca_display(),
            'model': f"{producto.compatibilidad if producto.compatibilidad else ''}",
            'stock': producto.cantidad,
            'price': float(producto.precio),
            'min_stock': producto.cantidad_minima,
            'imagen_url': imagen_url  # Agregar URL de la imagen
        })

    # Calcular valor total con formato
    valor_total = sum(p.cantidad * p.precio for p in productos)

    context = {
        'productos': productos_data,
        'total_productos': productos.count(),
        'productos_stock_bajo': productos.filter(cantidad__lte=models.F('cantidad_minima')).count(),
        'valor_total': valor_total
    }

    return render(request, "facturacion/reavastecer.html", context)


@csrf_exempt
@require_POST
def actualizar_stock(request):
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        nueva_cantidad = data.get('nueva_cantidad')

        # Validar datos
        if not producto_id or nueva_cantidad is None:
            return JsonResponse({'success': False, 'error': 'Datos incompletos'})

        # Validar que la cantidad sea un número positivo
        try:
            nueva_cantidad = int(nueva_cantidad)
            if nueva_cantidad < 0:
                return JsonResponse({'success': False, 'error': 'La cantidad no puede ser negativa'})
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Cantidad inválida'})

        # Buscar y actualizar el producto
        producto = EntradaProducto.objects.get(id=producto_id, activo=True)

        # Guardar cantidad anterior para el movimiento de stock
        cantidad_anterior = producto.cantidad

        # Actualizar cantidad
        producto.cantidad = nueva_cantidad
        producto.save()

        # Registrar movimiento de stock
        MovimientoStock = apps.get_model('facturacion', 'MovimientoStock')
        MovimientoStock.objects.create(
            producto=producto,
            tipo_movimiento='ajuste',
            cantidad=abs(cantidad_anterior - nueva_cantidad),
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=nueva_cantidad,
            motivo="Ajuste manual desde sistema de reabastecimiento",
            usuario=request.user if request.user.is_authenticated else None
        )

        return JsonResponse({
            'success': True,
            'nuevo_stock': producto.cantidad,
            'producto_nombre': producto.descripcion
        })

    except EntradaProducto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def devoluciones(request):
    return render(request, "facturacion/devoluciones.html")


@csrf_exempt
@require_http_methods(["POST"])
def buscar_factura_devolucion(request):
    try:
        data = json.loads(request.body)
        numero_factura = data.get('numero_factura', '').strip()

        if not numero_factura:
            return JsonResponse({'error': 'Por favor, ingrese un número de factura.'}, status=400)

        # Buscar la factura
        try:
            venta = Venta.objects.get(
                numero_factura=numero_factura, anulada=False)
        except Venta.DoesNotExist:
            return JsonResponse({'error': 'No se encontró ninguna factura con ese número.'}, status=404)

        # Obtener detalles de la venta
        detalles = DetalleVenta.objects.filter(venta=venta)

        # Preparar información de productos
        productos = []
        for detalle in detalles:
            producto = detalle.producto

            # Obtener imagen si existe
            imagen_url = '/static/images/default-product.png'
            if producto.imagen and hasattr(producto.imagen, 'url'):
                try:
                    imagen_url = producto.imagen.url
                except:
                    pass

            producto_info = {
                'id': detalle.id,
                'codigo': producto.codigo_producto,
                'producto': producto.descripcion,  # Usar descripcion en lugar de nombre_producto
                'marca': producto.get_marca_display() if producto.marca else 'N/A',
                'capacidad': 'N/A',  # Tu modelo no tiene campo capacidad
                'color': producto.get_color_display() if producto.color else 'N/A',
                # Tu modelo no tiene campo estado, usa activo
                'estado': 'Activo' if producto.activo else 'Inactivo',
                'cantidad': detalle.cantidad,
                'precio': str(detalle.precio_unitario),
                'chasis': 'N/A',  # Tu modelo no tiene imei_serial
                'imagen': imagen_url
            }
            productos.append(producto_info)

        # Información de la factura
        factura_info = {
            'id': venta.numero_factura,
            'fecha': venta.fecha_venta.strftime('%d/%m/%Y'),
            'cliente': venta.cliente_nombre,
            'total': str(venta.total),
            'estado': 'Pagada' if venta.completada else 'Pendiente',
            'vendedor': venta.vendedor.get_full_name() or venta.vendedor.username,
            'productos': productos
        }

        return JsonResponse({'factura': factura_info})

    except Exception as e:
        import traceback
        traceback.print_exc()  # Esto imprimirá el error completo en la consola
        return JsonResponse({'error': f'Error interno al buscar la factura: {str(e)}'}, status=500)


def registrar_movimiento_cuenta(cuenta, monto, tipo_movimiento, usuario, observaciones, referencia=None):
    """
    Registra un movimiento en la cuenta por cobrar para auditoría
    """
    from .models import MovimientoCuentaPorCobrar

    # Buscar si ya existe el modelo MovimientoCuentaPorCobrar
    try:
        MovimientoCuentaPorCobrar.objects.create(
            cuenta=cuenta,
            monto=monto,
            tipo_movimiento=tipo_movimiento,
            usuario=usuario,
            observaciones=observaciones,
            referencia=referencia
        )
    except:
        # Si no existe el modelo, solo registrar en logs
        print(f"Movimiento de Cuenta - {cuenta.id}: {observaciones}")


@user_passes_test(is_superuser, login_url='/')
@csrf_exempt
@require_http_methods(["POST"])
@transaction.atomic
def procesar_devolucion(request):
    try:
        data = json.loads(request.body)

        # Validar datos requeridos
        required_fields = ['factura_id', 'producto_id', 'motivo', 'cantidad']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'error': f'El campo {field} es requerido.'}, status=400)

        # Obtener la venta y el detalle
        venta = get_object_or_404(
            Venta, numero_factura=data['factura_id'], anulada=False)
        detalle = get_object_or_404(
            DetalleVenta, id=data['producto_id'], venta=venta)

        # Validar cantidad
        cantidad_devolver = int(data['cantidad'])
        if cantidad_devolver <= 0:
            return JsonResponse({'error': 'La cantidad a devolver debe ser mayor a 0.'}, status=400)

        if cantidad_devolver > detalle.cantidad:
            return JsonResponse({'error': 'No puede devolver más unidades de las vendidas.'}, status=400)

        # Realizar la devolución
        producto = detalle.producto
        producto.sumar_stock(
            cantidad=cantidad_devolver,
            usuario=request.user,
            motivo=f"Devolución - {data['motivo']}",
            referencia=f"Factura: {venta.numero_factura}"
        )

        # Calcular monto a descontar de la cuenta por cobrar
        monto_devolucion = cantidad_devolver * detalle.precio_unitario

        # Actualizar detalle de venta
        detalle.cantidad -= cantidad_devolver
        if detalle.cantidad == 0:
            detalle.delete()
        else:
            detalle.subtotal = detalle.cantidad * detalle.precio_unitario
            detalle.save()

        # Recalcular totales de la venta
        detalles_restantes = DetalleVenta.objects.filter(venta=venta)
        venta.subtotal = sum(
            detalle.subtotal for detalle in detalles_restantes)

        # Recalcular ITBIS basado en el nuevo subtotal
        venta.itbis_monto = venta.subtotal * (venta.itbis_porcentaje / 100)

        # Recalcular total con ITBIS
        venta.total = venta.subtotal + venta.itbis_monto - venta.descuento_monto

        # Recalcular total_a_pagar (sin ITBIS) - IMPORTANTE: Mantener sin ITBIS
        venta.total_a_pagar = venta.subtotal - venta.descuento_monto

        venta.save()

        # ACTUALIZAR CUENTA POR COBRAR - CORRECCIÓN CRÍTICA
        try:
            cuenta = CuentaPorCobrar.objects.get(
                venta=venta, anulada=False, eliminada=False)

            # IMPORTANTE: Actualizar BOTH campos para mantener consistencia
            cuenta.monto_total = venta.total_a_pagar  # SIN ITBIS

            # Recalcular el estado basado en el nuevo saldo
            saldo_pendiente = cuenta.monto_total - cuenta.monto_pagado

            if saldo_pendiente <= 0:
                cuenta.estado = 'pagada'
                cuenta.monto_pagado = cuenta.monto_total  # Ajustar si pagado > total
            elif cuenta.monto_pagado > 0:
                cuenta.estado = 'parcial'
            else:
                cuenta.estado = 'pendiente'

            # Verificar vencimiento
            if cuenta.esta_vencida:
                cuenta.estado = 'vencida'

            cuenta.save()

            # Registrar movimiento de devolución
            registrar_movimiento_cuenta(
                cuenta,
                monto_devolucion,
                'devolucion',
                request.user,
                f"Devolución de {cantidad_devolver} unidades del producto {producto.descripcion}"
            )

            # Devolver datos actualizados para actualización en tiempo real
            return JsonResponse({
                'success': True,
                'mensaje': f'Devolución procesada correctamente. Se han devuelto {cantidad_devolver} unidades.',
                'numero_devolucion': f'DEV-{timezone.now().strftime("%Y%m%d")}-{venta.id}',
                'monto_devolucion': str(monto_devolucion),
                'datos_actualizados': {
                    'cuenta_id': cuenta.id,
                    'nuevo_monto_total': float(cuenta.monto_total),
                    'nuevo_saldo_pendiente': float(max(0, saldo_pendiente)),
                    'nuevo_estado': cuenta.estado,
                    'nuevo_total_venta': float(venta.total_a_pagar),
                    'factura_numero': venta.numero_factura
                }
            })

        except CuentaPorCobrar.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró la cuenta por cobrar asociada a esta factura.'
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Error al procesar la devolución: {str(e)}'}, status=500)


@user_passes_test(is_superuser, login_url='/')
def roles(request):
    # Definir los módulos del sistema
    MODULOS_SISTEMA = [
        {'codename': 'ventas', 'name': 'Facturación'},
        {'codename': 'cotizacion', 'name': 'Cotización'},
        {'codename': 'registrodecliente', 'name': 'Registrar Cliente'},
        {'codename': 'listadecliente', 'name': 'Clientes'},
        {'codename': 'cuentaporcobrar', 'name': 'Cuenta por Cobrar'},
        {'codename': 'reimprimirfactura', 'name': 'Reimprimir'},
        {'codename': 'inventario', 'name': 'Inventario'},
        {'codename': 'entrada', 'name': 'Entrada Mercancía'},
        {'codename': 'registrosuplidores', 'name': 'Registrar Suplidores'},
        {'codename': 'gestiondesuplidores', 'name': 'Suplidores'},
        {'codename': 'devoluciones', 'name': 'Devoluciones'},
        {'codename': 'anular', 'name': 'Anular Factura'},
        {'codename': 'dashboard', 'name': 'Dashboard'},
        {'codename': 'roles', 'name': 'Roles'},
    ]

    # Crear permisos si no existen
    content_type = ContentType.objects.get_for_model(Group)
    for modulo in MODULOS_SISTEMA:
        Permission.objects.get_or_create(
            codename=f'access_{modulo["codename"]}',
            content_type=content_type,
            defaults={'name': f'Acceso a {modulo["name"]}'}
        )

    # Crear grupos especiales si no existen
    grupos_especiales = [
        {
            'name': 'Usuario Normal',
            'permisos': ['ventas', 'cotizacion', 'registrodecliente', 'listadecliente',
                         'cuentaporcobrar', 'reimprimirfactura', 'inventario']
        },
        {
            'name': 'Almacén',
            'permisos': ['entrada', 'registrosuplidores', 'gestiondesuplidores', 'inventario']
        }
    ]

    for grupo_info in grupos_especiales:
        group, created = Group.objects.get_or_create(name=grupo_info['name'])
        # Asignar permisos si el grupo es nuevo
        if created:
            for permiso_codename in grupo_info['permisos']:
                try:
                    permiso = Permission.objects.get(
                        codename=f'access_{permiso_codename}',
                        content_type=content_type
                    )
                    group.permissions.add(permiso)
                except Permission.DoesNotExist:
                    continue

    # Obtener todos los grupos (roles)
    groups = Group.objects.all().prefetch_related('permissions', 'user_set')

    # Obtener todos los usuarios
    users = User.objects.all().prefetch_related('groups')

    # Zona horaria República Dominicana para mostrar ultimo acceso en formato 12h
    import pytz
    tz_rd = pytz.timezone('America/Santo_Domingo')

    def format_last_access(last_login):
        if not last_login:
            return 'Nunca'
        if timezone.is_aware(last_login):
            last_login_local = last_login.astimezone(tz_rd)
        else:
            last_login_local = timezone.make_aware(last_login, tz_rd)
        return last_login_local.strftime('%d/%m/%Y %I:%M')

    # Procesar datos para los templates
    roles_data = []
    roles_para_usuarios = []  # Solo los roles que se mostrarán en usuarios

    for group in groups:
        permissions = list(
            group.permissions.values_list('codename', flat=True))

        # Obtener módulos asignados al rol
        modulos_asignados = []
        modulos_codename = []
        for modulo in MODULOS_SISTEMA:
            if f'access_{modulo["codename"]}' in permissions:
                modulos_asignados.append(modulo["name"])
                modulos_codename.append(modulo["codename"])

        # Determinar si es un grupo especial
        es_especial = group.name in ['Usuario Normal', 'Almacén']

        role_data = {
            'id': group.id,
            'name': group.name,
            'description': '',  # Los grupos de Django no tienen descripción por defecto
            'status': 'activo',  # Asumimos que todos están activos
            'userCount': group.user_set.count(),
            'modulos_asignados': modulos_asignados,
            'modulos_codename': modulos_codename,
            'es_especial': es_especial
        }

        roles_data.append(role_data)

        # Solo incluir los roles especiales para asignar a usuarios
        if group.name in ['Usuario Normal', 'Almacén']:
            roles_para_usuarios.append(role_data)

    users_data = []
    for user in users:
        user_group = user.groups.first()
        role_name = user_group.name if user_group else 'Sin rol'
        role_id = user_group.id if user_group else ''

        users_data.append({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'email': user.email,
            'role': role_name,
            'role_id': role_id,
            'status': 'activo' if user.is_active else 'inactivo',
            'lastAccess': format_last_access(user.last_login)
        })

    # Estadísticas
    total_roles = groups.count()
    active_roles = total_roles  # Asumimos que todos están activos
    inactive_roles = 0

    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    inactive_users = total_users - active_users

    context = {
        'roles_data': roles_data,
        'roles_para_usuarios': roles_para_usuarios,  # Nuevo contexto
        'users_data': users_data,
        'total_roles': total_roles,
        'active_roles': active_roles,
        'inactive_roles': inactive_roles,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'modulos_sistema': MODULOS_SISTEMA,
    }

    # Manejar búsquedas y filtros
    search_role = request.GET.get('search_role', '')
    status_filter = request.GET.get('status_filter', '')

    if search_role:
        context['roles_data'] = [r for r in context['roles_data']
                                 if search_role.lower() in r['name'].lower()]

    if status_filter:
        # En este caso, todos están activos, pero si quieres filtrar por inactivo, no mostrará ninguno
        context['roles_data'] = [r for r in context['roles_data']
                                 if r['status'] == status_filter]

    # Manejar búsquedas y filtros para usuarios
    search_user = request.GET.get('search_user', '')
    role_filter = request.GET.get('role_filter', '')
    user_status_filter = request.GET.get('user_status_filter', '')

    if search_user:
        context['users_data'] = [u for u in context['users_data']
                                 if search_user.lower() in u['name'].lower() or
                                 search_user.lower() in u['email'].lower()]

    if role_filter:
        context['users_data'] = [u for u in context['users_data']
                                 if u['role'] == role_filter]

    if user_status_filter:
        context['users_data'] = [u for u in context['users_data']
                                 if u['status'] == user_status_filter]

    # Manejar acciones POST (crear, editar, eliminar)
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_role':
            name = request.POST.get('name')
            modulos_seleccionados = request.POST.getlist('modulos')

            if not name:
                messages.error(request, 'El nombre del rol es obligatorio.')
            elif Group.objects.filter(name=name).exists():
                messages.error(request, 'Ya existe un rol con este nombre.')
            else:
                group = Group.objects.create(name=name)

                # Asignar permisos basados en los módulos seleccionados
                for modulo_codename in modulos_seleccionados:
                    try:
                        permiso = Permission.objects.get(
                            codename=f'access_{modulo_codename}',
                            content_type=content_type
                        )
                        group.permissions.add(permiso)
                    except Permission.DoesNotExist:
                        continue

                messages.success(request, 'Rol creado exitosamente.')
                return redirect('roles')

        elif action == 'edit_role':
            role_id = request.POST.get('role_id')
            name = request.POST.get('name')
            modulos_seleccionados = request.POST.getlist('modulos')

            if not name:
                messages.error(request, 'El nombre del rol es obligatorio.')
            else:
                group = get_object_or_404(Group, id=role_id)

                # No permitir editar nombres de grupos especiales
                if group.name in ['Usuario Normal', 'Almacén'] and name != group.name:
                    messages.error(
                        request, f'No se puede cambiar el nombre del rol especial "{group.name}".')
                elif Group.objects.filter(name=name).exclude(id=role_id).exists():
                    messages.error(
                        request, 'Ya existe otro rol con este nombre.')
                else:
                    group.name = name
                    group.save()

                    # Actualizar permisos (excepto para grupos especiales, pero en este caso, permitimos editar permisos?)
                    # Si quieres que los grupos especiales no se editen, puedes agregar una condición aquí.
                    group.permissions.clear()
                    for modulo_codename in modulos_seleccionados:
                        try:
                            permiso = Permission.objects.get(
                                codename=f'access_{modulo_codename}',
                                content_type=content_type
                            )
                            group.permissions.add(permiso)
                        except Permission.DoesNotExist:
                            continue

                    messages.success(request, 'Rol actualizado exitosamente.')
                    return redirect('roles')

        elif action == 'delete_role':
            role_id = request.POST.get('role_id')
            group = get_object_or_404(Group, id=role_id)

            # No permitir eliminar grupos especiales
            if group.name in ['Usuario Normal', 'Almacén']:
                messages.error(
                    request, 'No se pueden eliminar los roles especiales del sistema.')
            elif group.user_set.exists():
                messages.error(
                    request, 'No se puede eliminar un rol que tiene usuarios asignados.')
            else:
                group.delete()
                messages.success(request, 'Rol eliminado exitosamente.')
                return redirect('roles')

        elif action == 'create_user':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            role_id = request.POST.get('role_id')
            is_active = request.POST.get('status', 'activo') == 'activo'

            if not all([username, email, password, role_id]):
                messages.error(
                    request, 'Todos los campos obligatorios deben ser completados.')
            elif User.objects.filter(username=username).exists():
                messages.error(
                    request, 'Ya existe un usuario con este nombre de usuario.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Ya existe un usuario con este email.')
            else:
                try:
                    with transaction.atomic():
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            first_name=first_name,
                            last_name=last_name,
                            is_active=is_active
                        )

                        group = get_object_or_404(Group, id=role_id)
                        user.groups.add(group)

                    messages.success(request, 'Usuario creado exitosamente.')
                    return redirect('roles')
                except Exception as e:
                    messages.error(
                        request, f'Error al crear usuario: {str(e)}')

        elif action == 'edit_user':
            user_id = request.POST.get('user_id')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password', None)
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            role_id = request.POST.get('role_id')
            is_active = request.POST.get('status', 'activo') == 'activo'

            if not all([username, email, role_id]):
                messages.error(
                    request, 'Todos los campos obligatorios deben ser completados.')
            else:
                user = get_object_or_404(User, id=user_id)

                if User.objects.filter(username=username).exclude(id=user_id).exists():
                    messages.error(
                        request, 'Ya existe otro usuario con este nombre de usuario.')
                elif User.objects.filter(email=email).exclude(id=user_id).exists():
                    messages.error(
                        request, 'Ya existe otro usuario con este email.')
                else:
                    try:
                        with transaction.atomic():
                            user.username = username
                            user.email = email
                            user.first_name = first_name
                            user.last_name = last_name
                            user.is_active = is_active

                            if password:
                                user.set_password(password)

                            user.save()

                            # Actualizar el rol
                            user.groups.clear()
                            group = get_object_or_404(Group, id=role_id)
                            user.groups.add(group)

                        messages.success(
                            request, 'Usuario actualizado exitosamente.')
                        return redirect('roles')
                    except Exception as e:
                        messages.error(
                            request, f'Error al actualizar usuario: {str(e)}')

        elif action == 'delete_user':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)

            if user == request.user:
                messages.error(
                    request, 'No puedes eliminar tu propio usuario.')
            else:
                user.delete()
                messages.success(request, 'Usuario eliminado exitosamente.')
                return redirect('roles')

        elif action == 'export_roles_csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="roles.csv"'

            writer = csv.writer(response)
            writer.writerow(['Nombre', 'Usuarios Asignados', 'Módulos'])

            for group in Group.objects.all():
                user_count = group.user_set.count()
                modulos = [modulo['name'] for modulo in MODULOS_SISTEMA
                           if group.permissions.filter(codename=f'access_{modulo["codename"]}').exists()]
                writer.writerow([group.name, user_count, ', '.join(modulos)])

            return response

        elif action == 'export_users_csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="usuarios.csv"'

            writer = csv.writer(response)
            writer.writerow(['Nombre', 'Email', 'Rol',
                            'Estado', 'Último Acceso'])

            for user in User.objects.all().prefetch_related('groups'):
                user_group = user.groups.first()
                role_name = user_group.name if user_group else 'Sin rol'

                writer.writerow([
                    f"{user.first_name} {user.last_name}".strip() or user.username,
                    user.email,
                    role_name,
                    'activo' if user.is_active else 'inactivo',
                    format_last_access(user.last_login)
                ])

            return response

    return render(request, "facturacion/roles.html", context)


@receiver(post_migrate)
def crear_grupos_especiales(sender, **kwargs):
    # Solo ejecutar para esta aplicación
    if sender.name == 'facturacion':
        # CORRECCIÓN: Usar un modelo de tu aplicación en lugar de Group
        # Reemplaza 'CuentaPorPagar' con cualquier modelo de tu app
        from facturacion.models import CuentaPorPagar  # O cualquier otro modelo tuyo

        content_type = ContentType.objects.get_for_model(CuentaPorPagar)

        # Crear permisos si no existen
        MODULOS = [
            'ventas', 'cotizacion', 'registrodecliente', 'listadecliente',
            'cuentaporcobrar', 'reimprimirfactura', 'inventario',
            'entrada', 'registrosuplidores', 'gestiondesuplidores',
            'devoluciones', 'anular', 'dashboard', 'roles'
        ]

        for modulo in MODULOS:
            try:
                # Usar defaults para evitar problemas
                permission, created = Permission.objects.get_or_create(
                    codename=f'access_{modulo}',
                    content_type=content_type,
                    defaults={
                        'name': f'Acceso a {modulo}',
                    }
                )
                if created:
                    print(f"✓ Permiso creado: access_{modulo}")
                else:
                    print(f"→ Permiso ya existe: access_{modulo}")

            except IntegrityError as e:
                # Si hay error de duplicado, intenta obtener el existente
                print(f"⚠ IntegrityError al crear access_{modulo}: {e}")
                try:
                    permission = Permission.objects.get(
                        codename=f'access_{modulo}',
                        content_type=content_type
                    )
                    print(f"✓ Permiso obtenido: access_{modulo}")
                except Permission.DoesNotExist:
                    print(f"✗ No se pudo crear ni obtener: access_{modulo}")
                    continue

        # Crear grupos especiales
        grupos_especiales = [
            {
                'name': 'Usuario Normal',
                'permisos': ['ventas', 'cotizacion', 'registrodecliente', 'listadecliente',
                             'cuentaporcobrar', 'reimprimirfactura', 'inventario']
            },
            {
                'name': 'Almacén',
                'permisos': ['entrada', 'registrosuplidores', 'gestiondesuplidores', 'inventario']
            }
        ]

        for grupo_info in grupos_especiales:
            group, created = Group.objects.get_or_create(
                name=grupo_info['name'])

            if created:
                print(f"✓ Grupo creado: {grupo_info['name']}")
            else:
                print(f"→ Grupo ya existe: {grupo_info['name']}")

            # Asignar permisos (tanto si es nuevo como si existe)
            for permiso_codename in grupo_info['permisos']:
                try:
                    permiso = Permission.objects.get(
                        codename=f'access_{permiso_codename}',
                        content_type=content_type
                    )
                    group.permissions.add(permiso)
                    print(
                        f"  ✓ Permiso '{permiso_codename}' asignado a '{grupo_info['name']}'")
                except Permission.DoesNotExist:
                    print(
                        f"  ✗ Permiso no encontrado: access_{permiso_codename}")
                    continue


@user_passes_test(is_superuser, login_url='/')
@login_required
def anular(request):
    return render(request, "facturacion/anular.html")


def buscar_factura(request):
    """Busca una factura por su número para mostrar detalles antes de anular"""
    if request.method == 'POST':
        try:
            numero_factura = request.POST.get('numero_factura', '').strip()

            if not numero_factura:
                return JsonResponse({'error': 'Número de factura requerido'}, status=400)

            # Buscar la factura
            try:
                venta = Venta.objects.get(numero_factura=numero_factura)
            except Venta.DoesNotExist:
                return JsonResponse({'error': 'Factura no encontrada'}, status=404)

            # Obtener detalles de la venta
            detalles = DetalleVenta.objects.filter(venta=venta)

            # Información básica del cliente
            cliente_info = {
                'nombre': venta.cliente_nombre,
                'cedula': venta.cliente_documento,
                'telefono': 'N/A',
                'direccion': 'N/A',
            }

            # Determinar tipo de venta
            tipo_venta = 'Contado' if venta.tipo_venta == 'contado' else 'Crédito'

            # Formatear datos para la respuesta
            factura_data = {
                'id': venta.id,
                'numero_factura': venta.numero_factura,
                'fecha': venta.fecha_venta.strftime('%Y-%m-%d'),
                'estado': 'anulada' if venta.anulada else 'activa',
                'tipo_venta': tipo_venta,
                'cliente': cliente_info,
                'vendedor': f"{venta.vendedor.first_name} {venta.vendedor.last_name}",
                'items': [],
                'subtotal': float(venta.subtotal),
                'itbis': float(venta.itbis_monto),
                'total': float(venta.total),
                'total_a_pagar': float(venta.total_a_pagar),
                'forma_pago': venta.get_metodo_pago_display(),
                'motivo_anulacion': venta.motivo_anulacion if venta.anulada else None,
                'fecha_anulacion': venta.fecha_anulacion.isoformat() if venta.anulada and venta.fecha_anulacion else None,
            }

            # Agregar items
            for detalle in detalles:
                factura_data['items'].append({
                    'producto': detalle.producto.descripcion,
                    'cantidad': detalle.cantidad,
                    'precio': float(detalle.precio_unitario),
                    'subtotal': float(detalle.subtotal)
                })

            return JsonResponse(factura_data)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en buscar_factura: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def anular_factura(request):
    """Anula una factura usando el número de factura (no el ID)"""
    if request.method == 'POST':
        try:
            # CAMBIO IMPORTANTE: Ahora usamos numero_factura en vez de factura_id
            numero_factura = request.POST.get('numero_factura', '').strip()
            motivo = request.POST.get('motivo', '').strip()

            if not numero_factura:
                return JsonResponse({'error': 'Número de factura requerido'}, status=400)

            if not motivo:
                return JsonResponse({'error': 'Motivo de anulación requerido'}, status=400)

            # Usar transacción atómica para asegurar consistencia
            with transaction.atomic():
                # Buscar la factura por número (con lock para evitar concurrencia)
                try:
                    venta = Venta.objects.select_for_update().get(
                        numero_factura=numero_factura,
                        anulada=False
                    )
                except Venta.DoesNotExist:
                    return JsonResponse({
                        'error': 'Factura no encontrada o ya está anulada'
                    }, status=404)

                # Anular la factura
                venta.anulada = True
                venta.motivo_anulacion = motivo
                venta.fecha_anulacion = timezone.now()
                venta.usuario_anulacion = request.user
                venta.save()

                # Restaurar el inventario
                detalles = DetalleVenta.objects.filter(venta=venta)
                productos_restaurados = []

                for detalle in detalles:
                    if detalle.producto:
                        detalle.producto.cantidad += detalle.cantidad
                        detalle.producto.save()
                        productos_restaurados.append({
                            'producto': detalle.producto.descripcion,
                            'cantidad': detalle.cantidad
                        })

                return JsonResponse({
                    'success': True,
                    'message': f'Factura #{numero_factura} anulada correctamente',
                    'productos_restaurados': productos_restaurados
                })

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en anular_factura_action: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@user_passes_test(is_superuser_or_usuario_normal, login_url='/')
@login_required
def reimprimir_factura(request):
    # Esta vista renderiza la página de reimpresión
    return render(request, 'facturacion/reimprimirfactura.html')


@login_required
def buscar_facturaR(request):
    # Esta vista busca una factura por su número y devuelve los datos en JSON
    numero_factura = request.GET.get('numero_factura')

    if not numero_factura:
        return JsonResponse({'error': 'Número de factura no proporcionado'}, status=400)

    try:
        # Buscar la venta por número de factura
        venta = get_object_or_404(Venta, numero_factura=numero_factura)

        # Verificar si la factura está anulada
        if venta.anulada:
            return JsonResponse({'error': 'Esta factura ha sido anulada'}, status=400)

        # Obtener los detalles de la venta
        detalles = DetalleVenta.objects.filter(venta=venta)

        # Manejar el caso cuando el cliente es None
        if venta.cliente:
            cliente_nombre = venta.cliente.full_name
            cliente_documento = venta.cliente.identification_number
            cliente_telefono = venta.cliente.primary_phone
            cliente_direccion = venta.cliente.address
        else:
            cliente_nombre = venta.cliente_nombre or "Consumidor Final"
            cliente_documento = venta.cliente_documento or ""
            cliente_telefono = None
            cliente_direccion = None

        # Calcular totales
        total_articulos = sum(detalle.cantidad for detalle in detalles)

        # Preparar los datos de la venta para la respuesta JSON
        datos_venta = {
            'fecha': venta.fecha_venta.strftime('%d/%m/%Y'),
            'numero_factura': venta.numero_factura,
            'ncf': venta.ncf if hasattr(venta, 'ncf') and venta.ncf else '',
            'cliente_nombre': cliente_nombre,
            'cliente_documento': cliente_documento,
            'cliente_telefono': cliente_telefono,
            'cliente_direccion': cliente_direccion,
            'tipo_venta': venta.tipo_venta,
            'tipo_venta_display': venta.get_tipo_venta_display(),
            'metodo_pago': venta.metodo_pago,
            'metodo_pago_display': venta.get_metodo_pago_display(),
            'total': float(venta.subtotal),
            'subtotal': float(venta.subtotal),
            'itbis_porcentaje': venta.itbis_porcentaje if hasattr(venta, 'itbis_porcentaje') else 18,
            'itbis_monto': float(venta.itbis_monto) if hasattr(venta, 'itbis_monto') else 0,
            'descuento_monto': float(venta.descuento_monto),
            'total_a_pagar': float(venta.total_a_pagar),
            'total_articulos': total_articulos,
            'fecha_vencimiento': venta.fecha_vencimiento.strftime('%d/%m/%Y') if hasattr(venta, 'fecha_vencimiento') and venta.fecha_vencimiento else None,
            'es_financiada': venta.es_financiada if hasattr(venta, 'es_financiada') else False,
            'cuota_mensual': float(venta.cuota_mensual) if hasattr(venta, 'cuota_mensual') and venta.cuota_mensual else 0,
            'interes_total': float(venta.interes_total) if hasattr(venta, 'interes_total') and venta.interes_total else 0,
            'montoinicial': float(venta.montoinicial) if hasattr(venta, 'montoinicial') and venta.montoinicial else 0,
            'total_con_interes': float(venta.total_con_interes) if hasattr(venta, 'total_con_interes') and venta.total_con_interes else 0,
            'vendedor_nombre': venta.vendedor.get_full_name() if venta.vendedor and venta.vendedor.get_full_name() else (
                venta.vendedor.username if venta.vendedor else "Sistema"
            ),
            'detalles': []
        }

        # Agregar los detalles de los productos
        for detalle in detalles:
            datos_venta['detalles'].append({
                'producto_codigo': detalle.producto.codigo_producto if detalle.producto and hasattr(detalle.producto, 'codigo_producto') else "N/A",
                'producto_nombre': detalle.producto.nombre_producto if detalle.producto and hasattr(detalle.producto, 'nombre_producto') else "Producto",
                'producto_descripcion': detalle.producto.descripcion if detalle.producto and hasattr(detalle.producto, 'descripcion') else "",
                'cantidad': detalle.cantidad,
                'precio_unitario': float(detalle.precio_unitario),
                'subtotal': float(detalle.subtotal)
            })

        return JsonResponse(datos_venta)

    except Venta.DoesNotExist:
        return JsonResponse({'error': 'Factura no encontrada'}, status=404)
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error en buscar_facturaR: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)


def ultima_factura(request):
    # Esta vista devuelve la última factura según el tipo (crédito/contado)
    tipo_venta = request.GET.get('tipo_venta')

    if not tipo_venta or tipo_venta not in ['contado', 'credito']:
        return JsonResponse({'error': 'Tipo de venta no válido'}, status=400)

    try:
        # Buscar la última venta del tipo especificado
        ultima_venta = Venta.objects.filter(
            tipo_venta=tipo_venta,
            anulada=False
        ).order_by('-fecha_venta').first()

        if not ultima_venta:
            return JsonResponse({'error': f'No hay facturas de tipo {tipo_venta}'}, status=404)

        return JsonResponse({
            'numero_factura': ultima_venta.numero_factura,
            'fecha': ultima_venta.fecha_venta.strftime('%d/%m/%Y %H:%M'),
            'tipo_venta': ultima_venta.tipo_venta
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def buscar_comprobante(request):
    if request.method == 'POST':
        try:
            numero_comprobante = request.POST.get(
                'numero_comprobante', '').strip()

            if not numero_comprobante:
                return JsonResponse({'error': 'Número de comprobante requerido'}, status=400)

            # Buscar el comprobante por número
            comprobante = get_object_or_404(
                ComprobantePago, numero_comprobante=numero_comprobante)

            # Verificar si el comprobante ya está anulado
            if hasattr(comprobante, 'anulado') and comprobante.anulado:
                return JsonResponse({'error': 'Este comprobante ya ha sido anulado'}, status=400)

            # Verificar si el pago asociado está anulado
            if hasattr(comprobante.pago, 'anulado') and comprobante.pago.anulado:
                return JsonResponse({'error': 'El pago asociado a este comprobante ha sido anulado'}, status=400)

            # Verificar si la cuenta por cobrar está anulada
            if hasattr(comprobante, 'cuenta') and comprobante.cuenta and comprobante.cuenta.anulada:
                return JsonResponse({'error': 'La cuenta por cobrar asociada ha sido anulada'}, status=400)

            # Obtener información del pago asociado
            pago = comprobante.pago
            cuenta = comprobante.cuenta

            if not cuenta:
                return JsonResponse({'error': 'No se encontró la cuenta asociada'}, status=400)

            # Calcular el saldo antes del pago
            saldo_antes_pago = cuenta.saldo_pendiente + pago.monto

            # Calcular el saldo después del pago
            saldo_despues_pago = cuenta.saldo_pendiente

            # Preparar los datos del comprobante para la respuesta JSON
            datos_comprobante = {
                'numero_comprobante': comprobante.numero_comprobante,
                'fecha_emision': comprobante.fecha_emision.strftime('%Y-%m-%d %H:%M:%S'),
                'tipo_comprobante': comprobante.tipo_comprobante,
                'tipo_comprobante_display': comprobante.get_tipo_comprobante_display(),
                'cliente_nombre': comprobante.cliente.nombres if hasattr(comprobante.cliente, 'nombres') else "Cliente",
                'cliente_documento': comprobante.cliente.cedula if hasattr(comprobante.cliente, 'cedula') else "N/A",
                'cliente_telefono': comprobante.cliente.telefono if hasattr(comprobante.cliente, 'telefono') else None,
                'cliente_direccion': comprobante.cliente.direccion if hasattr(comprobante.cliente, 'direccion') else None,
                'monto_pago': float(pago.monto),
                'fecha_pago': pago.fecha_pago.strftime('%Y-%m-%d %H:%M:%S'),
                'metodo_pago': pago.metodo_pago,
                'metodo_pago_display': pago.get_metodo_pago_display(),
                'numero_factura': cuenta.venta.numero_factura if cuenta.venta else "N/A",
                # Usar monto_total en lugar de monto_total_con_interes
                'monto_original': float(cuenta.monto_total),
                'saldo_antes_pago': float(saldo_antes_pago),
                'saldo_despues_pago': float(saldo_despues_pago),
                'descripcion': pago.observaciones or f"Pago de cuota - {comprobante.numero_comprobante}",
                'estado': 'activo'
            }

            return JsonResponse(datos_comprobante)

        except ComprobantePago.DoesNotExist:
            return JsonResponse({'error': 'Comprobante no encontrado'}, status=404)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en buscar_comprobante: {str(e)}")
            return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def anular_comprobante_action(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        numero_comprobante = request.POST.get('numero_comprobante')
        motivo = request.POST.get('motivo')

        if not numero_comprobante or not motivo:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)

        # Buscar el comprobante
        comprobante = get_object_or_404(
            ComprobantePago, numero_comprobante=numero_comprobante)

        # Verificar si ya está anulado
        if hasattr(comprobante, 'anulado') and comprobante.anulado:
            return JsonResponse({'error': 'El comprobante ya está anulado'}, status=400)

        # Obtener el pago asociado
        pago = comprobante.pago
        cuenta = comprobante.cuenta

        # Verificar que el pago no esté anulado
        if pago.anulado:
            return JsonResponse({'error': 'El pago ya está anulado'}, status=400)

        # Iniciar transacción para asegurar la consistencia de datos
        with transaction.atomic():
            # Revertir el pago en la cuenta por cobrar
            cuenta.monto_pagado -= pago.monto
            # Aumentar el saldo pendiente
            cuenta.save()

            # Actualizar el estado de la cuenta según el nuevo saldo pendiente
            if cuenta.saldo_pendiente <= 0:
                cuenta.estado = 'pagada'
            elif cuenta.monto_pagado > 0:
                cuenta.estado = 'parcial'
            else:
                cuenta.estado = 'pendiente'

            cuenta.save()

            # Marcar el pago como anulado
            pago.anulado = True
            pago.fecha_anulacion = timezone.now()
            pago.motivo_anulacion = motivo
            pago.save()

            # Marcar el comprobante como anulado
            if hasattr(comprobante, 'anulado'):
                comprobante.anulado = True
                comprobante.fecha_anulacion = timezone.now()
                comprobante.motivo_anulacion = motivo
                comprobante.save()

        return JsonResponse({
            'success': True,
            'message': 'Comprobante anulado exitosamente',
            'numero_comprobante': comprobante.numero_comprobante,
            'nuevo_saldo_pendiente': float(cuenta.saldo_pendiente)
        })

    except ComprobantePago.DoesNotExist:
        return JsonResponse({'error': 'Comprobante no encontrado'}, status=404)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error en anular_comprobante_action: {str(e)}")
        return JsonResponse({'error': f'Error al anular el comprobante: {str(e)}'}, status=500)


def ultimo_comprobante(request):
    # Esta vista devuelve el último comprobante emitido
    try:
        # Buscar el último comprobante
        ultimo_comprobante = ComprobantePago.objects.filter(
            anulado=False  # Asumiendo que agregas este campo
        ).order_by('-fecha_emision').first()

        if not ultimo_comprobante:
            return JsonResponse({'error': 'No hay comprobantes registrados'}, status=404)

        return JsonResponse({
            'numero_comprobante': ultimo_comprobante.numero_comprobante,
            'fecha': ultimo_comprobante.fecha_emision.strftime('%d/%m/%Y %H:%M'),
            'tipo_comprobante': ultimo_comprobante.tipo_comprobante
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@user_passes_test(is_superuser_or_usuario_normal, login_url='/')
@login_required
def cotizacion(request):
    return render(request, "facturacion/cotizacion.html")


def obtener_productoscotizacion(request):
    productos = EntradaProducto.objects.filter(activo=True).values(
        'id', 'codigo_producto', 'descripcion', 'marca', 'compatibilidad',
        'color', 'cantidad', 'costo', 'precio', 'precio_por_mayor', 'imagen'
    )
    for producto in productos:
        if producto['imagen']:
            producto['imagen_url'] = request.build_absolute_uri(
                settings.MEDIA_URL + producto['imagen'])
        else:
            producto['imagen_url'] = None
    return JsonResponse(list(productos), safe=False)

    try:
        # Obtener datos de la cotización
        producto_ids = []
        i = 0
        while f'producto_{i}_id' in request.GET:
            producto_id = request.GET.get(f'producto_{i}_id')
            if producto_id:
                producto_ids.append(producto_id)
            i += 1

        productos_seleccionados = []
        subtotal = 0

        # Procesar productos seleccionados
        for i, producto_id in enumerate(producto_ids):
            try:
                producto = EntradaProducto.objects.get(
                    id=producto_id, activo=True)
                cantidad = int(request.GET.get(f'producto_{i}_cantidad', 1))
                precio = float(request.GET.get(
                    f'producto_{i}_precio', producto.precio))

                marca_display = producto.get_marca_display() if hasattr(
                    producto, 'get_marca_display') else producto.marca

                imagen_url = None
                if producto.imagen:
                    try:
                        imagen_url = request.build_absolute_uri(
                            settings.MEDIA_URL + str(producto.imagen))
                    except:
                        imagen_url = None

                producto_data = {
                    'id': producto.id,
                    'codigo_producto': producto.codigo_producto,
                    'descripcion': producto.descripcion,
                    'marca': marca_display,
                    'precio': precio,
                    'cantidad': cantidad,
                    'subtotal': precio * cantidad,
                    'imagen_url': imagen_url
                }

                productos_seleccionados.append(producto_data)
                subtotal += precio * cantidad

            except EntradaProducto.DoesNotExist:
                print(f"Producto con ID {producto_id} no encontrado")
                continue
            except Exception as e:
                print(f"Error procesando producto {producto_id}: {str(e)}")
                continue

        if not productos_seleccionados:
            return HttpResponse("Error: No se encontraron productos para generar la factura", status=400)

        # Calcular totales
        itbis = subtotal * 0.18
        total = subtotal + itbis

        # Preparar datos para la factura
        factura_data = {
            'productos': productos_seleccionados,
            'cliente_nombre': request.GET.get('cliente_nombre', 'Cliente General'),
            'cliente_telefono': request.GET.get('cliente_telefono', 'N/A'),
            'cliente_rnc': request.GET.get('cliente_rnc', 'N/A'),
            'fecha': request.GET.get('fecha', '2024-01-01'),
            'factura_numero': request.GET.get('factura_numero', 'F' + str(random.randint(100000, 999999))),
            'vendedor': request.GET.get('vendedor', 'Sistema'),
            'subtotal': subtotal,
            'itbis': itbis,
            'total': total,
        }

        # Guardar los datos en la sesión para usarlos en la vista de factura
        request.session['factura_data'] = factura_data

        # Redirigir al apartado de generar factura
        # Cambia 'nombre_url_generar_factura' por el nombre real de tu URL
        return redirect('generar_factura')

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print("Error completo en generar_factura:")
        print(error_details)
        return HttpResponse(
            f"Error al procesar la factura: {str(e)}",
            status=500
        )


def obtener_productoscotizacion(request):
    productos = EntradaProducto.objects.filter(activo=True).values(
        'id', 'codigo_producto', 'descripcion', 'marca', 'compatibilidad',
        'color', 'cantidad', 'costo', 'precio', 'precio_por_mayor', 'imagen'
    )
    for producto in productos:
        if producto['imagen']:
            producto['imagen_url'] = request.build_absolute_uri(
                settings.MEDIA_URL + producto['imagen'])
        else:
            producto['imagen_url'] = None
    return JsonResponse(list(productos), safe=False)


def generar_factura(request):
    try:
        # Obtener datos de la cotización
        producto_ids = []
        i = 0
        while f'producto_{i}_id' in request.GET:
            producto_id = request.GET.get(f'producto_{i}_id')
            if producto_id:
                producto_ids.append(producto_id)
            i += 1

        productos_seleccionados = []
        subtotal = 0

        # Procesar productos seleccionados
        for i, producto_id in enumerate(producto_ids):
            try:
                producto = EntradaProducto.objects.get(
                    id=producto_id, activo=True)
                cantidad = int(request.GET.get(f'producto_{i}_cantidad', 1))
                precio = float(request.GET.get(
                    f'producto_{i}_precio', producto.precio))

                marca_display = producto.get_marca_display() if hasattr(
                    producto, 'get_marca_display') else producto.marca

                imagen_url = None
                if producto.imagen:
                    try:
                        imagen_url = request.build_absolute_uri(
                            settings.MEDIA_URL + str(producto.imagen))
                    except:
                        imagen_url = None

                producto_data = {
                    'id': producto.id,
                    'codigo_producto': producto.codigo_producto,
                    'descripcion': producto.descripcion,
                    'marca': marca_display,
                    'precio': precio,
                    'cantidad': cantidad,
                    'subtotal': precio * cantidad,
                    'imagen_url': imagen_url
                }

                productos_seleccionados.append(producto_data)
                subtotal += precio * cantidad

            except EntradaProducto.DoesNotExist:
                print(f"Producto con ID {producto_id} no encontrado")
                continue
            except Exception as e:
                print(f"Error procesando producto {producto_id}: {str(e)}")
                continue

        if not productos_seleccionados:
            return HttpResponse("Error: No se encontraron productos para generar la factura", status=400)

        # Calcular totales
        itbis = subtotal * 0.18
        total = subtotal + itbis

        # Preparar datos para la factura
        factura_data = {
            'productos': productos_seleccionados,
            'cliente_nombre': request.GET.get('cliente_nombre', 'Cliente General'),
            'cliente_telefono': request.GET.get('cliente_telefono', 'N/A'),
            'cliente_rnc': request.GET.get('cliente_rnc', 'N/A'),
            'fecha': request.GET.get('fecha', '2024-01-01'),
            'factura_numero': request.GET.get('factura_numero', 'F' + str(random.randint(100000, 999999))),
            'vendedor': request.GET.get('vendedor', 'Sistema'),
            'subtotal': subtotal,
            'itbis': itbis,
            'total': total,
        }

        # Guardar los datos en la sesión para usarlos en la vista de factura
        request.session['factura_data'] = factura_data

        # Redirigir a la vista ver-factura (con guión)
        return redirect('ver_factura')  # Usa el nombre de la URL

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print("Error completo en generar_factura:")
        print(error_details)
        return HttpResponse(
            f"Error al procesar la factura: {str(e)}",
            status=500
        )


def ver_factura(request):
    # Obtener los datos de la factura de la sesión
    factura_data = request.session.get('factura_data')

    if not factura_data:
        return HttpResponse("No hay datos de factura disponibles", status=400)

    # Renderizar la plantilla de factura
    return render(request, 'facturacion/ver_factura.html', factura_data)


@user_passes_test(is_superuser_or_almacen, login_url='/')
@login_required
def compras(request):
    proveedores = Proveedor.objects.filter(activo=True)
    return render(request, "facturacion/compras.html", {'proveedores': proveedores})


@require_GET
def buscar_productos_cuentas_pagar(request):
    query = request.GET.get('q', '')
    productos = EntradaProducto.objects.filter(
        activo=True
    ).select_related('proveedor')

    if query:
        productos = productos.filter(
            models.Q(descripcion__icontains=query) |
            models.Q(codigo_producto__icontains=query) |
            models.Q(marca__icontains=query)
        )[:10]

    resultados = []
    for producto in productos:
        resultados.append({
            'id': producto.id,
            'codigo': producto.codigo_producto,
            'descripcion': producto.descripcion,
            'marca': producto.marca,
            'compatibilidad': producto.compatibilidad or '',
            'color': producto.color,
            'costo_actual': str(producto.costo),
            'proveedor_id': producto.proveedor.id,
            'proveedor_nombre': producto.proveedor.nombre_empresa,
            'proveedor_rnc': producto.proveedor.rnc,
            'cantidad_disponible': producto.cantidad
        })

    return JsonResponse(resultados, safe=False)


@require_POST
@csrf_exempt
def guardar_cuenta_por_pagar(request):
    try:
        data = json.loads(request.body)

        # Validar que el proveedor existe
        proveedor = Proveedor.objects.get(id=data['proveedor_id'])

        # Crear la cuenta por pagar
        cuenta = CuentaPorPagar(
            proveedor=proveedor,
            numero_factura=data['numero_factura'],
            fecha_entrada=data['fecha_entrada'],
            condicion=data['condicion'],
            rnc=data['rnc'],
            descripcion=data.get('descripcion', '')
        )

        # Si es crédito, establecer fecha de vencimiento
        if data['condicion'] == 'credito':
            fecha_entrada = datetime.strptime(
                data['fecha_entrada'], '%Y-%m-%d').date()
            cuenta.fecha_vencimiento = fecha_entrada + timedelta(days=30)

        cuenta.save()

        # Crear los detalles de productos
        for producto_data in data['productos']:
            producto = EntradaProducto.objects.get(
                id=producto_data['producto_id'])

            detalle = DetalleCuentaPorPagar(
                cuenta_por_pagar=cuenta,
                producto=producto,
                cantidad=int(producto_data['cantidad']),
                costo_unitario=Decimal(producto_data['costo'])
            )
            detalle.save()

        return JsonResponse({
            'success': True,
            'message': f'Cuenta por pagar registrada exitosamente con {len(data["productos"])} productos'
        })

    except Proveedor.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'El proveedor seleccionado no existe'
        })
    except EntradaProducto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Uno de los productos seleccionados no existe'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al guardar: {str(e)}'
        })


@user_passes_test(is_superuser_or_usuario_normal, login_url='/')
@login_required
def cuentaporpagar(request):
    return render(request, "facturacion/cuentaporpagar.html")


@csrf_exempt
@require_http_methods(["GET"])
def cuentas_por_pagar_datos(request):
    """Obtener todas las cuentas por pagar para la gestión"""
    try:
        cuentas = CuentaPorPagar.objects.select_related(
            'proveedor').prefetch_related('detalles').all()

        datos_cuentas = []
        for cuenta in cuentas:
            # Obtener detalles de productos
            productos = []
            for detalle in cuenta.detalles.all():
                productos.append({
                    'nombre': detalle.producto.descripcion if detalle.producto else 'Producto no disponible',
                    'cantidad': float(detalle.cantidad),
                    'costo_unitario': float(detalle.costo_unitario),
                    'subtotal': float(detalle.subtotal),
                    'unidad': getattr(detalle.producto, 'unidad_medida', 'Und') if detalle.producto else 'Und'
                })

            datos_cuentas.append({
                'id': cuenta.id,
                'numero_factura': cuenta.numero_factura,
                'fecha_factura': cuenta.fecha_entrada.isoformat() if cuenta.fecha_entrada else None,
                'suplidor_nombre': cuenta.proveedor.nombre_empresa if cuenta.proveedor else 'Proveedor no disponible',
                'suplidor': cuenta.proveedor.nombre_empresa if cuenta.proveedor else 'Proveedor no disponible',
                'condicion': cuenta.get_condicion_display(),
                'condicion_valor': cuenta.condicion,
                'total': float(cuenta.total),
                'estado': cuenta.estado,
                'estado_display': cuenta.get_estado_display(),
                'fecha_vencimiento': cuenta.fecha_vencimiento.isoformat() if cuenta.fecha_vencimiento else None,
                'fecha_pago': cuenta.fecha_pago.isoformat() if cuenta.fecha_pago else None,
                'metodo_pago': cuenta.metodo_pago,
                'referencia_pago': cuenta.referencia_pago,
                'descripcion': cuenta.descripcion,
                'rnc': cuenta.rnc,
                'productos': productos
            })

        # Ordenar: pendientes primero, luego vencidos, luego pagados
        datos_cuentas.sort(key=lambda x: (
            0 if x['estado'] in ['pendiente', 'vencido'] else 1,
            x['fecha_vencimiento'] or '9999-12-31'
        ))

        return JsonResponse(datos_cuentas, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def procesar_pago_cuenta(request, cuenta_id):
    """Procesar el pago de una cuenta por pagar"""
    try:
        data = json.loads(request.body)
        cuenta = CuentaPorPagar.objects.get(id=cuenta_id)

        # Actualizar datos del pago
        cuenta.estado = 'pagado'
        cuenta.fecha_pago = data.get('fecha_pago')
        cuenta.metodo_pago = data.get('metodo_pago')
        cuenta.referencia_pago = data.get('referencia_pago')
        cuenta.notas_pago = f"Pago procesado el {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        cuenta.save()

        return JsonResponse({
            'success': True,
            'message': 'Pago registrado exitosamente'
        })

    except CuentaPorPagar.DoesNotExist:
        return JsonResponse({'error': 'Cuenta no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def obtener_detalle_cuenta(request, cuenta_id):
    """Obtener detalle completo de una cuenta por pagar"""
    try:
        print(f"🔍 Buscando cuenta con ID: {cuenta_id}")

        # Obtener la cuenta con manejo de errores
        try:
            cuenta = CuentaPorPagar.objects.select_related(
                'proveedor').prefetch_related('detalles').get(id=cuenta_id)
        except CuentaPorPagar.DoesNotExist:
            print(f"❌ Cuenta con ID {cuenta_id} no encontrada")
            return JsonResponse({'error': 'Cuenta no encontrada'}, status=404)

        print(f"✅ Cuenta encontrada: {cuenta.numero_factura}")

        # Obtener detalles de productos con manejo seguro
        productos = []
        for detalle in cuenta.detalles.all():
            try:
                producto_info = {
                    'id': detalle.id,
                    'nombre': 'Producto no disponible',
                    'cantidad': float(detalle.cantidad),
                    'costo_unitario': float(detalle.costo_unitario),
                    'subtotal': float(detalle.subtotal),
                    'unidad': 'Und',
                    'codigo': 'N/A'
                }

                if detalle.producto:
                    producto_info['nombre'] = getattr(
                        detalle.producto, 'descripcion', 'Producto sin descripción')
                    producto_info['unidad'] = getattr(
                        detalle.producto, 'unidad_medida', 'Und')
                    producto_info['codigo'] = getattr(
                        detalle.producto, 'codigo', 'N/A')

                productos.append(producto_info)

            except Exception as e:
                print(f"⚠️ Error procesando detalle {detalle.id}: {str(e)}")
                continue

        # Construir datos del proveedor con manejo seguro
        proveedor_data = {
            'id': None,
            'nombre': 'Proveedor no disponible',
            'telefono': '',
            'direccion': '',
            'rnc': ''
        }

        if cuenta.proveedor:
            proveedor_data = {
                'id': cuenta.proveedor.id,
                'nombre': getattr(cuenta.proveedor, 'nombre_empresa', 'Proveedor sin nombre'),
                'telefono': getattr(cuenta.proveedor, 'telefono', ''),
                'direccion': getattr(cuenta.proveedor, 'direccion', ''),
                'rnc': getattr(cuenta.proveedor, 'rnc', '')
            }

        # Construir respuesta
        datos_cuenta = {
            'id': cuenta.id,
            'numero_factura': cuenta.numero_factura,
            'fecha_factura': cuenta.fecha_entrada.isoformat() if cuenta.fecha_entrada else None,
            'fecha_vencimiento': cuenta.fecha_vencimiento.isoformat() if cuenta.fecha_vencimiento else None,
            'fecha_pago': cuenta.fecha_pago.isoformat() if cuenta.fecha_pago else None,
            'proveedor': proveedor_data,
            'condicion': cuenta.condicion,
            'condicion_display': cuenta.get_condicion_display(),
            'estado': cuenta.estado,
            'estado_display': cuenta.get_estado_display(),
            'metodo_pago': cuenta.metodo_pago or '',
            'metodo_pago_display': cuenta.get_metodo_pago_display() if cuenta.metodo_pago else '',
            'referencia_pago': cuenta.referencia_pago or '',
            'rnc': cuenta.rnc or '',
            'descripcion': cuenta.descripcion or '',
            'notas_pago': cuenta.notas_pago or '',
            'total': float(cuenta.total) if hasattr(cuenta, 'total') and cuenta.total else 0.0,
            'total_productos': cuenta.total_productos if hasattr(cuenta, 'total_productos') else 0,
            'productos': productos,
            'fecha_registro': cuenta.fecha_registro.isoformat() if cuenta.fecha_registro else None,
            'fecha_actualizacion': cuenta.fecha_actualizacion.isoformat() if cuenta.fecha_actualizacion else None
        }

        print(f"✅ Datos de cuenta {cuenta_id} preparados exitosamente")

        return JsonResponse({
            'success': True,
            'cuenta': datos_cuenta
        })

    except Exception as e:
        print(f"❌ ERROR en obtener_detalle_cuenta: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def actualizar_cuenta_por_pagar(request, cuenta_id):
    """Actualizar una cuenta por pagar"""
    try:
        data = json.loads(request.body)
        cuenta = CuentaPorPagar.objects.get(id=cuenta_id)

        # Actualizar campos
        cuenta.numero_factura = data.get(
            'numero_factura', cuenta.numero_factura)

        if data.get('fecha_factura'):
            cuenta.fecha_entrada = data['fecha_factura']

        if data.get('fecha_vencimiento'):
            cuenta.fecha_vencimiento = data['fecha_vencimiento']

        cuenta.condicion = data.get('condicion', cuenta.condicion)
        cuenta.descripcion = data.get('notas', cuenta.descripcion)
        cuenta.save()

        return JsonResponse({
            'success': True,
            'message': 'Cuenta actualizada exitosamente'
        })

    except CuentaPorPagar.DoesNotExist:
        return JsonResponse({'error': 'Cuenta no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def eliminar_cuenta_por_pagar(request, cuenta_id):
    """Eliminar una cuenta por pagar"""
    try:
        cuenta = CuentaPorPagar.objects.get(id=cuenta_id)

        # Solo permitir eliminar cuentas pagadas
        if cuenta.estado != 'pagado':
            return JsonResponse({
                'error': 'Solo se pueden eliminar cuentas pagadas'
            }, status=400)

        numero_factura = cuenta.numero_factura
        cuenta.delete()

        return JsonResponse({
            'success': True,
            'message': f'Cuenta {numero_factura} eliminada exitosamente'
        })

    except CuentaPorPagar.DoesNotExist:
        return JsonResponse({'error': 'Cuenta no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def generar_factura_pago(request, cuenta_id):
    """Generar factura de pago"""
    try:
        cuenta = CuentaPorPagar.objects.get(id=cuenta_id)

        # Datos para la factura
        datos_factura = {
            'numero_factura': cuenta.numero_factura,
            'fecha_emision': timezone.now().date().isoformat(),
            'proveedor': cuenta.proveedor.nombre_empresa if cuenta.proveedor else '',
            'rnc_proveedor': cuenta.proveedor.rnc if cuenta.proveedor else cuenta.rnc,
            'monto_total': float(cuenta.total),
            'metodo_pago': cuenta.get_metodo_pago_display() if cuenta.metodo_pago else '',
            'referencia_pago': cuenta.referencia_pago,
            'fecha_pago': cuenta.fecha_pago.isoformat() if cuenta.fecha_pago else ''
        }

        return JsonResponse({
            'success': True,
            'factura': datos_factura,
            'message': 'Factura generada exitosamente'
        })

    except CuentaPorPagar.DoesNotExist:
        return JsonResponse({'error': 'Cuenta no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# facturacion/views.py - Vista corregida para generar_factura_pdf
@csrf_exempt
@require_http_methods(["GET"])
def generar_factura_pdf(request, cuenta_id):
    """Generar PDF real de factura"""
    try:
        print(f"📄 Generando PDF para cuenta ID: {cuenta_id}")

        # Obtener la cuenta
        try:
            cuenta = CuentaPorPagar.objects.select_related(
                'proveedor').prefetch_related('detalles').get(id=cuenta_id)
        except CuentaPorPagar.DoesNotExist:
            return JsonResponse({'error': 'Cuenta no encontrada'}, status=404)

        # Verificar que la cuenta esté pagada
        if cuenta.estado != 'pagado':
            return JsonResponse({
                'error': 'Solo se pueden generar facturas para cuentas pagadas'
            }, status=400)

        # Crear el buffer para el PDF
        buffer = io.BytesIO()

        # Crear el documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Elementos del documento
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        style_heading = styles['Heading1']
        style_normal = styles['Normal']
        style_bold = ParagraphStyle(
            'Bold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold'
        )

        # Encabezado de la factura
        elements.append(Paragraph("FACTURA DE PAGO", style_heading))
        elements.append(Spacer(1, 20))

        # Información de la empresa
        empresa_data = [
            ["AGROINVENTARIO", ""],
            ["Sistema de Fertilizantes", ""],
            ["RNC: 1-23-45678-9", f"Factura: {cuenta.numero_factura}"],
            ["Tel: 809-555-5555",
                f"Fecha: {datetime.now().strftime('%d/%m/%Y')}"],
            ["Santo Domingo, República Dominicana", ""]
        ]

        empresa_table = Table(empresa_data, colWidths=[3.5*inch, 3.5*inch])
        empresa_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, 0), 'Helvetica-Bold', 14),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(empresa_table)
        elements.append(Spacer(1, 20))

        # Información del proveedor
        elements.append(Paragraph("INFORMACIÓN DEL PROVEEDOR", style_bold))
        proveedor_info = [
            ["Nombre:", cuenta.proveedor.nombre_empresa if cuenta.proveedor else 'Proveedor no disponible'],
            ["RNC:", cuenta.proveedor.rnc if cuenta.proveedor and cuenta.proveedor.rnc else cuenta.rnc or 'N/A'],
            ["Teléfono:", cuenta.proveedor.telefono if cuenta.proveedor else 'N/A'],
            ["Dirección:", cuenta.proveedor.direccion if cuenta.proveedor else 'N/A']
        ]

        proveedor_table = Table(proveedor_info, colWidths=[1.5*inch, 5*inch])
        proveedor_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        elements.append(proveedor_table)
        elements.append(Spacer(1, 20))

        # Información del pago
        elements.append(Paragraph("INFORMACIÓN DEL PAGO", style_bold))
        pago_info = [
            ["Fecha de Pago:", cuenta.fecha_pago.strftime(
                '%d/%m/%Y') if cuenta.fecha_pago else 'N/A'],
            ["Método de Pago:", cuenta.get_metodo_pago_display(
            ) if cuenta.metodo_pago else 'No especificado'],
            ["Referencia:", cuenta.referencia_pago or 'N/A'],
            ["Condición:", cuenta.get_condicion_display()]
        ]

        pago_table = Table(pago_info, colWidths=[1.5*inch, 5*inch])
        pago_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        elements.append(pago_table)
        elements.append(Spacer(1, 20))

        # Tabla de productos
        elements.append(Paragraph("DETALLE DE PRODUCTOS", style_bold))

        # Encabezados de la tabla
        product_data = [['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']]

        # Agregar productos - CORRECCIÓN: Convertir Decimal a float
        total_general = 0.0
        for detalle in cuenta.detalles.all():
            # Convertir Decimal a float para evitar errores
            cantidad = float(detalle.cantidad)
            costo_unitario = float(detalle.costo_unitario)
            subtotal = cantidad * costo_unitario
            total_general += subtotal

            product_data.append([
                detalle.producto.descripcion if detalle.producto else 'Producto no disponible',
                f"{cantidad} {getattr(detalle.producto, 'unidad_medida', 'Und') if detalle.producto else 'Und'}",
                f"RD$ {costo_unitario:.2f}",
                f"RD$ {subtotal:.2f}"
            ])

        # Crear tabla de productos
        product_table = Table(product_data, colWidths=[
                              3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        product_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(product_table)
        elements.append(Spacer(1, 20))

        # Totales - CORRECCIÓN: Usar float para cálculos
        itbis = total_general * 0.18  # 18% ITBIS
        total_con_itbis = total_general + itbis

        total_data = [
            ["Subtotal:", f"RD$ {total_general:.2f}"],
            ["ITBIS (18%):", f"RD$ {itbis:.2f}"],
            ["TOTAL:", f"RD$ {total_con_itbis:.2f}"]
        ]

        total_table = Table(total_data, colWidths=[1.5*inch, 1.5*inch])
        total_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 12),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONT', (-1, -1), (-1, -1), 'Helvetica-Bold', 14),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 30))

        # Pie de página
        elements.append(Paragraph("AGRADECEMOS SU PREFERENCIA", style_bold))
        elements.append(
            Paragraph("Factura generada electrónicamente", styles['Normal']))
        elements.append(Paragraph(
            f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))

        # Construir PDF
        doc.build(elements)

        # Obtener el PDF del buffer
        pdf = buffer.getvalue()
        buffer.close()

        # Crear respuesta HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{cuenta.numero_factura}.pdf"'
        response.write(pdf)

        print(f"✅ PDF generado exitosamente para {cuenta.numero_factura}")
        return response

    except Exception as e:
        print(f"❌ ERROR en generar_factura_pdf: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': f'Error al generar PDF: {str(e)}'}, status=500)


# revisar Ojo
@login_required
def reportes(request):
    # Fechas por defecto (últimos 30 días)
    fecha_hasta = timezone.now()
    fecha_desde = fecha_hasta - timedelta(days=30)

    # Calcular fechas para botones de período
    hoy = timezone.now().date()
    semana_pasada = hoy - timedelta(days=7)
    mes_pasado = hoy - timedelta(days=30)

    # Procesar filtros del formulario
    if request.method == 'GET':
        fecha_desde_str = request.GET.get('fecha_desde')
        fecha_hasta_str = request.GET.get('fecha_hasta')
        vendedor_id = request.GET.get('vendedor')
        producto_id = request.GET.get('producto')
        tipo_venta = request.GET.get('tipo_venta')  # Nuevo filtro

        if fecha_desde_str:
            try:
                fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d')
                fecha_desde = timezone.make_aware(fecha_desde)
            except ValueError:
                pass
        if fecha_hasta_str:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d')
                fecha_hasta = timezone.make_aware(fecha_hasta)
                # Ajustar para incluir todo el día
                fecha_hasta = fecha_hasta.replace(
                    hour=23, minute=59, second=59)
            except ValueError:
                pass

    # Filtrar ventas
    ventas = Venta.objects.filter(
        completada=True,
        anulada=False,
        fecha_venta__range=[fecha_desde, fecha_hasta]
    )

    # Aplicar filtros adicionales
    if vendedor_id and vendedor_id != '':
        ventas = ventas.filter(vendedor_id=vendedor_id)

    # Aplicar filtro por tipo de venta (nuevo)
    if tipo_venta and tipo_venta != '':
        ventas = ventas.filter(tipo_venta=tipo_venta)

    # Obtener detalles de ventas
    detalles = DetalleVenta.objects.filter(
        venta__in=ventas
    ).select_related('venta', 'producto', 'venta__vendedor', 'venta__cliente')

    if producto_id and producto_id != '':
        detalles = detalles.filter(producto_id=producto_id)

    # Estadísticas generales
    total_vendido = ventas.aggregate(total=Sum('total'))[
        'total'] or Decimal('0.00')
    total_transacciones = ventas.count()

    # Estadísticas por tipo de venta
    ventas_contado = ventas.filter(tipo_venta='contado').count()
    ventas_credito = ventas.filter(tipo_venta='credito').count()
    monto_contado = ventas.filter(tipo_venta='contado').aggregate(
        total=Sum('total'))['total'] or Decimal('0.00')
    monto_credito = ventas.filter(tipo_venta='credito').aggregate(
        total=Sum('total'))['total'] or Decimal('0.00')

    # Vendedores únicos en el período
    vendedores_activos = ventas.values('vendedor').distinct().count()

    # Ticket promedio
    ticket_promedio = ventas.aggregate(promedio=Avg('total'))[
        'promedio'] or Decimal('0.00')

    # Calcular total por vendedor
    total_por_vendedor = {}
    for venta in ventas:
        vendedor_nombre = venta.vendedor.get_full_name() or venta.vendedor.username
        if vendedor_nombre not in total_por_vendedor:
            total_por_vendedor[vendedor_nombre] = Decimal('0.00')
        total_por_vendedor[vendedor_nombre] += venta.total

    # Preparar datos para la tabla principal
    ventas_detalladas = []
    for detalle in detalles:
        venta = detalle.venta
        ventas_detalladas.append({
            'id': detalle.id,
            'fecha': venta.fecha_venta.strftime('%Y-%m-%d'),
            'numero_factura': venta.numero_factura,
            'producto_nombre': detalle.producto.descripcion if detalle.producto else 'N/A',
            'producto_codigo': detalle.producto.codigo_producto if detalle.producto else '',
            'cliente_nombre': venta.cliente_nombre,
            'cliente_documento': venta.cliente_documento,
            'vendedor_nombre': venta.vendedor.get_full_name() or venta.vendedor.username,
            'vendedor_id': venta.vendedor.id,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.precio_unitario,
            'monto': detalle.subtotal,
            'metodo_pago': venta.get_metodo_pago_display(),
            'tipo_venta': venta.get_tipo_venta_display(),
            'total_vendedor': total_por_vendedor.get(venta.vendedor.get_full_name() or venta.vendedor.username, Decimal('0.00')),
        })

    # Resumen por vendedor con tipo de venta
    resumen_vendedores = []
    for vendedor in ventas.values('vendedor__id', 'vendedor__username', 'vendedor__first_name', 'vendedor__last_name').distinct():
        ventas_vendedor = ventas.filter(vendedor_id=vendedor['vendedor__id'])

        ventas_contado_vendedor = ventas_vendedor.filter(
            tipo_venta='contado').count()
        ventas_credito_vendedor = ventas_vendedor.filter(
            tipo_venta='credito').count()

        monto_contado_vendedor = ventas_vendedor.filter(tipo_venta='contado').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')
        monto_credito_vendedor = ventas_vendedor.filter(tipo_venta='credito').aggregate(
            total=Sum('total'))['total'] or Decimal('0.00')

        cantidad_ventas = ventas_vendedor.count()
        monto_total = ventas_vendedor.aggregate(total=Sum('total'))[
            'total'] or Decimal('0.00')
        ticket_promedio_vendedor = ventas_vendedor.aggregate(
            promedio=Avg('total'))['promedio'] or Decimal('0.00')

        porcentaje = (monto_total / total_vendido *
                      100) if total_vendido > 0 else 0

        resumen_vendedores.append({
            'vendedor__id': vendedor['vendedor__id'],
            'vendedor__username': vendedor['vendedor__username'],
            'vendedor__first_name': vendedor['vendedor__first_name'],
            'vendedor__last_name': vendedor['vendedor__last_name'],
            'cantidad_ventas': cantidad_ventas,
            'ventas_contado': ventas_contado_vendedor,
            'ventas_credito': ventas_credito_vendedor,
            'monto_contado': monto_contado_vendedor,
            'monto_credito': monto_credito_vendedor,
            'monto_total': monto_total,
            'ticket_promedio': ticket_promedio_vendedor,
            'porcentaje': porcentaje,
        })

    # Ordenar por monto total descendente
    resumen_vendedores = sorted(
        resumen_vendedores, key=lambda x: x['monto_total'], reverse=True)

    # Resumen por producto
    resumen_productos = detalles.values(
        'producto__id',
        'producto__descripcion',
        'producto__codigo_producto'
    ).annotate(
        cantidad_vendida=Sum('cantidad'),
        monto_total=Sum('subtotal'),
        precio_promedio=Avg('precio_unitario')
    ).order_by('-monto_total')

    # Calcular porcentaje del total para cada producto
    for resumen in resumen_productos:
        if total_vendido > 0:
            resumen['porcentaje'] = (
                resumen['monto_total'] / total_vendido) * 100
        else:
            resumen['porcentaje'] = 0

    # Obtener listas para filtros
    vendedores_disponibles = User.objects.filter(
        id__in=ventas.values_list('vendedor', flat=True)
    ).distinct().order_by('first_name', 'last_name')

    productos_ids = detalles.values_list('producto', flat=True).distinct()
    productos_disponibles = EntradaProducto.objects.filter(
        id__in=productos_ids
    ).order_by('descripcion')

    # Ventas por día
    ventas_por_dia = ventas.annotate(
        fecha_dia=TruncDate('fecha_venta')
    ).values('fecha_dia').annotate(
        total_dia=Sum('total'),
        cantidad_ventas=Count('id')
    ).order_by('fecha_dia')

    # Preparar datos para el gráfico
    chart_labels = []
    chart_data = []
    for venta_dia in ventas_por_dia:
        chart_labels.append(venta_dia['fecha_dia'].strftime('%d/%m'))
        chart_data.append(float(venta_dia['total_dia'] or 0))

    context = {
        'fecha_desde': fecha_desde.strftime('%Y-%m-%d'),
        'fecha_hasta': fecha_hasta.strftime('%Y-%m-%d'),
        'hoy': hoy,
        'semana_pasada': semana_pasada,
        'mes_pasado': mes_pasado,
        'ventas_detalladas': ventas_detalladas,
        'resumen_vendedores': resumen_vendedores,
        'resumen_productos': resumen_productos,
        'ventas_por_dia': ventas_por_dia,
        'vendedores_disponibles': vendedores_disponibles,
        'productos_disponibles': productos_disponibles,
        'total_vendido': total_vendido,
        'total_transacciones': total_transacciones,
        'ventas_contado': ventas_contado,
        'ventas_credito': ventas_credito,
        'monto_contado': monto_contado,
        'monto_credito': monto_credito,
        'vendedores_activos': vendedores_activos,
        'ticket_promedio': ticket_promedio,
        'tipo_venta_selected': tipo_venta,  # Para mantener el filtro seleccionado
        'total_por_vendedor': json.dumps(total_por_vendedor, default=str),
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }

    return render(request, "facturacion/reportes.html", context)


@login_required
def reporte_detallado_vendedor(request, vendedor_id):
    """Reporte detallado de un vendedor específico"""
    fecha_hasta = timezone.now()
    fecha_desde = fecha_hasta - timedelta(days=30)

    if request.method == 'GET':
        fecha_desde_str = request.GET.get('fecha_desde')
        fecha_hasta_str = request.GET.get('fecha_hasta')

        if fecha_desde_str:
            fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d')
            fecha_desde = timezone.make_aware(fecha_desde)
        if fecha_hasta_str:
            fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d')
            fecha_hasta = timezone.make_aware(fecha_hasta)
            fecha_hasta = fecha_hasta.replace(hour=23, minute=59, second=59)

    # Obtener ventas del vendedor
    ventas = Venta.objects.filter(
        vendedor_id=vendedor_id,
        completada=True,
        anulada=False,
        fecha_venta__range=[fecha_desde, fecha_hasta]
    ).select_related('cliente')

    # Detalles de ventas
    detalles = DetalleVenta.objects.filter(
        venta__in=ventas
    ).select_related('producto', 'venta')

    # Estadísticas del vendedor
    total_vendido = ventas.aggregate(total=Sum('total'))[
        'total'] or Decimal('0.00')
    cantidad_ventas = ventas.count()
    ticket_promedio = ventas.aggregate(promedio=Avg('total'))[
        'promedio'] or Decimal('0.00')

    # Ventas por tipo
    ventas_contado = ventas.filter(tipo_venta='contado').count()
    ventas_credito = ventas.filter(tipo_venta='credito').count()
    monto_contado = ventas.filter(tipo_venta='contado').aggregate(
        total=Sum('total'))['total'] or Decimal('0.00')
    monto_credito = ventas.filter(tipo_venta='credito').aggregate(
        total=Sum('total'))['total'] or Decimal('0.00')

    # Ventas por día
    ventas_por_dia = ventas.annotate(
        fecha_dia=TruncDate('fecha_venta')
    ).values('fecha_dia').annotate(
        total_dia=Sum('total'),
        cantidad_ventas=Count('id')
    ).order_by('fecha_dia')

    # Ventas por cliente
    ventas_por_cliente = ventas.values(
        'cliente_nombre',
        'cliente_documento'
    ).annotate(
        total_cliente=Sum('total'),
        cantidad_compras=Count('id')
    ).order_by('-total_cliente')

    # Obtener información del vendedor
    try:
        vendedor = User.objects.get(id=vendedor_id)
        vendedor_nombre = vendedor.get_full_name() or vendedor.username
    except User.DoesNotExist:
        vendedor_nombre = "Vendedor no encontrado"

    context = {
        'vendedor_id': vendedor_id,
        'vendedor_nombre': vendedor_nombre,
        'fecha_desde': fecha_desde.strftime('%Y-%m-%d'),
        'fecha_hasta': fecha_hasta.strftime('%Y-%m-%d'),
        'ventas': ventas,
        'detalles': detalles,
        'total_vendido': total_vendido,
        'cantidad_ventas': cantidad_ventas,
        'ticket_promedio': ticket_promedio,
        'ventas_contado': ventas_contado,
        'ventas_credito': ventas_credito,
        'monto_contado': monto_contado,
        'monto_credito': monto_credito,
        'ventas_por_dia': ventas_por_dia,
        'ventas_por_cliente': ventas_por_cliente,
    }

    return render(request, "facturacion/reporte_vendedor.html", context)


@login_required
def exportar_reporte_csv(request):
    """Exportar reporte a CSV"""
    import csv
    from django.http import HttpResponse

    # Obtener filtros
    fecha_desde_str = request.GET.get('fecha_desde')
    fecha_hasta_str = request.GET.get('fecha_hasta')
    vendedor_id = request.GET.get('vendedor')
    tipo_venta = request.GET.get('tipo_venta')  # Nuevo filtro

    fecha_desde = datetime.strptime(
        fecha_desde_str, '%Y-%m-%d') if fecha_desde_str else timezone.now() - timedelta(days=30)
    fecha_desde = timezone.make_aware(fecha_desde)
    fecha_hasta = datetime.strptime(
        fecha_hasta_str, '%Y-%m-%d') if fecha_hasta_str else timezone.now()
    fecha_hasta = timezone.make_aware(fecha_hasta)
    fecha_hasta = fecha_hasta.replace(hour=23, minute=59, second=59)

    # Filtrar ventas
    ventas = Venta.objects.filter(
        completada=True,
        anulada=False,
        fecha_venta__range=[fecha_desde, fecha_hasta]
    )

    if vendedor_id:
        ventas = ventas.filter(vendedor_id=vendedor_id)

    if tipo_venta:
        ventas = ventas.filter(tipo_venta=tipo_venta)

    # Crear respuesta HTTP con CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{fecha_desde.date()}_al_{fecha_hasta.date()}.csv"'

    writer = csv.writer(response, delimiter=';')

    # Encabezados
    writer.writerow([
        'Fecha', 'N° Factura', 'Vendedor', 'Cliente', 'Cédula/RIF',
        'Producto', 'Cantidad', 'Precio Unitario', 'Subtotal',
        'Método Pago', 'Tipo Venta', 'Total Factura'
    ])

    # Datos
    for venta in ventas:
        detalles = DetalleVenta.objects.filter(venta=venta)
        for detalle in detalles:
            writer.writerow([
                venta.fecha_venta.strftime('%Y-%m-%d'),
                venta.numero_factura,
                venta.vendedor.get_full_name() or venta.vendedor.username,
                venta.cliente_nombre,
                venta.cliente_documento,
                detalle.producto.descripcion if detalle.producto else 'N/A',
                detalle.cantidad,
                detalle.precio_unitario,
                detalle.subtotal,
                venta.get_metodo_pago_display(),
                venta.get_tipo_venta_display(),
                venta.total
            ])

    return response


@login_required
def exportar_reporte_pdf(request):
    """Exportar reporte a PDF"""
    # Importar los modelos necesarios
    from .models import Venta, DetalleVenta, EntradaProducto
    from django.contrib.auth.models import User

    # Obtener filtros
    fecha_desde_str = request.GET.get('fecha_desde')
    fecha_hasta_str = request.GET.get('fecha_hasta')
    vendedor_id = request.GET.get('vendedor')
    producto_id = request.GET.get('producto')
    tipo_venta = request.GET.get('tipo_venta')  # Nuevo filtro

    # Convertir fechas
    if fecha_desde_str:
        fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d')
        fecha_desde = timezone.make_aware(fecha_desde)
    else:
        fecha_desde = timezone.now() - timedelta(days=30)

    if fecha_hasta_str:
        fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d')
        fecha_hasta = timezone.make_aware(fecha_hasta)
        fecha_hasta = fecha_hasta.replace(hour=23, minute=59, second=59)
    else:
        fecha_hasta = timezone.now()

    # Filtrar ventas
    ventas = Venta.objects.filter(
        completada=True,
        anulada=False,
        fecha_venta__range=[fecha_desde, fecha_hasta]
    ).select_related('vendedor', 'cliente')

    if vendedor_id:
        ventas = ventas.filter(vendedor_id=vendedor_id)

    if tipo_venta:
        ventas = ventas.filter(tipo_venta=tipo_venta)

    # Obtener detalles
    detalles = DetalleVenta.objects.filter(
        venta__in=ventas
    ).select_related('producto', 'venta')

    if producto_id and producto_id != '':
        detalles = detalles.filter(producto_id=producto_id)

    # Estadísticas
    total_vendido_result = ventas.aggregate(total=Sum('total'))
    total_vendido = total_vendido_result['total'] or Decimal('0.00')

    total_transacciones = ventas.count()
    vendedores_activos = ventas.values('vendedor').distinct().count()

    ticket_promedio_result = ventas.aggregate(promedio=Avg('total'))
    ticket_promedio = ticket_promedio_result['promedio'] or Decimal('0.00')

    # Estadísticas por tipo de venta para el PDF
    ventas_contado = ventas.filter(tipo_venta='contado').count()
    ventas_credito = ventas.filter(tipo_venta='credito').count()
    monto_contado = ventas.filter(tipo_venta='contado').aggregate(
        total=Sum('total'))['total'] or Decimal('0.00')
    monto_credito = ventas.filter(tipo_venta='credito').aggregate(
        total=Sum('total'))['total'] or Decimal('0.00')

    # Crear el PDF
    buffer = BytesIO()

    # Usar orientación landscape para más espacio horizontal
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()

    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1  # Centrado
    )

    elements.append(Paragraph("REPORTE DE VENTAS - SUPER BESTIA", title_style))

    # Información del período
    periodo_text = f"Período: {fecha_desde.strftime('%d/%m/%Y')} al {fecha_hasta.strftime('%d/%m/%Y')}"
    elements.append(Paragraph(periodo_text, styles["Normal"]))

    # Información de filtros aplicados
    filtros_text = []
    if vendedor_id:
        try:
            vendedor = User.objects.get(id=vendedor_id)
            vendedor_nombre = vendedor.get_full_name() or vendedor.username
            filtros_text.append(f"Vendedor: {vendedor_nombre}")
        except User.DoesNotExist:
            pass

    if tipo_venta:
        tipo_text = "Contado" if tipo_venta == 'contado' else "Crédito"
        filtros_text.append(f"Tipo Venta: {tipo_text}")

    if filtros_text:
        elements.append(Paragraph(" | ".join(filtros_text), styles["Normal"]))

    elements.append(Spacer(1, 20))

    # Estadísticas rápidas
    stats_data = [
        ['Total Vendido', 'Transacciones', 'Contado', 'Crédito'],
        [f"${total_vendido:,.2f}", str(
            total_transacciones), f"${monto_contado:,.2f}", f"${monto_credito:,.2f}"],
        ['', '', f"({ventas_contado} ventas)", f"({ventas_credito} ventas)"]
    ]

    stats_table = Table(stats_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, 2), colors.white),
        ('GRID', (0, 0), (-1, 2), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, 2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, 1), 11),
        ('FONTSIZE', (0, 2), (-1, 2), 9),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.grey),
    ]))

    elements.append(stats_table)
    elements.append(Spacer(1, 30))

    # Tabla de detalles de ventas
    elements.append(Paragraph("DETALLE DE VENTAS", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    # Preparar datos para la tabla
    table_data = [['Fecha', 'Factura', 'Tipo', 'Producto',
                   'Cliente', 'Vendedor', 'Cant.', 'Precio', 'Total']]

    # Limitar a 100 registros para el PDF para evitar archivos muy grandes
    detalles_limitados = detalles[:100]

    for detalle in detalles_limitados:
        venta = detalle.venta
        producto_desc = detalle.producto.descripcion if detalle.producto else 'N/A'
        if len(producto_desc) > 30:
            producto_desc = producto_desc[:27] + "..."

        cliente_nombre = venta.cliente_nombre or 'N/A'
        if len(cliente_nombre) > 20:
            cliente_nombre = cliente_nombre[:17] + "..."

        vendedor_nombre = venta.vendedor.get_full_name() or venta.vendedor.username
        if len(vendedor_nombre) > 15:
            vendedor_nombre = vendedor_nombre[:12] + "..."

        tipo_venta_display = "C" if venta.tipo_venta == 'contado' else "Créd"

        row = [
            venta.fecha_venta.strftime('%d/%m/%Y'),
            venta.numero_factura or 'N/A',
            tipo_venta_display,
            producto_desc,
            cliente_nombre,
            vendedor_nombre,
            str(detalle.cantidad),
            f"${detalle.precio_unitario:,.2f}",
            f"${detalle.subtotal:,.2f}"
        ]
        table_data.append(row)

    # Si no hay detalles, agregar mensaje
    if not detalles_limitados:
        table_data.append(
            ['', '', 'No hay datos para mostrar', '', '', '', '', '', ''])

    # Crear tabla
    ventas_table = Table(table_data, colWidths=[
                         0.8*inch, 1*inch, 0.5*inch, 2*inch, 1.5*inch, 1.5*inch, 0.5*inch, 0.8*inch, 1*inch])
    ventas_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (6, 1), (8, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    elements.append(ventas_table)

    # Resumen por vendedor (solo si hay ventas)
    if ventas.exists():
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("RESUMEN POR VENDEDOR", styles["Heading2"]))
        elements.append(Spacer(1, 10))

        # Agrupar por vendedor
        resumen_vendedores = ventas.values(
            'vendedor__first_name',
            'vendedor__last_name',
            'vendedor__username'
        ).annotate(
            cantidad_ventas=Count('id'),
            monto_total=Sum('total'),
            ticket_promedio=Avg('total')
        ).order_by('-monto_total')

        vendedor_data = [['Vendedor', 'Ventas',
                          'Monto Total', 'Ticket Promedio', '%']]

        for resumen in resumen_vendedores:
            nombre = f"{resumen['vendedor__first_name'] or ''} {resumen['vendedor__last_name'] or ''}".strip(
            )
            if not nombre:
                nombre = resumen['vendedor__username']

            if len(nombre) > 20:
                nombre = nombre[:17] + "..."

            porcentaje = (float(resumen['monto_total'] or 0) /
                          float(total_vendido) * 100) if total_vendido > 0 else 0

            row = [
                nombre,
                str(resumen['cantidad_ventas']),
                f"${resumen['monto_total'] or 0:,.2f}",
                f"${resumen['ticket_promedio'] or 0:,.2f}",
                f"{porcentaje:.1f}%"
            ]
            vendedor_data.append(row)

        vendedor_table = Table(vendedor_data, colWidths=[
                               2*inch, 1*inch, 1.5*inch, 1.5*inch, 1*inch])
        vendedor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (4, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.lightgrey]),
        ]))

        elements.append(vendedor_table)

    # Pie de página
    elements.append(Spacer(1, 40))
    fecha_generacion = timezone.now().strftime("%d/%m/%Y %H:%M:%S")
    elements.append(
        Paragraph(f"Generado el: {fecha_generacion}", styles["Normal"]))
    elements.append(
        Paragraph(f"Total registros en período: {detalles.count()}", styles["Normal"]))
    if detalles.count() > 100:
        elements.append(Paragraph(f"Nota: Mostrando solo los primeros 100 registros de {detalles.count()}",
                                  ParagraphStyle('Note', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))

    # Construir el PDF
    doc.build(elements)

    # Obtener el valor del buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Crear la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{fecha_desde.strftime("%Y-%m-%d")}_al_{fecha_hasta.strftime("%Y-%m-%d")}.pdf"'
    response.write(pdf)

    return response
