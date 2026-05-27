import os
import glob

template_dir = r"c:\Users\Acosta\Desktop\spbestia\repuesto-alexander\repuesto_alexander\sytem_phone\facturacion\templates\facturacion"
html_files = glob.glob(os.path.join(template_dir, "*.html"))

old_injection_block = """    <!-- Menú para Usuario Especial -->
    {% if user|has_group:"Usuario Especial" and not user.is_superuser %}
    <a href="{% url 'ventas' %}" class="menu-item">
        <i class='bx bx-receipt'></i>
        <span>Facturación</span>
    </a>
    <a href="{% url 'cuentaporcobrar' %}" class="menu-item">
        <i class='bx bx-money'></i>
        <span>Cuenta por Cobrar</span>
    </a>
    <a href="{% url 'entrada' %}" class="menu-item">
        <i class='bx bx-package'></i>
        <span>Entrada Mercancía</span>
    </a>
    {% endif %}"""

new_injection_block = """    <!-- Menú para Usuario Especial -->
    {% if user|has_group:"Usuario Especial" and not user.is_superuser %}
    <a href="{% url 'ventas' %}" class="menu-item">
        <i class='bx bx-receipt'></i>
        <span>Facturación</span>
    </a>
    <a href="{% url 'cuentaporcobrar' %}" class="menu-item">
        <i class='bx bx-money'></i>
        <span>Cuenta por Cobrar</span>
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
    {% endif %}"""

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine if we have to replace the old block or add a new one
    if "<!-- Menú para Usuario Especial -->" in content:
        # replace the old block with the new block. We use regex to match the old block in case spacing varies
        import re
        pattern = r"<!-- Menú para Usuario Especial -->.*?{% endif %}"
        content = re.sub(pattern, new_injection_block, content, flags=re.DOTALL)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {os.path.basename(file_path)}")
