from django.conf import settings

from celery import Celery
import iron_celery
import requests

app = Celery('edx_pr_webhooks', broker='ironmq://', backend='ironcache://')


@app.task
def acquire_github_token_task(code, state):
    """
    Given a temporary Github code and the OAuth flow state token, get
    an access token and persist it with the correct repos.
    """
    response = requests.post(
        settings.GITHUB_OAUTH_TOKEN_URL,
        headers={'accept': 'application/json'},
        data={
            'client_id': settings.GITHUB_OAUTH_CLIENT_ID,
            'client_secret': settings.GITHUB_OAUTH_CLIENT_SECRET,
            'code': code,
            'redirect_uri': '',
            'state': state
        }
    )
    access_token = response.json()['access_token']
    print access_token
