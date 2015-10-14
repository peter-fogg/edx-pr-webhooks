"""
URLs for working with Github.
"""
from django.conf.urls import include, url
from django.contrib import admin

from edx_pr_webhooks import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^login/token/$', views.acquire_github_token, name='acquire_github_token'),
    url(r'^login/token/error/$', views.github_error_callback, name='github_error_callback'),
    url(r'^pr/$', views.pull_request_created, name='pull_request_created'),
]
