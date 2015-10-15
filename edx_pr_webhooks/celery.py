from __future__ import absolute_import

import os

import iron_celery
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edx_pr_webhooks.settings')

from django.conf import settings

app = Celery('edx_pr_webhooks', broker='ironmq://', backend='ironcache://')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
