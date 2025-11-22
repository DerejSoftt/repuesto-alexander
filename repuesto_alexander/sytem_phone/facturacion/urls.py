from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('logout/', views.logout_view, name='logout'),  
    path('', views.index, name='login'),  # Página de login
    path("" , views.index, name="index"),
    path("dashboard" , views.dashboard, name="dashboard"),
    path('dashboard/data/', views.dashboard_data, name='dashboard_data'),
    path("inventario", views.inventario, name="inventario"),
    path('inventario/datos/', views.inventario_datos, name='inventario_datos'),
    path('inventario/editar/<int:id>/', views.inventario_editar, name='inventario_editar'),
    path('inventario/eliminar/<int:id>/', views.inventario_eliminar, name='inventario_eliminar'),
    # path("facturacion", views.facturacion, name="facturacion"),
    path("listadecliente", views.listadecliente, name="listadecliente"),
    path("registrodecliente", views.registrodecliente,  name="registrodecliente"),
    path("entrada", views.entrada, name="entrada"),
    path('agregar-nuevo-producto/', views.agregar_nuevo_producto, name='agregar_nuevo_producto'),
    path('productos-disponibles/', views.obtener_productos_disponibles, name='obtener_productos_disponibles'),
    path('producto/<int:entrada_id>/', views.obtener_datos_entrada, name='obtener_datos_entrada'),
    path('obtener-datos-plantilla/<int:plantilla_id>/', views.obtener_datos_plantilla, name='obtener_datos_plantilla'),
    path('buscar-productos-similares/', views.buscar_productos_similares, name='buscar_productos_similares'),
    path("cuentaporcobrar", views.cuentaporcobrar, name="cuentaporcobrar"),
    path("gestiondesuplidores", views.gestiondesuplidores, name="gestiondesuplidores"),
    path("registrosuplidores", views.registrosuplidores, name="registrosuplidores"),
    path('proveedores/agregar/', views.agregar_proveedor, name='agregar_proveedor'),
    path('proveedores/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('proveedores/<int:id>/data/', views.get_proveedor_data, name='get_proveedor_data'),
    path('guardar-cliente/', views.guardar_cliente, name='guardar_cliente'),
    path('obtener-clientes/', views.obtener_clientes, name='obtener_clientes'),
    path('eliminar-cliente/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('editar-cliente/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('iniciocaja', views.iniciocaja, name='iniciocaja'),
    path('ventas', views.ventas, name='ventas'),
    path('buscar-productos/', views.buscar_productos, name='buscar_productos'),
    path('procesar-venta/', views.procesar_venta, name='procesar_venta'),
    #   path('historial-ventas/', views.historial_ventas, name='historial_ventas'),
    path('comprobante-venta/<int:venta_id>/', views.comprobante_venta, name='comprobante_venta'),
    path('buscar-productos/', views.buscar_productos_similares, name='buscar_productos'),
    path('registrar-pago/', views.registrar_pago, name='registrar_pago'),
    path('cuentas-por-cobrar/<int:cuenta_id>/', views.detalle_cuenta, name='detalle_cuenta'),
    path('cierredecaja', views.cierredecaja, name='cierredecaja'),
    path('procesar-cierre/', views.procesar_cierre_caja, name='procesar_cierre_caja'),
    path('cuadre', views.cuadre, name='cuadre'),
    path('reavastecer', views.reavastecer, name='reavastecer'),
    path('actualizar-stock/', views.actualizar_stock, name='actualizar_stock'),
    path('devoluciones', views.devoluciones, name='devoluciones'),
    path('roles', views.roles, name='roles'),
    path('anular', views.anular, name='anular'),
    path('buscar-factura/', views.buscar_factura, name='buscar_factura'),
    # path('anular-factura/', views.anular_factura, name='anular_factura_action'),
    path('buscar-factura-devolucion/', views.buscar_factura_devolucion, name='buscar_factura_devolucion'),
    path('procesar-devolucion/', views.procesar_devolucion, name='procesar_devolucion'),
    path('anular-cuenta/<int:cuenta_id>/', views.anular_cuenta, name='anular_cuenta'),
    path('generar-comprobante-pdf/<int:comprobante_id>/', views.generar_comprobante_pdf, name='generar_comprobante_pdf'),
    path('lista-comprobantes/', views.lista_comprobantes, name='lista_comprobantes'),
    path('reimprimirfactura/', views.reimprimir_factura, name='reimprimirfactura'),
    path('buscar-facturaR/', views.buscar_facturaR, name='buscar_facturaR'),
    path('ultima-factura/', views.ultima_factura, name='ultima_factura'), 
    path('eliminar-cuenta-pagada/<int:cuenta_id>/', views.eliminar_cuenta_pagada, name='eliminar_cuenta_pagada'),
    path('anular_factura/', views.anular_factura, name='anular_factura_action'),
    path('buscar_comprobante/', views.buscar_comprobante, name='buscar_comprobante'),
    path('anular_comprobante/', views.anular_comprobante_action, name='anular_comprobante_action'),
    path('ultimo-comprobante/', views.ultimo_comprobante, name='ultimo_comprobante'),
    path('cotizacion', views.cotizacion, name='cotizacion'),
    path('generar-factura/', views.generar_factura, name='generar_factura'),
    path('obtener-productoscotizacion/', views.obtener_productoscotizacion, name='obtener_productoscotizacion'),
    path('ver-factura/', views.ver_factura, name='ver_factura'),
     path('dashboard/usuarios/', views.get_usuarios, name='get_usuarios'),
    path('dashboard/cuadres/', views.get_cuadres, name='get_cuadres'),
    path('dashboard/cuadre/<int:cuadre_id>/pdf/', views.generar_pdf_cuadre, name='generar_pdf_cuadre'),
     path('dashboard/cuadres/pdf-todos/', views.generar_pdf_todos_cuadres, name='pdf_todos_cuadres'),
    path('dashboard/cuadre/<int:cuadre_id>/pdf/', views.generar_pdf_cuadre, name='pdf_cuadre_individual'),

    path('compras', views.compras, name='compras'),
      path('buscar-productos-cuentas-pagar/', views.buscar_productos_cuentas_pagar, name='buscar_productos_cuentas_pagar'),
    path('guardar-cuenta-por-pagar/', views.guardar_cuenta_por_pagar, name='guardar_cuenta_por_pagar'),
    path('cuentaporpagar', views.cuentaporpagar, name='cuentaporpagar'),
   path('cuentas-por-pagar/datos/', views.cuentas_por_pagar_datos, name='cuentas_por_pagar_datos'),
    path('cuentas-por-pagar/procesar-pago/<int:cuenta_id>/', views.procesar_pago_cuenta, name='procesar_pago_cuenta'),
    path('cuentas-por-pagar/detalle/<int:cuenta_id>/', views.obtener_detalle_cuenta, name='obtener_detalle_cuenta'),
    path('cuentas-por-pagar/actualizar/<int:cuenta_id>/', views.actualizar_cuenta_por_pagar, name='actualizar_cuenta_por_pagar'),
    path('cuentas-por-pagar/eliminar/<int:cuenta_id>/', views.eliminar_cuenta_por_pagar, name='eliminar_cuenta_por_pagar'),
    path('cuentas-por-pagar/factura/<int:cuenta_id>/', views.generar_factura_pago, name='generar_factura_pago'),
      path('cuentas-por-pagar/factura-pdf/<int:cuenta_id>/', views.generar_factura_pdf, name='generar_factura_pdf_real'),
      # En tu urls.py
     # En tu urls.py
    path('dashboard/movimientos/', views.movimientos_stock, name='movimientos_stock'),
    path('dashboard/movimientos/pdf/', views.movimientos_stock_pdf, name='movimientos_stock_pdf'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    



    



