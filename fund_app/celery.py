# project_name/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fund_app.settings')

app = Celery('fund_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
