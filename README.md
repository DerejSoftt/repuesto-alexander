![Logo del sistema](img-doc/derejautix.png)

# Documentación Técnica del Sistema Derej Autix

## 1. Introducción

El proyecto **Derej Autix** es una plataforma integral para la operación diaria de comercios de repuestos y productos. Centraliza la gestión de inventario, ciclo de ventas, control de caja, créditos, cobranzas, devoluciones y generación de comprobantes. Está construido sobre **Django 4.2.20** y utiliza **MySQL** como base de datos principal, con una app principal denominada `facturacion` que concentra modelos, vistas, plantillas y recursos estáticos propios del negocio.

## 2. Tecnologías y dependencias clave

- **Django 4.2.20** para el framework web y ORM.
- **MySQL** como motor de base de datos principal.
- **Celery 5.6.2** para tareas asíncronas y programadas.
- **ReportLab** y **xhtml2pdf** para la emisión de comprobantes PDF y reportes impresos.
- **Pillow**, **cryptography**, **pandas**, **factory_boy**, **Faker** y más (ver `requirements.txt`).
- **Configuración regional**: `LANGUAGE_CODE='es-do'`, `TIME_ZONE='America/Santo_Domingo'`.
- **Autenticación estándar de Django**, decoradores `login_required` y permisos para operaciones sensibles.

## 3. Arquitectura general

- **App única (`facturacion`)**: concentra los modelos de dominio, vistas basadas en funciones y rutas declaradas en [urls.py](sytem_phone/facturacion/urls.py).
- **Plantillas HTML** bajo [`templates/facturacion`](sytem_phone/facturacion/templates/facturacion/), organizadas por vistas (ventas, dashboard, entradas, cuentas por cobrar, etc.).
- **Recursos estáticos** ubicados en [static/image](sytem_phone/facturacion/static/image/).
- **Configuración central** en [settings.py](sytem_phone/sytem_phone/settings.py), donde se habilitan middlewares, almacenamiento de estáticos y parámetros regionales.
- **Seguridad**: autenticación estándar de Django, decoradores y permisos para operaciones sensibles (por ejemplo edición o eliminación de inventario).

## Estructura de Carpetas

```
sytem_phone/
│   manage.py
│   requirements.txt
│
├── facturacion/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   │   └── facturacion/
│   │       ├── ventas.html
│   │       ├── dashboard.html
│   │       ├── inventario.html
│   │       ├── registrodecliente.html
│   │       ├── roles.html
│   │       ├── anular.html
│   │       ├── cierredecaja.html
│   │       ├── cuadre.html
│   │       ├── cuentaporcobrar.html
│   │       ├── cuentaporpagar.html
│   │       ├── devoluciones.html
│   │       ├── entrada.html
│   │       ├── gestiondesuplidores.html
│   │       ├── index.html
│   │       ├── iniciocaja.html
│   │       ├── listadecliente.html
│   │       ├── lista_comprobantes.html
│   │       ├── reavastecer.html
│   │       ├── registrosuplidores.html
│   │       ├── reimprimirfactura.html
│   │       ├── reportes.html
│   │       ├── reporte_cuadre.html
│   │       ├── ver_factura.html
│   ├── migrations/
│   ├── templatetags/
│   ├── tests.py
│   ├── admin.py
│   ├── apps.py
│
├── sytem_phone/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│
├── static/
│   └── image/
```

## 4. Modelo de datos principal

Los modelos residen en [models.py](sytem_phone/facturacion/models.py) y cubren todo el ciclo operativo.

