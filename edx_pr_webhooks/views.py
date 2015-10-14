"""
Views for responding to Github API events.
"""

from django.http import HttpResponse


def pull_request_created(request):
    print request.body
    return HttpResponse("Lookin' good.")
