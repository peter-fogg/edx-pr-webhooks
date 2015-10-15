"""
Views for responding to Github API events.
"""
import json
import requests
from urllib import urlencode
from uuid import uuid4

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .models import Repo
from .tasks import acquire_github_token_task


@require_GET
def index(request):
    """Home page."""
    random_state = uuid4().hex
    request.session['state'] = random_state
    query = {
        'client_id': settings.GITHUB_OAUTH_CLIENT_ID,
        'redirect_uri': request.build_absolute_uri(reverse('acquire_github_token')),
        'scope': settings.GITHUB_API_SCOPES,
        'state': random_state
    }
    return render_to_response('edx_pr_webhooks/index.html', context={
        'github_url': request.build_absolute_uri('{base_url}?{params}'.format(
            base_url=settings.GITHUB_OAUTH_AUTHORIZE_URL,
            params=urlencode(query)
        ))
    })


@require_POST
@csrf_exempt
def pull_request_created(request):
    request_body = json.loads(request.body)
    action = request_body['action']
    pull_request = request_body['pull_request']

    if request_body.has_key('pull_request') and action == 'opened':
        repo = Repo.objects.get(full_name=request_body['repository']['full_name'])
        template = loader.get_template('edx_pr_webhooks/pr_cover_letter.md')
        requests.patch(
            pull_request['url'],
            data=json.dumps({
                'title': pull_request['title'],
                'body': '{original_body}\n\n{cover_letter}'.format(
                    original_body=pull_request['body'],
                    cover_letter=template.render({'username': request_body['pull_request']['user']['login']})
                ),
                'state': pull_request['state']
            }),
            headers={'Authorization': 'token {access_token}'.format(access_token=repo.access_token)}
        )
    return HttpResponse()


@require_GET
def acquire_github_token(request):
    """
    Called by Github after a user has successfully authenticated this
    app.
    """
    state = request.GET['state']
    # Ensure that this request is coming from the Github user we want
    # to authorize, not a third party.
    if request.session['state'] != state:
        return HttpResponseForbidden('Your session has expired. Please try again.')
    # Get the temporary Github code to exchange for an OAuth token.
    code = request.GET['code']
    acquire_github_token_task.delay(code, state)
    return HttpResponseRedirect(reverse('index'))


@require_GET
def github_error_callback(request):
    """
    Called by Github in case of an API error. For now, just log the
    error.
    """
    print request.GET['error']
    return HttpResponse('')