| Modelo                | Rol principal                                                  | Relacionamientos destacados                                        |
| --------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------ |
| `Rol`                 | Gestión de roles y permisos de usuario                         | Extiende `Group` de Django, vincula usuarios y permisos.           |
| `Proveedor`           | Información de proveedores y condiciones de pago               | Relacionado a productos (`EntradaProducto`).                       |
| `EntradaProducto`     | Inventario, stock, precios y trazabilidad de productos         | Consumido por ventas, movimientos de stock, detalles de venta.     |
| `Cliente`             | Registro de clientes con límite de crédito y datos de contacto | Asociado a ventas, cuentas por cobrar.                             |
| `Venta`               | Facturación, pagos, descuentos, auditoría                      | Relación 1:N con `DetalleVenta`, 1:1 con `CuentaPorCobrar`.        |
| `DetalleVenta`        | Desglose de productos vendidos, cantidades y precios unitarios | FK a `Venta`, `EntradaProducto`.                                   |
| `CuentaPorCobrar`     | Gestión de créditos y cuentas pendientes                       | 1:1 con `Venta`, N:1 con `Cliente`, N:1 con `PagoCuentaPorCobrar`. |
| `PagoCuentaPorCobrar` | Registro de pagos a cuentas por cobrar                         | FK a `CuentaPorCobrar`.                                            |
| `Caja`                | Control de apertura/cierre y movimientos de caja               | Relacionado a usuario y cierres de caja.                           |
| `MovimientoStock`     | Trazabilidad de entradas, salidas y ajustes de stock           | FK a `EntradaProducto`, usuario.                                   |
| `CierreCaja`          | Registro de cierres de caja y conciliaciones                   | FK a `Caja`.                                                       |

## 5. Módulos funcionales

### 5.1 Autenticación y roles

- Vista `index` maneja login utilizando `django.contrib.auth`. Redirige a dashboard tras autenticarse.
- Decoradores `login_required` protegen todas las vistas operativas. Los permisos restringen endpoints críticos (por ejemplo edición o eliminación de inventario).
- Vista `roles` y plantillas asociadas permiten administrar permisos básicos (frente a `User`, `Group`, `Permission`).

### 5.2 Dashboard y analítica

- `dashboard` y vistas asociadas calculan métricas diarias/mensuales con ORM y consultas agregadas.
- Indicadores: ventas, créditos, acumulados mensuales, evolución semanal, inventario disponible, productos con stock bajo, cuentas vencidas, top productos y últimas ventas.

### 5.3 Gestión de inventario

- Vista `inventario` expone un catálogo editable con edición y eliminación protegida para usuarios autorizados.
- `EntradaProducto.save()` genera códigos únicos, calcula precios y controla stock. Cada variación de cantidad dispara `MovimientoStock` para trazabilidad.
- Endpoints adicionales soportan altas manuales y carga de plantillas.

### 5.4 Clientes

- `registrodecliente` y `listadecliente` gestionan el ciclo de vida de clientes y validan límites de crédito.
- Endpoints REST permiten integraciones front-end.

### 5.5 Pedidos y facturación

- `ventas` carga formulario con clientes activos e inventario disponible.
- Creación de venta valida totales, controla descuentos y soporta ventas al contado y crédito.
- Cada `DetalleVenta` descuenta stock y registra movimientos. El view final retorna respuesta con desglose de totales para usar en el frontend.

### 5.6 Devoluciones y anulaciones

- `devoluciones` y `anular` controlan devoluciones, reponiendo stock y marcando razones.
- Endpoints permiten revertir ventas o productos, restaurando inventario y dejando trazabilidad.

### 5.7 Reporting y utilitarios

- Reportes PDF: comprobantes, listados de cuentas vencidas y facturas reimpresas (basado en ReportLab/xhtml2pdf).
- Exportaciones desde funciones auxiliares en [views.py](sytem_phone/facturacion/views.py).

### 5.8 Organización de `views.py`

El archivo [views.py](sytem_phone/facturacion/views.py) agrupa todas las vistas de la app y está dividido por bloques temáticos, cada uno con decoradores y helpers específicos:

