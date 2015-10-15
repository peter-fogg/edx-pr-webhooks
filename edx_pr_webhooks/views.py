"""
Views for responding to Github API events.
"""

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from urllib import urlencode
from uuid import uuid4

import requests

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


@require_http_methods(('GET', 'POST'))
@csrf_exempt
def pull_request_created(request):
    print request.body
    return HttpResponse("Lookin' good.")


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
