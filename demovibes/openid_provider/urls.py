# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 : */

from django.conf.urls.defaults import *

urlpatterns = patterns('openid_provider.views',
    url(r'^$', 'openid_server', name='openid-provider-root'),
    url(r'^decide/$', 'openid_decide', name='openid-provider-decide'),
    url(r'^xrds/$', 'openid_xrds', name='openid-provider-xrds'),
    url(r'^(?P<id>.*)/$', 'openid_xrds', {'identity': True}, name='openid-provider-identity'),
)
