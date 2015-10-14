"""
Views for responding to Github API events.
"""

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def pull_request_created(request):
    print request.body
    return HttpResponse("Lookin' good.")
