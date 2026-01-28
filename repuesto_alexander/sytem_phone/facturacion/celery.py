import os
from celery import Celery
from celery.schedules import crontab

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sytem_phone.settings')

app = Celery('tu_proyecto')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configurar tareas programadas
app.conf.beat_schedule = {
    'cerrar-cajas-automaticamente': {
        'task': 'facturacion.tasks.cerrar_cajas_automaticamente_task',
        'schedule': crontab(hour=17, minute=30),  # 5:30 PM todos los días
    },
}