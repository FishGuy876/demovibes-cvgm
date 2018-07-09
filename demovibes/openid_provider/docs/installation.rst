============
Requirements
============

Python OpenID library is required to run `openid_provider`.

Optional you can add django_openid_auth_ for its `DjangoOpenIDStore` - otherwise `openid_provider`
will use FileOpenIDStore which is less secure in shared hosting environments.

.. _django_openid_auth: https://launchpad.net/django-openid-auth


==================
Basic Installation
==================

1. Copy ``openid_provider`` into your project directory (or link to it).
2. Add ``'openid_provider'`` to ``INSTALLED_APPS``, openid_provider requre at least::

    'django.contrib.auth',
    'django.contrib.sessions',
    'openid_provider',
3. Add ``openid_provider/urls.py`` to your urlpatterns, e.g.::

    urlpatterns = patterns('',
        ...
        url(r'^openid/', include('openid_provider.urls')),
        ...
    )

4. Run::

    python manage.py syncdb
to create required tables to your database.