- **Autenticación y dashboard**: `index`, `dashboard` y métricas diarias/mensuales.
- **Inventario**: `inventario`, control de stock y trazabilidad.
- **Clientes y ventas**: `registrodecliente`, `ventas`, validaciones y creación de transacciones.
- **Devoluciones y anulaciones**: `devoluciones`, `anular`, control de reversos y restablecimiento de stock.
- **Comprobantes y utilitarios**: generación de PDFs y reportes.

## 6. Flujo operativo end-to-end

1. **Ingreso de mercancía**: usuarios registran productos y entradas, generando códigos únicos y movimientos de stock.
2. **Habilitación de caja**: cada vendedor abre su sesión.
3. **Venta**:
   - Selección de cliente (existente o nuevo).
   - Construcción de carrito con validación de stock en tiempo real.
   - Configuración de pago: contado o crédito.
   - Confirmación: se crea `Venta`, `DetalleVenta`, se descuenta stock y se actualiza el dashboard.
4. **Facturación**: se genera factura, se calcula ITBIS, descuentos y totales; se imprime comprobante.
5. **Devoluciones / anulaciones**: flujos dedicados revierten ventas o productos, restaurando inventario y dejando trazabilidad.
6. **Cierre**: al final del día se consolidan los datos para arqueos diarios.

## 7. Integraciones internas y archivos relevantes

- **Rutas**: cubren todo el dominio y se centralizan en [urls.py](sytem_phone/facturacion/urls.py).
- **Plantillas**: cada feature tiene su HTML (por ejemplo [ventas.html](sytem_phone/facturacion/templates/facturacion/ventas.html), [dashboard.html](sytem_phone/facturacion/templates/facturacion/dashboard.html), [cuentaporcobrar.html](sytem_phone/facturacion/templates/facturacion/cuentaporcobrar.html)).
- **Assets**: imágenes y scripts en [static/image/](sytem_phone/facturacion/static/image/).

## 8. Seguridad y cumplimiento

- Credenciales de base de datos y llaves se cargan desde variables de entorno (no versionado).
- CSRF está habilitado globalmente; endpoints AJAX críticos usan `@csrf_exempt` solo cuando es imprescindible y se compensan con permisos.
- Validaciones server-side para montos, descuento, stock y límites de crédito evitan inconsistencias contables.
- Soft delete en modelos críticos preserva histórico sin exponer datos sensibles en documentos.

## 9. Despliegue y configuración

1. Instalar dependencias ([requirements.txt](sytem_phone/requirements.txt)).
2. Configurar base de datos y variables de entorno en `settings.py` y/o `.env`.
3. Ejecutar migraciones (`python manage.py migrate`).
4. Crear superusuario (`python manage.py createsuperuser`).
5. Colectar estáticos (`python manage.py collectstatic`).
6. Ejecutar el servidor: `python manage.py runserver`.

## 10. Métricas y mejoras futuras sugeridas

- **KPI adicionales**: rotación de inventario, margen por categoría, aging de cuentas.
- **Alertas proactivas**: notificaciones por correo o WhatsApp para cuentas vencidas o stock crítico.
- **API pública**: encapsular endpoints clave en una API REST (Django REST Framework) para integraciones externas.
- **Pruebas automatizadas**: ampliar `tests.py` con casos de venta, rebaja de deuda y devoluciones.

---

## Modelos Clave

- **Rol:** Controla roles y permisos de usuario.
- **Proveedor:** Registro de proveedores, condiciones de pago y contacto.
- **EntradaProducto:** Controla productos con stock, precios, trazabilidad y subtotales automáticos.
- **Cliente:** Control de clientes, crédito, teléfonos, dirección y estado.
- **Venta:** Maneja ventas, tipos, estados, items, auditoría y relación con cuentas por cobrar.
- **DetalleVenta:** Desglose de productos vendidos, cantidades y precios unitarios.
- **CuentaPorCobrar:** Registra créditos, pagos, vencimientos y estado de cuentas.
- **PagoCuentaPorCobrar:** Pagos realizados a cuentas por cobrar.
- **Caja:** Control de caja, apertura, cierre y arqueos.
- **MovimientoStock:** Registra movimientos de inventario por diferentes motivos.
- **CierreCaja:** Rastrea cierres y conciliaciones de caja.

