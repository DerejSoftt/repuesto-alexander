import os
import glob

template_dir = r"c:\Users\Acosta\Desktop\spbestia\repuesto-alexander\repuesto_alexander\sytem_phone\facturacion\templates\facturacion"
html_files = glob.glob(os.path.join(template_dir, "*.html"))

injection_block = """
    <!-- Menú para Usuario Especial -->
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
    {% endif %}

"""

for file_path in html_files:
    if "ventas.html" in file_path or "entrada.html" in file_path:
        continue  # Already updated these manually
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "<!-- Menú para Usuario Especial -->" in content:
        continue # Already updated

    # Try to find the common superuser markers
    target_markers = [
        "<!-- Menú EXCLUSIVO para superusuarios -->",
        "<!-- Menú solo para superusuarios -->"
    ]
    
    replaced = False
    for marker in target_markers:
        if marker in content:
            content = content.replace(marker, injection_block + "    " + marker)
            replaced = True
            break
            
    if replaced:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {os.path.basename(file_path)}")
    else:
        print(f"Could not find marker in {os.path.basename(file_path)}")
