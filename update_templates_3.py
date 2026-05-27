import os
import glob
import re

template_dir = r"c:\Users\Acosta\Desktop\spbestia\repuesto-alexander\repuesto_alexander\sytem_phone\facturacion\templates\facturacion"
html_files = glob.glob(os.path.join(template_dir, "*.html"))

new_injection_block = """    <!-- Menú para Usuario Especial -->
    {% if user|has_group:"Usuario Especial" and not user.is_superuser %}
    <a href="{% url 'ventas' %}" class="menu-item">
        <i class='bx bx-receipt'></i>
        <span>Facturación</span>
    </a>
    <a href="{% url 'registrodecliente' %}" class="menu-item">
        <i class='bx bx-user-plus'></i>
        <span>Registrar Cliente</span>
    </a>
    <a href="{% url 'listadecliente' %}" class="menu-item">
        <i class='bx bx-group'></i>
        <span>Clientes</span>
    </a>
    <a href="{% url 'cuentaporcobrar' %}" class="menu-item">
        <i class='bx bx-money'></i>
        <span>Cuenta por Cobrar</span>
    </a>
    <a href="{% url 'cuentaporpagar' %}" class="menu-item">
        <i class='bx bx-credit-card'></i>
        <span>Cuenta Por Pagar</span>
    </a>
    <a href="{% url 'entrada' %}" class="menu-item">
        <i class='bx bx-package'></i>
        <span>Entrada Mercancía</span>
    </a>
    <a href="{% url 'compras' %}" class="menu-item">
        <i class='bx bx-cart-download'></i>
        <span>Compras</span>
    </a>
    <a href="{% url 'inventario' %}" class="menu-item">
        <i class='bx bx-archive'></i>
        <span>Inventario</span>
    </a>
    <a href="{% url 'registrosuplidores' %}" class="menu-item">
        <i class='bx bx-building'></i>
        <span>Registrar Suplidores</span>
    </a>
    <a href="{% url 'gestiondesuplidores' %}" class="menu-item">
        <i class='bx bx-buildings'></i>
        <span>Suplidores</span>
    </a>
    {% endif %}"""

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if "<!-- Menú para Usuario Especial -->" in content:
        pattern = r"<!-- Menú para Usuario Especial -->.*?{% endif %}"
        new_content = re.sub(pattern, new_injection_block, content, flags=re.DOTALL)
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {os.path.basename(file_path)}")
