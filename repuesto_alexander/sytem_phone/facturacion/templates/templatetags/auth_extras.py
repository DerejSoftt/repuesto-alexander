# facturacion/templatetags/auth_extras.py
from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Verifica si un usuario pertenece a un grupo específico
    """
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()

@register.filter(name='has_any_group')
def has_any_group(user, group_names):
    """
    Verifica si un usuario pertenece a alguno de los grupos especificados
    """
    if not user or not user.is_authenticated:
        return False
    group_list = [name.strip() for name in group_names.split(',')]
    return user.groups.filter(name__in=group_list).exists()