## Templates

La aplicación cuenta con templates personalizados para cada funcionalidad, con diseño moderno y sidebar fijo. Ejemplos:

- `ventas.html`: Panel de ventas y facturación.
- `dashboard.html`: Dashboard de métricas.
- `inventario.html`: Control de productos y stock.
- `registrodecliente.html`: Registro y consulta de clientes.
- `roles.html`: Gestión de usuarios y permisos.
- `anular.html`: Anulación de ventas.
- `cierredecaja.html`: Cierre de caja.
- `cuadre.html`: Cuadre de caja.
- `cuentaporcobrar.html`: Gestión de cuentas por cobrar.
- `cuentaporpagar.html`: Gestión de cuentas por pagar.
- `devoluciones.html`: Devoluciones y anulaciones.
- `entrada.html`: Entrada de productos.
- `gestiondesuplidores.html`: Gestión de proveedores.
- `index.html`: Login y acceso.
- `iniciocaja.html`: Inicio de caja.
- `listadecliente.html`: Listado de clientes.
- `lista_comprobantes.html`: Listado de comprobantes.
- `reavastecer.html`: Reabastecimiento de stock.
- `registrosuplidores.html`: Registro de proveedores.
- `reimprimirfactura.html`: Reimpresión de facturas.
- `reportes.html`: Reportes generales.
- `reporte_cuadre.html`: Reporte de cuadre de caja.
- `ver_factura.html`: Visualización de facturas.

## Instalación

1. **Requisitos:**
   - Python 3.10+
   - Django 4.2.20
   - Paquetes adicionales: ver `requirements.txt`.

2. **Instalación de dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configuración de base de datos:**
   - Edita las variables de entorno en `settings.py` o `.env` para definir la conexión a la base de datos.

4. **Migraciones:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Creación de superusuario:**

   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecución del servidor:**
   ```bash
   python manage.py runserver
   ```

## Uso

- Accede al sistema desde el navegador en `http://localhost:8000`.
- Inicia sesión con usuario registrado.
- Utiliza el dashboard para visualizar métricas.
- Gestiona inventario, ventas, facturación, devoluciones y clientes desde el menú lateral.
- Imprime facturas y reportes desde las vistas correspondientes.

## Seguridad y Roles

- El sistema implementa autenticación y autorización basada en usuarios, grupos y permisos de Django.
- Los roles permiten segmentar el acceso a funcionalidades críticas.

## Pruebas

- El archivo `tests.py` está preparado para pruebas unitarias con Django TestCase.
- Se recomienda implementar pruebas para cada modelo y vista crítica.

## Personalización

- Los templates pueden ser adaptados para branding propio.
- El sistema soporta ampliación de modelos y vistas para nuevas funcionalidades.

## Dependencias

Ver archivo [requirements.txt](sytem_phone/requirements.txt) para la lista completa.

## Configuración

Variables de entorno recomendadas para el archivo `.env`:

```bash
SECRET_KEY="tu_clave_secreta"
DB_NAME="nombre_base_datos"
DB_USER="usuario"
DB_PASSWORD="contraseña"
DB_HOST="localhost"
DB_PORT="3306"
ALLOWED_HOSTS="localhost,127.0.0.1"
CSRF_TRUSTED_ORIGINS="http://localhost,http://127.0.0.1"
DEBUG=True
```

- Variables de entorno para seguridad y base de datos.
- Soporte para archivos estáticos y media.
- Configuración de zona horaria: `America/Santo_Domingo`.

## Contacto y Soporte

Para soporte, contactar al desarrollador o consultar la documentación de Django.
