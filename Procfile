web: gunicorn edx_pr_webhooks.wsgi --log-file -
celeryd: celery -A edx_pr_webhooks.tasks worker --loglevel=info -E
